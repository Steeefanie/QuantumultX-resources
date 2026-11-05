# 重写库（按功能分类）

本地整理日期：2026-11-05。保存可直接订阅的 Quantumult X 重写正文；调用的脚本完整保存在同仓库 `scripts/`，100% 本地托管、零外部依赖。当前收录 **37 个精选重写模块、36 个完整脚本、27 份配套分流**（合并为 `filter/adblock/combined.list`），全部按用途归类在三个功能目录下：

- **`rewrite/vip/`**：会员破解与本地 VIP 解锁（8 个模块）
- **`rewrite/purify/`**：主流软件深度界面净化（24 个模块）
- **`rewrite/enhance/`**：功能增强与效率工具（5 个模块）

完整清单见 [37 个模块总表](catalog.md)。

## 1. 会员破解与本地 VIP（`rewrite/vip/`）

| 文件 | 用途与说明 |
| --- | --- |
| [vip/netease-svip.conf](vip/netease-svip.conf) | 网易云音乐净化 + 本地黑胶 SVIP 7；含本地 `wyres.js` |
| [vip/netease-vip.conf](vip/netease-vip.conf) | 网易云音乐纯 VIP 试听请求头处理；含本地 `Wyy.js`（与上一条二选一） |
| [vip/spotify.conf](vip/spotify.conf) | Spotify VIP 解锁（去切歌限制、音质≤高、去广告 @app2smile） |
| [vip/revenuecat.conf](vip/revenuecat.conf) | RevenueCat 通用内购 VIP 解锁（支持 No Fusion、Notability、Goodnotes、Locket、VSCO、Darkroom 等） |
| [vip/xmind.conf](vip/xmind.conf) | Xmind 思维导图客户端本地 Pro 会员解锁 |
| [vip/meitu.conf](vip/meitu.conf) | 美图秀秀 / Wink 客户端本地粉钻 VIP 解锁 |
| [vip/wps-camscanner.conf](vip/wps-camscanner.conf) | WPS 超级会员/稻壳会员 & 扫描全能王高级账户本地解锁 |
| [vip/kuwo-vip.conf](vip/kuwo-vip.conf) | 酷我音乐豪华 VIP 解锁 + 界面净化 |

## 2. 主流软件深度净化（`rewrite/purify/`）

| 文件 | 用途与说明 |
| --- | --- |
| [purify/youtube.conf](purify/youtube.conf) | 油管视频贴片与信息流深度净化 + 后台画中画（@Maasea） |
| [purify/xiaohongshu.conf](purify/xiaohongshu.conf) | 小红书深度净化 + 无水印保存原图/实况/视频 |
| [purify/wechat-mp.conf](purify/wechat-mp.conf) | 微信公众号文章底部与订阅号流广告净化 |
| [purify/wechat-applet.conf](purify/wechat-applet.conf) | 微信小程序激励视频与弹窗广告净化 |
| [purify/bilibili.conf](purify/bilibili.conf) | 哔哩哔哩 App 开屏、首页推荐、动态与播放页深度净化 |
| [purify/zhihu.conf](purify/zhihu.conf) | 知乎 App 开屏、悬浮框、推荐流与回答列表净化 |
| [purify/weibo.conf](purify/weibo.conf) | 微博客户端时间流推广微博、热推卡片与超话广告净化 |
| [purify/amap.conf](purify/amap.conf) | 高德地图开屏、首页底部推广卡片与导航结束页净化 |
| [purify/startup-ads.conf](purify/startup-ads.conf) | 墨鱼通用去开屏 2.0（常见国内 App 启动开屏净化） |
| [purify/ad-sdk.conf](purify/ad-sdk.conf) | 穿山甲、优量汇、快手联盟等四大广告联盟 SDK 净化 |
| [purify/tieba.conf](purify/tieba.conf) | 百度贴吧帖子列表与详情页深度净化 |
| [purify/quark.conf](purify/quark.conf) | 夸克浏览器与网盘界面净化 |
| [purify/baidu-netdisk.conf](purify/baidu-netdisk.conf) | 百度网盘弹窗与横幅净化 |
| [purify/jd.conf](purify/jd.conf) / [purify/taobao.conf](purify/taobao.conf) / [purify/meituan.conf](purify/meituan.conf) | 京东、淘宝、美团 App 界面净化 |
| [purify/smzdm.conf](purify/smzdm.conf) / [purify/ithome.conf](purify/ithome.conf) / [purify/douban.conf](purify/douban.conf) | 什么值得买、IT之家、豆瓣 App 界面净化 |

## 3. 功能增强与效率工具（`rewrite/enhance/`）

| 文件 | 用途与说明 |
| --- | --- |
| [enhance/wechat-unlock-url.conf](enhance/wechat-unlock-url.conf) | 微信外链解锁（直接点击打开淘宝/抖音链接 @zZPiglet） |
| [enhance/youtube-subtitle.conf](enhance/youtube-subtitle.conf) | 油管官方外文字幕自动机翻为简体中文（@id77） |
| [enhance/url-redirect.conf](enhance/url-redirect.conf) | 神机重定向（京东/知乎/贴吧短链与拦截页直达 @DivineEngine） |
| [enhance/safari-qsearch.conf](enhance/safari-qsearch.conf) | Safari 超级搜索 Q-Search（地址栏输入 `gh`/`yt`/`zh`/`bili`/`xh` 快捷搜索） |
| [enhance/web-adblock.conf](enhance/web-adblock.conf) | 影视网站与网页弹窗去广告 |

## 配套分流与许可证

- 全部重写模块剥离出的域名与 IP 拦截条件已合并去重为单文件 [filter/adblock/combined.list](../filter/adblock/combined.list)，在 [examples/quantumult_steeefanie.conf](../examples/quantumult_steeefanie.conf) 的 `[filter_remote]` 首行默认启用。
- 各上游来源的开源许可证保留在 [licenses/](licenses/) 与 [scripts/licenses/](../scripts/licenses/) 下。
