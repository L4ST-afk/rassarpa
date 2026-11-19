# 罗蛇 · Rassarpa

[![selfcheck](https://github.com/L4ST-afk/rassarpa/actions/workflows/selfcheck.yml/badge.svg)](.github/workflows/selfcheck.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

中文一格，西文一词，本仓只理中间那道缝。

`Rassarpa` 是拉丁名，`罗蛇` 是中文名；目录、包名、分支一律用 `rassarpa`。

**English**: CJK–Latin mixed typesetting rules for Chinese text that carries English words and Arabic digits — the quarter-em gap, punctuation squeezing, quote style, line breaking, vertical/multi-column variants, and the web-side hard rules (`lang`, no negative letter-spacing, no faux italic, minimum size, explicit font stack). Ships as plain CSS, two scripts, and one SKILL.md.

## 它管什么

汉字与拉丁字母、阿拉伯数字交界处的那道间隙，以及围着它的一整套判断：

- **间隙**加不加、加多宽（四分空＝1/4 em），什么时候必须不加
- **标点**：避头尾、相邻标点挤压、简体统一直角引号
- **字距与行距**：中文正文不用负字距；行距 1.6–1.9；行长 28–40 字
- **断行与对齐**：按字断行，正文左对齐，行长取整字
- **网页五条红线**：`lang` 必写、字距不为负、不用假斜体、字号有下限、字体栈显式
- **版式变体**：古文／诗词／行间注／多栏／竖排（根容器加一个 class 即切换）
- **暗色**：`prefers-color-scheme` 自动切换 `color-scheme`；**色板不预置**，由使用方给前景／背景令牌（对比度 ≥4.5:1 按实际渲染色值验）
- **字体授权四档**：能自托管／只能出图／只能调系统／要商业授权

不管：纯西文排版、纯中文（没有文种边界）、海报级展示字的版面构图——但「字距不为负／不用假斜体／字号有下限」这三条字符级红线仍然管。

## 读它之前先看四个读数

本机实测（HeadlessChrome 158 · macOS · PingFang SC · 32px 与 64px 两档），三条与常见教程相反：

| 项 | 量到的值 |
|---|---|
| `text-autospace: normal`，单边界间隙 | +4px / +8px = **0.125 em**（1/8 em，比例恒定） |
| 不写声明 vs 显式 `no-autospace` | 差 0 —— **不声明等于关闭** |
| 串里已有 ASCII 空格时加 `normal` | 差 0 —— **测法本身会骗人** |
| `.mx` 空白盒 | +8px = **0.25 em**（四分空） |
| 挤压 · PingFang SC | −16px |
| 挤压 · Songti SC / Heiti SC | 0（`CSS.supports()` 却返回 true） |

所以本仓的默认不是 CSS 那档：**要四分空就给 `.mx` 盒，`text-autospace` 只当可选档**。

量法与复跑命令见 [docs/测量方法.md](docs/测量方法.md)。

## 三步接上

```html
<html lang="zh-CN">
<link rel="stylesheet" href="tools/cjk-typo.css">
<article class="cjk">…</article>
<script src="tools/cjk_spacing.js"></script>
<script>new CJKSpacing('.cjk').run()</script>
```

1. `lang` 写在根元素上，CSS 替代不了——它是标点、字体回退、断行的前提。
2. 引样式、正文容器加 `class="cjk"`；间隙默认由 `.mx` 盒给足 1/4 em，两侧对称，复制不带走字符。
3. 要批量落间隙、并把相邻标点挤半字，再引脚本跑一次。

**想交给浏览器引擎**（不插 DOM，约 1/8 em）：根容器再加 `class="cjk--autospace"`。代价三条：宽度只有一半、Safari 只在拉丁前面加、不挤压标点。

## 当作 agent skill 用

把本仓整个目录放进宿主 skills 根，`SKILL.md` 即判据正本（359 行，含反例、何时用／不用、体量预算、上游声明）。规则与脚本都按需读，不通读。

判据只由一处负责：`SKILL.md`。`docs/` 与 `references/` 是细则卷，出现两处说法不一致时以 `SKILL.md` 为准。

## 跑自检

```bash
python3 tools/selfcheck.py
# 期望：五项全 OK —— A1 脚本 API 名一致｜A2 引用文件都在盘上｜A3 §九 编号有落点｜A4 开箱样式红线｜C1 混用检查器有牙
python3 tests/test_spacing.py
# 期望末行 ALL OK —— 边界落间隙、代码块不动、标点挤压、已有空格不被吃掉
```

另有两个单点检查器：

```bash
python3 tools/check_spacing_consistency.py <文件或目录>   # 数字-量词混用（3 个 / 3个）
python3 tools/glyph_optical_correct.py --font <字体> --size 75 --mode fixed --json   # 逐字墨迹居中
```

## 上游与许可

| 上游 | 许可 | 本仓用了什么 |
|---|---|---|
| [赫蹏 heti](https://github.com/sivan/heti) | MIT | 挤压规则与正则思路 → 已内化在 `tools/cjk_spacing.js` |
| [pangu.js](https://github.com/vinta/pangu.js) | MIT | 部分边界正则，文件头注明 |
| [分寸 · Measure](https://github.com/dososo/blcaptain-measure-cjk) | 代码 Apache-2.0；字体数据 CC BY 4.0 | 网页硬规则编号体系（T/F）与校验纪律；`measure.css` 与 `data/licenses.json` **不内置，自取** |

不内置的理由：字体授权是会变的数据，抄一份快照进仓库，等于把过期结论当正本；留通道比留副本稳。自取方法见 [README 原始指针](docs/上游与许可.md)。

本仓代码 MIT，署名见 [LICENSE](LICENSE)。

## 目录

```
SKILL.md                  判据正本：反例优先 → 规则 → 网页硬规则 → 体量预算 → 上游声明
references/               七卷细则（知识地图、排版通则、校验循环、字体授权、主题、光学修正、命名）
tools/
  cjk-typo.css            开箱样式（令牌 + .mx + 变体 + 暗色）
  cjk_spacing.js          浏览器端：逐文本节点包裹间隙与挤压盒
  cjk_spacing.py          服务端：同规则正则替换
  selfcheck.py            五项自检
  check_spacing_consistency.py   数字-量词混用
  glyph_optical_correct.py       逐字墨迹居中
examples/demo.html        三种做法同屏对照，打开即见差别
docs/                     测量方法、上游与许可、封面文案
```

## 已知限制

- **跨元素边界的缝，脚本补不上**：间隙是按文本节点落的，`<span>学习</span><span>CSS</span>` 这种把缝拆到两个元素上的写法拿不到盒子。WebKit 的原生 `text-autospace` 同样在元素边界不加。
- **Safari 与 Firefox 未实测**：单侧加间隙、元素边界丢缝等说法来自 WebKit 记录，本仓标「未复现」，引用时请连这句一起引。
- **字体矩阵只覆盖本机三款**：挤压是否生效随字体而变，换字体要重量。

## 不做什么

- 不做 CSS 框架、不发 npm 包：要现成的排版样式，用赫蹏或汉字标准格式（Han）；本仓给的是判据与两个薄脚本。
- 不用字符凑间隙：不插普通空格、不插 `U+2009`。
- 不凭记忆引用文献结论：抓不到原文就记「未获取」；字体授权结论须回官方原文复核。

## 名字

罗蛇／Rassarpa——谢灵运与罗浮山，「罗，罗山也；浮，浮山也」的二名对举，龟蛇交叉换位。来历见 [references/naming.md](references/naming.md)，只记录名字，不改行为。

## 索引词

`CJK` · `typography` · `text-autospace` · `text-spacing-trim` · `mixed Chinese English spacing` · `四分空` · `中西文混排` · `punctuation squeezing` · `vertical writing` · `font stack`
