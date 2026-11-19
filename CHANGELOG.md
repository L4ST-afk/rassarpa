# 罗蛇 · 变更记录

`[中文](CHANGELOG.md) · [English](CHANGELOG.en.md)`

## 0.1.0（2026-11-20）

首个公开版本。目录名、包名、分支一律 `rassarpa`。

- **默认档翻转**：间隙默认由 `.mx` 空白盒给足 1/4 em（四分空），`text-autospace` 降为可选档 `.cjk--autospace`。理由是本仓实测：引擎给的是 1/8 em、规范不给宽度参数、Safari 只在一侧加。
- **弃用** `@supports not (text-autospace: normal)` 回落块：Chrome 140 起该属性已被识别，回落块恒不触发，属于死代码。
- **新增判据**：网页硬规则 T01/T07/T08/T11/T11b/T13 与字体授权 F03/F04/F06 逐条写入 `SKILL.md` §九，来源编号保留以便回上游核对。
- **新增三件工具**：`cjk_spacing.js`（逐文本节点包裹，含 `unicode-bidi: isolate`）、`cjk_spacing.py`（服务端同规则）、`check_spacing_consistency.py`（数字-量词混用）。
- **新增逐字光学修正**：`glyph_optical_correct.py`，按墨迹中心对齐而非字身框居中，解决网格里 `1` 发飘、`8` 偏左。
- **自检**：`tools/selfcheck.py` 五项（API 名一致、引用在盘、§九编号有落点、开箱样式红线、混用检查器有牙），CI 同跑。
- **已知缺口**：Safari 与 Firefox 未在本机实测，其单侧加间隙与跨元素边界丢缝来自 WebKit 记录，标「未复现」。
- **修**：`cjk_spacing.js` 的跳过判定改为走完整祖先链（`closest`），此前只查直接父元素，`<code><span>中a</span></code>` 这类嵌套会把代码里的字也改掉。
- **修**：`cjk_spacing.py` 同样改成按标签嵌套深度跳过 `pre/code/script/style`，此前 `SKIP_TAGS` 定义了却没用上。
- **修**：`cjk_spacing.py` 会把串里已有的 ASCII 空格吃掉（`中 a 中` → `中a中`）。现按规范原样放回，⛔ 不改文本内容。
- **删**：`CJKSpacing` 的 `quoteSet` 参数——存了不用，与文档宣称不符；引号切换归 CSS `q { quotes }`，`QUOTE_SET` 降为数据表。
- **修**：`.cjk--poetry` 补齐宋体正文与楷体标题，与 §G 判据对齐。
- **文案**：暗色一节写明只切 `color-scheme`、色板不预置；README 增「已知限制」三条。
- **新增** `tests/test_spacing.py` 八条白盒回归（离线），CI 同跑；`THIRD_PARTY_NOTICES.md` 收 heti、pangu.js 的 MIT 全文。
- **题图**：`docs/cover.jpg`（1280 × 853，289 KB）从题图库 `cover-v2-1536.jpg` 按 `sips -Z 1280 -s formatOptions 72` 导出，首页宽 720 压在标题下；位图原件不进仓库。出处、导出与两处待核见 `docs/封面.md`。
- **文案**：README 增「先说这块是空的」一节，写清为什么值得开这个仓：Chrome《Modern Web Guidance》209 篇指南里 `autospace`／`CJK` 命中为 0（离线包 1.0.0 + `5e5cd33`，2026-11-20 检索），最近的 `visual-design/typography.md` 只有西文口径。
