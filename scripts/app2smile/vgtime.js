/*
 * 名称：游戏时光开屏广告处理
 * 用途：将游戏时光初始化响应中的 data.ad 置空，处理对应开屏广告。
 * 处理阶段：响应体：JSON
 * 使用前提：原模块匹配 HTTP 接口，不因本条规则本身要求 HTTPS 解密。
 * 使用边界：只处理该初始化接口；其他信息流广告可能需要广告联盟模块。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/app2smile/rules/blob/df6366a7024e0b3f0aa3510c5b791eea6f3cba89/js/vgtime.js
 * 来源许可：MIT；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
console.log('vgtime-开屏页');
let body = JSON.parse($response.body);
if (!body.data?.ad) {
    console.log('data/ad字段为空');
    console.log(`body:${$response.body}`);
} else {
    body.data.ad = null;
    console.log('成功');
}
body = JSON.stringify(body);

$done({
    body
});

