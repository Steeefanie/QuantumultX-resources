/*
 * 名称：高德地图首页与导航页卡片净化
 * 用途：清理高德地图开屏、首页底部推广卡片、横幅及活动浮层字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由高德地图净化重写规则调用；需要个人 MITM 证书及对应 hostname。
 * 使用边界：不影响核心定位、路线规划与实时导航功能。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://raw.githubusercontent.com/ddgksf2013/Scripts/master/amap.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留 @ddgksf2013 原始脚本正文（V1.0.34）。
 */
const version = "V1.0.34";

let body = $response.body;
if (!body) {
  $done({});
} else {
  try {
    let obj = JSON.parse(body);
    const url = $request.url || "";

    if (url.indexOf("valueadded/alimama/splash_screen") !== -1) {
      if (obj.data && Array.isArray(obj.data.ad)) {
        for (let item of obj.data.ad) {
          if (item.set && item.set.setting) {
            item.set.setting.display_time = 0;
          }
          if (Array.isArray(item.creative) && item.creative[0]) {
            item.creative[0].start_time = 2240150400;
            item.creative[0].end_time = 2240150400;
          }
        }
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("faas/amap-navigation/main-page") !== -1) {
      if (obj.data?.cardList) {
        obj.data.cardList = Object.values(obj.data.cardList).filter(
          item => item.dataType === "LoginCard" || item.dataType === "FrequentLocation"
        );
      }
      if (obj.data?.pull3?.msgs) {
        obj.data.pull3.msgs = [];
      }
      if (obj.data?.business_position) {
        obj.data.business_position = [];
      }
      if (obj.data?.mapBizList) {
        obj.data.mapBizList = [];
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("profile/index/node") !== -1) {
      if (obj.data) {
        delete obj.data.tipData;
      }
      if (obj.data?.cardList) {
        obj.data.cardList = Object.values(obj.data.cardList).filter(
          item => item.dataType === "MyOrderCard" || item.dataType === "GdRecommendCard"
        );
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("new_hotword") !== -1) {
      if (obj.data?.header_hotword) {
        obj.data.header_hotword = [];
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("ws/promotion-web/resource") !== -1) {
      const propertiesToDelete = ["icon", "banner", "tips", "popup", "bubble", "other"];
      for (const prop of propertiesToDelete) {
        if (obj.data?.[prop]) {
          obj.data[prop] = [];
        }
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("ws/msgbox/pull") !== -1) {
      if (obj.msgs) {
        obj.msgs = [];
      }
      if (obj.pull3?.msgs) {
        obj.pull3.msgs = [];
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("ws/message/notice/list") !== -1) {
      if (obj.data?.noticeList) {
        obj.data.noticeList = [];
      }
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("ws/shield/frogserver/aocs") !== -1) {
      const keywords = [
        "gd_notch_logo",
        "home_business_position_config",
        "his_input_tip",
        "operation_layer",
        "aiNative",
        "ai_",
        "_ai"
      ];
      Object.keys(obj.data || {}).forEach(key => {
        if (keywords.some(kw => key.includes(kw))) {
          obj.data[key] = { status: 1, version: "", value: "" };
        }
      });
      $done({ body: JSON.stringify(obj) });
    } else if (url.indexOf("search/nearbyrec_smart") !== -1) {
      const propsToDelete = ["coupon", "scene", "activity", "commodity_rec", "operation_activity"];
      if (obj.data) {
        propsToDelete.forEach(prop => {
          delete obj.data[prop];
        });
        if (Array.isArray(obj.data.modules)) {
          obj.data.modules = obj.data.modules.filter(m => !propsToDelete.includes(m));
        }
      }
      $done({ body: JSON.stringify(obj) });
    } else {
      $done({});
    }
  } catch (e) {
    $done({});
  }
}
