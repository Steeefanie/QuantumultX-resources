/*
 * 名称：美图秀秀与 Wink 客户端 VIP 状态调整
 * 用途：处理美图秀秀及 Wink 用户与会员信息接口响应，将客户端本地 VIP 标识与有效期字段设为开启。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由美图秀秀重写规则调用；需要个人 MITM 证书及对应 hostname。
 * 使用边界：仅调整客户端本地滤镜、修图与工具权限判断，云端 AI 算力类功能由服务端鉴权。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/meitu.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
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
