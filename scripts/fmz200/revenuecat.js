/*
 * 名称：RevenueCat 通用内购订阅状态调整
 * 用途：移除请求头中的 ETag 缓存标识，并在匹配的 RevenueCat 订阅校验响应中注入客户端订阅与权益有效期字段。
 * 处理阶段：请求头与响应体：JSON
 * 使用前提：仅由 RevenueCat 通用内购重写规则调用；需要个人 MITM 证书及 api.revenuecat.com、api.rc-backup.com 的 hostname。
 * 使用边界：适用于采用 RevenueCat 客户端校验的摄影、笔记与工具类应用（如 No Fusion、Locket、Notability 等）；服务端强校验功能不保证生效。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/revenuecat.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
const resp = {};
const headers = Object.fromEntries(
  Object.entries($request.headers || {}).map(([k, v]) => [k.toLowerCase(), v])
);

if (typeof $response === "undefined") {
  delete $request.headers["x-revenuecat-etag"];
  delete $request.headers["X-RevenueCat-ETag"];
  resp.headers = $request.headers;
} else if ($response.body) {
  let obj = JSON.parse($response.body);
  if (obj && obj.subscriber) {
    obj.subscriber.subscriptions = obj.subscriber.subscriptions || {};
    obj.subscriber.entitlements = obj.subscriber.entitlements || {};
    const subData = {
      is_sandbox: false,
      ownership_type: "PURCHASED",
      billing_issues_detected_at: null,
      period_type: "normal",
      expires_date: "2099-09-09T09:09:09Z",
      grace_period_expires_date: null,
      unsubscribe_detected_at: null,
      original_purchase_date: "2023-09-09T09:09:09Z",
      purchase_date: "2023-09-09T09:09:09Z",
      store: "app_store"
    };
    const entData = {
      grace_period_expires_date: null,
      purchase_date: "2023-09-09T09:09:09Z",
      product_identifier: "com.revenuecat.pro.yearly",
      expires_date: "2099-09-09T09:09:09Z"
    };
    const commonEntitlements = [
      "pro", "Pro", "PRO", "premium", "Premium", "vip", "VIP",
      "plus", "Plus", "gold", "all_access", "unlimited", "nofusion_pro",
      "locket_gold", "vsco_pro", "notability_plus", "goodnotes_special_edition"
    ];
    obj.subscriber.subscriptions["com.revenuecat.pro.yearly"] = subData;
    for (const key of commonEntitlements) {
      obj.subscriber.entitlements[key] = Object.assign({}, entData);
    }
    resp.body = JSON.stringify(obj);
  }
}
$done(resp);
