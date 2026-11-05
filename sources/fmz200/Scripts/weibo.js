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
