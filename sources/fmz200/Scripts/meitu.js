let body = $response.body || "";
try {
  let obj = JSON.parse(body);
  if (obj.data) {
    obj.data.vip_type = 1;
    obj.data.is_vip = true;
    obj.data.is_valid_user = 1;
    obj.data.valid_time = 4092599349;
    obj.data.expire_time = 4092599349;
    obj.data.sub_biz_type = 1;
    if (obj.data.vip_info) {
      obj.data.vip_info.is_vip = true;
      obj.data.vip_info.vip_type = 1;
      obj.data.vip_info.valid_time = 4092599349;
    }
  }
  body = JSON.stringify(obj);
} catch (e) {
  body = body
    .replace(/"vip_type"\s*:\s*0/g, '"vip_type":1')
    .replace(/"is_vip"\s*:\s*false/g, '"is_vip":true');
}
$done({ body });
