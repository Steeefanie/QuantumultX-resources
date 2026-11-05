/*
 * 名称：阿里系与高德 AMDC 移动调度防绕过
 * 用途：拦截高德地图、淘宝、菜鸟、闲鱼、飞猪、盒马等阿里系应用的 amdc/mobileDispatch HTTPDNS 调度响应，强制回退标准域名解析以保证去广告重写生效。
 * 处理阶段：响应体：文本
 * 使用前提：由高德地图净化及通用去开屏重写规则按 URL 调用。
 * 使用边界：仅对 User-Agent 匹配的阿里系与高德客户端生效，不影响其他应用的正常网络调度。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/amdc.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
/***********************************************
> 应用名称：墨鱼自用amdc脚本
> 脚本作者：@ddgksf2013
> 微信账号：墨鱼手记
> 更新时间：2025-09-06
> 通知频道：https://t.me/ddgksf2021
> 特别提醒：如需转载请注明出处，谢谢合作！
***********************************************/

const version = 'V1.0.11';

var ua = $request.headers["User-Agent"] || $request.headers["user-agent"];
/(AMap|Cainiao|%E9%97%B2%E9%B1%BC|%E9%A3%9E%E7%8C%AA%E6%97%85%E8%A1%8C|%E5%96%B5%E8%A1%97|%E5%A4%A9%E7%8C%AB|Alibaba|MovieApp|Hema4iPhone|Moon|DMPortal)/.test(ua)
  ? $done({ body: "ddgksf2013" })
  : $done({});
