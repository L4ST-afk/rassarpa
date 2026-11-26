# 罗蛇 · 变更记录

`[中文](CHANGELOG.md) · [English](CHANGELOG.en.md)`

## 未发版（2026-11-27）· 分支保护：加 quality-gate 汇总门

- **问题**：仓库此前无分支保护，任何人可直推 main；本地对账与 jsdom 回归再全，远端也没人拦。
- **改法**：`selfcheck.yml` 末尾加 `quality-gate` 汇总 job（`needs: [checks, engines]`、`if: always()`）：自检与引擎对账都必须 success，红／取消／跳过一律判红。
- **为什么不钉矩阵 job**：引擎矩阵成员名随引擎增减变化，一改必过检查就静默失效；汇总门名字稳定。
- **配套**：main 分支保护 required `quality-gate`、`strict: true`、`enforce_admins: true`；此后走 PR，直推 main 会被拒。
- **未动**：判据、`tools/selfcheck.py`、`tests/` 与卷册。

## 未发版（2026-11-23）

外部代码审查（GitHub Copilot CLI 只读模式）1 中 2 低：

- **纯英文文本节点不再被插间隙**：`RE_BOUNDARY` 的前置组原是 `[{ANS}]+`，对 `<p>hello</p>` 会回吐成 `hell` + `o`，单词内部多出一个 `cjk-spacing` 元素。改为「前置组只收一个汉字」。
- **README 说清了 `.cjk` 的实际作用**：它只关掉引擎自动间距，四分空来自 `.mx` 空盒或脚本插的 `cjk-spacing` 元素；原来两步写法让人以为引了样式就有默认四分空。
- **`measure_pw.mjs` 遇未知引擎不再假通过**：`--engine typo` 原本循环全跳过、`failed` 为空、退出码 0；现在前置校验并退出 2。

## 未发版（2026-11-23，第二批：CI 门禁）

CI 审查（GitHub Copilot CLI 只读模式）3 中 3 低，采纳如下：

- **修**：`tools/selfcheck.py --self-test` 的变异点原本改的是说明文字里的 `CJKSpacing`（第一个出现处），真正的调用仍叫 `new CJKSpacing(...)`，于是自检恒判「闸有牙」却不真验证——现在改到调用点 `new CJKSpacing(`，变异件如实判红（本地 `rc=0`，此前 `rc=3`）。
- **CI 加**：`python3 tools/selfcheck.py --self-test` 进 `checks` job，自检本身退化会红。
- **CI 加**：工作流级 `permissions: contents: read`；`concurrency` 取消同分支旧跑；`checks` 15→20 分钟、`engines` 35 分钟时限；两处 `setup-node` 开 `cache: npm`。
- **CI 改**：三个第三方 action pin 到 commit SHA（注释留 `# v4` / `# v5`）。
- **不采纳**：`check_engines.py` 的 darwin 限制。Linux CI 没有苹方／宋体，缺字体时引擎本就不加间隙，把这条差异当门禁只会造出假红；口径已在脚本注释与 `docs/判据表.md` 证据列写清。

## 0.1.1 之后（未发版）

把「Safari 与 Firefox 未实测」这件事做实。

- **新**：`tools/measure_pw.mjs` —— 同一份 probe 交 Playwright 起 Firefox 159 与 WebKit 27.2 各量一遍。三家读数：间隙都是 0.125 em，不声明都等于关闭；差别在跨元素边界，Chrome／Firefox 两缝各补 4px 共 8px，WebKit 只补一侧共 4px，且每缝包空 span 会把那 4px 打掉。
- **新**：`tools/measure_safari.mjs` —— 走系统 safaridriver 量 Safari 本体。2026-11-20 在 Safari 18.6 上跑通：间隙 0.125 em、不声明等于关闭、两缝只补 4px、包空 span 后掉到 0，与 WebKit 27.2 构建逐项一致。
- **新**：`tools/check_engines.py` —— 跨引擎三条不变式（不声明等于关闭、已有空格不补、`.mx` 四分空）进 CI；`check_readings.py` 只管 Chrome 那份，两者分工写进脚本注释。
- **新**：CI 加 `engines` job，Ubuntu 上真起两家引擎，读数作为 artifact 留档。
- **改**：`docs/判据表.md` 加「证据」列，三种等级：实测／引擎记录／实现约束。C1、C2、C4 由「实测一家」升为三家；C5 记下两家的差别；C6 由纯引擎记录变成「WebKit 构建实测＋Safari 本体待跑」。
- **新**：题图换 v2.1（`cover-v2-1536-v2.jpg`），订正西文名用字；逐像素比对，两版差异只在下方拉丁名的单个字母上。
- **修**：字体探针不能用 `document.fonts.check()`（没装也返回 true），也不能靠量字宽（macOS 回退本身就是苹方，分不清）。改用 `FontFace` 的 `local()`：装了就 load 成功。

