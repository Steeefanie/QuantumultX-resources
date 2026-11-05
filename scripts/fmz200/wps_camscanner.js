/*
 * 名称：WPS 与扫描全能王客户端会员状态调整
 * 用途：处理 WPS Office 用户概览及扫描全能王资产查询接口响应，调整客户端本地会员等级与到期时间字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由 WPS 与扫描全能王重写规则调用；需要个人 MITM 证书及对应 hostname。
 * 使用边界：仅影响客户端本地会员功能判断，不提供云空间扩容或服务端付费接口权限。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/wps_camscanner.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
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
