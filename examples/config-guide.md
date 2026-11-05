# Quantumult X 配置参数说明

本地更新日期：2026-11-04（北京时间）。结合用户提供的原始配置及本仓库 [完整模板](quantumult_steeefanie.conf)解释，不包含私人订阅、证书或密码。官方语法依据见 [sample.conf](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)；实际支持情况以所用客户端版本为准。

## 1. 先看懂文件形式

| 写法 | 含义 |
| --- | --- |
| `[general]` 等方括号标题 | 配置段，决定后续参数属于哪个功能 |
| `key = value` | 把某个参数设置成指定值 |
| 行首 `#`、`;`、`//` | 注释整行，不执行；删除注释符后才参与配置 |
| `true` / `false` | 开启 / 关闭，但具体作用取决于参数 |
| 逗号 | 分隔同一行中的候选或参数，不宜随意删除 |

原始配置开头的 `@Author`、`@UpdateTime` 等位于注释中，用于署名和记录历史，不会据此判断配置是否过期或自动更新。

不要重复添加同名段落。保留已有配置时，把所需行放进对应的已有段落。

## 2. 各段负责什么

| 配置段 | 负责的内容 |
| --- | --- |
| `[general]` | 检测地址、图标及其他全局行为 |
| `[dns]` | 域名到 IP 的查询方式 |
| `[server_local]` | 手动填写的具体节点，通常带有凭据 |
| `[server_remote]` | 从机场订阅加载节点 |
| `[policy]` | 选择节点、地区或其他策略的方式 |
| `[filter_remote]` | 引用分流规则文件 |
| `[filter_local]` | 直接写在主配置里的规则，包括 IP 补充和兜底 |
| `[task_local]` | 定时或事件触发的脚本任务 |
| `[rewrite_local]` / `[rewrite_remote]` | 本地 / 远程的请求和响应改写规则 |
| `[http_backend]` | 运行本地 HTTP 脚本接口，供面板或工具访问 |
| `[mitm]` | HTTPS 解密所需的证书与主机名范围 |

基础分流主要用 DNS、节点、策略和 filter。原配置的任务、重写与证书还承担额外功能，因此比本模板长很多。

## 3. `[general]`：原配置里的全局设置

| 参数 | 作用 | 本模板处理 |
| --- | --- | --- |
| `server_check_url` | 通过节点请求检测地址，测量响应延迟；结果不等于下载带宽或所有服务的解锁能力 | 保留 |
| `server_check_timeout` | 节点检测的超时阈值，单位毫秒；原配置 3000 为 3 秒，不是所有连接的超时 | 沿用 3000，不把官方示例的 5000 当成网络优化结论 |
| `profile_img_url` | 整份配置的显示图标 | 引用本仓库图标 |
| `geo_location_checker` | 配置 IP／地区展示所用的查询入口与处理脚本；原配置设置为 `disabled` | 沿用 `disabled` |
| `resource_parser_url` | 指定资源解析脚本，供资源转换、筛选等使用 | 沿用 Shawn 的解析器入口；需要转换的资源单独启用 `opt-parser=true`，本库规则仍为 `false` |
| `excluded_routes` | 指定不交给 QX 处理的目标 IP 网段，跳过范围比一条 `direct` 分流更广 | 不复制原配置的例外列表 |
| `udp_whitelist` | 允许通过隧道处理的 UDP 目标端口；不在列表中的 UDP 包会被丢弃 | 按用户要求沿用原写法，默认限制 UDP 443 |
| `running_mode_trigger` | 根据移动网络或指定 Wi-Fi 等条件切换运行模式 | 保留注释模板，先填真实 Wi-Fi 名称再按需启用 |
| `dns_exclusion_list` | 对指定域名停用 QX 的占位 IP 映射机制，改变 DNS／连接处理方式 | 沿用原配置的六项兼容例外，不改变它们的分流策略 |

**两个具体区别：**

- 原配置 `udp_whitelist=1-442,444-65535` 正好排除了 **UDP 443**。这会影响使用该端口的 QUIC／HTTP/3 等通信；部分应用可能回退 TCP，不能保证全部会回退。它不等于关闭 TCP 443，也不等于禁用 HTTPS。
- `dns_exclusion_list` 不会把域名自动设成直连，也不是 MITM 排除列表。服务走哪个出口仍看分流与策略。`excluded_routes` 中部分 IP 的具体设置目的无法从配置本身确认，不应根据地址猜测用途。

