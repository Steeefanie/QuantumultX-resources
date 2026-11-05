"""给生成脚本添加用途说明，原始来源正文保持不变。"""
import json


def annotate_script(root, output, content, repository, commit, source, license_id, source_url=None, local_mod=None):
    path = root/'sources/script-info.json'
    if not path.exists():
        return content
    info = json.loads(path.read_text()).get(output)
    if not info:
        raise ValueError('缺少脚本用途说明：'+output)
    fields = ['title','purpose','stage','requirements','notes','annotation_date']
    for key in fields:
        if not isinstance(info.get(key),str) or any(x in info[key] for x in ('\r','\n','*/')):
            raise ValueError('脚本说明字段不合法：'+output+' / '+key)
    resolved_url = source_url or f'https://github.com/{repository}/blob/{commit}/{source}'
    resolved_mod = local_mod or '仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。'
    for val in (resolved_url, resolved_mod, license_id):
        if not isinstance(val, str) or any(x in val for x in ('\r', '\n', '*/')):
            raise ValueError('脚本来源或修改说明不合法：'+output)
    return (f'/*\n * 名称：{info["title"]}\n * 用途：{info["purpose"]}\n'
            f' * 处理阶段：{info["stage"]}\n * 使用前提：{info["requirements"]}\n'
            f' * 使用边界：{info["notes"]}\n * 本地说明日期：{info["annotation_date"]}（非上游更新时间）\n'
            f' * 来源：{resolved_url}\n'
            f' * 来源许可：{license_id}；原作者署名及源代码保留在下方原文中，对应许可随目录保存。\n'
            f' * 本地修改：{resolved_mod}\n'
            ' */\n'+content)
