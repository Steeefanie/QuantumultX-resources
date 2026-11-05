/*
 * 名称：知乎 App 广告接口净化
 * 用途：处理知乎开屏、推荐列表、问题回答列表及文章相关推荐接口中的广告字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由对应重写规则按 URL 调用；HTTPS 响应处理通常需要个人 MITM 证书及对应 hostname。
 * 使用边界：只处理源配置列明的接口，不是浏览器页面 CSS 去广告规则。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/app2smile/rules/blob/df6366a7024e0b3f0aa3510c5b791eea6f3cba89/js/zhihu.js
 * 来源许可：MIT；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
const url = $request.url;
const method = $request.method;
if (!$response.body) {
    console.log(`$response.body为undefined:${url}`);
    $done({});
}
console.log(`2022-12.6`)

const noticeTitle = "知乎去广告脚本错误";
let body = JSON.parse($response.body);

if (method !== "GET") {
    console.log(url);
    $notification.post(noticeTitle, "method错误:", method);
}

if (url.includes("api.zhihu.com/commercial_api/real_time_launch_v2")) {
    console.log('知乎-开屏页');
    if (!body.launch) {
        console.log(`body:${$response.body}`);
        $notification.post(noticeTitle, name, "launch字段为空");
    }
    let launch = JSON.parse(body.launch);
    if (!launch.ads) {
        // ads字段有时候为空,有时候没有ads字段
        console.log(`body:${$response.body}`);
        // $notification.post(noticeTitle, name, "launch-ads字段为空");
    } else {
        launch.ads = [];
        console.log('成功');
    }
    body.launch = JSON.stringify(launch);
} else if (url.includes("api.zhihu.com/topstory/recommend")) {
    console.log('知乎-推荐列表');
    let dataArr = body.data;
    if (!dataArr) {
        console.log(`body:${$response.body}`);
        $notification.post(noticeTitle, "知乎推荐", "data字段为空");
    } else {
        body.data = dataArr.filter(item => {
            if (item.extra?.type === "zvideo") {
                let videoUrl = item.common_card.feed_content.video.customized_page_url;
                let videoID = getUrlParamValue(videoUrl, "videoID");
                if (!videoID) {
                    console.log('zvideo未获取到videoID');
                    console.log(`body:${$response.body}`);
                    // 部分获取不到videoId并且视频可以播放
                } else {
                    console.log(`videoID处理成功,原始:${item.common_card.feed_content.video.id},修改为:${videoID}`);
                    item.common_card.feed_content.video.id = videoID;
                }
            } else if (item.type === 'market_card' && item.fields?.header?.url && item.fields.body?.video?.id) {
                let videoID = getUrlParamValue(item.fields.header.url, "videoID");
                if (!videoID) {
                    console.log(`body:${$response.body}`);
                    $notification.post(noticeTitle, "知乎推荐列表视频", "videoID获取错误");
                } else {
                    console.log(`market_card-videoID处理成功,原始:${item.fields.body.video.id},修改为:${videoID}`);
                    item.fields.body.video.id = videoID;
                }
            } else if (item.common_card?.feed_content?.video?.id) {
                let search = '"feed_content":{"video":{"id":';
                let str = $response.body.substring($response.body.indexOf(search) + search.length);
                let videoID = str.substring(0, str.indexOf(','));
                console.log(`其他-videoID处理成功,原始:${item.common_card.feed_content.video.id},修改为:${videoID}`);
                item.common_card.feed_content.video.id = videoID;
            }
            return item.type !== 'feed_advert';
        });
        if (body.data.length === dataArr.length) {
            console.log('列表数据无广告');
        } else {
            console.log('成功');
        }
    }
} else if (url.includes("api.zhihu.com/questions") || url.includes("api.zhihu.com/v4/questions")) {
    if (url.includes("v4/questions")) {
        console.log('v4/questions');
    } else {
        console.log('questions');
    }
    console.log('知乎-问题回答列表');
    if (!body.data.ad_info && !body.ad_info) {
        // 个别问题回答列表无广告
        console.log("问题回答列表无广告");
    } else {
        body.data.ad_info = null;
        body.ad_info = null;
        console.log('成功');
    }
} else if (url.includes("www.zhihu.com/api/v4/answers")) {
    console.log('知乎-回答下的广告');
    if (!body.paging || !body.data) {
        console.log(`body:${$response.body}`);
        $notification.post(noticeTitle, '知乎回答下广告', "paging/data字段为空");
    } else {
        body.paging = null;
        body.data = null;
        console.log('成功');
    }
} else if (url.includes("www.zhihu.com/api/v4/articles/")) {
    console.log('知乎-文章articles回答下广告');
    if (!body.ad_info) {
        console.log(`body:${$response.body}`);
        $notification.post(noticeTitle, name, "articles-ad_info字段为undefined");
    } else {
        body.ad_info = null;
        console.log('成功');
    }
} else if (url.includes("appcloud2.zhihu.com/v3/config")) {
    console.log('知乎-appcloud2 config配置');
    if (body.config?.zhcnh_thread_sync?.ZHBackUpIP_Switch_Open === '1') {
        body.config.zhcnh_thread_sync.ZHBackUpIP_Switch_Open = '0';
        console.log('ZHBackUpIP_Switch_Open改为0');
    } else {
        console.log('无需更改ZHBackUpIP_Switch_Open');
        console.log(`body:${$response.body}`);
    }
} else if (url.includes("api.zhihu.com/commercial_api/app_float_layer")) {
    console.log('知乎-首页右下角悬浮框');
    if ('feed_egg' in body) {
        console.log('成功');
        body = {};
    } else {
        console.log('无需处理');
    }
} else {
    $notification.post(noticeTitle, "路径匹配错误:", url);
}

body = JSON.stringify(body);

$done({
    body
});


function getUrlParamValue(url, queryName) {
    return Object.fromEntries(url.substring(url.indexOf("?") + 1)
        .split("&")
        .map(pair => pair.split("="))
    )[queryName];
}
