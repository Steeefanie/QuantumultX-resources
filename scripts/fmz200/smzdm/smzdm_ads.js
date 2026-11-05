/*
 * 名称：什么值得买列表广告处理
 * 用途：清理个人中心、详情、排行榜、搜索结果及搜索热榜中的指定广告或营销字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由对应重写规则按 URL 调用；HTTPS 响应处理通常需要个人 MITM 证书及对应 hostname。
 * 使用边界：只处理源配置列明的接口，与首页净化脚本的职责范围不同。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/fmz200/wool_scripts/blob/4b7830670baf235ed945085cb926dc499cf619e0/Scripts/smzdm/smzdm_ads.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
/**
 * @author fmz200
 * @function 什么值得买去广告
 * @date 2025-06-04 09:11:00
 */

let requestUrl = $request.url;
let responseBody = $response.body;

let obj = JSON.parse(responseBody);

if (requestUrl.includes("/vip/creator_user_center")) {
  obj.data = {};
  console.log('去除个人中心广告💕');
}

if (requestUrl.includes("/util/update")) {
  obj.data.operation_float = [];
  console.log('去除弹窗图片广告💕');
}

if (requestUrl.includes("/detail_modul/user_related_modul")) {
  delete obj.data.super_coupon;
  console.log('去除详情页广告💕');
}

if (requestUrl.includes("/ranking_list/articles?")) {
  obj.data.rows = obj.data.rows.filter(item => item.model_type !== "ads");
  console.log('去除排行榜广告💕');
}

if (requestUrl.includes("/sou/list_v10")) {
  obj.data.rows = obj.data.rows.filter(item => item.model_type !== "ads");
  console.log('去除搜索结果广告💕');
}

if (requestUrl.includes("/sou/filter/tags/hot_tags?")) {
  obj.data.search_hot.home = obj.data.search_hot.home.filter(item => item.pos);
  delete obj.data.tonglan;
  delete obj.data.hongbao;
  console.log('去除搜索热榜广告💕');
}

$done({body: JSON.stringify(obj)});
