/*
 * 名称：掌上公交小程序接口去广告
 * 用途：清理掌上公交小程序 ApiData 接口响应中的广告字段。
 * 处理阶段：响应体：JSON / 文本
 * 使用前提：仅由微信小程序去广告重写规则按 URL 调用；需要个人 MITM 证书及 wx.mygolbs.com 的 hostname。
 * 使用边界：仅作用于掌上公交小程序接口。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/zhangshanggongjiao.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
/***********************************
 > 應用名稱：掌上公交（微信小程序）
 > 軟件版本：0.0.0
 > 下載地址：微信小程序搜索掌上公交
 > 更新時間：2022-03-01
 > 特别說明：本腳本僅供學習交流使用，禁止轉載售賣

 [rewrite_local]
 # 掌上公交微信小程序去除广告（2022-03-01）
 https?:\/\/wx\.mygolbs\.com\/WxBusServer\/ApiData\.do url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhangshanggongjiao.js

 [mitm]
 hostname=wx.mygolbs.com

 ***********************************/

var body = $response.body.replace(/Ad":1/g, 'Ad":0').replace(/Ad_ab":1/g, 'Ad_ab":0')
$done({body});
