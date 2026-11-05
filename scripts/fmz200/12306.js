/*
 * 名称：铁路 12306 开屏与信息流广告净化
 * 用途：根据请求体中的广告位编号构造空广告返回数据，消除 12306 启动开屏等待与页面横幅广告。
 * 处理阶段：请求分析与本地回包：script-analyze-echo-response
 * 使用前提：由通用去开屏重写规则调用；需要个人 MITM 证书、ad.12306.cn 的 hostname，且该域名不能在分流层直接 reject。
 * 使用边界：若分流层直接 reject ad.12306.cn 会导致开屏超时黑屏等待，必须放行至重写层由本脚本回包。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/12306.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
/***********************************************
> 应用名称：墨鱼自用12306去广告脚本
> 脚本作者：@ddgksf2013
> 微信账号：墨鱼手记
> 更新时间：2024-08-24
> 通知频道：https://t.me/ddgksf2021
> 特别提醒：如需转载请注明出处，谢谢合作！
> 脚本说明：目前脚本是最简洁也是最完美的了（低调使用），Enjoy！
> 使用说明：请在本地添加分流 host, ad.12306.cn, direct
***********************************************/

const version = 'V1.0.23';

var obj = JSON.parse($request.body), ddgksf2013 = {};
"0007" == obj.placementNo
  ? ((ddgksf2013.materialsList = [{ billMaterialsId: "6491", filePath: "ddgksf2013", creativeType: 1 }]),
    (ddgksf2013.advertParam = { skipTime: 1 }),
    (ddgksf2013.code = "00"))
  : (ddgksf2013 = "G0054" == obj.placementNo ? { code: "00", materialsList: [{}] } : { code: "00", message: "无广告返回" });
"undefined" != typeof $task
  ? $done({ body: JSON.stringify(ddgksf2013) })
  : $done({ response: { body: JSON.stringify(ddgksf2013) } });
