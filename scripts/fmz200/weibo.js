/*
 * 名称：微博信息流与搜索卡片净化
 * 用途：过滤微博时间流、卡片列表与搜索结果响应中的推广微博、热推及广告数组字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由微博净化重写规则调用；需要个人 MITM 证书及对应 hostname。
 * 使用边界：保留正常关注流与热搜正文，仅剔除带有广告或推广标记的条目。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://github.com/ddgksf2013/Rewrite/raw/master/AdBlock/Weibo.conf
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：按微博客户端时间流、详情页、个人主页与搜索接口响应结构编写的本地 JSON 过滤脚本。
 */
let body = $response.body || "{}";
try {
  let obj = JSON.parse(body);
  const isAdStatus = item =>
    item &&
    (item.promotion ||
      item.ad_state ||
      item.mblogtypename === "广告" ||
      item.mblogtypename === "热推" ||
      item.mblogtypename === "廣告" ||
      item.WEIBO_SECOND_PROFILE_WEIBO_AD);
  if (Array.isArray(obj.statuses)) {
    obj.statuses = obj.statuses.filter(item => !isAdStatus(item));
  }
  if (Array.isArray(obj.items)) {
    obj.items = obj.items.filter(
      item => !item.data || !isAdStatus(item.data)
    );
  }
  if (Array.isArray(obj.cards)) {
    obj.cards = obj.cards.filter(
      card =>
        card.card_type !== 6 &&
        !card.mblog?.promotion &&
        !isAdStatus(card.mblog)
    );
  }
  if (obj.trend) delete obj.trend;
  if (obj.ads) obj.ads = [];
  if (obj.ad) obj.ad = [];
  body = JSON.stringify(obj);
} catch (e) {}
$done({ body });
