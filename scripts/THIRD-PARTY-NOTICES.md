# 第三方代码与许可

核对日期：2026-11-04。本库保存 app2smile 提供的脚本原文；其中部分脚本捆绑了开源编码或协议运行库。保留以下许可副本及识别依据，不将上游捆绑文件的全部代码归为本项目原创。

| 来源 | 识别依据 | 保留许可 |
| --- | --- | --- |
| fmz200/wool_scripts 及补充来源 | 来源快照、单文件真实出处（`sources/rewrite-catalog.json` 的 `file_origins`）、原生重写及脚本完整保存，保留各文件原作者署名；本地派生与修改已逐文件注明 | [GPL-3.0](fmz200/LICENSE)，不以根目录 MIT 替代 |
| app2smile/rules | 模块和脚本来自固定仓库版本 | [MIT](app2smile/LICENSE.md)，Copyright (c) 2023 app2smile |
| Maasea/sgmodule | `scripts/fmz200/youtube.response.js` 与 `rewrite/purify/youtube.conf` | [Apache-2.0](licenses/maasea-sgmodule-Apache-2.0.txt)，Copyright (c) Maasea |
| blackmatrix7/ios_rule_script | `rewrite/enhance/url-redirect.conf`（神机重定向） | [GPL-2.0](licenses/blackmatrix7-GPL-2.0.txt) |
| protobuf.js | Spotify 协议脚本中的捆绑运行库；未单独标注具体运行库版本 | [BSD-3-Clause](licenses/protobufjs-BSD-3-Clause.txt)，Daniel Wirtz |
| text-encoding | YouTube、哔哩哔哩、贴吧协议脚本中的编码兼容代码；具体版本未标注 | [Unlicense / Apache-2.0 双许可原文](licenses/text-encoding-LICENSE.txt) |
| protobuf-ts | YouTube 与哔哩哔哩脚本注释为 2.9.0，贴吧为 2.10.0 | [Apache-2.0](licenses/protobuf-ts-Apache-2.0.txt) |

来源链接、许可原文哈希与核对日期见 `sources/rewrites.json` 的 `third_party_licenses`。没有单独标注版本的组件不作精确版本归属承诺；这些记录也不代表已穷尽上游代码的所有来源。
