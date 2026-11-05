#!/usr/bin/env python3
"""查询域名在服务和集合中的候选匹配；不推断设备上的最终命中。"""
import argparse
from pathlib import Path
from urllib.parse import urlsplit

def parse_domain(value):
    raw = value.strip()
    host = urlsplit(raw).hostname if '://' in raw else raw
    if not host or any(ch in host for ch in '/:@?#') or any(ch.isspace() for ch in host):
        raise ValueError('请输入有效域名或包含域名的完整网址')
    return host.rstrip('.').encode('idna').decode('ascii').lower()


def find_matches(host, root, scope='all'):
    folders = ('services', 'collections', 'custom', 'adblock') if scope == 'all' else (scope,)
    matches = []
    for folder in folders:
        for path in sorted((root/'filter'/folder).glob('*.list')):
            for line in path.read_text().splitlines():
                if not line or line.startswith('#'):
                    continue
                kind, domain, policy = [x.strip() for x in line.split(',')]
                if (host == domain
                        or (kind == 'host-suffix' and host.endswith('.'+domain))
                        or (kind == 'host-keyword' and domain in host)):
                    matches.append((path.relative_to(root).as_posix(), kind, domain, policy))
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('domain', help='域名或完整网址')
    parser.add_argument('--scope', choices=['all','services','collections','custom','adblock'], default='all', help='查询全部、服务、合集、原有自定义规则或配套广告规则')
    args = parser.parse_args()
    try:
        host = parse_domain(args.domain)
    except (ValueError, UnicodeError) as exc:
        parser.error(str(exc))
    matches = find_matches(host, Path(__file__).resolve().parents[1], args.scope)
    print('规则文件\t匹配类型\t匹配条件\t文件默认策略')
    for match in matches:
        print('\t'.join(match))
    if not matches:
        print('没有找到候选匹配；不代表该域名无需代理或不存在。')
    print('仅按当前库中的域名条件查询；集合可以重叠，force-policy、主配置及设备加载顺序决定实际去向。')

if __name__=='__main__':main()
