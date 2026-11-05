/*
 * 名称：微信公众号文章底部与文中广告净化
 * 用途：解析微信公众号 getappmsgad 接口 JSON 响应，将 advertisement_num 置零并清空 advertisement_info 与推广标识。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由微信公众号及小程序去广告重写规则调用；需要个人 MITM 证书及 mp.weixin.qq.com 的 hostname。
 * 使用边界：替代旧版单次字符串替换规则，完整清空文章底部与文中广告数组。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://raw.githubusercontent.com/NobyDa/Script/master/QuantumultX/File/Wechat.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：基于 @NobyDa Wechat.js 公众号去广告逻辑整理，补充小程序 ad_info/pos_info 置空与异常捕获保护。
 */
let body = $response.body || "{}";
try {
  let obj = JSON.parse(body);
  obj.advertisement_num = 0;
  obj.advertisement_info = [];
  if (obj.ad_info) obj.ad_info = [];
  if (obj.pos_info) obj.pos_info = [];
  delete obj.appid;
  body = JSON.stringify(obj);
} catch (e) {}
$done({ body });
