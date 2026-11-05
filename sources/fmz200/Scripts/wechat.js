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
