"""生成无私人订阅或凭据的 Quantumult X 完整配置模板。"""
import json
import re
from pathlib import Path

PROJECT = json.loads((Path(__file__).resolve().parents[1]/'sources/project.json').read_text())
if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', PROJECT['repository']):
    raise ValueError('项目仓库名称无效')
REF = PROJECT.get('ref', 'main')
if not re.fullmatch(r'[A-Za-z0-9_.-]+', REF):
    raise ValueError('项目版本引用无效')
RAW_ROOT = f'https://raw.githubusercontent.com/{PROJECT["repository"]}/{REF}'

# 代码、英文全称、节点名匹配表达式、默认是否生成地区组定义。
# 使用完整地名、旗帜或独立的两字母代码，避免单个“新”“美”等字误匹配。
REGIONS = (
    ('HK', 'Hong Kong', r'香港|hong[ _-]?kong|🇭🇰|(?<![a-z])hk(?![a-z])', True),
    ('TW', 'Taiwan', r'台湾|台灣|台北|臺北|台中|新北|高雄|彰化|hinet|cht|taiwan|taipei|🇹🇼|(?<![a-z])tw(?![a-z])', True),
    ('JP', 'Japan', r'日本|东京|東京|大阪|japan|tokyo|osaka|🇯🇵|(?<![a-z])jp(?![a-z])', True),
    ('SG', 'Singapore', r'新加坡|狮城|獅城|singapore|🇸🇬|(?<![a-z])sg(?![a-z])', True),
    ('US', 'United States', r'美国|美國|洛杉矶|洛杉磯|圣何塞|聖荷西|西雅图|西雅圖|纽约|紐約|united[ _-]?states|american?|los[ _-]?angeles|san[ _-]?jose|seattle|new[ _-]?york|🇺🇸|(?<![a-z])us(?![a-z])', True),
    ('KR', 'South Korea', r'韩国|韓國|韓国|首尔|首爾|korean?|seoul|🇰🇷|(?<![a-z])kr(?![a-z])', False),
    ('GB', 'United Kingdom', r'英国|英國|united[ _-]?kingdom|great[ _-]?britain|伦敦|倫敦|london|🇬🇧|(?<![a-z])(?:gb|uk)(?![a-z])', False),
    ('DE', 'Germany', r'德国|德國|法兰克福|法蘭克福|柏林|germany|frankfurt|berlin|🇩🇪|(?<![a-z])de(?![a-z])', False),
    ('FR', 'France', r'法国|法國|巴黎|france|paris|🇫🇷|(?<![a-z])fr(?![a-z])', False),
    ('CA', 'Canada', r'加拿大|多伦多|多倫多|温哥华|溫哥華|canada|toronto|vancouver|🇨🇦|(?<![a-z])ca(?![a-z])', False),
    ('AU', 'Australia', r'澳大利亚|澳大利亞|澳洲|悉尼|墨尔本|墨爾本|australia|sydney|melbourne|🇦🇺|(?<![a-z])au(?![a-z])', False),
    ('TR', 'Turkey', r'土耳其|turkey|turkish|türkiye|turkiye|istanbul|伊斯坦布尔|伊斯坦堡|🇹🇷|(?<![a-z])tr(?![a-z])', False),
    ('ID', 'Indonesia', r'印尼|印度尼西亚|印度尼西亞|indonesian?|jakarta|雅加达|雅加達|🇮🇩|(?<![a-z])id(?![a-z])', False),
)
NOTICE_NAMES = r'流量|到期|剩余|重置|套餐|公告|traffic|expire|reset|quota|balance|(?<![a-z])beta(?![a-z])'


def region_regex(expression):
    return rf'(?i)^(?!.*(?:{NOTICE_NAMES})).*(?:{expression}).*$'