## 4. `[dns]`：域名查询

| 写法 | 含义 |
| --- | --- |
| `server=223.5.5.5` | 增加一个 DNS 查询服务器 |
| `server=/*.example.com/119.29.29.29` | 为指定域名范围指定 DNS；原配置对部分服务做了类似设置 |
| `no-system` | 停用系统取得的 DNS，需要有其他可用的自定义 DNS |
| `no-ipv6` | 让 QX DNS 模块的 AAAA 查询失败，影响客户端取得 IPv6 地址；不等于设备全局 IPv6 总开关 |
| `doh-server` | 通过 HTTPS 进行 DNS 查询 |
| `prefer-doh3` | 在支持的环境中优先尝试 HTTP/3 形式的 DoH |

本模板沿用原配置的 `no-system` 和 `no-ipv6`，并完整保留原配置中的三个普通 DNS 地址及 iCloud、腾讯、微信四项域名绑定。普通 DNS 不加密，且不一定适合所有网络。如需加密查询（DoH），可将 `[dns]` 段替换为：

```ini
[dns]
no-system
no-ipv6
doh-server = https://dns.alidns.com/dns-query
```

（境外网络可改为 `doh-server = https://cloudflare-dns.com/dns-query`；若在酒店 Wi-Fi 登录页或内网环境需要跟随系统 DNS，可仅保留 `no-ipv6` 并注释 `no-system`。）配置 DoH 后，未绑定特定域名的普通 DNS 会被忽略，不能把普通 DNS 行视为必然可用的故障备用。当前主模板的 DNS 有效设置与原配置一致。

