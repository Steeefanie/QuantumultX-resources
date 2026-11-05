let body = $response.body || "{}";
try {
  let obj = JSON.parse(body);
  if (Array.isArray(obj.statuses)) {
    obj.statuses = obj.statuses.filter(
      item => !item.promotion && item.mblogtypename !== "广告" && item.mblogtypename !== "热推"
    );
  }
  if (Array.isArray(obj.items)) {
    obj.items = obj.items.filter(
      item => !item.data || (!item.data.promotion && item.data.mblogtypename !== "广告")
    );
  }
  if (obj.ads) obj.ads = [];
  if (obj.ad) obj.ad = [];
  body = JSON.stringify(obj);
} catch (e) {}
$done({ body });
