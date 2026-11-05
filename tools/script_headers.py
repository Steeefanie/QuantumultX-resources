"""给生成脚本添加用途说明，原始来源正文保持不变。"""
import json


def annotate_script(root, output, content, repository, commit, source, license_id):
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
    return (f'/*\n * 名称：{info["title"]}\n * 用途：{info["purpose"]}\n'
            f' * 处理阶段：{info["stage"]}\n * 使用前提：{info["requirements"]}\n'
            f' * 使用边界：{info["notes"]}\n * 本地说明日期：{info["annotation_date"]}（非上游更新时间）\n'
            f' * 来源：https://github.com/{repository}/blob/{commit}/{source}\n'
            f' * 来源许可：{license_id}；原作者署名及源代码保留在下方原文中，对应许可随目录保存。\n'
            ' * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。\n'
            ' */\n'+content)
