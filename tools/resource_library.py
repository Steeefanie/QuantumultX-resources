"""从固定来源构建重写配置与完整脚本，不在构建时访问网络。"""
import csv
import hashlib
import io
import json
from pathlib import PurePosixPath
import re

from rewrite_catalog import create_plan as catalog_plan
from script_headers import annotate_script


def csv_text(columns, rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader(); writer.writerows(rows)
    return '\ufeff'+buffer.getvalue()


def create_plan(root, raw_root):
    manifest = json.loads((root/'sources/rewrites.json').read_text())
    if manifest.get('schema') != 1 or manifest.get('license') != 'MIT':
        raise ValueError('重写来源配置版本或许可不支持')
    commit = manifest['commit']; repository = manifest['repository']
    if repository != 'app2smile/rules' or not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('重写来源缺少已核查仓库或固定提交')
    source = {}; files = {}; rows = []; scripts = {}; module_ids = set()
    for path, digest in manifest['files'].items():
        parts = PurePosixPath(path)
        if parts.is_absolute() or '..' in parts.parts:
            raise ValueError('重写来源路径不安全')
        content = (root/'sources/app2smile'/path).read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError('重写来源内容与固定哈希不符：'+path)
        source[path] = content.decode('utf-8')
    license_text = source[manifest['license_path']]
    if not license_text.startswith('MIT License') or 'app2smile' not in license_text:
        raise ValueError('重写来源许可文本与预期不符')
    files['rewrite/licenses/app2smile-MIT.txt'] = license_text
    files['scripts/app2smile/LICENSE.md'] = license_text
    resource_lines = ['# 将所需资源行复制到主配置的 [rewrite_remote]，不要把本文件当作单个重写订阅。',
                      '# 全部默认关闭；同一业务选择一套重写，启用前在本机配置并信任自己的 MITM 证书。',
                      '# 具体功能、兼容限制与上游出处见 rewrite/README.md；不提供付费服务可用性承诺。',
                      '[rewrite_remote]']
    companion_lines = ['# 仅在使用对应重写时按需启用；不要 force-policy=direct 或 PROXY 覆盖拦截。',
                       '# 放在宽泛业务规则之前，并检查实际命中；源规则包含域名和 IP 条件。', '[filter_remote]']
    companions = {}
    for module in manifest['modules']:
        name = module['id']
        if not re.fullmatch('[a-z][a-z0-9-]*', name) or name in module_ids:
            raise ValueError('重写模块名称不合法或重复')
        module_ids.add(name)
        body = source[module['source']]
        dependencies = re.findall(r'https://raw\.githubusercontent\.com/app2smile/rules/(?:master|main)/([^\s]+\.js)', body)
        if set(dependencies) != set(module['scripts']):
            raise ValueError('重写声明依赖与正文不一致：'+name)
        outputs = []
        for dependency in dependencies:
            if dependency not in source or not dependency.startswith('js/'):
                raise ValueError('缺少完整脚本正文：'+dependency)
            target = 'scripts/app2smile/'+PurePosixPath(dependency).name
            if target in scripts and scripts[target] != dependency:
                raise ValueError('脚本文件名冲突：'+target)
            scripts[target] = dependency
            files[target] = annotate_script(root,target,source[dependency],repository,commit,dependency,'MIT')
            for branch in ('master','main'):
                body = body.replace(f'https://raw.githubusercontent.com/{repository}/{branch}/{dependency}', f'{raw_root}/{target}')
            outputs.append(target)
        if re.search(r'\burl\s+script-\S+\s+(?!'+re.escape(raw_root+'/')+r')https?://', body):
            raise ValueError('仍有未收录的外部脚本入口：'+name)
        category = module.get('category', '')
        path = f'rewrite/{category}/{name}.conf' if category else f'rewrite/{name}.conf'
        companion_outputs = []
        for dependency in module.get('filters', []):
            target = f'filter/adblock/{name}.list'
            if dependency not in source or target in companions:
                raise ValueError('配套分流缺失或输出重复：'+dependency)
            companions[target] = dependency
            files[target] = (f'# {module["title"]}的配套分流；来源：{repository}@{commit}/{dependency}\n'
                             f'# 本地整理日期：{manifest["checked_on"]}；保留原文，许可见 rewrite/licenses/app2smile-MIT.txt。\n'
                             +source[dependency])
            companion_outputs.append(target)
            companion_lines.append(f'{raw_root}/{target}, tag={module["title"]}配套分流, force-policy=reject, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=false')
        header = (f'# 名称：{module["title"]}\n# 用途：{module.get("description",module["title"])}\n# 本地整理日期：{manifest["checked_on"]}；来源版本固定，不是实时同步。\n'
                  f'# 原作者与来源：https://github.com/{repository}/blob/{commit}/{module["source"]}\n'
                  '# 许可：MIT，原始版权及完整许可见 rewrite/licenses/app2smile-MIT.txt。\n'
                  '# 本地修改：保留原重写正文，仅把直接脚本依赖改为本仓库完整脚本地址。\n'
                  '# 状态：未完成真实设备业务验证；具体 App 版本、iOS 要求与功能限制见上游原文。\n')
        files[path] = header+body.rstrip()+'\n'
        resource_lines.append(f'{raw_root}/{path}, tag={module["title"]}, update-interval=86400, opt-parser=false, enabled=false')
        rows.append({'模块':f'{category}/{name}' if category else name,'用途':module.get('description',module['title']),'重写文件':path,'源文件':module['source'],
                     '上游提交':commit,'核对日期':manifest['checked_on'],'许可':'MIT',
                     '脚本文件':' / '.join(outputs),'配套分流':' / '.join(companion_outputs),
                     'MITM':'需要个人证书及对应 hostname' if module.get('needs_mitm',True) else '仅 HTTP 条目，不要求 HTTPS 解密','默认启用':False,
                     '设备验证':'未完成','限制':module['notes']})
    for notice in manifest.get('third_party_licenses', []):
        path = root/notice['path']
        path.resolve().relative_to((root/'sources/third-party-licenses').resolve())
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != notice['sha256']:
            raise ValueError('脚本依赖许可与登记哈希不符：'+notice['path'])
        files['scripts/licenses/'+path.name] = content.decode('utf-8')
    remotes_file = root/'sources/remote-resources.lock.json'
    if remotes_file.exists():
        remotes = json.loads(remotes_file.read_text())
        for resource in remotes.get('resources', []):
            source_rel = resource.get('source_path')
            local_rel = resource.get('local_path')
            if source_rel and local_rel:
                src_path = root/source_rel
                src_path.resolve().relative_to((root/'sources/remote').resolve())
                raw_bytes = src_path.read_bytes()
                if hashlib.sha256(raw_bytes).hexdigest() != resource['sha256']:
                    raise ValueError('收录工具脚本与锁定哈希不符：'+source_rel)
                files[local_rel] = raw_bytes.decode('utf-8')
    catalog_files,catalog_rows,catalog_review,catalog_summary = catalog_plan(root,raw_root,files)
    files.update(catalog_files); rows.extend(catalog_rows)
    combined_adblock = []
    seen_adblock = set()
    for path in sorted(p for p in files if p.startswith('filter/adblock/') and p.endswith('.list')):
        for line in files[path].splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(('#',';','//')):
                continue
            key = re.sub(r'\s+', '', stripped.lower())
            if key not in seen_adblock:
                seen_adblock.add(key)
                combined_adblock.append(stripped)
    files['filter/adblock/combined.list'] = (
        f'# 名称：重写配套去广告合集（合并自全部 27 份 filter/adblock/*.list）\n'
        f'# 本地整理日期：{manifest["checked_on"]}；共 {len(combined_adblock)} 条去重域名与 IP 拦截条件。\n'
        '# 说明：供主配置单条订阅使用，避免在 Quantumult X 分流界面展开 27 条独立 reject 项。\n'
        '# 许可：MIT（app2smile）与 GPL-3.0（fmz200），详见 rewrite/licenses/。\n'
        + '\n'.join(combined_adblock) + '\n'
    )
    catalog_lines = ['# 重写模块清单', '', '由锁定来源生成；全部默认关闭，同一业务选择一套。依赖齐全不等于已通过设备验证。', '',
                     '| 模块 | 用途 | 许可 | 收录范围 | 配套分流 |', '| --- | --- | --- | --- | --- |']
    for row in rows:
        state = '基础条目，有隔离行' if '有脚本行隔离' in row['限制'] else '配置和直接依赖已收录'
        link = row['重写文件'].removeprefix('rewrite/')
        companion = f"[需要时启用](../{row['配套分流']})" if row['配套分流'] else '无'
        catalog_lines.append(f"| [{row['模块']}]({link}) | {row['用途'].replace('|',' / ')} | {row['许可']} | {state} | {companion} |")
    catalog_lines.extend(['', '隔离行号及说明详见对应重写文件头部注释。只有域名/IP 条件的来源不会生成空重写，相关拦截保存在配套分流目录。'])
    files['rewrite/catalog.md'] = '\n'.join(catalog_lines)+'\n'
    records = [{'source':path,'source_sha256':manifest['files'][path],
                'url':f'https://raw.githubusercontent.com/{repository}/{commit}/{path}'} for path in sorted(source)]
    summary = {'schema':1,'repository':repository,'commit':commit,'checked_on':manifest['checked_on'],
               'module_count':len(module_ids)+catalog_summary['modules'],'script_count':len(scripts)+catalog_summary['scripts'],
               'companion_filter_count':len(companions)+catalog_summary['filters'],'sources':records,
               'additional_projects':catalog_summary['projects'],
               'partial_module_count':sum('有脚本行隔离' in row['限制'] for row in rows),
               'complete_direct_dependency_count':sum('有脚本行隔离' not in row['限制'] for row in rows),
               'outputs':{p:hashlib.sha256(t.encode('utf-8')).hexdigest() for p,t in sorted(files.items())}}
    files['sources/rewrites.lock.json'] = json.dumps(summary,ensure_ascii=False,indent=2)+'\n'
    return files, summary


def local_rule_plan(root, definitions, annotation_date):
    files = {}; paths = {}
    for item in definitions:
        name = item['id']; source = item['source']
        if not re.fullmatch('[a-z][a-z0-9-]*', name) or name in paths:
            raise ValueError('本地兼容规则名称不合法或重复')
        path = root/source
        path.resolve().relative_to((root/'sources/local').resolve())
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != item['sha256']:
            raise ValueError('本地兼容规则与登记的原文哈希不符：'+source)
        safe = set()
        for line in content.decode('utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith(('#',';','//')):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 3 or parts[0] not in ('host','host-suffix') or parts[2] != 'proxy':
                raise ValueError('原有 OneDrive 兼容规则出现未支持的条件：'+source)
            if not re.fullmatch(r'[a-z0-9.-]+\.[a-z0-9-]+',parts[1]):
                raise ValueError('本地兼容规则域名不合法：'+source)
            safe.add(tuple(parts[:2]))
        if not safe:
            raise ValueError('本地兼容规则为空：'+source)
        output = f'filter/custom/{name}.list'; paths[name] = output
        files[output] = (f'# 名称：{item["title"]}\n# 本地整理日期：{annotation_date}；正文沿用用户此前的本地规则。\n'
                         f'# 来源原文：{source}；不冒充 V2Fly 社区规则。\n'
                         '# 边界：按目标域名划分，无法保证区分网页与同步客户端；两份规则存在交叉。\n'
                         '# 使用：Web 条目优先于 Sync；force-policy 决定实际策略。共享登录和租户域名可能影响其他 Microsoft 服务。\n'
                         +content.decode('utf-8'))
    return files, paths
