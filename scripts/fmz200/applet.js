/*
 * 名称：微信小程序内容接口去广告
 * 用途：清理匹配 WordPress 类小程序文章接口响应中的激励视频广告、弹窗广告及推广字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由微信小程序去广告重写规则按 URL 调用；HTTPS 响应处理需要个人 MITM 证书及对应 hostname。
 * 使用边界：只针对规则匹配的小程序接口生效，无法去除所有微信小程序的通用 5 秒开屏广告。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/applet.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
//############################################
//#!name=微信小程序去广告脚本
//#!date：2023-03-19
//#############################################


re('"excitationAd":"\\d"@Ad":"\d"@ad":true@AdId":"[^"]*"@adid":"[^"]*"@fr_videp_if":"1@adunit[^"]*"','"excitationAd":"0"@Ad":"0"@ad":false@AdId":""@adid":""@fr_videp_if":"0@"')

function re(){var e=$response.body;if(arguments[0].includes("@")){var r=arguments[0].split("@"),l=arguments[1].split("@");for(i=0;i<r.length;i++){var a=RegExp(r[i],"g");e=e.replace(a,l[i])}}else{var a=RegExp(arguments[0],"g");e=e.replace(a,arguments[1])}$done(e)}
