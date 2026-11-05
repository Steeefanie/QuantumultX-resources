# 配置模板

本地更新日期：2026-11-04（北京时间）。模板与本仓库规则配套使用，确认发布后再读取新文件和图标的远程地址。

## 目录说明

| 文件 | 内容 | 使用方法 |
| --- | --- | --- |
| [quantumult_steeefanie.conf](quantumult_steeefanie.conf) | 完整主配置模板 | 在本机填入订阅，检查策略与规则后导入；导入前先备份现有配置 |
| [config-guide.md](config-guide.md) | 逐段配置参数说明与 DNS 备选方案 | 查阅 `[general]`、`[dns]`、`[policy]`、`[mitm]` 等各段落参数含义 |

完整主配置从 `sources/selection.json` 与 `tools/config_templates.py` 生成，包含个人常用分流、广告拦截、国内/海外集合、私网 IP、GeoIP、兜底策略及精选重写模块。不要同时启用所有父组和子业务。

完整配置包含所有主要段落，已复用原配置的检测、DNS 兼容设置、资源解析器入口及流媒体交互查询；BoxJS 入口保持关闭，新增重写库的关闭条目，MITM 段不附证书或密码。模板不含机场账号、可用私人订阅或证书。文件是可填写的模板，不是已完成连通性验证的个人配置。

### 原配置复用范围

| 项目 | 模板设置 |
| --- | --- |
| 节点检测 | 原检测地址及 3000 毫秒阈值 |
| 资源解析器 | 引用 Shawn 的解析器；原生 QX 资源仍用 `opt-parser=false`，需要转换的订阅再改为 `true` |
| DNS | 原 DNS 地址、`no-system`、`no-ipv6` 及六项 `dns_exclusion_list` 兼容设置 |
| 流媒体查询 | 单条 `event-interaction` 任务，手动触发；不自动切换地区 |
| BoxJS | 保留入口，`enabled=false` |
| UDP 443 限制 | 沿用原配置，默认启用 `udp_whitelist=1-442,444-65535` |
| 按 Wi-Fi 切换模式 | 保留注释选项，按需启用 |

在复用上述设置的基础上，本轮为远程分流行加入 `inserted-resource=true`，补充 DNS 替换方案，并固定模板直接引用的解析器、交互查询和 BoxJS 地址版本。PROXY 与地区组的选择结构保持不变；规则正文另有共享根域名修正及有来源的 AI 接口补充。原始私人订阅和证书只留在本机。

逐段参数解释、原始配置中其他设置的作用，以及与本模板的差异，见 [配置参数说明](config-guide.md)。

## 策略与节点如何对应

```text
机场订阅 → 带名称的节点 → 地区名称筛选 → Hong Kong / Taiwan / Japan / Singapore / United States / South Korea 等组
服务规则 → PROXY → 手动选择某个地区组 → 在该地区内按检测延迟自动选择节点
```

`Global` 对应原配置的“全球加速”总组（避免占用 Quantumult X 系统保留名 `PROXY`/`proxy`），使用 `static` 手动选择地区，候选默认列入 **5 个主力地区**（`Hong Kong`、`Taiwan`、`Japan`、`Singapore`、`United States`）及内置 `proxy`、`direct`，其余 8 个地区保留注释备用；默认使用香港，可随时改选。香港保留在首个候选，首次导入后在客户端确认已勾选 `Hong Kong`，实际选中状态以界面为准。各地区组沿用 `url-latency-benchmark`，在筛选出的同地区节点中按检测延迟自动择优，`check-interval=600`、`tolerance=50`；`alive-checking=false` 表示不为空闲组持续检测。检测时机还受策略活动状态影响，不保证故障瞬间切换，也不保证低延迟节点能访问所有服务。

分流时可选择 `reject`（拒绝）、`direct`（直连）、`Global`（跟随总组当前所选地区），或直接选择 `Hong Kong`、`Japan` 等地区组。直接指定地区的资源独立于 `Global` 的地区选择。各地区在 `[policy]` 中分别定义筛选与测速，再由 `Global` 引用；这种引用形成总组与地区组的关系，配置文件不通过缩进表达层级。

| 地区组 | 节点名称中匹配的示例 | 默认状态 |
| --- | --- | --- |
| `Hong Kong` | 香港、Hong Kong、HK、🇭🇰 | 默认启用 |
| `Taiwan` | 台湾／台灣、台北／臺北、台中、新北、高雄、彰化、HiNet、CHT、Taiwan、Taipei、TW、🇹🇼 | 默认启用 |
| `Japan` | 日本、东京／東京、大阪、Japan、JP、🇯🇵 | 默认启用 |
| `Singapore` | 新加坡、狮城／獅城、Singapore、SG、🇸🇬 | 默认启用 |
| `United States` | 美国／美國、United States、America、LosAngeles、SanJose、Seattle、New York、US、🇺🇸 | 默认启用 |
| `South Korea` | 韩国／韓國、首尔／首爾、Korea、Korean、Seoul、KR、🇰🇷 | 注释备用 |
| `United Kingdom` | 英国／英國、United Kingdom、London、GB／UK、🇬🇧 | 注释备用 |
| `Germany` | 德国／德國、Germany、Frankfurt、Berlin、法兰克福、柏林、DE、🇩🇪 | 注释备用 |
| `France` | 法国／法國、France、Paris、FR、🇫🇷 | 注释备用 |
| `Canada` | 加拿大、Canada、Toronto、Vancouver、CA、🇨🇦 | 注释备用 |
| `Australia` | 澳大利亚、澳洲、Australia、Sydney、Melbourne、悉尼、墨尔本、AU、🇦🇺 | 注释备用 |
| `Turkey` | 土耳其、Turkey、Turkish、Türkiye、Istanbul、TR、🇹🇷 | 注释备用 |
| `Indonesia` | 印尼、印度尼西亚、Indonesia、Indonesian、Jakarta、ID、🇮🇩 | 注释备用 |

