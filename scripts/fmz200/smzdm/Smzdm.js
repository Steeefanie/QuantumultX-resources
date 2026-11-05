/*
 * 名称：什么值得买首页与界面净化
 * 用途：处理首页广告卡片、个人中心推广、悬浮入口及部分导航服务字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由对应重写规则按 URL 调用；HTTPS 响应处理通常需要个人 MITM 证书及对应 hostname。
 * 使用边界：与 smzdm_ads.js 分别匹配不同接口，某些活动或服务入口可能被隐藏。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/smzdm/Smzdm.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
// 2024-09-08 20:59
// 修改：2025-06-01 14:37:50 
const url = $request.url;

if (!$response.body) {
  $done({});
}

let obj = JSON.parse($response.body);

if (url.includes("/v3/home")) {
  const recursivelyFilterByCellType = (data) => {
    if (Array.isArray(data)) {
      return data.map(item => recursivelyFilterByCellType(item)).filter(Boolean);
    } else if (typeof data === 'object') {
      if (data['cell_type'] === '23008' || data['cell_type'] === '23005' || data['cell_type'] === '23024') {
        return null;
      } else {
        for (const key in data) {
          data[key] = recursivelyFilterByCellType(data[key]);
        }
        return data;
      }
    }
    return data;
  };

  obj.data = recursivelyFilterByCellType(obj.data);
}

const fixPos = (arr) => {
  for (let i = 0; i < arr.length; i++) {
    arr[i].pos = i + 1;
  }
};

if (url.includes("/vip") && obj.data.big_banner) {
  delete obj.data.big_banner;
  delete obj.data.top_banner;
  delete obj.data.yaoqingshaiwu;
}

if (url.includes("/publish/get_bubble") && obj.data) {
  delete obj.data;
}

if (url.includes("/v3/home") && obj.data && obj.data.functions) {
  obj.data.functions = obj.data.functions.filter((item) => item.type === "message");
  fixPos(obj.data.functions);
}

if (obj && obj.data && obj.data.services) {
  obj.data.services = obj.data.services.filter((item) => item.type === "articel_manage" || item.type === "199794" || item.type === "199796");
  fixPos(obj.data.services);
}

if (url.includes("/vip/bottom_card_list") && obj.data.rows) {
  delete obj.data.rows;
}

if (url.includes("/v3/home")) {
  obj.data.component = obj.data.component.filter((item) =>
    item.zz_type === "circular_banner" || item.zz_type === "fixed_banner" || item.zz_type === "filter" || item.zz_type === "list"
  );
  fixPos(obj.data.component);
}

if (url.includes("/util/update") && obj.data) {
  if (obj.data.ad_black_list) {
    delete obj.data.ad_black_list;
  }

  if (obj && obj.data && obj.data.operation_float) {
    delete obj.data.operation_float;
  }

  if (obj.data.haojia_widget) {
    delete obj.data.haojia_widget;
  }
}


if (obj && obj.data && obj.data.widget) {
  delete obj.data.widget;
}

if (obj && obj.data && obj.data.operation_float_screen) {
  delete obj.data.operation_float_screen;
}

if (url.includes("/home/list") && obj.data.banner_v2) {
  delete obj.data.banner_v2;
}

if (obj?.data?.rows?.length > 0) {
  obj.data.rows = obj.data.rows.filter(
    (i) => !(i?.hasOwnProperty("ad_banner_id") || ["ad_campaign_id_", "ad_campaign_name", "abs_position"]?.includes(i?.ad))
  );
}

if (url.includes("/publish") && obj.data && obj.data.hongbao) {
  delete obj.data.hongbao;
}

if (url.includes("/loading") && obj && obj.data) {
  delete obj.data;
}

if (url.includes("/ajax_app/ajax_get_footer_list") && obj.data.activity_banner && obj.data.activity_banner.hot_widget) {
  obj.data.activity_banner.hot_widget.forEach(widget => {
    if (widget.pic_url) {
      delete widget.pic_url;
    }
  });
}

if (url.includes("/v1/app/home") && obj.data) {
  if (obj.data) {
    obj.data = obj.data.filter((item) => item.id === "40" || item.id === "20");
    fixPos(obj.data);
  }
}

$done({ body: JSON.stringify(obj) });