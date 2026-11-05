let body = $response.body || "{}";
const url = $request.url || "";
try {
  let obj = JSON.parse(body);
  if (url.includes("wps.cn")) {
    obj.result = "ok";
    obj.total_cost = -30;
    obj.wealth = 9999;
    obj.exp = 0;
    obj.vip = {
      name: "超级会员",
      has_ad: 0,
      memberid: 40,
      expire_time: 4092599349,
      enabled: [
        { memberid: 40, name: "超级会员", expire_time: 4092599349 },
        { memberid: 20, name: "WPS会员", expire_time: 4092599349 },
        { memberid: 12, name: "稻壳会员", expire_time: 4092599349 }
      ]
    };
  } else if (url.includes("intsig.net")) {
    obj.data = obj.data || {};
    obj.data.psnl_vip_property = {
      expiry: "4092599349",
      svip: 1,
      nxt_renew_tm: "4092599349",
      level_info: { level: 1, days: 9999, end_days: 9999 }
    };
  }
  body = JSON.stringify(obj);
} catch (e) {}
$done({ body });