def render_full_config(profile, filter_text, annotation_date, rewrite_text='', companion_text=''):
    """将同一份个人资源清单嵌入完整模板，保留各条目的默认关闭状态。"""
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root/'sources/remote-resources.lock.json').read_text())
    if lock.get('schema') != 1:
        raise ValueError('外部资源锁定记录版本不支持')
    urls = {}
    for resource in lock['resources']:
        if not re.fullmatch(r'[0-9a-f]{40}', resource['commit']):
            raise ValueError('外部资源缺少固定提交')
        expected = f'https://raw.githubusercontent.com/{resource["repository"]}/{resource["commit"]}/{resource["path"]}'
        if resource['url'] != expected or any(c in expected for c in '\r\n, '):
            raise ValueError('外部资源地址与锁定记录不符')
        local_path = resource.get('local_path', '')
        if local_path:
            if not (root/resource.get('source_path', local_path)).is_file() or any(c in local_path for c in '\r\n, '):
                raise ValueError('本地收录的工具脚本缺失或路径不合法：'+local_path)
            urls[resource['id']] = f'{RAW_ROOT}/{local_path}'
        else:
            urls[resource['id']] = expected
    active = ', '.join(label for _, label, _, enabled in REGIONS if enabled)
    policies = [
        f'static = Global, {active}, proxy, direct, img-url={RAW_ROOT}/icon/Global.png',
        '# Global 对应原配置的“全球加速”总组（避免占用 Quantumult X 系统保留名 PROXY/proxy）。',
        '# 默认使用香港，可随时手动改选地区；首次导入后确认 Global 已勾选 Hong Kong。',
        '# Hong Kong 保留在首个候选；实际选中项以客户端界面为准，各地区内部自动按延迟择优。',
        '# 分流资源可直接选 reject / direct / Global，也可直接指定 Hong Kong 等地区组。',
        '# 检测间隔 check-interval=600、延迟容差 tolerance=20。',
        '# 检测受策略活动状态影响，不保证故障发生时立即切换，也不验证所有业务可用性。',
        f'# {sum(enabled for _, _, _, enabled in REGIONS)} 个地区默认全部定义，不保证空地区自动隐藏；没有候选的地区不要选择。',
        '# 不需要某地区时，注释该地区行，并从 Global 中移除同名候选。',
        '# 以下筛选默认跨所有已启用订阅。限定机场时，在地区行添加：',
        '# resource-tag-regex=^(Airport-A|Airport-B)$',
        '# Airport-A / Airport-B 必须与 [server_remote] 的 tag 一致。',
    ]
    for code, label, expression, enabled in REGIONS:
        icon_name = label.replace(' ', '')
        line = (f'url-latency-benchmark = {label}, server-tag-regex={region_regex(expression)}, '
                'check-interval=600, tolerance=20, '
                f'img-url={RAW_ROOT}/icon/{icon_name}.png')
        policies.extend([f'# {label} ({code})', line if enabled else '# ' + line])
    filter_body = filter_text.split('[filter_remote]\n', 1)[1].rstrip()
    curated_rewrites = [
        '# ======= 1. 会员破解与本地 VIP (rewrite/vip/) ======= #',
        f'{RAW_ROOT}/rewrite/vip/netease-svip.conf, tag=网易云净化+本地黑胶 SVIP, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/vip/netease-vip.conf, tag=网易云音乐 VIP, update-interval=86400, opt-parser=false, enabled=false',
        f'{RAW_ROOT}/rewrite/vip/spotify.conf, tag=Spotify VIP[音质≤高]@app2smile, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/vip/revenuecat.conf, tag=RevenueCat 通用内购破解(No Fusion/Notability/Locket等), update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/vip/xmind.conf, tag=Xmind 思维导图 Pro 解锁, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/vip/meitu.conf, tag=美图秀秀与 Wink 粉钻 VIP, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/vip/wps-camscanner.conf, tag=WPS 超级会员与扫描全能王 VIP, update-interval=86400, opt-parser=false, enabled=true',
        '# ======= 2. 主流软件深度净化 (rewrite/purify/) ======= #',
        f'{RAW_ROOT}/rewrite/purify/youtube.conf, tag=油管深度净化 @Maasea, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/xiaohongshu.conf, tag=小红书净化+无水印存原图, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/wechat-mp.conf, tag=微信公众号文章净化, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/wechat-applet.conf, tag=微信小程序去激励广告净化, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/bilibili.conf, tag=哔哩哔哩深度净化, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/zhihu.conf, tag=知乎深度净化, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/weibo.conf, tag=微博客户端深度净化 @ddgksf2013, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/amap.conf, tag=高德地图界面深度净化 @ddgksf2013, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/startup-ads.conf, tag=墨鱼通用去开屏 2.0, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/purify/ad-sdk.conf, tag=四大广告联盟 SDK 净化, update-interval=86400, opt-parser=false, enabled=true',
        '# ======= 3. 功能增强与效率工具 (rewrite/enhance/) ======= #',
        f'{RAW_ROOT}/rewrite/enhance/wechat-unlock-url.conf, tag=微信解锁被屏蔽的URL @zZPiglet, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/enhance/youtube-subtitle.conf, tag=油管字幕自动中译 @id77, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/enhance/url-redirect.conf, tag=神机重定向 @DivineEngine, update-interval=86400, opt-parser=false, enabled=true',
        f'{RAW_ROOT}/rewrite/enhance/safari-qsearch.conf, tag=Safari 超级搜索 Q-Search @ddgksf2013, update-interval=86400, opt-parser=false, enabled=false',
        f'{RAW_ROOT}/rewrite/enhance/web-adblock.conf, tag=影视网站与网页弹窗净化, update-interval=86400, opt-parser=false, enabled=true',
        '# 更多软件净化与 VIP 模块（酷我音乐、百度贴吧、夸克、百度网盘、京东、淘宝、美团、什么值得买、IT之家、豆瓣等）均按功能归类在 rewrite/vip/、rewrite/purify/、rewrite/enhance/ 目录。',
    ]
    rewrite_body = '\n'.join(curated_rewrites)
    companion_body = f'{RAW_ROOT}/filter/adblock/combined.list, tag=重写配套去广告合集, force-policy=reject, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=true'
    return f'''# Quantumult X 完整配置模板 · {profile}
# 本地整理日期：{annotation_date}（北京时间）；规则、重写、脚本与图标的独立许可见仓库 README。
# 写法参考用户提供的现有配置与 Quantumult X 官方示例，按本项目策略重新编写。
# 使用前：填入自己的 QX 格式订阅、检查地区候选节点，再启用所需分流资源。
# 模板不包含可用机场订阅或节点凭据；新规则与图标地址需本次发布后才可访问。
# 请先备份现有配置；完整模板导入会替换现有配置，保留配置时只合并所需段落。
# 模板更新日期：2026-11-04（北京时间）。
# 参数解释见 examples/config-guide.md；# 开头的行是注释，不参与运行。

[general]
# 节点延迟检测地址；测得的是请求响应时间，不等于下载带宽。
server_check_url = http://www.gstatic.com/generate_204
# 沿用原配置的节点检测阈值：3000 毫秒为 3 秒，不是所有连接的超时设置。
server_check_timeout = 3000
# 整份配置的显示图标；策略组各自的图标由 img-url 设置。
profile_img_url = {RAW_ROOT}/icon/Global.png
# 沿用原配置：关闭额外的 IP 地区查询入口。
geo_location_checker = disabled
# 沿用 Shawn 的资源解析器入口；本库原生 QX 规则继续使用 opt-parser=false。
# 其他受支持格式的节点订阅需要转换时，再为该资源设置 opt-parser=true。
resource_parser_url = {urls['resource_parser']}
# 固定版本及哈希见 sources/remote-resources.lock.json；上游变化只报告，不自动替换。
# 沿用原配置的兼容例外：停用这些域名的占位 IP 映射，不会把它们自动设为直连。
dns_exclusion_list = *.cmpassport.com, *.jegotrip.com.cn, *.icitymobile.mobi, id6.me, *.pingan.com.cn, *.cmbchina.com
# 沿用原配置：绕过 TUN 接管的局域网多播投屏（SSDP/UPnP）及特定直通路由。
excluded_routes = 239.255.255.250/32, 24.105.30.129/32, 185.60.112.157/32, 185.60.112.158/32, 182.162.132.1/32
# 沿用原配置：丢弃 UDP 443，其他 UDP 目标端口放行；可能影响 QUIC / HTTP/3。
udp_whitelist = 1-442, 444-65535
# 已由路由器处理代理的 Wi-Fi 可按需切换直连模式；先替换为真实 Wi-Fi 名称。
# running_mode_trigger = filter, filter, HOME_WIFI:all_direct, WORK_WIFI:all_direct

[dns]
# 域名查询服务器：把域名解析成 IP；不会凭此决定服务走哪个代理地区。
# 沿用原配置：不用系统 DNS，并停用 QX DNS 模块的 AAAA 查询。
no-ipv6
no-system
server = 223.5.5.5
server = 119.29.29.29
server = 114.114.114.114
server = /*.icloud.com/119.29.29.29
server = /*.icloud.com.cn/119.29.29.29
server = /*.tencent.com/119.29.29.29
server = /*.weixin.com/119.29.29.29
# 如需系统 DNS 或 IPv6 查询，分别注释对应的 no-system / no-ipv6 行。
# 普通 DNS 不加密；DoH 与随网络 DNS 的备选写法见 examples/config-guide.md。

[server_local]
# 如有手动节点，在本机添加；请勿把含密码的配置提交到仓库。

[server_remote]
# 在本机把示例地址换成机场提供的订阅链接，再移除行首 #。
# 设 opt-parser=true 时，资源解析器会自动转换格式并补充节点地区旗帜 Emoji：
# https://example.com/airport-a/sub, tag=Airport-A, update-interval=86400, opt-parser=true, enabled=true
# https://example.com/airport-b/sub, tag=Airport-B, update-interval=86400, opt-parser=true, enabled=true
# tag 是订阅名；update-interval 单位为秒；opt-parser 控制资源解析器；enabled 控制启用。

[policy]
{chr(10).join(policies)}

[filter_remote]
# tag 为资源显示名；force-policy 覆盖该资源中全部规则的策略。
# update-interval=86400 为每天更新；opt-parser=false 为不经过资源解析器。
# enabled=true 代表默认启用，暂不需要的资源可改为 false；这与地区组是否定义相互独立。
# inserted-resource=true 用于插入资源规则；核对展开顺序，确保专用域名在 GeoIP / final 前匹配。
# 重写配套去广告拦截，放在宽泛业务规则之前。
{companion_body}
# 通用广告与跟踪域名拦截；放行特例已前置在 [filter_local] 中。
{RAW_ROOT}/filter/collections/advertising.list, tag=广告与跟踪, force-policy=reject, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=true
# 个人服务：共用 Global；固定地区时改为 Hong Kong / Taiwan / Japan / Singapore / United States / South Korea 等已定义组。
{filter_body}

# 通用域名后置兜底集合，置于专用业务之后；集合并非互补，也不覆盖全部网站。
{RAW_ROOT}/filter/collections/domestic.list, tag=国内域名, force-policy=direct, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=true
{RAW_ROOT}/filter/collections/global.list, tag=海外域名, force-policy=Global, inserted-resource=true, update-interval=86400, opt-parser=false, enabled=true

[filter_local]
# 防广告域名一刀切拦截导致开屏卡死（放行连接交由重写层处理响应）：
host, ad.12306.cn, direct
host, gg.caixin.com, direct
host, sdkapp.uve.weibo.com, direct
# 确保本仓库托管的图标、分流与重写在远程规则首次拉取前即可经代理解析下载，避免国内 DNS 污染为 127.0.0.1 命中直连：
host-suffix, githubusercontent.com, Global
host-suffix, github.com, Global
# 拦截百度贴吧与阿里/B站 HTTPDNS 抢答，防止 App 绕过域名分流与去广告规则：
ip-cidr, 180.76.76.200/32, reject
ip-cidr, 203.107.1.1/24, reject
# 本地网络与 IP 补充。以客户端展开后的匹配顺序和实际请求记录为准。
# ip-cidr 为 IPv4 网段，ip6-cidr 为 IPv6 网段；direct 为直接连接。
ip-cidr, 10.0.0.0/8, direct
ip-cidr, 127.0.0.0/8, direct
ip-cidr, 169.254.0.0/16, direct
ip-cidr, 172.16.0.0/12, direct
ip-cidr, 192.168.0.0/16, direct
ip-cidr, 224.0.0.0/24, direct
ip-cidr, 182.254.116.0/24, direct
ip6-cidr, ::1/128, direct
ip6-cidr, fc00::/7, direct
ip6-cidr, fe80::/10, direct
# 依赖客户端当前 GeoIP 数据；不是对所有国内服务的覆盖承诺。
geoip, cn, direct
# 仍未命中其他规则的请求，最终交给 Global。
final, Global

[task_local]
# 沿用原配置的流媒体查询任务：在节点 / 策略交互菜单中手动触发，不后台定时巡检。
# 返回结果受平台接口变化影响；只是检测参考，不会自动切换地区或改变分流。
event-interaction {urls['streaming_check']}, tag=流媒体解锁查询, img-url=arrowtriangle.right.square.system, enabled=true
# 其他 UI 任务的手动添加入口；已添加单条任务时避免重复添加同名项。
# {urls['task_collection']}
# 集合内可能继续引用可变地址；不由本库递归锁定，不建议重复批量导入。

[rewrite_local]
# 本机定义的 HTTP 请求/响应改写；基础分流不需要，按需在本机添加。

[rewrite_remote]
# 个人常用重写默认启用（网易云音乐 VIP 默认关闭，避免与第一条网易云净化+本地黑胶冲突）。
# 与分流策略独立，不会替你选择地区；启用前请在本机配置 MITM 证书。
{rewrite_body}

[http_backend]
# 本地 HTTP 脚本接口，用于面板或工具；基础分流不需要。
# 保留原配置的 BoxJS 入口供按需配置；本模板默认关闭。
{urls['boxjs']}, host=boxjs.com, tag=BoxJS, path=^/, enabled=false

[mitm]
# 仅域名分流不需要 MITM；上述 HTTPS 重写需要自己的证书（passphrase 与 p12 请在导入手机后粘贴，勿提交到公开仓库）。
skip_validating_cert = true
force_sni_domain_name = false
# 排除强校验证书的苹果服务、天气、丰巢、华米及抖音系域名，防止 App Store 无法切换账号或应用断网：
hostname = -*.apple.com, -consumer.fcbox.com, -*huami.com, -weather-data.apple.com, -*amemv.com, -*snssdk.com, -www.google.com
'''