英文匹配忽略大小写；短代码限制相邻字符，减少落入普通英文单词的情况。规则排除常见流量／到期提示名称，仍无法兼容所有机场命名。本模板按常见的单地区节点名适配，不为假设的多地区中转命名增加额外逻辑。名称分类不验证实际出口 IP、地区解锁或连通性。

默认启用 **港、台、日、新、美 5 个主力地区** 并列入 `Global`；其余 8 个地区保留注释备用，需要时取消对应策略行注释并加入 `Global` 候选即可。

## 多机场筛选

`[server_remote]` 的 `tag` 标识机场订阅；节点自身也有名称。对应关系为：

| 配置项 | 筛选对象 |
| --- | --- |
| `resource-tag-regex` | 机场订阅的 `tag` |
| `server-tag-regex` | 节点名称 |

默认地区组跨所有已启用的订阅收集节点。例如机场 A 的“韩国首尔 01”和机场 B 的“Korean Premium”都会进入 `South Korea`；`South Korea` 本身不代表某个机场。

需要限定来源时，在相应地区组行添加参数，保留该行原有的 `server-tag-regex`：

```ini
resource-tag-regex=^Airport-A$
```

允许两个机场时使用 `resource-tag-regex=^(Airport-A|Airport-B)$`。这些名字必须与订阅 `tag` 一致；订阅名含正则特殊字符时需要转义。模板地址使用 `example.com` 占位，不能提供节点；换成自己的 QX 原生订阅并移除行首注释后才能加载。其他受支持格式可使用模板登记的解析器，并为对应资源设置 `opt-parser=true`。

## 各服务选不同地区

大多数服务沿用 `force-policy=PROXY`，需要固定地区的单项再改为例如 `force-policy=South Korea`；需要直连或拒绝时使用 `direct`／`reject`。地区组必须先在主配置中定义，不按服务另建同名策略组。

切换 `PROXY` 影响所有引用它的服务；直接绑定 `South Korea` 等地区组的服务独立于 `PROXY` 的地区选择。YouTube 位于 Google 综合规则之前；Gemini 与 Antigravity 的可选 AI 子项也在 Google 之前，需要独立地区时再启用并改策略；OneDrive 等子项例外在 Microsoft 之前。请以客户端展开后的实际规则顺序为准。

远程资源使用 `inserted-resource=true`，并不免除顺序检查。特别注意专用域名必须在可能覆盖它的综合分类、IP/GeoIP 和 final 之前参与匹配。国内与海外合集并非互斥；模板按国内在前组织，特殊服务应通过更靠前的专用资源明确处理。不要一次性启用全部父子分类。

## 来源与维护

写法参考用户提供的本地 `quantumult_20261019170533.conf`（文件头署名 ddgksf2013，含用户个人调整），并核对 [Quantumult X 官方示例](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)。本项目重新编写地区表达式、模板注释与策略结构；原始个人配置保留在本地忽略清单中。第三方规则、脚本与完整配置的出处说明见 [仓库 README](../README.md#来源署名与许可)。

`tools/config_templates.py` 保存完整模板结构与地区表达式，`sources/selection.json` 保存个人资源选择；执行 `python3 tools/build.py --rebuild` 同步生成分流片段和完整配置，生成文件不宜单独手改。请把实际订阅和凭据填写到仓库外的个人副本中。

策略图标来自本仓库 [icon/](../icon/README.md)，包含 PNG 与 SVG 源文件。图标仅作显示，不参与节点筛选。

外部脚本版本、内容哈希、核对日期及用途见 [外部资源锁定记录](../sources/remote-resources.lock.json)。仓库不镜像未确认再分发许可的脚本；固定 URL 减少入口静默变化，但不能防止所有 404，也不代表客户端会核验这些哈希。注释中的 UI 任务集合内部可能继续引用可变地址，本库未递归锁定。

发布后，每周一北京时间 10:23 的只读工作流检查数据、图标与上述直接引用；也可手动运行。报告在 Actions 运行摘要查看，不自动修改文件、创建 PR 或 push，不保证发现变化就主动通知。定时任务是否执行及运行通知由 GitHub 设置决定。人工复核本地 AI 补充、更新许可与内容之后，才能调整锁定版本并重新生成模板。

原有 OneDrive-Web / Sync 规则及策略已沿用，分流正文统一在 `filter/`，重写模块统一按功能分类在 `rewrite/vip/`、`rewrite/purify/`、`rewrite/enhance/`。


## 本轮城市名与服务入口

地区筛选在国家/地区名、代码和旗帜之外，只补少量常用城市：Taipei、Tokyo、Osaka、Los Angeles / LosAngeles、San Jose / SanJose、Seattle、New York、London、Frankfurt、Berlin、Paris、Toronto、Vancouver、Sydney、Melbourne、Seoul、Istanbul、Jakarta，兼容所列城市的常用中文名称。不会根据城市名称验证实际出口。

个人分流清单新增独立“小红书”资源，指向 `filter/services/xiaohongshu.list`，默认 `direct`。小红书深度净化+去水印重写位于 `rewrite/purify/xiaohongshu.conf`，两者分别作用于分流与响应改写。

按本轮要求，UDP 443 限制及 DNS 三个服务器、四项域名绑定均沿用原配置。不迁移个人放行、校内直连等修正规则；已确认保留的 OneDrive-Web / Sync 不变。
