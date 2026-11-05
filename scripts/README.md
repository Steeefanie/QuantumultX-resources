# 脚本正文

当前保存 43 个完整脚本与资源（`app2smile/` 13 个、`fmz200/` 26 个、`tools/` 4 个）；来源版本、单文件真实出处（`file_origins`）及 SHA256 见 `sources/rewrites.json`、`sources/rewrite-catalog.json`、`sources/rewrites.lock.json` 和 `sources/remote-resources.lock.json`。原始快照逐字节保留；生成脚本仅在原文之前添加中文用途、真实来源与本地修改说明，原作者及功能归对应上游。

这些文件由 `tools/build.py --rebuild` 从锁定快照生成，不要单独编辑生成文件。资源更新需要审阅原始脚本、模块依赖、许可和功能变化，再更新来源记录并重新生成。脚本会参与处理匹配请求或响应，先在个人副本中按需启用，不批量打开全部模块。

本目录不是节点订阅，也不提供策略组；分流走哪个地区仍由 `filter/` 和主配置决定。所有脚本尚未完成真实设备验证，不保证适用于所有 App 版本。

主体许可见 [app2smile/LICENSE.md](app2smile/LICENSE.md)，已识别的运行库许可见 [第三方说明](THIRD-PARTY-NOTICES.md)。本轮收录的是重写配置声明的直接脚本；条件分支中的 Node.js 专用依赖和运行时业务 API 不等同于 Quantumult X 会额外下载执行的脚本。

`fmz200/` 脚本与其来源分别保留 GPL-3.0 许可及原作者署名，许可见 `fmz200/LICENSE`，不能以根目录 MIT 替代。该来源引用的 app2smile 脚本复用 `app2smile/` 中的完整正文，继续保留原 MIT 许可。未能收录的外链脚本不会静默留在可执行重写里，隔离行号详见对应重写文件头部注释。

全部 39 个重写脚本均补充：名称、具体用途、请求/响应处理阶段、使用前提、使用边界、本地说明日期、固定来源及许可。说明输入保存在 `sources/script-info.json`，跨上游或本地派生/修改脚本的真实出处登记在 `sources/rewrite-catalog.json` 的 `file_origins` 中，生成时由 `tools/script_headers.py` 加入；不要单独手改输出注释。重写配置头也补充对应用途与真实来源，完整清单见 `rewrite/catalog.md`。混淆源码或权限字段相关行为在说明中如实标明，不把用途描述冒充运行效果保证。
