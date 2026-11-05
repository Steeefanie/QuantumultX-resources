/*
 * 名称：IT之家新闻列表去广告
 * 用途：过滤 IT之家匹配新闻列表中的广告标签及特定广告 feedType。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由对应重写规则按 URL 调用；HTTPS 响应处理通常需要个人 MITM 证书及对应 hostname。
 * 使用边界：只处理源配置列出的新闻列表接口，接口字段变化会影响效果。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/ithome/ithome.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
/**
 * IT之家去广告
 * 
 * @author 奶思
 * @since 2026-06-01 18:17:00
 * 
 * 
 * =========== QuanX ===========
 [rewrite_local]
 ^https:\/\/napi\.ithome\.com\/api\/(news\/index|topmenu\/getfeeds) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/ithome/ithome.js
 ^https:\/\/napi\.ithome\.com\/api\/news\/indexv2\/iphone\/927 url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/ithome/ithome.js

 [mitm]
 hostname = napi.ithome.com
 */

const url = $request.url;
if (!$response.body) $done({});
let obj = JSON.parse($response.body);

if (url.includes("/api/news/index") || url.includes("/api/topmenu/getfeeds")) {
  if (obj?.data?.list?.length > 0) {
    let list = obj.data.list;
    const newList = [];
    for (let item of list) {
      if (item?.feedContent?.smallTags?.some((i) => i?.text?.includes("广告"))) {
        continue;
      }
      if ([10002, 10003].includes(item?.feedType)) {
        continue;
      }
      newList.push(item);
    }
    obj.data.list = newList;
  }
}

// 信息流618广告
if (url.includes("/api/news/indexv2/iphone/927")) {
  if (obj?.data?.list?.length > 0) {
    obj.data.list = obj.data.list.filter((item) => item?.feedType !== 10004);
  }
}

$done({body: JSON.stringify(obj)});