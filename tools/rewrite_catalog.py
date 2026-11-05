"""构建额外来源的原生 QX 重写，保留独立许可并隔离缺少正文的脚本行。"""
import hashlib
import json
from pathlib import PurePosixPath
import re

from script_headers import annotate_script


def create_plan(root, raw_root, existing_files):
    path = root/'sources/rewrite-catalog.json'
    if not path.exists():
        return {}, [], [], {'modules':0,'scripts':0,'filters':0,'projects':[]}
    catalog = json.loads(path.read_text())
    if catalog.get('schema') != 1:
        raise ValueError('额外重写来源版本不支持')
    files = {}; rows = []; review = []; scripts = set(); filter_count = 0; project_records = []
    resources = []; companions = []
    for project in catalog['projects']:
        if project['repository'] != 'fmz200/wool_scripts' or project['license'] != 'GPL-3.0':
            raise ValueError('额外重写来源或许可尚未核查')
        name = project['id']; commit = project['commit']; repository = project['repository']
        if not re.fullmatch(r'[a-z][a-z0-9-]*',name) or not re.fullmatch('[0-9a-f]{40}',commit):
            raise ValueError('重写来源缺少合法名称或固定提交')
        source_root = root/project['source_directory']
        source_root.resolve().relative_to((root/'sources').resolve())
        source = {}
        for source_path, digest in project['files'].items():
            parts = PurePosixPath(source_path)
            if parts.is_absolute() or '..' in parts.parts:
                raise ValueError('额外重写来源路径不安全')
            content = (source_root/source_path).read_bytes()
            if hashlib.sha256(content).hexdigest() != digest:
                raise ValueError('额外重写来源哈希不符：'+source_path)
            source[source_path] = content.decode('utf-8')
        license_text = source[project['license_path']]
        if 'GNU GENERAL PUBLIC LICENSE' not in license_text or 'Version 3' not in license_text:
            raise ValueError('GPL-3.0 许可文本与登记不符')
        license_output = f'rewrite/licenses/{name}-GPL-3.0.txt'
        files[license_output] = license_text
        files[f'scripts/{name}/LICENSE'] = license_text
        file_origins = project.get('file_origins', {})
        for orig_path, orig_meta in file_origins.items():
            if orig_path not in source:
                raise ValueError('file_origins 引用了未登记的源文件：'+orig_path)
            for req_key in ('upstream', 'status', 'license', 'local_modification'):
                val = orig_meta.get(req_key)
                if not isinstance(val, str) or not val.strip() or any(c in val for c in ('\r', '\n', '*/')):
                    raise ValueError(f'file_origins 字段不合法：{orig_path} / {req_key}')
        project_records.append({'repository':repository,'commit':commit,'license':project['license'],
                                'source_files':project['files'],'file_origins':file_origins,'script_outputs':{}})
        seen = set()
        for module in project['modules']:
            module_id = module['id']
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',module_id) or module_id in seen:
                raise ValueError('额外重写模块名不合法或重复')
            seen.add(module_id)
            category = module.get('category', '')
            output = f'rewrite/{category}/{module_id}.conf' if category else f'rewrite/{name}/{module_id}.conf'
            body = []; domain_rules = []; used_scripts = set(); omitted = []; rule_count = 0
            filter_only = bool(module.get('filter_only'))
            for line_number,line in enumerate(source[module['source']].splitlines(),1):
                stripped = line.strip()
                if not stripped or stripped.startswith(('#',';','//')):
                    if stripped.startswith('#!raw-url='): line = f'#!raw-url={raw_root}/{output}'
                    if stripped.startswith('#!icon='): line = f'#!icon={raw_root}/icon/Global.png'
                    if stripped.startswith('#!date='): line = f'#!date={project["checked_on"]}'
                    body.append(line); continue
                if re.match(r'(?i)^(host|host-suffix|host-keyword|ip-cidr|ip6-cidr),',stripped):
                    if stripped.rsplit(',',1)[-1].strip().lower() != 'reject':
                        raise ValueError('配套分流存在非拦截动作，停止自动拆分：'+module_id)
                    domain_rules.append(line); continue
                if filter_only:
                    continue
                match = re.search(r'\burl\s+(script-\S+)\s+(\S+)',stripped)
                if match:
                    url = match[2]; dependency = None; target = None
                    for prefix in (f'https://raw.githubusercontent.com/{repository}/main/',
                                   f'https://github.com/{repository}/raw/main/'):
                        if url.startswith(prefix):
                            dependency = url[len(prefix):]
                            if dependency in source and dependency.startswith('Scripts/') and dependency.endswith('.js'):
                                target = f'scripts/{name}/'+dependency[len('Scripts/'):]
                                orig = file_origins.get(dependency, {})
                                files[target] = annotate_script(
                                    root, target, source[dependency], repository, commit, dependency,
                                    orig.get('license', project['license']),
                                    source_url=orig.get('upstream'),
                                    local_mod=orig.get('local_modification'),
                                )
                                scripts.add(target)
                                project_records[-1]['script_outputs'][target] = dependency
                    external_aliases = {
                        'https://raw.githubusercontent.com/Keywos/rule/main/script/wy/js/wyres.js': 'Scripts/wyres.js',
                        'https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js': 'Scripts/UnblockURLinWeChat.js',
                    }
                    if url in external_aliases and external_aliases[url] in source:
                        dependency = external_aliases[url]
                        target = f'scripts/{name}/'+dependency[len('Scripts/'):]
                        orig = file_origins.get(dependency, {})
                        files[target] = annotate_script(
                            root, target, source[dependency], repository, commit, dependency,
                            orig.get('license', project['license']),
                            source_url=orig.get('upstream'),
                            local_mod=orig.get('local_modification'),
                        )
                        scripts.add(target)
                        project_records[-1]['script_outputs'][target] = dependency
                    app_prefix = 'https://raw.githubusercontent.com/app2smile/rules/master/js/'
                    if url.startswith(app_prefix):
                        candidate = 'scripts/app2smile/'+url[len(app_prefix):]
                        if candidate in existing_files: target = candidate
                    if target is None:
                        omitted.append(line_number)
                        review.append({'来源':repository,'模块':module_id,'源文件':module['source'],'行号':line_number,
                                       '处理':'隔离脚本行','内容':line,'原因':'缺少当前可收录的脚本正文或明确来源，未把外链入口算作完整模块'})
                        continue
                    line = line.replace(url,f'{raw_root}/{target}'); used_scripts.add(target)
                if re.search(r'\burl\s+',line): rule_count += 1
                body.append(line)
            title = re.sub(r'[,=\r\n]',' ',module['title'])
            mod_orig = file_origins.get(module['source'], {})
            mod_source_url = mod_orig.get('upstream') or f'https://github.com/{repository}/blob/{commit}/{module["source"]}'
            mod_license = mod_orig.get('license') or project['license']
            mod_local_mod = mod_orig.get('local_modification') or '分离配套分流，直接脚本地址改为本仓库；保留原作者署名。'
            companion = ''
            if domain_rules:
                companion = f'filter/adblock/{name}/{module_id}.list'; filter_count += 1
                files[companion] = (f'# {module["title"]} 配套拦截；{mod_license}，许可见 {license_output}\n'
                                    f'# 来源：{mod_source_url}\n'
                                    '# 从原重写拆出域名/IP 分流；仅在选择该模块时按需启用。\n'
                                    +'\n'.join(domain_rules)+'\n')
                companions.append(f'{raw_root}/{companion}, tag={title}配套分流（{name}）, force-policy=reject, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=false')
            if not rule_count:
                if not filter_only:
                    review.append({'来源':repository,'模块':module_id,'源文件':module['source'],'行号':'',
                                   '处理':'仅保留分流，未生成空重写' if companion else '未生成空重写','内容':companion,'原因':'没有可保留的 URL 重写条件'})
                continue
            partial = bool(omitted)
            status = '保留基础条目，有脚本行隔离' if partial else '配置及直接依赖已收录'
            header = (f'# 名称：{module["title"]}\n# 用途：{module.get("description",module["title"])}\n# 本地整理日期：{project["checked_on"]}\n'
                      f'# 来源：{mod_source_url}\n'
                      f'# 许可：{mod_license}；完整许可见 {license_output}，不改为根目录 MIT。\n'
                      f'# 本地修改：{mod_local_mod}\n'
                      f'# 收录状态：{status}；隔离行号：{",".join(map(str,omitted)) or "无"}。\n'
                      '# 尚未完成真实设备验证，不承诺所有 App 版本可用或与其他来源模块等效。\n')
            files[output] = header+'\n'.join(body).rstrip()+'\n'
            title = re.sub(r'[,=\r\n]',' ',module['title'])
            resources.append(f'{raw_root}/{output}, tag={title}, update-interval=86400, opt-parser=false, enabled=false')
            rows.append({'模块':(f'{category}/{module_id}' if category else f'{name}/{module_id}'),'用途':module.get('description',module['title']),'重写文件':output,'源文件':module['source'],
                         '上游提交':commit,'核对日期':project['checked_on'],'许可':mod_license,
                         '脚本文件':' / '.join(sorted(used_scripts)),'配套分流':companion,
                         'MITM':'按原文 hostname 配置个人证书','默认启用':False,'设备验证':'未完成',
                         '限制':status+'；'+module['notes']})
    return files,rows,review,{'modules':len(rows),'scripts':len(scripts),'filters':filter_count,'projects':project_records}
