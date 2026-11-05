#!/usr/bin/env python3
"""只读比较上游版本与固定脚本哈希；不刷新、提交或推送任何规则。需要 curl。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote, urlencode

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r'[0-9a-f]{40}')


def download(url):
    result = subprocess.run(
        ['curl', '--fail', '--silent', '--show-error', '--location', '--proto', '=https',
         '--proto-redir', '=https', '--connect-timeout', '10', '--max-time', '30',
         '--max-filesize', '10000000', '--user-agent', 'QuantumultX-resources-update-check', url],
        capture_output=True, timeout=40, check=False)
    if result.returncode:
        raise ValueError(f'下载失败，curl 状态 {result.returncode}：{url}')
    if len(result.stdout) > 10_000_000:
        raise ValueError('响应超过大小限制')
    return result.stdout


def api(endpoint):
    return json.loads(download('https://api.github.com/repos/'+endpoint))


def check_sha(value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError('上游提交标识无效')
    return value


def check_snapshot(repository, branch, pinned):
    latest = check_sha(api(f'{repository}/commits/{quote(branch, safe="")}')['sha'])
    return {'name':repository, 'status':'有新提交，待审阅' if latest != pinned else '版本未变',
            'pinned':pinned, 'latest':latest,
            'details':f'https://github.com/{repository}/compare/{pinned}...{latest}'}


def check_resource(resource):
    repository = resource['repository']; path = resource['path']
    pinned = check_sha(resource['commit'])
    expected = f'https://raw.githubusercontent.com/{repository}/{pinned}/{path}'
    if resource['url'] != expected or not re.fullmatch(r'[0-9a-f]{64}', resource['sha256']):
        raise ValueError('锁定地址或哈希无效')
    if hashlib.sha256(download(expected)).hexdigest() != resource['sha256']:
        raise ValueError('固定版本当前内容与锁定哈希不符；不要加载或覆盖旧记录')
    query = urlencode({'sha':resource['branch'], 'path':path, 'per_page':1})
    commits = api(f'{repository}/commits?{query}')
    if not isinstance(commits, list) or not commits:
        raise ValueError('未找到该文件的上游提交')
    latest = check_sha(commits[0]['sha'])
    content = download(f'https://raw.githubusercontent.com/{repository}/{latest}/{path}')
    current_hash = hashlib.sha256(content).hexdigest()
    changed = current_hash != resource['sha256']
    return {'name':resource['id'], 'status':'内容有变化，待审阅' if changed else '内容未变，哈希一致',
            'pinned':pinned, 'latest':latest, 'pinned_sha256':resource['sha256'],
            'latest_sha256':current_hash,
            'details':f'https://github.com/{repository}/compare/{pinned}...{latest}'}


def markdown(rows, checked):
    lines = ['# 上游只读更新检查', '', f'查询时间：{checked}。', '',
             '发现变更只作报告，未改动版本、规则、模板或策略。接口失败不计为没有更新。', '',
             '| 来源 | 状态 | 锁定提交 | 查询到的提交 |', '| --- | --- | --- | --- |']
    for row in rows:
        status = row['status']; name = row['name']
        if row.get('details'):
            name = f'[{name}]({row["details"]})'
        lines.append(f'| {name} | {status} | {row.get("pinned", "—")[:12]} | {row.get("latest", "—")[:12]} |')
    lines.extend(['', '脚本比较内容哈希；数据与图标比较上游分支提交，不据此判断变更是否影响当前选用文件。',
                  '分支已更新也可能只涉及说明文件。固定入口可用不代表其内部引用全部固定，亦不代表完成设备验证。',
                  'Google 官方文档中的本地补充端点仍需人工复核：sources/local-additions.json。'])
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='将 Markdown 报告写到指定位置，建议放在仓库外')
    args = parser.parse_args()
    rows = []
    lock = json.loads((ROOT/'sources/lock.json').read_text())
    remotes = json.loads((ROOT/'sources/remote-resources.lock.json').read_text())
    jobs = [('v2fly/domain-list-community', lambda:check_snapshot('v2fly/domain-list-community', 'master', lock['提交']))]
    rewrite_file = ROOT/'sources/rewrites.json'
    if rewrite_file.exists():
        rewrites = json.loads(rewrite_file.read_text())
        jobs.append((rewrites['repository'], lambda:check_snapshot(rewrites['repository'], rewrites['branch'], rewrites['commit'])))
    catalog_file = ROOT/'sources/rewrite-catalog.json'
    if catalog_file.exists():
        catalog = json.loads(catalog_file.read_text())
        jobs.extend((p['repository'], lambda p=p:check_snapshot(p['repository'],p['branch'],p['commit']))
                    for p in catalog['projects'])
    jobs.extend((r['id'], lambda r=r:check_resource(r)) for r in remotes['resources'])
    for name, action in jobs:
        try:
            row = action()
        except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as error:
            row = {'name':name, 'status':'查询失败，需重试', 'error':str(error)}
            print(f'{name}：{error}', file=sys.stderr, flush=True)
        rows.append(row)
        print(f'{name}：{row["status"]}', flush=True)
    report = markdown(rows, datetime.now(timezone.utc).isoformat(timespec='seconds'))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding='utf-8')
    else:
        print(report)
    return int(any('error' in row for row in rows))


if __name__ == '__main__':
    raise SystemExit(main())
