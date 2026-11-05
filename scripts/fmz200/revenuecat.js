/*
 * 名称：RevenueCat 通用内购订阅状态调整
 * 用途：移除请求头中的 ETag 缓存标识，并在匹配的 RevenueCat 订阅校验响应中注入客户端订阅与权益有效期字段。
 * 处理阶段：请求头与响应体：JSON
 * 使用前提：仅由 RevenueCat 通用内购重写规则调用；需要个人 MITM 证书及 api.revenuecat.com、api.rc-backup.com 的 hostname。
 * 使用边界：适用于采用 RevenueCat 客户端校验的摄影、笔记与工具类应用（如 No Fusion、Locket、Notability 等）；服务端强校验功能不保证生效。
 * 本地说明日期：2026-11-05（非上游更新时间）
 * 来源：https://raw.githubusercontent.com/Yu9191/Rewrite/main/Revenuecat.js
 * 来源许可：GPL-3.0；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：基于 @Yu9191 Revenuecat.js 的 110+ 应用 UAMappings 映射表整理，并补充通用 pro/vip/premium 兜底权益字段。
 */
const resp = {};

if (typeof $response === "undefined") {
  delete $request.headers["x-revenuecat-etag"];
  delete $request.headers["X-RevenueCat-ETag"];
  resp.headers = $request.headers;
} else if ($response.body) {
  let obj = JSON.parse($response.body);
  if (obj && obj.subscriber) {
    obj.subscriber.subscriptions = obj.subscriber.subscriptions || {};
    obj.subscriber.entitlements = obj.subscriber.entitlements || {};
    const ua = $request.headers["User-Agent"] || $request.headers["user-agent"] || "";
    const UAMappings = {
      "Pocket%20Widgets": { name: "Subscription", id: "com.niko.PocketWidgetsApp.lifetimePlus" },
      "ClipyBoard": { name: "premium", id: "clipyboard_yearly" },
      "Wake%20Music": { name: "premium", id: "com.OfflineMusic.www.lifetime298" },
      "Spark": { name: "premium", id: "spark_c_5999_1y_d50" },
      "Barcodes": { name: "Unlimited", id: "com.barcodesapp.lifetime" },
      "Relax": { name: "pro", id: "com.happydogteam.relax.lifetimePro" },
      "Nightcam": { name: "nightcam_pro", id: "com.ahmetserdarkaradeniz.nightcamyearlyalternative" },
      "Jellycuts": { name: "pro", id: "standart" },
      "Finale%E2%80%A2Pad": { name: "Pro", id: "com.cherpake.finale.lt" },
      "outside": { name: "Outside Pro", id: "outside_sub_yearly_super_cheap_free_trial" },
      "Sibelius%E2%80%A2Pad": { name: "Premium", id: "com.cherpake.musicpad.all" },
      "NumPad": { name: "Pro", id: "com.cherpake.numpad.pro.discount" },
      "Drive": { name: "Pro", id: "com.cherpake.drive.viewer.free" },
      "TV%20Remote": { name: "Pro", id: "com.cherpake.tvr.all.discount" },
      "Remote": { name: "Pro", id: "com.cherpake.macrc.more" },
      "Chatty": { name: "pro AI Pro", id: "chatty.yearly.1" },
      "ainotes": { name: "HoneyNote AI Pro", id: "NCIAP_A_149_99" },
      "quitnow": { name: "pro_features", id: "pro_features_year_subscription" },
      "ChatPub": { name: "Unlimited Access", id: "conversationai.year" },
      "Unfold": { name: "FF2_STORY", id: "UNFOLD_PRO_YEARLY" },
      "Origami": { name: "Premium", id: "origami_499_1m" },
      "Reader": { name: "standard", id: "vd_monthly_999" },
      "Vocai-iOS": { name: "AI Pro", id: "vocabAI_900_1m" },
      "Treering": { name: "Pro", id: "Treering.pro.yearly1" },
      "AmazingWidget": { name: "pro", id: "com.moyo.forever.vip" },
      "dtdVibe": { name: "pro", id: "com.dtd.aroundu.year" },
      "DtdVibe": { name: "pro", id: "com.dtd.playlist.premium.subscription.yearr" },
      "AdGuard%20Home%20Remote": { name: "aghrpro", id: "adguard.home.remote.pro" },
      "Chatme": { name: "premium", id: "chatme_premium_year_discount" },
      "Alpenglow": { name: "newPro", id: "ProLifetime" },
      "Opal": { name: "premium_tier_2", id: "com.withopal.opal.premiumtier2lifetime" },
      "Photoooo": { name: "lifetime", id: "canoe_28_rnb_forever" },
      "Baby%20Generator": { name: "premium_features", id: "babygenerator_499_weekly" },
      "Boring": { name: "pro", id: "month" },
      "Snipd": { name: "premium", id: "test_snipd_premium_grandfather_1y_4200_trial_2w_v1" },
      "Overdue": { name: "Pro", id: "1" },
      "iScape": { name: "Pro", id: "Limited_YearlyProAutoRenew" },
      "GigaBody": { name: "Pro", id: "GigaBodySubscriptionYear_v1" },
      "FunPix": { name: "premium", id: "intro_price_weekly" },
      "WiseMate": { name: "vip_entitlement", id: "wisemate.ai.ios.week" },
      "Loora": { name: "Yearly", id: "yearly_119_99_no_trial" },
      "Browser": { name: "pro", id: "pro_zoomable" },
      "becoming": { name: "Strength Pro", id: "strength_membership_monthly" },
      "Chords": { name: "FullUnlock", id: "cas_full_unlock_yearly_50_off" },
      "reader": { name: "subscriptions", id: "com.valo.reader.vip1.forever" },
      "Gradient": { name: "unlimited", id: "com.tickettothemoon.gradient.unlimited.yearly.small" },
      "Python3IDE": { name: "pro", id: "python3ide_six_month" },
      "Scale%20Finder": { name: "Pro", id: "sf_2999_1y_1w0" },
      "Who%20Stalks": { name: "Premium", id: "ws_999_1m" },
      "PrevisShot": { name: "VIP", id: "com.previsshot.previsshot.continuous_subscribe_12month_vip" },
      "Super%20AI%20Chat": { name: "premium", id: "chatbot_v4_1999_1y" },
      "MusicPutty": { name: "pro_version", id: "mp_3599_1y" },
      "Linearity": { name: "pro", id: "linearity_curve_pro_yearly_special_offer_trial" },
      "iplayTV": { name: "com.ll.btplayer.12", id: "com.ll.btplayer.12" },
      "%E8%B5%84%E6%BA%90%E6%90%AC%E8%BF%90%E5%A4%A7%E5%B8%88": { name: "SaveTikYoutu_common", id: "LifetimeSubscription" },
      "DHWaterMarkManager": { name: "Vip", id: "lifetimeVIP_001" },
      "Krishna%20VPN%20Plus%20Browser": { name: "vpnz-lifetime", id: "vpnz-lifetime" },
      "XBListeningEnglish": { name: "enPro", id: "com.shenming.newconceptvip.year" },
      "FretTrainer": { name: "pro", id: "frettrainer.sub.yearly.pro" },
      "%E9%B2%B8%E8%90%BD%E6%96%87%E6%A1%88": { name: "vip", id: "jl_year" },
      "PeachTree": { name: "GoldMember", id: "LifetimeGoldMembership" },
      "No%20Fusion": { name: "LivePhoto", id: "com.grey.livephoto.reference.price" },
      "mark_cup": { name: "premiun", id: "202403180021" },
      "VOX": { name: "VOX Premium", id: "com.coppertino.VoxMobile.AU.Loop1_v8" },
      "PDF%20Viewer": { name: "sub.pro", id: "com.pspdfkit.viewer.sub.pro.yearly" },
      "Text%20Workflow": { name: "pro", id: "tw_99_1m" },
      "FaceMa": { name: "Pro access", id: "Pro_Lifetime" },
      "MadeYu": { name: "pro_plus", id: "my_549_1m_400" },
      "clica": { name: "pro", id: "clica.vip.year" },
      "FoJiCam": { name: "ProVersionLifeTime", id: "com.uzero.cn.fojicam.life2" },
      "ShellBoxKit": { name: "pro", id: "ShellBoxKit.Lifetime" },
      "PicSeedClient": { name: "Pro", id: "com.picseed.sub.pro.monthly" },
      "StarDiary": { name: "pro", id: "com.gsdyx.StarDiary.nonConsumable.forever" },
      "CountDuck": { name: "premium", id: "Lifetime" },
      "StarFocus": { name: "pro", id: "com.gsdyx.StarFocus.nonConsumable.forever" },
      "Context_iOS": { name: "pro", id: "ctx_3y_sspai_preorder_angel" },
      "Vision": { name: "promo_3.0", id: "vis_lifetime_3.0_promo" },
      "Structured": { name: "pro", id: "today.structured.pro" },
      "Cookie": { name: "allaccess", id: "app.ft.Bookkeeping.lifetime" },
      "HTTPBot": { name: "Pro", id: "httpbot_1499_1y_1w0" },
      "MyPianist": { name: "pro", id: "com.collaparte.mypianist.pro.gift.twelve" },
      "TouchRetouchBasic": { name: "premium", id: "tr5_yearlysubsc_30_and_20_dlrs" },
      "Free": { name: "pro", id: "appspree_pro_lifetime" },
      "Version": { name: "pro", id: "httpbot_1499_1y_1w0" },
      "wordswag": { name: "pro", id: "Pro_Launch_Monthly" },
      "BlackBox": { name: "plus", id: "app.filmnoir.appstore.purchases.lifetime" },
      "LongmaoApp": { name: "pro", id: "douyina_forever_01" },
      "AnkiPro": { name: "Premium", id: "com.ankipro.app.lifetime" },
      "AIChat": { name: "AI Plus", id: "aiplus_yearly" },
      "SmartAIChat": { name: "Premium", id: "sc_3999_1y" },
      "AIKeyboard": { name: "plus_keyboard", id: "aiplus_keyboard_yearly" },
      "TextMask": { name: "pro", id: "tm_lifetime" },
      "MusicMate": { name: "premium", id: "mm_lifetime_68_premium" },
      "ImagineAI": { name: "pro", id: "artistai.yearly.1" },
      "VoiceAI": { name: "Special Offer", id: "voiceannualspecial" },
      "Langster": { name: "Premium", id: "com.langster.universal.lifetime" },
      "Chat%E7%BB%83%E5%8F%A3%E8%AF%AD": { name: "Premium", id: "com.tech.AiSpeak.All" },
      "Readle": { name: "Premium", id: "com.hello.german.yearly" },
      "image_upscaler": { name: "pro", id: "yearly_sub_pro" },
      "Muse": { name: "pro", id: "monthly_pro_muse" },
      "Funexpected%20Math": { name: "plus", id: "Plus6Months14DaysTrial" },
      "cdiary": { name: "Premium", id: "pub.kiya.daymoment.lifetime" },
      "Sex%20Actions": { name: "Premium Plus", id: "ru.sexactions.subscriptionPlusWeek1" },
      "Law": { name: "vip", id: "LawVIPOneYear" },
      "Emoji+%20%F0%9F%98%9": { name: "premium", id: "com.emoji.freemium.subscription.premium" },
      "universal": { name: "Premium", id: "remotetv.yearly.01" },
      "HabitKit": { name: "Pro", id: "habitkit_1799_lt" },
      "windiary": { name: "Pro", id: "windiary_1799_lt" },
      "Liftbear": { name: "Pro", id: "liftbear_2399_1y" },
      "Currency": { name: "plus", id: "com.jeffreygrossman.currencyapp.iap.pro.crossgrade" },
      "VSCO": { name: "pro", id: "vscopro_global_5999_annual_7D_free" },
      "Pillow": { name: "premium", id: "com.neybox.pillow.premium.yearly" }
    };
    const subData = {
      is_sandbox: false,
      ownership_type: "PURCHASED",
      billing_issues_detected_at: null,
      period_type: "normal",
      expires_date: "2099-12-31T12:00:00Z",
      grace_period_expires_date: null,
      unsubscribe_detected_at: null,
      original_purchase_date: "2023-09-01T11:00:00Z",
      purchase_date: "2023-09-01T11:00:00Z",
      store: "app_store"
    };
    let matched = false;
    for (const key in UAMappings) {
      if (new RegExp(`^${key}`, "i").test(ua)) {
        const { name, id } = UAMappings[key];
        obj.subscriber.subscriptions = {};
        obj.subscriber.subscriptions[id] = subData;
        obj.subscriber.entitlements[name] = Object.assign({}, subData, { product_identifier: id });
        matched = true;
        break;
      }
    }
    if (!matched) {
      const entData = {
        grace_period_expires_date: null,
        purchase_date: "2023-09-01T11:00:00Z",
        product_identifier: "com.revenuecat.pro.yearly",
        expires_date: "2099-12-31T12:00:00Z"
      };
      const commonEntitlements = [
        "pro", "Pro", "PRO", "premium", "Premium", "vip", "VIP",
        "plus", "Plus", "gold", "all_access", "unlimited", "LivePhoto",
        "nofusion_pro", "locket_gold", "vsco_pro", "notability_plus", "goodnotes_special_edition"
      ];
      obj.subscriber.subscriptions["com.revenuecat.pro.yearly"] = subData;
      obj.subscriber.subscriptions["com.grey.livephoto.reference.price"] = subData;
      for (const key of commonEntitlements) {
        obj.subscriber.entitlements[key] = Object.assign({}, entData);
      }
    }
    resp.body = JSON.stringify(obj);
  }
}
$done(resp);
