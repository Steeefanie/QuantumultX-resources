/*
 * 名称：腾讯新闻接口去广告
 * 用途：清理开屏及新闻列表响应中的 adList、广告组件等字段。
 * 处理阶段：响应体：JSON
 * 使用前提：仅由对应重写规则按 URL 调用；HTTPS 响应处理通常需要个人 MITM 证书及对应 hostname。
 * 使用边界：代码按对应 POST 接口处理；接口版本变化时可能只保留部分效果。
 * 本地说明日期：2026-11-04（非上游更新时间）
 * 来源：https://github.com/app2smile/rules/blob/df6366a7024e0b3f0aa3510c5b791eea6f3cba89/js/qq-news.js
 * 来源许可：MIT；原作者署名及源代码保留在下方原文中，对应许可随目录保存。
 * 本地修改：仅添加本段用途说明；下方保留上游正文，不把原始代码归为本项目原创。
 */
let url = $request.url;
let method = $request.method;
if (!$response.body) {
    console.log(`$response.body为undefined:${url}`);
    $done({});
}

let body = JSON.parse($response.body);

if (method !== "POST") {
    $notification.post("腾讯新闻App脚本错误", "method错误:", method);
}

if (url.includes("r.inews.qq.com/gw/page/event_detail")) {
    removeAdList('event_detail');
} else if (url.includes("r.inews.qq.com/gw/page/channel_feed")) {
    removeAdList('channel_feed');
} else {
    let name = "";
    if (url.includes("news.ssp.qq.com/app")) {
        name = '开屏页';
    } else if (url.includes("r.inews.qq.com/getQQNewsUnreadList")) {
        // 是否弃用,还需要验证
        name = '要闻/财经等';
    } else if (url.includes("r.inews.qq.com/news_feed/hot_module_list")) {
        name = '财经精选-更多';
    } else if (url.includes("r.inews.qq.com/gw/event/list")) {
        // 弃用
        name = '专题gw/event/list';
    } else if (url.includes("r.inews.qq.com/getTwentyFourHourNews")) {
        // 弃用
        name = '热点精选getTwentyFourHourNews';
    } else if (url.includes("r.inews.qq.com/getQQNewsListItems")) {
        // 弃用
        name = '热点精选getQQNewsListItems';
    } else if (url.includes("r.inews.qq.com/getTagFeedList")) {
        // 如地方专区下的 XX旅游 XX美食列表广告
        name = 'getTagFeedList';
    } else {
        $notification.post('腾讯新闻App脚本错误', "路径匹配错误:", url);
    }
    console.log(name);
    if (!body.adList) {
        // 部分专题列表无广告,没有adList字段
        console.log('无广告');
    } else {
        body.adList = null;
        console.log('成功');
    }
}

body = JSON.stringify(body);

$done({
    body
});

function removeAdList(name) {
    console.log(`gw/page/${name}`);
    if (body.data.widget_list) {
        body.data.widget_list = body.data.widget_list.filter(item => {
            if (item.widget_type === 'ad_list') {
                console.log('去除ad_list广告');
                return false;
            }
            return true;
        });
    } else {
        console.log($response.body);
        $notification.post('腾讯新闻App脚本错误', name, '无widget_list字段');
    }
}
