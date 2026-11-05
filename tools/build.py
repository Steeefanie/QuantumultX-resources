#!/usr/bin/env python3
"""从明确许可的上游生成 Quantumult X 域名规则；仅使用 Python 标准库。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import ipaddress
import json
import re
import sys
import tarfile
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

from config_templates import RAW_ROOT, render_full_config
from resource_library import create_plan as resource_plan, local_rule_plan

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/v2fly/domain-list-community'
SHARED = {
    'amazonaws.com', 'cloudfront.net', 'azure.com', 'azureedge.net',
    'windows.net', 'cloudflare.com', 'akamaihd.net', 'akamaized.net',
    'fastly.net', 'googleapis.com', 'googleusercontent.com', 'gstatic.com',
    'live.com', 'microsoft.com', 'sharepoint.com', 'sharepointonline.com',
    'auth0.com', 'algolia.net', 'intercom.io', 'intercomcdn.com',
    'launchdarkly.com', 'segment.io', 'sentry.io', 'stripe.com',
    'identrust.com', 'doubleclick.net', 'googletagmanager.com',
    'googleadservices.com', 'google-analytics.com',
}
# 仅在平台自身的上游分类中保留其根域名；第三方业务里仍隔离共享根域名。
FIRST_PARTY_SHARED = {
    'googleapis.com': {'google'}, 'googleusercontent.com': {'google'}, 'gstatic.com': {'google'},
    'live.com': {'microsoft'}, 'microsoft.com': {'microsoft'}, 'windows.net': {'microsoft'},
    'sharepoint.com': {'microsoft'}, 'sharepointonline.com': {'microsoft'},
    'azure.com': {'azure'}, 'azureedge.net': {'azure'},
    'cloudflare.com': {'cloudflare'}, 'amazonaws.com': {'aws'}, 'cloudfront.net': {'aws'},
}


def load_archive(content):
    """只在内存读取普通文件，不解压任意路径或符号链接。"""
    data = {}
    license_text = ''
    with tarfile.open(fileobj=io.BytesIO(content), mode='r:gz') as archive:
        commit = archive.pax_headers.get('comment', '')
        if not re.fullmatch('[0-9a-f]{40}', commit):
            raise ValueError('上游压缩包未包含可核验的提交标识')
        for item in archive:
            if not item.isfile():
                continue
            parts = item.name.split('/')
            if len(parts) == 3 and parts[1] == 'data':
                if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.!@+-]*', parts[2]):
                    raise ValueError(f'不安全的分类名：{parts[2]}')
                if item.size > 10_000_000:
                    raise ValueError('单个上游文件超过大小限制')
                data[parts[2]] = archive.extractfile(item).read().decode('utf-8')
            elif len(parts) == 2 and parts[1] == 'LICENSE':
                license_text = archive.extractfile(item).read().decode('utf-8')
    if not license_text.startswith('MIT License'):
        raise ValueError('上游许可已变化或不可确认，停止构建')
    if not data:
        raise ValueError('上游没有规则数据')
    return data, license_text, commit


class Resolver:
    def __init__(self, data):
        self.entries = defaultdict(list)
        self.memo = {}
        for name, text in data.items():
            for number, line in enumerate(text.splitlines(), 1):
                content = line.split('#', 1)[0].strip()
                if not content:
                    continue
                tokens = content.split()
                term = tokens[0]
                kind, sep, value = term.partition(':')
                if not sep:
                    kind, value = 'domain', term
                attrs = frozenset(t[1:] for t in tokens[1:] if t.startswith('@'))
                unknown = [t for t in tokens[1:] if not t.startswith(('@', '&'))]
                if unknown:
                    raise ValueError(f'{name}:{number} 未识别的附加字段')
                entry = (kind, value, attrs, name, number)
                self.entries[name].append(entry)
                for token in tokens[1:]:
                    if token.startswith('&'):
                        if kind == 'include':
                            raise ValueError('暂不支持 include 的 affiliation')
                        self.entries[token[1:]].append(entry)

    def resolve(self, name, stack=()):
        if name in stack:
            raise ValueError('循环引用：' + ' -> '.join((*stack, name)))
        if name in self.memo:
            return self.memo[name]
        if name not in self.entries:
            raise ValueError(f'引用不存在的分类：{name}')
        result = set()
        for entry in self.entries[name]:
            kind, value, attrs, source, line = entry
            if kind != 'include':
                result.add(entry)
                continue
            for child in self.resolve(value, (*stack, name)):
                tags = child[2]
                if all((tag[1:] not in tags if tag.startswith('-') else tag in tags) for tag in attrs):
                    result.add(child)
        self.memo[name] = tuple(sorted(result, key=lambda e: (e[0], e[1], tuple(sorted(e[2])), e[3], e[4])))
        return self.memo[name]


def normalize(entry, ads_only=False, include_ads=False, allow_shared=False):
    kind, value, attrs, source, line = entry
    if source == 'sources/local-additions.json' and kind in ('host', 'host-suffix', 'host-keyword', 'user-agent', 'ip-cidr'):
        if ads_only:
            return None, '不是广告属性规则'
        return (kind, value), ''
    if ads_only and 'ads' not in attrs:
        return None, '不是广告属性规则'
    if not ads_only and not include_ads and 'ads' in attrs:
        return None, '广告属性：不混入业务规则'
    if (ads_only or include_ads) and value in ('ad.12306.cn', 'optimus-ads.amap.com'):
        return None, '交由重写层处理响应：避免分流层直接断开导致开屏超时等待'
    if kind not in ('full', 'domain'):
        return None, '关键词或正则：不作无损转换声明'
    try:
        value = value.rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError:
        return None, '域名编码不合法'
    try:
        ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        return None, 'IP 地址不能作为域名条件直接转换'
    if len(value) > 253 or '.' not in value or any(
        not re.fullmatch(r'[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?', label)
        for label in value.split('.')
    ):
        return None, '域名格式或长度需要审查'
    if value in SHARED and not allow_shared:
        return None, '共享平台或身份服务根域名：需单独决定去向'
    return ('host' if kind == 'full' else 'host-suffix', value), ''


MODULE_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.!@+-]*')
BLOCK_COLLECTIONS = {
    'category-ads', 'category-ads-all', 'category-ads-and-telemetry',
    'category-ads-ir', 'category-telemetry',
}


def is_collection(name):
    return name.startswith(('category-', 'geolocation-', 'tld-')) or name in ('cn', 'private')


def snapshot_hash(data):
    digest = hashlib.sha256()
    for name, content in sorted(data.items()):
        for part in (name.encode(), content.encode()):
            digest.update(len(part).to_bytes(8, 'big'))
            digest.update(part)
    return digest.hexdigest()


def csv_text(columns, rows):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return '\ufeff' + output.getvalue()


def load_local_additions(resolver):
    """以独立来源注入明确主机名，不修改已锁定的上游快照。"""
    path = ROOT/'sources/local-additions.json'
    if not path.exists():
        return [], ''
    content = path.read_bytes()
    config = json.loads(content)
    if config.get('schema') != 1:
        raise ValueError('本地补充配置版本不支持')
    rows = []; seen = set()
    for number, item in enumerate(config.get('entries', []), 1):
        module = item.get('module'); host = item.get('domain', '')
        reference = item.get('reference', ''); checked = item.get('checked_on', '')
        reason = item.get('reason', '')
        if not isinstance(reason, str) or not reason.strip() or any(c in reason for c in '\r\n'):
            raise ValueError(f'本地补充第 {number} 项缺少有效说明')
        if module not in resolver.entries or not reference.startswith('https://') or any(c in reference for c in '\r\n'):
            raise ValueError(f'本地补充第 {number} 项缺少有效分类或来源')
        if date.fromisoformat(checked).isoformat() != checked:
            raise ValueError(f'本地补充第 {number} 项日期无效')
        kind = item.get('kind', 'full')
        if kind not in ('full', 'host', 'host-suffix', 'host-keyword', 'user-agent', 'ip-cidr'):
            raise ValueError(f'本地补充第 {number} 项匹配类型无效：{kind}')
        if (module, kind, host) in seen:
            raise ValueError(f'本地补充重复：{module} / {kind} / {host}')
        seen.add((module, kind, host))
        entry = (kind, host, frozenset(), 'sources/local-additions.json', number)
        rule, reason = normalize(entry)
        if not rule or rule[1] != host:
            raise ValueError(f'本地补充第 {number} 项域名无效：{reason}')
        resolver.entries[module].append(entry)
        rows.append({**item, 'index':number})
    return rows, hashlib.sha256(content).hexdigest()


def exclude_conditions(rules, excluded):
    """剔除被排除分类覆盖的条件；保留无法表达差集的宽泛父后缀并单独提示。"""
    suffixes = {value for kind,value in excluded if kind == 'host-suffix'}
    exact = {value for kind,value in excluded if kind == 'host'}
    kept = set(); removed = set(); broad = set()
    for kind, value in rules:
        labels = value.split('.')
        covered = any('.'.join(labels[i:]) in suffixes for i in range(len(labels)))
        if covered or (kind == 'host' and value in exact):
            removed.add((kind,value))
        else:
            kept.add((kind,value))
    for kind, value in excluded:
        labels = value.split('.')
        for i in range(len(labels)):
            ancestor = '.'.join(labels[i:])
            if ('host-suffix', ancestor) in kept:
                broad.add(('host-suffix',ancestor,kind,value))
    return kept, removed, broad


def service_names(resolver, manifest):
    """只对人工选定父组中的无条件 include 后代添加前缀，不推断股权关系。"""
    candidates = defaultdict(set)
    for parent in manifest.get('group_roots', []):
        if not MODULE_NAME.fullmatch(parent) or parent not in resolver.entries or is_collection(parent):
            raise ValueError(f'服务父组不存在或名称不合法：{parent}')
        pending = [parent]; seen = {parent}
        while pending:
            current = pending.pop()
            for kind, child, attrs, source, line in resolver.entries[current]:
                if kind != 'include' or attrs or child in seen:
                    continue
                if child not in resolver.entries:
                    raise ValueError(f'{parent} 引用不存在的分类：{child}')
                seen.add(child); pending.append(child)
                if not is_collection(child):
                    candidates[child].add(parent)
    names = {}; groups = {}; used = {}
    for original in sorted(resolver.entries):
        if is_collection(original):
            continue
        parent = next(iter(candidates[original])) if len(candidates[original]) == 1 else ''
        filename = original if not parent or original.startswith(parent+'-') else parent+'-'+original
        filename = manifest.get('filename_overrides', {}).get(original, filename)
        if not MODULE_NAME.fullmatch(filename):
            raise ValueError(f'服务文件名不合法：{filename}')
        if filename in used:
            raise ValueError(f'服务文件名冲突：{used[filename]} 与 {original} -> {filename}')
        names[original] = filename; groups[original] = parent; used[filename] = original
    missing = set(manifest.get('filename_overrides', {})) - set(names)
    if missing:
        raise ValueError('文件名映射引用不存在的服务：'+'、'.join(sorted(missing)))
    return names, groups


def describe_service(name, definition, rules, resolver, profiles):
    profile = profiles.get(name, {})
    parent = definition.get('parent', '')
    company = profile.get('provider', '')
    if not company:
        group_label = profiles.get(parent, {}).get('label', parent)
        company = (f'按上游 {group_label} 规则归组；具体运营主体未逐项核实' if parent
                   else '运营主体未核实，不根据分类名推断公司归属')
    description = profile.get('description')
    if not description:
        description = f'上游 {name} 分类的域名汇总，用于对这组服务地址设置独立连接策略。'
    if name in profiles and 'provider' not in profile:
        status = '服务用途说明；运营主体未单独核实'
    elif 'provider' in profile:
        status = '人工登记，依据所列官方页面；不等同于对全部域名的归属核验'
    else:
        status = '按上游分类生成基础说明，详细用途及主体待补充'
    refs = profile.get('references', [])
    if not refs:
        refs = [f'{REPO}/tree/{definition["commit"]}/data/{name}']
    for text in [company, description, status, *refs]:
        if not isinstance(text, str) or any(ch in text for ch in '\r\n'):
            raise ValueError(f'{name} 的服务说明包含不合法字段或换行')
    children = sorted({e[1] for e in resolver.entries[name] if e[0] == 'include'})
    return {'company':company, 'description':description, 'status':status, 'references':refs,
            'children':children}


def render_service(definition, rules, commit, info, annotation_date):
    name = definition['name']; filename = definition['filename']
    examples = '、'.join(value for kind,value in sorted(rules)[:3])
    children = '、'.join(info['children'][:10]) or '无直接 include 子分类'
    if len(info['children']) > 10:
        children += f' 等 {len(info["children"])} 项'
    parent = definition.get('parent') or '无已确认的命名前缀父组'
    local_count = len(definition.get('local_additions', []))
    return (
        f'# 名称：{filename}；原始分类：{name}\n'
        f'# 本地整理日期：{annotation_date}（北京时间；非上游更新时间，离线重建不自动刷新）\n'
        f'# 公司/组织：{info["company"]}\n'
        f'# 服务说明：{info["description"]}\n'
        f'# 说明状态：{info["status"]}\n'
        f'# 说明依据：{"、".join(info["references"])}\n'
        f'# 规则分组：{parent}；分组依据上游无条件 include，不代表股权或运营主体关系。\n'
        f'# 上游直接引用：{children}\n'
        f'# 覆盖：{len(rules)} 条域名条件；示例：{examples}。不承诺覆盖该服务的全部连接。\n'
        f'# 来源：{REPO}/tree/{commit}/data/{name}\n'
        f'# 本地补充：{local_count} 个明确主机名；核对日期和官方依据见 sources/local-additions.json；上游快照未修改。\n'
        '# 原作者：V2Fly / V2Ray 社区贡献者；上游许可：MIT\n'
        '# 本项目角色：收集、整理、格式转换和校验；原始域名数据贡献归上游作者与社区。\n'
        '# 本地修改：展开引用、去重、分离广告属性；共享根域名按原始分类保留或隔离。\n'
        '# 默认策略：proxy；请用 force-policy 指定实际去向，文件名前缀不决定匹配顺序。\n'
        '# 状态：静态校验通过不代表真实设备业务验证通过。\n'
        + ''.join(f'{kind}, {value}, proxy\n' for kind, value in sorted(rules))
    )


def render_collection(name, definition, rules, commit, annotation_date):
    source_links = '、'.join(f'{REPO}/tree/{commit}/data/{n}' for n in definition['include'])
    policy = definition['policy']
    return (
        f'# 名称：{name}；说明：{definition["title"]}\n'
        f'# 本地整理日期：{annotation_date}（北京时间；非上游更新时间，离线重建不自动刷新）\n'
        '# 公司/组织：本文件为分类集合，不将集合名称解释为某家公司的运营主体。\n'
        f'# 覆盖：{len(rules)} 条域名条件；包含的上游分类：{"、".join(definition["include"])}。\n'
        f'# 排除分类：{"、".join(definition.get("exclude", [])) or "未设置"}；排除专用条件不等于隔离共享登录或接口。\n'
        '# 排除边界：可能保留覆盖被排除子域名的宽泛父后缀；独立业务规则应优先匹配。\n'
        f'# 来源：{source_links}\n'
        f'# 本地补充：{len(definition.get("local_additions", []))} 个明确主机名；核对日期和官方依据见 sources/local-additions.json。\n'
        '# 原作者：V2Fly / V2Ray 社区贡献者；上游许可：MIT\n'
        '# 本项目角色：收集、整理、格式转换和校验；感谢原始规则作者与开源社区。\n'
        '# 本地修改：展开引用、合并去重并转换为 Quantumult X 域名规则；正文不引用外部文件。\n'
        '# 边界：关键词、正则及不合法条件未转换；共享根域名按原始分类处理。\n'
        f'# 属性：广告属性条件{"保留（可选拦截集合）" if definition.get("include_ads") else "排除"}。\n'
        f'# 默认策略：{policy}；可用 force-policy 覆盖。集合不保证覆盖所有网站或与其他集合互斥。\n'
        '# 状态：尚未完成真实设备业务验证；专用业务规则应优先于可能覆盖它的综合规则。\n'
        + ''.join(f'{kind}, {value}, {policy}\n' for kind, value in sorted(rules))
    )


def create_plan(data, license_text, commit, archive_hash, manifest):
    """先在内存生成全部文件；缺失引用或配置错误时不改动工作目录。"""
    if not license_text.startswith('MIT License'):
        raise ValueError('上游许可已变化或不可确认')
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('上游提交标识不合法')
    if not re.fullmatch('[0-9a-f]{64}', archive_hash):
        raise ValueError('上游压缩包哈希不合法')
    if manifest.get('schema') not in (1, 2):
        raise ValueError('不支持的选择配置版本')
    resolver = Resolver(data)
    local_additions, additions_hash = load_local_additions(resolver)
    annotation_date = manifest.get('annotation_date', '')
    try:
        if date.fromisoformat(annotation_date).isoformat() != annotation_date:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError('请在选择配置中登记 annotation_date，格式为 YYYY-MM-DD') from None
    profile_file = ROOT/'sources/service-info.json'
    profiles = json.loads(profile_file.read_text()) if profile_file.exists() else {}
    filenames, groups = service_names(resolver, manifest)
    preferred = manifest['services']
    missing = sorted(set(preferred) - set(resolver.entries))
    if missing:
        raise ValueError('指定服务分类不存在：' + ', '.join(missing))
    definitions = {}
    for name in sorted(resolver.entries):
        if not MODULE_NAME.fullmatch(name):
            raise ValueError(f'分类名不能用作安全文件名：{name}')
        collection = is_collection(name)
        selected = name in preferred or manifest.get('all_collections' if collection else 'all_services', False)
        if not selected:
            continue
        blocked = name in BLOCK_COLLECTIONS
        folder = 'collections' if collection else 'services'
        filename = name if collection else filenames[name]
        path = f'filter/{folder}/{filename}.list'
        definitions[path] = {
            'name': name, 'title': preferred.get(name, '上游综合分类' if collection else '上游服务分类'),
            'include': [name], 'policy': 'reject' if blocked else ('direct' if name in ('cn', 'geolocation-cn', 'private') else 'proxy'),
            'include_ads': blocked, 'type': '上游集合' if collection else '服务分类',
            'required': name in preferred,
            'filename': filename, 'parent': groups.get(name, ''), 'commit': commit,
        }
    for name, definition in manifest.get('collections', {}).items():
        if not MODULE_NAME.fullmatch(name):
            raise ValueError(f'集合名不合法：{name}')
        path = f'filter/collections/{name}.list'
        if path in definitions:
            raise ValueError(f'集合与上游分类重名：{name}')
        if not definition.get('include') or definition.get('policy') not in ('direct', 'proxy', 'reject'):
            raise ValueError(f'集合缺失来源或策略错误：{name}')
        if not isinstance(definition.get('title'), str) or '\n' in definition['title']:
            raise ValueError(f'集合说明不合法：{name}')
        for source in definition['include'] + definition.get('exclude', []):
            if source not in resolver.entries:
                raise ValueError(f'{name} 引用不存在的分类：{source}')
        definitions[path] = {**definition, 'name': name, 'type': '常用集合', 'required': True}
    files = {}; review = []; inventory = []; membership = []; descriptions = []; migrations = []; exclusions = []
    owners = defaultdict(set); unique = set(); counts = defaultdict(int)
    cache = {}; resolved_rules = {}

    def convert(source, include_ads, service_mode=False):
        key = (source, include_ads, service_mode)
        if key not in cache:
            safe = set(); excluded = []
            for entry in resolver.resolve(source):
                if not service_mode and entry[0] in ('host-keyword', 'user-agent', 'ip-cidr'):
                    continue
                rule, reason = normalize(entry, include_ads=include_ads,
                                         allow_shared=entry[3] in FIRST_PARTY_SHARED.get(entry[1], set()))
                if rule:
                    safe.add(rule)
                else:
                    excluded.append((entry, reason))
            cache[key] = (safe, excluded)
        return cache[key]

    for path, definition in definitions.items():
        safe = set(); excluded = set(); include_ads = definition.get('include_ads', False)
        service_mode = (definition['type'] == '服务分类')
        for source in definition['include']:
            rules, skipped = convert(source, include_ads, service_mode=service_mode)
            safe.update(rules); excluded.update(skipped)
            membership.append({'集合文件': path, '上游分类': source, '可转换条件数': len(rules), '默认策略': definition['policy']})
        excluded_rules = set()
        for source in definition.get('exclude', []):
            excluded_rules.update(convert(source, True)[0])
        if excluded_rules:
            safe, removed, broad = exclude_conditions(safe, excluded_rules)
            excluded_names = ' / '.join(definition['exclude'])
            for kind,value in sorted(removed):
                exclusions.append({'集合文件':path, '排除分类':excluded_names, '处理':'剔除专用条件',
                                   '集合条件':f'{kind}, {value}', '被覆盖的排除条件':'',
                                   '说明':'已从当前合集正文中移除；其他业务的共享接口不能完全分离'})
            for kind,value,child_kind,child_value in sorted(broad):
                exclusions.append({'集合文件':path, '排除分类':excluded_names, '处理':'保留宽泛父后缀，需顺序控制',
                                   '集合条件':f'{kind}, {value}', '被覆盖的排除条件':f'{child_kind}, {child_value}',
                                   '说明':'删除父后缀会影响其他服务；请让被排除业务的独立规则优先于本合集'})
        local_indexes = {e[4] for source in definition['include'] for e in resolver.resolve(source)
                         if e[3] == 'sources/local-additions.json' and (
                             ('host' if e[0] == 'full' else e[0]), e[1]) in safe}
        definition['local_additions'] = [r for r in local_additions if r['index'] in local_indexes]
        for entry, reason in sorted(excluded, key=lambda item: (item[0][3], item[0][4], item[1])):
            kind, value, attrs, source, line = entry
            review.append({'服务': definition['name'], '输出文件': path, '源文件': source, '行号': line,
                           '类型': kind, '内容': value, '原因': reason})
        if not safe and definition['required']:
            raise ValueError(f'{path} 没有可转换的域名条件，停止构建')
        info = None
        if definition['type'] == '服务分类':
            info = describe_service(definition['name'], definition, safe, resolver, profiles)
            descriptions.append({'原始分类':definition['name'], '规则文件':path if safe else '',
                                 '排序父组':definition['parent'], '公司或组织':info['company'],
                                 '服务说明':info['description'], '说明状态':info['status'],
                                 '依据':' / '.join(info['references']), '本地整理日期':annotation_date})
            old_path = f'rules/services/{definition["name"]}.list'
            if safe and old_path != path:
                migrations.append({'原规则文件':old_path, '新规则文件':path, '排序父组':definition['parent'],
                                   '说明':'文件名按上游包含关系调整；转换修正另见版本说明；发布后需更新旧订阅地址'})
        row = {'服务': definition['name'], '分类': definition['title'], '类型': definition['type'],
               '已构建': bool(safe), '域名规则数': len(safe), '待审查数': len(excluded),
               '规则文件': path if safe else '', '默认策略': definition['policy'],
               '上游分类': ' / '.join(definition['include']),
               '来源': ' / '.join(f'{REPO}/tree/{commit}/data/{n}' for n in definition['include'])
                      + (' / sources/local-additions.json（官方文档补充）' if local_indexes else ''),
               '说明': (info['description'] if info else definition['title']) if safe else '无可转换域名条件；未生成空订阅文件',
               '排序父组':definition.get('parent', ''), '本地整理日期':annotation_date,
               '排除分类':' / '.join(definition.get('exclude', []))}
        inventory.append(row)
        if not safe:
            continue
        if definition['type'] != '服务分类':
            migrations.append({'原规则文件':'rules/collections/'+Path(path).name, '新规则文件':path,
                               '排序父组':'', '说明':'分流目录由 rules 改为 filter；部分合集原为本地待发布文件'})
        files[path] = (render_service(definition, safe, commit, info, annotation_date) if info
                       else render_collection(definition['name'], definition, safe, commit, annotation_date))
        resolved_rules[path] = safe
        counts['services' if definition['type'] == '服务分类' else 'collections'] += 1
        counts['conditions'] += len(safe); unique.update(safe)
        for key in safe:
            owners[key].add(path)
    # 分类未选中时也在目录中如实标记，方便检查覆盖范围。
    represented = {s for d in definitions.values() for s in d['include']}
    for name in sorted(set(resolver.entries) - represented):
        inventory.append({'服务':name, '分类':'其他上游分类', '类型':'未选分类', '已构建':False,
                          '域名规则数':'', '待审查数':'', '规则文件':'', '默认策略':'', '上游分类':name,
                          '来源':f'{REPO}/tree/{commit}/data/{name}', '说明':'配置未选择',
                          '排序父组':'', '本地整理日期':annotation_date, '排除分类':''})
    shared_rows = []
    for name, entries in sorted(resolver.entries.items()):
        for entry in entries:
            kind, value, attrs, source, line = entry
            if kind not in ('domain','full') or value not in SHARED:
                continue
            allowed = source in FIRST_PARTY_SHARED.get(value, set())
            shared_rows.append({'原始分类':name, '源文件':source, '行号':line, '域名':value,
                                '处理':'平台自身分类保留' if allowed else '共享根域名隔离'})
    resource_summary = None
    if (ROOT/'sources/rewrites.json').exists():
        resource_files, resource_summary = resource_plan(ROOT, RAW_ROOT)
        files.update(resource_files)
    local_paths = {}
    if manifest.get('local_rules'):
        local_files, local_paths = local_rule_plan(ROOT, manifest['local_rules'], annotation_date)
        files.update(local_files)
    for profile, items in manifest.get('personal_profiles', {}).items():
        if not MODULE_NAME.fullmatch(profile) or not items:
            raise ValueError(f'个人资源清单名称不合法或为空：{profile}')
        lines = [f'# {profile} 个人分流资源清单，不是可以整体订阅的分流规则文件。',
                 '# 将所需条目复制到主配置已有的[filter_remote]段；不要把这个txt作为单个分流资源添加。',
                 '# 一行对应一个独立资源，可分别绑定不同地区、节点或策略组；不合并规则正文。',
                 '# 代理默认使用Global；按需将单项改为Hong Kong / Taiwan / Japan / Singapore / United States / South Korea等已有地区策略组，不按服务创建策略组。',
                 '# Global可选择地区组；地区组再选择相应节点。所有自定义策略组须已在主配置中定义。',
                 '# 直连与拒绝按Quantumult X语法写direct/reject；所有条目默认启用。',
                 '# YouTube优先于Google；OneDrive等子项例外优先于Microsoft等父组。以客户端展开后的顺序为准。',
                 '[filter_remote]']
        seen_paths = set()
        for order, item in enumerate(items, 1):
            source = item['source']
            if item['kind'] == 'service' and source in filenames:
                path = f'filter/services/{filenames[source]}.list'
            elif item['kind'] == 'collection' and MODULE_NAME.fullmatch(source):
                path = f'filter/collections/{source}.list'
            elif item['kind'] == 'local' and source in local_paths:
                path = local_paths[source]
            else:
                raise ValueError(f'{profile} 的资源类型或分类无效：{source}')
            if path not in files or path in seen_paths:
                raise ValueError(f'{profile} 的资源未生成或重复：{path}')
            seen_paths.add(path)
            tag = item['tag']; policy = item['policy']
            if any(not isinstance(v,str) or not v.strip() or any(c in v for c in ',=\r\n') for v in (tag,policy)):
                raise ValueError(f'{profile} 的资源标签或策略名不合法：{source}')
            if item.get('optional'):
                lines.append('# 可选子项例外：仅在本项需要独立策略时启用。')
            enabled = bool(item.get('enabled', True))
            lines.append(f'{RAW_ROOT}/{path}, '
                         f'tag={tag}, force-policy={policy}, inserted-resource=true, update-interval=86400, opt-parser=false, enabled={str(enabled).lower()}')
        lines.extend(['', '# 主配置中的国内直连、IP补充和final继续按实际需求管理。',
                      '# 每条资源的策略独立设置；同一请求匹配多个资源时，仍需检查实际匹配顺序。'])
        filter_text = '\n'.join(lines)+'\n'
        files[f'examples/quantumult_{profile}.conf'] = render_full_config(profile, filter_text, annotation_date)
    summary = {'项目':REPO, '许可':'MIT', '提交':commit, '压缩包SHA256':archive_hash,
               '快照内容SHA256':snapshot_hash(data), '上游文件数':len(data), '上游含虚拟分类数':len(resolver.entries),
               '构建模块数':counts['services']+counts['collections'], '服务模块数':counts['services'],
               '综合集合数':counts['collections'], '域名规则数':counts['conditions'],
               '去重域名条件数':len(unique), '未生成分类数':sum(not r['已构建'] for r in inventory),
               '本地整理日期':annotation_date, '文件改名数':sum(Path(r['原规则文件']).name != Path(r['新规则文件']).name for r in migrations), '分流路径迁移数':len(migrations),
               '本地补充主机名数':len(local_additions), '本地补充SHA256':additions_hash,
               '保留平台根域名数':len({r['域名'] for r in shared_rows if r['处理'] == '平台自身分类保留'})}
    if resource_summary:
        summary.update({'重写模块数':resource_summary['module_count'],'完整脚本数':resource_summary['script_count'],
                        '重写配套分流数':resource_summary['companion_filter_count']})
    summary['本地兼容规则数'] = len(local_paths)
    summary['分流文件总数'] = sum(p.startswith('filter/') and p.endswith('.list') for p in files)
    files['sources/lock.json'] = json.dumps(summary, ensure_ascii=False, indent=2)+'\n'
    return files, summary


def read_snapshot():
    lock = json.loads((ROOT/'sources/lock.json').read_text())
    # 保留原始换行；新快照可能同时包含 LF 与 CRLF，不能由文本读取静默归一化。
    data = {p.name:p.read_bytes().decode('utf-8') for p in sorted((ROOT/'sources/v2fly/data').iterdir()) if p.is_file()}
    if lock.get('快照内容SHA256') and snapshot_hash(data) != lock['快照内容SHA256']:
        raise ValueError('上游快照与锁定记录不一致，请核实或从上游压缩包重新构建')
    license_text = (ROOT/'sources/v2fly/LICENSE').read_text()
    return data, license_text, lock


def write_plan(files):
    for name, text in files.items():
        path = ROOT/name
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix+'.tmp')
        temporary.write_bytes(text.encode('utf-8'))
        temporary.replace(path)
    for folder, pattern in (('filter/services','*.list'), ('filter/collections','*.list'), ('filter/custom','*.list'),
                            ('filter/adblock','*.list'),
                            ('rewrite','*.conf'), ('scripts/app2smile','*.js'), ('scripts/fmz200','*.js')):
        for path in (ROOT/folder).rglob(pattern):
            if path.relative_to(ROOT).as_posix() not in files:
                path.unlink()
    for base in (ROOT/'rewrite', ROOT/'scripts/fmz200'):
        for path in sorted(base.rglob('*'), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()


def build(content):
    data, license_text, commit = load_archive(content)
    manifest = json.loads((ROOT/'sources/selection.json').read_text())
    files, summary = create_plan(data, license_text, commit, hashlib.sha256(content).hexdigest(), manifest)
    # 全部分类及输出已成功解析后再更新上游快照和生成文件。
    source_dir = ROOT/'sources/v2fly/data'; source_dir.mkdir(parents=True, exist_ok=True)
    for name, text in data.items():
        (source_dir/name).write_bytes(text.encode('utf-8'))
    (ROOT/'sources/v2fly/LICENSE').write_text(license_text)
    (ROOT/'LICENSE').write_text(license_text)
    for path in source_dir.iterdir():
        if path.is_file() and path.name not in data:
            path.unlink()
    write_plan(files)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def rebuild():
    data, license_text, lock = read_snapshot()
    manifest = json.loads((ROOT/'sources/selection.json').read_text())
    files, summary = create_plan(data, license_text, lock['提交'], lock['压缩包SHA256'], manifest)
    write_plan(files)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def validate():
    data, license_text, lock = read_snapshot()
    manifest = json.loads((ROOT/'sources/selection.json').read_text())
    expected, summary = create_plan(data, license_text, lock['提交'], lock['压缩包SHA256'], manifest)
    errors = []
    for name, content in expected.items():
        path = ROOT/name
        if not path.is_file() or path.read_bytes() != content.encode('utf-8'):
            errors.append(f'缺失或与上游快照及转换规则不一致：{name}')
    for folder, pattern in (('filter/services','*.list'), ('filter/collections','*.list'), ('filter/custom','*.list'),
                            ('filter/adblock','*.list'),
                            ('rewrite','*.conf'), ('scripts/app2smile','*.js'), ('scripts/fmz200','*.js')):
        for path in (ROOT/folder).rglob(pattern):
            if path.relative_to(ROOT).as_posix() not in expected:
                errors.append(f'存在不在构建计划中的规则文件：{path.relative_to(ROOT)}')
    if (ROOT/'LICENSE').read_text() != license_text:
        errors.append('根目录许可与上游许可不一致')
    if errors:
        raise ValueError('\n'.join(errors))
    print(f'校验通过：{summary["服务模块数"]} 个服务、{summary["综合集合数"]} 个集合，'
          f'累计 {summary["域名规则数"]} 条条件，去重 {summary["去重域名条件数"]} 条')
    if summary.get('重写模块数'):
        print(f'资源校验通过：{summary["重写模块数"]} 个重写、{summary["完整脚本数"]} 个完整脚本、'
              f'{summary["重写配套分流数"]} 个配套分流、{summary["本地兼容规则数"]} 个本地兼容分流')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--archive', type=Path, help='使用本地上游 tar.gz 构建')
    action.add_argument('--refresh', action='store_true', help='下载最新上游并构建；不会自动提交或推送')
    action.add_argument('--rebuild', action='store_true', help='使用已锁定的本地快照重新生成，无需访问上游')
    parser.add_argument('--check', action='store_true', help='检查规则、CSV及来源锁定记录')
    args = parser.parse_args()
    if args.refresh:
        req = urllib.request.Request('https://codeload.github.com/v2fly/domain-list-community/tar.gz/refs/heads/master',
                                     headers={'User-Agent':'QuantumultX-resources-maintenance'})
        with urllib.request.urlopen(req,timeout=60) as response:
            content = response.read(20_000_001)
        if len(content) > 20_000_000:
            raise ValueError('上游包超过大小限制')
        build(content)
    elif args.archive:
        build(args.archive.read_bytes())
    elif args.rebuild:
        rebuild()
    if args.check or args.refresh or args.archive or args.rebuild:
        validate()
    else:
        parser.print_help()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'失败：{exc}', file=sys.stderr)
        sys.exit(1)
