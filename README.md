# QuantumultX-resources

**100% 自托管、零外部依赖**的 Quantumult X 分流规则、重写模块、脚本、策略图标与完整主配置库。

所有分流规则、重写配置、配套 JS 脚本、解析器工具及策略组图标均完整保存在本仓库内，运行时不引用任何第三方仓库外链，避免因上游删库或改链导致配置失效。

---

## 目录结构

```text
QuantumultX-resources/
├── examples/                   # 主配置文件与参数说明
│   ├── quantumult_steeefanie.conf  # 完整主配置模板（主力配置文件）
│   ├── README.md                   # 订阅填写与多机场节点筛选说明
│   └── config-guide.md             # 各段落配置参数详解（含 DoH 等 DNS 备选方案）
├── filter/                     # 分流与去广告规则（共 1,584 份 .list）
│   ├── services/                   # 1,417 个按具体服务细分的分流规则（如 openai.list、xiaohongshu.list）
│   ├── collections/                # 137 个综合分类合集（如 domestic.list、global.list、advertising.list）
│   ├── adblock/                    # 重写配套去广告规则（含单条合并去重版 combined.list）
│   └── custom/                     # OneDrive 网页端与同步端独立规则
├── rewrite/                    # 重写模块（共 37 个模块，按功能分为 3 类）
│   ├── vip/                        # 会员解锁与本地 VIP（网易云、Spotify、RevenueCat、Xmind、美图、WPS 等）
│   ├── purify/                     # 软件去广告与界面净化（小红书、微信、B站、知乎、微博、高德、油管、去开屏等）
│   ├── enhance/                    # 功能增强与效率工具（微信外链解锁、油管字幕自动中译、神机重定向、Safari 搜索等）
│   ├── catalog.md                  # 全部 37 个重写模块清单
│   └── README.md                   # 重写分类说明与 MITM 证书排除说明
├── scripts/                    # 重写与工具脚本（共 40 个文件）
│   ├── app2smile/                  # 13 个重写配套脚本（MIT 许可）
│   ├── fmz200/                     # 23 个重写配套脚本（GPL-3.0 许可）
│   └── tools/                      # 4 个全局工具脚本（Shawn 资源解析器、流媒体解锁检测、BoxJS、UI 任务）
├── icon/                       # 策略组图标（256×256 PNG）
│   ├── proxy.png                   # PROXY 总组与配置封面蓝绿地球图标
│   └── hk.png / tw.png / ...       # 13 个国家／地区正方形旗帜图标
├── sources/                    # 上游原始快照、个人选择配置与版本哈希锁文件
└── tools/                      # 规则构建、配置生成、域名查询与自动化测试工具
```

---

## 快速开始：使用完整主配置

直接导入或参考 [`examples/quantumult_steeefanie.conf`](examples/quantumult_steeefanie.conf)，只需在本机完成以下两步：

1. **填写机场节点订阅（`[server_remote]`）**
   - 将示例链接替换为你的机场订阅地址，并去掉行首 `#`。
   - 开启 `opt-parser=true` 时，内置的资源解析器支持多格式订阅转换并为节点自动添加地区旗帜 Emoji。
2. **填入个人 MITM 证书（`[mitm]`，可选）**
   - 仅域名分流不需要 MITM；若启用 `[rewrite_remote]` 中的去广告与 VIP 重写，请在本机生成并粘贴自己的 `passphrase` 与 `p12` 证书。
   - `[mitm]` 已默认排除 `*.apple.com`、丰巢、华米、抖音系等强校验证书域名，防止 App Store 无法切换账号或应用断网。

### 策略组结构（`[policy]`）

