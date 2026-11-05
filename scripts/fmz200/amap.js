/*
 * 名称：高德地图首页与导航页卡片净化
 * 用途：清理高德地图开屏、首页底部推广卡片、横幅及活动浮层字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由高德地图净化重写规则调用；需要个人 MITM 证书及对应 hostname。
 * 使用边界：不影响核心定位、路线规划与实时导航功能。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/amap.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
let body = $response.body || "{}";
try {
  let obj = JSON.parse(body);
  if (obj.data) {
    delete obj.data.ad;
    delete obj.data.ads;
    delete obj.data.banner;
    delete obj.data.activity;
    delete obj.data.pull3;
    if (Array.isArray(obj.data.cardList)) {
      obj.data.cardList = obj.data.cardList.filter(
        c => !["ad", "banner", " finance", "hotel", "activity"].includes(c.dataType)
      );
    }
  }
  body = JSON.stringify(obj);
} catch (e) {}
$done({ body });