解析器只在相关资源需要解析时使用。登记入口后，保持原生 QX 资源的 `opt-parser=false`；其他受支持格式的节点订阅可设为 `true`。节点重命名、筛选、旗帜与排序可按 [作者说明](https://github.com/KOP-XIAO/QuantumultX/blob/master/Scripts/resource-parser.js)设置，不额外预设会删减节点的参数。

**DNS 决定如何查询地址；分流规则和策略决定连接去向。** 单独换 DNS，不会把 OpenAI 等服务自动指定到某个地区。

## 5. 订阅与资源行里的参数

例如个人模板中的一行：

```ini
https://raw.githubusercontent.com/Steeefanie/QuantumultX-resources/main/filter/services/openai.list, tag=OpenAI, force-policy=PROXY, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=false
```

| 部分 | 含义 |
| --- | --- |
| 开头的地址 | 下载资源正文的位置；在 `[server_remote]` 是节点资源，在 `[filter_remote]` 是分流规则 |
| `tag=OpenAI` | 资源显示名称，不会仅凭名称自动识别某个服务的流量 |
| `force-policy=PROXY` | 整个分流资源统一使用 `PROXY`，覆盖正文中各条规则原有策略 |
| `update-interval=86400` | 更新间隔 86400 秒，即一天；原配置的 172800 为两天 |
| `opt-parser=false` | 不通过所配置的资源解析器处理；原生 QX 格式通常无需额外解析 |
| `enabled=false` | 这个资源暂不启用；需要使用时改为 `true` |

模板为远程分流资源添加 `inserted-resource=true`，按官方示例使用资源插入方式，目的是让专用域名规则在本地 GeoIP / final 补充前参与匹配。官方示例没有穷尽所有排序场景，仍须核对客户端展开后的列表与实际命中；它不能当作启用开关，也不保证本地放行例外一定优先于插入的远程拦截规则。

所有地区组默认定义，与远程分流资源默认关闭是两回事。地区组有候选之后，还需启用相应分流资源，服务才会按该资源匹配。

## 6. `[policy]`：选谁、怎么选

```ini
static = Global, Hong Kong, Taiwan, Japan, Singapore, United States, proxy, direct
```

这行创建一个名为 `Global` 的手动选择组，对应原图里的“全球加速”（避免占用系统保留字 `PROXY`/`proxy`），逗号后面是默认启用的 5 个主力地区候选与内置兜底项，模板实际行还附有 `img-url`。默认使用香港、可以手动更改；首次导入后确认勾选 `Hong Kong`，不要仅靠候选排列位置判断当前选择。

`direct` 和 `reject` 为内置动作。分流可使用这两个动作、自定义总组 `Global`，也可直接指向某个英文地区组；例如 `force-policy=Japan` 表示固定使用日本组，不跟随 `Global` 当前选择。地区组分别定义是为了设置各自的筛选和测速，再以名称加入 `Global`，不依靠配置文件的缩进嵌套。

| 参数／类型 | 作用 |
| --- | --- |
| `static` | 使用你手动选定的候选，不自动按延迟换节点 |
| `server-tag-regex` | 按节点名称筛选候选，例如韩国的多种语言写法 |
| `resource-tag-regex` | 按订阅 `tag` 限定机场来源 |
| `img-url` | 这个策略组的显示图标，不影响流量出口 |
| `url-latency-benchmark` | 原配置使用的按请求响应延迟选择候选的类型；测速快不保证特定服务可用 |
| `check-interval=600` | 自动检测相关的间隔，单位秒，即 10 分钟；实际检测受策略活动状态等条件影响 |
| `tolerance` | 延迟选择的容差；它影响结果选择，不是超时时间 |

本模板的 `Global` 是手动选择地区的 `static` 组；地区内部恢复原配置的 `url-latency-benchmark`，按检测延迟自动择优。例如选择 `Hong Kong` 后，仅在匹配到的香港节点之间比较，不会因日本节点更快而自动换到日本。

检测参数设置 `check-interval=600`（10 分钟）、`tolerance=20`（20 毫秒容差）。实际检测时机受策略活动状态等条件影响，因此不是即时、无中断的故障接管。检测地址可访问也不代表所有 AI、登录或流媒体业务可用。

`tolerance=20` 表示新候选节点需比当前节点快超过 20 毫秒才会触发切换，减少同地区延迟接近的节点因微小波动频繁跳动 IP；仍不等于长期会话出口绝对固定，需要在实际业务中观察。

默认启用 **港、台、日、新、美 5 个主力地区**，其余 8 个地区保留注释备用。如需启用备用地区，取消其定义行注释并加入 `Global` 候选即可；不需要某地区时，注释它的定义行，并移除 `Global` 中对应候选。

原配置的地区表达式用了包含、排除和忽略大小写等正则写法；本模板重新编写了匹配规则。详细多机场示例见 [模板说明](README.md#多机场筛选)。

## 7. `[filter_local]`：一条规则怎么读

| 示例 | 意思 |
| --- | --- |
| `host, example.com, direct` | 精确匹配 `example.com`，直接连接 |
| `host-suffix, example.com, PROXY` | 匹配根域名及其子域名，交给 `PROXY` |
| `ip-cidr, 192.168.0.0/16, direct` | 匹配该 IPv4 网段并直连；`/16` 表示网络前缀长度 |
| `ip6-cidr, fc00::/7, direct` | 匹配该 IPv6 网段并直连 |
| `geoip, cn, direct` | 依据客户端当前 GeoIP 数据，将被识别为中国的目标 IP 直连 |
| `final, PROXY` | 没有被其他有效规则匹配的请求交给 `PROXY` |

GeoIP 数据可能变化或存在误差，域名集合也会重叠。最终顺序还涉及远程资源、本地规则及客户端相关设置，不能仅按配置文件上下位置推断全部优先级，应查看展开后的列表和实际请求记录。

## 8. 任务、重写与 HTTP 后端

原配置有 `event-interaction` 任务，表示用户触发交互时运行脚本；定时任务则使用 cron 形式的时间表达式。原配置中的流媒体查询任务只是查询工具，不会凭此让所有节点自动解锁。

`rewrite` 可修改请求地址、请求头或响应内容，也可以调用脚本处理响应。域名分流负责选连接出口，重写负责处理请求／响应，作用不同；HTTPS 内容改写通常还需要相应 MITM 配置，具体看脚本要求。

原配置的 `[http_backend]` 为 BoxJS 类工具预留入口，对应资源处于关闭状态。HTTP 后端可以通过本地 HTTP 接口提供脚本处理能力，官方 [sample-backend.js](https://github.com/crossutility/Quantumult-X/blob/master/sample-backend.js)展示了这种用法。

模板复用了流媒体查询任务，BoxJS 入口保持 `enabled=false`。任务是由用户手动触发的查询，不会后台循环或自动改选策略；重写段提供精选常用模块，关联的重写脚本与工具脚本均已完整保存在本仓库 `scripts/` 中（无外部仓库依赖）；具体能力与限制见 [重写库说明](../rewrite/README.md)。

模板中的工具脚本版本和内容哈希见 [锁定记录](../sources/remote-resources.lock.json)。

### 原配置里的“流媒体解锁查询”

用户提供的任务段包含一个合集入口和一条具体脚本任务：

| 内容 | 作用 |
| --- | --- |
| 行首有 `;` 的 `UI-Action.json` 地址 | 注释中的手动添加入口；文件本身是 UI 脚本合集，单独放在注释中不会自动加载 |
| `event-interaction` | 在客户端的交互菜单里由用户触发，不是定时自动巡检 |
| `streaming-ui-check.js` | 通过交互时传入的节点或策略发请求，显示其流媒体／服务检测结果 |
| `tag=流媒体解锁查询` | 菜单中显示的名称 |
| `img-url=arrowtriangle.right.square.system` | 客户端系统图标，不是额外的远程图标地址 |
| `enabled=true` | 启用此交互任务；不代表后台一直运行 |

读取到的 [脚本原文](https://github.com/KOP-XIAO/QuantumultX/blob/master/Scripts/streaming-ui-check.js)尝试检查 Netflix、YouTube Premium、Disney+、DAZN、Paramount+、Discovery+ 和 ChatGPT，并展示支持情况、识别到的地区或检测错误。比如可用它比较两个候选节点对 Netflix 的检测结果；它不会自动遍历全部机场节点并改选出口。

这里“解锁”指检测出口 IP 是否被服务接受、是否有地区或代理限制，不会替账号增加会员权益。脚本不是播放验证；平台页面和接口变化、网络错误等都可能影响判断，本次仅阅读代码，没有在客户端实测其当前准确率。

[UI-Action.json](https://github.com/KOP-XIAO/QuantumultX/blob/master/Scripts/UI-Action.json)除综合查询外，还列出单项查询、切换、GeoIP 与流量查询等不同任务。综合查询脚本和合集中的切换脚本作用不同。模板已经引用单条查询任务，合集地址只保留作注释入口，避免重复添加同名项。模板仅引用作者地址，没有复制第三方脚本正文。

## 9. `[mitm]`：证书和解密范围

| 参数 | 作用及注意事项 |
| --- | --- |
| `passphrase` | 解开 PKCS#12 数据所用的密码 |
| `p12` | Base64 编码的证书数据，通常含私钥；不应随公开模板发布 |
| `hostname` | 需要由 MITM 处理的主机名范围；不是地区分流列表 |
| `skip_validating_cert` | 是否跳过 MITM 连接原站时的证书验证；原配置设为 `true`，会降低相应验证保护，不建议无目的照搬 |
| `force_sni_domain_name` | 原配置包含的历史字段；本次当前官方示例未列出，未确认其当前版本的完整行为，本模板不采用 |

正常的 HTTPS 代理转发不必解密网页内容；为域名选择代理地区也不需要安装此证书。需要修改 HTTPS 内容时再按实际功能要求单独配置。本模板的 MITM 段为空，不复制原始证书与密码。

## 10. 开始使用时主要改什么

1. 在本机个人副本中填写自己的 QX 原生节点订阅。
2. 检查地区组候选是否符合实际节点名称，不需要的地区自行注释并清理引用。
3. 启用需要的分流资源，多数服务使用 `PROXY`，固定地区的单项再改为英文地区全称。
4. 在客户端选择 `PROXY` 的地区（通常香港），由地区组根据检测结果在同地区节点内择优。

其余参数先理解用途，再按实际需求调整。原有 OneDrive-Web / Sync 规则及策略已沿用，分流正文统一在 `filter/`，重写模块统一按功能分类在 `rewrite/vip/`、`rewrite/purify/`、`rewrite/enhance/`。
