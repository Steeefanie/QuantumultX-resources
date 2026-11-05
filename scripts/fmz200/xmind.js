/*
 * 名称：Xmind 客户端 Pro 状态调整
 * 用途：处理 Xmind 设备与订阅校验接口响应，将客户端订阅状态字段设为有效。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由 Xmind 重写规则调用；需要个人 MITM 证书及对应 hostname。
 * 使用边界：仅调整客户端本地功能状态显示与导出限制，不包含云端账号同步权益。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://yfamily.vercel.app/rewrite/xmind.conf
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：按 Xmind 客户端订阅校验响应结构编写的本地解锁脚本。
 */
let obj = {};
try {
  obj = JSON.parse($response.body || "{}");
} catch (e) {}

obj.license = {
  status: "sub",
  expireTime: 4092599349000
};
obj._code = 200;
obj.raw_data = "G0b6Wu5efcf/+093/V7+4/e4=";
if (obj.sub) {
  obj.sub.status = "sub";
  obj.sub.expireTime = 4092599349000;
}

$done({ body: JSON.stringify(obj) });
