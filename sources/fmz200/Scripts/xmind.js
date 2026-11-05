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
