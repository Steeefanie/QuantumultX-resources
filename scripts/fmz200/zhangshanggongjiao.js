/*
 * 名称：掌上公交小程序接口去广告
 * 用途：清理掌上公交小程序 ApiData 接口响应中的广告字段。
 * 处理阶段：响应体：JSON / 文本
 * 使用前提：仅由微信小程序去广告重写规则按 URL 调用；需要个人 MITM 证书及 wx.mygolbs.com 的 hostname。
 * 使用边界：仅作用于掌上公交小程序接口。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/13c0f82112a54965b33d573bc00a48fc13c7d8fa/Scripts/zhangshanggongjiao.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：取自 fmz200/wool_scripts 历史提交 13c0f82112a54965b33d573bc00a48fc13c7d8fa；仅添加本段用途说明。
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
