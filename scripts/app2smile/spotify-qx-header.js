/*
 * 名称：Spotify 请求缓存头处理
 * 用途：移除匹配请求中的 If-None-Match 缓存校验头，让对应接口重新返回响应内容。
 * 处理阶段：请求头
 * 使用前提：由 Spotify 模块的 script-request-header 规则调用。
 * 使用边界：只处理匹配请求的头部，不负责代理地区、响应广告过滤或账户服务端权限。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/app2smile/rules/blob/df6366a7024e0b3f0aa3510c5b791eea6f3cba89/js/spotify-qx-header.js
 * 来源许可：MIT；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
let headers = $request.headers;
delete headers['If-None-Match'];
console.log('2025.03.20-qx-spotify删除请求头')
$done({headers});