## 0.1.1（2026-11-20）

发版当日修的三处，都属"会动用户正文"或"到别人机器上会坏"的那一类。

- **修**：`cjk_spacing.js` 会吃掉边界上已有的 ASCII 空格（`中 a 中` → `中a中`）。与 `cjk_spacing.py` 及判据冲突，两个实现各有半条用例，遂补齐 JS 侧。现在边界上已有空格时不插盒、不删字符。
- **修**：旧引擎降级路径（无 lookbehind）把前一个汉字一起包进间隙盒，并按匹配长度额外加一，吞掉后一个字符；标点挤压同样中招。改为按前缀长度切分、按真实匹配长度推进。
- **修**：`glyph_optical_correct.py` 缺 `fontTools` 时报一屏 traceback；改一行指路。本仓只有它需要外装依赖。
- **测试**：新增 `tests/test_spacing_js.mjs`（jsdom，14 项：空格、幂等、code 嵌套、挤压、跨元素不崩、降级路径四条），CI 同跑。
- **CI**：文档逐份检查改 `git ls-files -z`，带空格的文件名不再切坏。

## 0.1.0（2026-11-20）

首个公开版本。目录名、包名、分支一律 `rassarpa`。

- **默认档翻转**：间隙默认由 `.mx` 空白盒给足 1/4 em（四分空），`text-autospace` 降为可选档 `.cjk--autospace`。理由是本仓实测：引擎给的是 1/8 em、规范不给宽度参数、Safari 只在一侧加。
- **弃用** `@supports not (text-autospace: normal)` 回落块：Chrome 140 起该属性已被识别，回落块恒不触发，属于死代码。
- **新增判据**：网页硬规则 T01/T07/T08/T11/T11b/T13 与字体授权 F03/F04/F06 逐条写入 `SKILL.md` §九，来源编号保留以便回上游核对。
- **新增三件工具**：`cjk_spacing.js`（逐文本节点包裹，含 `unicode-bidi: isolate`）、`cjk_spacing.py`（服务端同规则）、`check_spacing_consistency.py`（数字-量词混用）。
- **新增逐字光学修正**：`glyph_optical_correct.py`，按墨迹中心对齐而非字身框居中，解决网格里 `1` 发飘、`8` 偏左。
- **自检**：`tools/selfcheck.py` 五项（API 名一致、引用在盘、§九编号有落点、开箱样式红线、混用检查器有牙），CI 同跑。
- **已知缺口**：Safari 与 Firefox 未实测，其单侧加间隙与跨元素边界丢缝来自 WebKit 记录，标「未复现」。
- **修**：`cjk_spacing.js` 的跳过判定改为走完整祖先链（`closest`），此前只查直接父元素，`<code><span>中a</span></code>` 这类嵌套会把代码里的字也改掉。
- **修**：`cjk_spacing.py` 同样改成按标签嵌套深度跳过 `pre/code/script/style`，此前 `SKIP_TAGS` 定义了却没用上。
- **修**：`cjk_spacing.py` 会把串里已有的 ASCII 空格吃掉（`中 a 中` → `中a中`）。现按规范原样放回，⛔ 不改文本内容。
- **删**：`CJKSpacing` 的 `quoteSet` 参数——存了不用，与文档宣称不符；引号切换归 CSS `q { quotes }`，`QUOTE_SET` 降为数据表。
- **修**：`.cjk--poetry` 补齐宋体正文与楷体标题，与 §G 判据对齐。
- **文案**：暗色一节写明只切 `color-scheme`、色板不预置；README 增「已知限制」三条。
- **新增** `tests/test_spacing.py` 八条白盒回归（离线），CI 同跑；`THIRD_PARTY_NOTICES.md` 收 heti、pangu.js 的 MIT 全文。
- **题图**：`docs/cover.jpg`（1280 × 853，289 KB）从题图库 `cover-v2-1536.jpg` 按 `sips -Z 1280 -s formatOptions 72` 导出，首页宽 720 压在标题下；位图原件不进仓库。出处、导出与字形说明见 `docs/封面.md`。
- **文案**：README 增「先说这块是空的」一节，写清为什么值得开这个仓：Chrome《Modern Web Guidance》209 篇指南里 `autospace`／`CJK` 命中为 0（离线包 1.0.0 + `5e5cd33`，2026-11-20 检索），最近的 `visual-design/typography.md` 只有西文口径。
