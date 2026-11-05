/*
 * 名称：Spotify 请求 URL 兼容调整
 * 用途：将匹配请求中的 platform=iphone 改为 platform=ipad，并处理主机名后的 :443 写法。
 * 处理阶段：请求阶段：由 script-request-header 调用，实际返回改写后的 URL
 * 使用前提：由 Spotify 重写中对应的请求头阶段规则调用；按实际匹配 hostname 配置。
 * 使用边界：文件名含 json，但本脚本不解析响应 JSON；不要把它挂到响应体阶段。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/app2smile/rules/blob/df6366a7024e0b3f0aa3510c5b791eea6f3cba89/js/spotify-json.js
 * 来源许可：MIT；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
console.log(`spotify-json-2025.06.20`);
let url = $request.url;
// console.log(`原始url:${url}`);
if (url.includes('com:443')) {
    url = url.replace(/com:443/, 'com');
}
if (url.includes('platform=iphone')) {
    url = url.replace(/platform=iphone/, 'platform=ipad');
    // console.log(`替换platform:${url}`);
} else {
    console.log('无需处理');
}
$done({
    url
});
