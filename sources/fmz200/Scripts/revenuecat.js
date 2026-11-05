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
