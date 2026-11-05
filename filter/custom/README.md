# 原有自定义分流

这里保存用户要求沿用的 OneDrive 规则，区别于从 V2Fly 转换的通用服务分类。原文在 `sources/local/`，哈希见 `sources/lock.json`；生成文件保留原始正文。

| 文件 | 沿用的模板策略 |
| --- | --- |
| [microsoft-onedrive-web.list](microsoft-onedrive-web.list) | `Hong Kong` |
| [microsoft-onedrive-sync.list](microsoft-onedrive-sync.list) | `direct` |

个人清单按 Web → Sync → Microsoft 综合规则排序，在主配置中默认启用；不需要拆分时可只使用 `filter/services/microsoft-onedrive.list`，避免重复启用。

名称只说明原配置的分组意图，不能识别网页进程或同步客户端。两份规则共享 `onedrive.live.com` 等目标，优先的 Web 条目仍会让对应客户端连接走 Web 策略；同步规则中的 SharePoint 根域名也可能影响其他 Microsoft 服务。这里保留旧行为，不宣称修复或消除这些交叉。
