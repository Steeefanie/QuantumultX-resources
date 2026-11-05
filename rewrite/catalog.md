# 重写模块清单

由锁定来源生成；全部默认关闭，同一业务选择一套。依赖齐全不等于已通过设备验证。

| 模块 | 用途 | 许可 | 收录范围 | 配套分流 |
| --- | --- | --- | --- | --- |
| [vip/spotify](vip/spotify.conf) | 移除匹配请求中的 If-None-Match 缓存校验头，让对应接口重新返回响应内容。 / 解码并重编码匹配的协议响应，调整广告、播放行为及部分客户端账户属性字段。 / 将匹配请求中的 platform=iphone 改为 platform=ipad，并处理主机名后的 :443 写法。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/youtube-feed](purify/youtube-feed.conf) | 处理 browse / next 协议响应中的首页信息流和播放页推荐广告条目。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/zhihu](purify/zhihu.conf) | 处理知乎开屏、推荐列表、问题回答列表及文章相关推荐接口中的广告字段。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/bilibili](purify/bilibili.conf) | 处理开屏、首页推荐及部分导航字段，过滤源代码列出的广告卡片或推广入口。 / 解码并重编码匹配的二进制协议响应，处理动态、视频详情等接口中的广告与推广字段。 | MIT | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/bilibili.list) |
| [purify/tieba](purify/tieba.conf) | 处理开屏、帖子列表、详情、看图模式及部分广告配置字段。 / 处理匹配二进制接口中的帖子列表、详情及广告相关字段。 | MIT | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/tieba.list) |
| [purify/qidian](purify/qidian.conf) | 处理起点阅读匹配接口中的开屏、活动入口、书架及书城推广字段。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/ad-sdk](purify/ad-sdk.conf) | 处理穿山甲、腾讯优量汇、快手联盟匹配接口的返回码与填充状态，使对应广告不下发。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/qq-news](purify/qq-news.conf) | 清理开屏及新闻列表响应中的 adList、广告组件等字段。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/vgtime](purify/vgtime.conf) | 将游戏时光初始化响应中的 data.ad 置空，处理对应开屏广告。 | MIT | 配置和直接依赖已收录 | 无 |
| [purify/baidu-netdisk](purify/baidu-netdisk.conf) | 按所列 URL 条件处理百度网盘的广告或推广接口；具体处理见下方保留原文。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/caixin](purify/caixin.conf) | 按所列 URL 条件处理财新网的广告或推广接口；具体处理见下方保留原文。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/caixin.list) |
| [purify/douban](purify/douban.conf) | 处理如开启可自行添加主机名 img*.douban.com, frodo.douban.com, erebor.douban.com等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/douban.list) |
| [purify/ithome](purify/ithome.conf) | 处理移除 轮播图 置顶文章 信息流广告等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/jd](purify/jd.conf) | 处理屏蔽DNS、禁京东直播小窗等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/jd.list) |
| [vip/kuwo-vip](vip/kuwo-vip.conf) | 处理广告、会员等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/kuwo-vip.list) |
| [purify/quark](purify/quark.conf) | 按所列 URL 条件处理夸克的广告或推广接口；具体处理见下方保留原文。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/meituan](purify/meituan.conf) | 按所列 URL 条件处理美团的广告或推广接口；具体处理见下方保留原文。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/meituan.list) |
| [purify/smzdm](purify/smzdm.conf) | 处理感谢【怎么肥事】分享等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/smzdm.list) |
| [purify/taobao](purify/taobao.conf) | 处理host-suffix, ai.m.taobao.com, reject等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/taobao.list) |
| [vip/netease-svip](vip/netease-svip.conf) | 按所列 URL 条件处理网易云音乐的广告或推广接口；具体处理见下方保留原文。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/wechat-mp](purify/wechat-mp.conf) | 处理公众号文章下方广告、微信公众号去除商品推广等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/wechat-mp.list) |
| [enhance/wechat-unlock-url](enhance/wechat-unlock-url.conf) | 按所列 URL 条件处理微信解除链接限制的广告或推广接口；具体处理见下方保留原文。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/xiaohongshu](purify/xiaohongshu.conf) | 处理惊喜弹窗、信息流、搜索页等原文列出的接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/xiaohongshu.list) |
| [vip/netease-vip](vip/netease-vip.conf) | 处理网易云音乐播放地址、歌单及搜索接口请求头以尝试解锁会员歌曲试听。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/wechat-applet](purify/wechat-applet.conf) | 处理便利蜂、顺丰速运、掌上公交及 WordPress 类微信小程序与公众号图文广告接口。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/startup-ads](purify/startup-ads.conf) | 集中处理常见 App 的开屏广告、启动横幅与初始化推广接口。 | GPL-3.0 | 配置和直接依赖已收录 | [需要时启用](../filter/adblock/fmz200/startup-ads.list) |
| [purify/youtube](purify/youtube.conf) | 处理 YouTube 视频贴片广告、首页瀑布流、搜索页、播放页、短视频及后台画中画播放。 | Apache-2.0 | 配置和直接依赖已收录 | 无 |
| [enhance/youtube-subtitle](enhance/youtube-subtitle.conf) | 匹配 YouTube timedtext 外文字幕请求并自动机翻为简体中文（tlang=zh-Hans）。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [enhance/url-redirect](enhance/url-redirect.conf) | 对 Google 本地域名、电商 HTTP 链接及常见国内软件渠道代理域名执行 302 重定向。 | GPL-2.0 | 配置和直接依赖已收录 | 无 |
| [enhance/web-adblock](enhance/web-adblock.conf) | 清理常见伪装影视应用与网页接口中的启动公告、版本弹窗及广告配置字段。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [vip/revenuecat](vip/revenuecat.conf) | 拦截 RevenueCat 订阅校验接口并注入客户端本地 Pro/VIP 订阅与权益有效期。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [vip/xmind](vip/xmind.conf) | 处理 Xmind 客户端设备与订阅校验接口响应以解锁本地 Pro 会员功能。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [vip/meitu](vip/meitu.conf) | 处理美图秀秀及 Wink 用户与会员信息接口响应以开启客户端本地 VIP 标识。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [vip/wps-camscanner](vip/wps-camscanner.conf) | 处理 WPS Office 用户概览与扫描全能王资产查询接口以解锁本地会员特权。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/weibo](purify/weibo.conf) | 清理微博客户端时间流、卡片列表、搜索结果及开屏接口中的广告与推广内容。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [purify/amap](purify/amap.conf) | 清理高德地图开屏、首页底部推广卡片、语音包横幅及导航结束页广告。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |
| [enhance/safari-qsearch](enhance/safari-qsearch.conf) | 在 Safari 地址栏输入 gh/yt/zh/bili/xh/db/wk/bd 加关键词直达对应站内搜索，无前缀默认转 Google。 | GPL-3.0 | 配置和直接依赖已收录 | 无 |

隔离行号及说明详见对应重写文件头部注释。只有域名/IP 条件的来源不会生成空重写，相关拦截保存在配套分流目录。
