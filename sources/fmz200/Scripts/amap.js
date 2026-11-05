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