- **内置动作**：`DIRECT`（直连）、`REJECT`（拒绝）。
- **总代理组 `PROXY`**：手动选择地区（默认候选首位为 `Hong Kong`），切换 `PROXY` 时所有绑定 `PROXY` 的服务同步切换出口地区。
- **地区策略组（默认启用 5 个主力地区 + 8 个注释备用）**：
  - 默认启用：`Hong Kong`、`Taiwan`、`Japan`、`Singapore`、`United States`（各地区内部采用 `url-latency-benchmark`，间隔 600 秒、容差 50 毫秒自动按延迟择优）。
  - 注释备用：`South Korea`、`United Kingdom`、`Germany`、`France`、`Canada`、`Australia`、`Turkey`、`Indonesia`（如需使用，取消对应行注释并加入 `PROXY` 候选即可）。
- **多机场筛选**：见 [`examples/README.md`](examples/README.md#多机场筛选)。

### 个人分流清单（`[filter_remote]`）

主配置按优先级依次加载（默认均已设为 `enabled=true`）：
1. **重写配套去广告合集**：[`filter/adblock/combined.list`](filter/adblock/combined.list)（合并全部 27 份重写配套拦截规则，策略 `REJECT`）
2. **通用广告与跟踪拦截**：[`filter/collections/advertising.list`](filter/collections/advertising.list)（策略 `REJECT`）
3. **专用服务独立分流**：
   - **YouTube**（[`google-youtube.list`](filter/services/google-youtube.list)）置于 **Google 综合规则**（[`google-without-youtube.list`](filter/collections/google-without-youtube.list)）之前，支持单独指定地区；另提供可选的 [`google-gemini.list`](filter/services/google-gemini.list) 独立子项。
   - **OneDrive** 拆分为网页端（[`onedrive-web.list`](filter/custom/onedrive-web.list)，走 `Hong Kong`）与同步端（[`onedrive-sync.list`](filter/custom/onedrive-sync.list)，走 `DIRECT`），置于 **Microsoft** 综合规则之前。
   - **小红书**（[`xiaohongshu.list`](filter/services/xiaohongshu.list)）默认 `DIRECT`；**Steam、维基百科、Spotify、OpenAI、Anthropic、LinkedIn、Disney、Netflix、Meta、X (Twitter)** 均作为独立分流项默认指向 `PROXY`，可随时单独改绑任意地区组。
4. **国内与海外兜底合集**：[`domestic.list`](filter/collections/domestic.list)（`DIRECT`）→ [`global.list`](filter/collections/global.list)（`PROXY`）→ `geoip, cn, DIRECT` → `final, PROXY`。

---

## 分流规则库（`filter/`）

基于 V2Fly `domain-list-community` 快照转换，共 **1,417 个服务文件**（`filter/services/*.list`）与 **137 个分类集合**（`filter/collections/*.list`），并补充了 14 个 Google AI / Antigravity 官方端点（见 [`sources/local-additions.json`](sources/local-additions.json)）。

### 常用综合集合

| 集合文件 | 用途 | 条件数 | 文件内默认策略 |
| --- | --- | ---: | --- |
| [domestic.list](filter/collections/domestic.list) | 国内接入域名合集 | 7,909 | `direct` |
| [global.list](filter/collections/global.list) | 海外接入域名合集 | 25,593 | `proxy` |
| [advertising.list](filter/collections/advertising.list) | 广告及跟踪域名合集 | 840 | `reject` |
| [ai-global.list](filter/collections/ai-global.list) | 境外 AI 与模型服务 | 223 | `proxy` |
| [ai-domestic.list](filter/collections/ai-domestic.list) | 境内接入 AI 与模型服务 | 120 | `direct` |
| [media.list](filter/collections/media.list) | 流媒体与音视频服务 | 1,576 | `proxy` |
| [development.list](filter/collections/development.list) | 开发与软件服务 | 681 | `proxy` |
| [games.list](filter/collections/games.list) | 游戏平台与下载服务 | 1,155 | `proxy` |
| [social-global.list](filter/collections/social-global.list) | 境外社交媒体 | 606 | `proxy` |
| [scholar-global.list](filter/collections/scholar-global.list) | 境外学术与出版服务 | 484 | `proxy` |
| [cloud-global.list](filter/collections/cloud-global.list) | 境外网盘服务 | 58 | `proxy` |
| [lan.list](filter/collections/lan.list) | 私有网络与路由器域名 | 124 | `direct` |
| [google-without-youtube.list](filter/collections/google-without-youtube.list) | 排除 YouTube 专用条件后的 Google 综合域名 | 888 | `proxy` |

---

## 重写模块与脚本（`rewrite/` & `scripts/`）

共收录 **37 个重写模块** 与 **40 个本地脚本**，按用途归入 3 个子目录（完整列表见 [`rewrite/catalog.md`](rewrite/catalog.md)，详细说明见 [`rewrite/README.md`](rewrite/README.md)）：

- **[`rewrite/vip/`](rewrite/vip)**：网易云音乐本地黑胶 SVIP、Spotify VIP、RevenueCat 通用内购解锁（支持 No Fusion、Notability、Goodnotes、Locket、VSCO 等）、Xmind Pro、美图秀秀/Wink VIP、WPS 超级会员/扫描全能王 VIP、酷我音乐 VIP。
- **[`rewrite/purify/`](rewrite/purify)**：YouTube、小红书（含无水印原图保存）、微信公众号、微信小程序去激励广告、哔哩哔哩、知乎、微博、高德地图、墨鱼通用去开屏 2.0、四大广告联盟 SDK、淘宝、京东、美团、豆瓣、百度网盘、夸克、什么值得买、IT之家等深度净化。
- **[`rewrite/enhance/`](rewrite/enhance)**：微信外链直接打开、YouTube 字幕自动中译、神机重定向、Safari 超级搜索 Q-Search、网页与影视站点弹窗净化。

---

## 日常维护命令

要求 Python 3.10+（仅依赖标准库）：

```bash
# 修改 sources/selection.json 或 tools/config_templates.py 后，离线重新生成全部规则与主配置
python3 tools/build.py --rebuild

# 校验所有规则、重写、脚本与锁文件哈希是否一致
python3 tools/build.py --check

# 运行全部 45 项单元测试
python3 -m unittest discover -s tools -p 'test_*.py'

# 查询某个域名命中了哪些规则文件
python3 tools/query.py chatgpt.com

# 从上游拉取最新 V2Fly 域名数据并重新构建
python3 tools/build.py --refresh
```

---

## 来源署名与许可

本项目自编构建工具与配置模板采用 [MIT 许可](LICENSE)。仓库内收录的第三方规则、脚本与图标均保留原作者署名与各自独立许可：

| 来源项目 | 本仓库收录内容 | 许可 |
| --- | --- | --- |
| [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) | 分流规则上游快照（`sources/v2fly/`）及转换后的 `filter/` 规则 | [MIT](sources/v2fly/LICENSE) |
| [app2smile/rules](https://github.com/app2smile/rules) | 9 个重写模块与 13 个配套脚本（`scripts/app2smile/`） | [MIT](rewrite/licenses/app2smile-MIT.txt)（运行库见 [第三方说明](scripts/THIRD-PARTY-NOTICES.md)） |
| [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) | 28 个重写模块、23 个配套脚本（`scripts/fmz200/`）及去广告分流 | [GPL-3.0](rewrite/licenses/fmz200-GPL-3.0.txt) |
| [KOP-XIAO/QuantumultX](https://github.com/KOP-XIAO/QuantumultX) & [chavyleung/scripts](https://github.com/chavyleung/scripts) | 资源解析器、流媒体解锁检测、UI 任务与 BoxJS 脚本（`scripts/tools/`） | 保留原作者署名与固定版本哈希（[`sources/remote-resources.lock.json`](sources/remote-resources.lock.json)） |
| [lipis/flag-icons](https://github.com/lipis/flag-icons) & [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) | `icon/` 下的 13 个国家／地区旗帜与 `proxy.png` 地球图标 | [MIT](icon/licenses/flag-icons-MIT.txt) & [Public Domain](icon/licenses/natural-earth-PUBLIC-DOMAIN.txt) |
