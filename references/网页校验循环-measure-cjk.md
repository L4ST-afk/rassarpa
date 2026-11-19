# 网页校验循环 · measure-cjk（吸收自「分寸 · Measure」，有扬弃）

> 来源：`dososo/blcaptain-measure-cjk`，代码 **Apache-2.0**。校验器当前版本 **0.1.0**。
> 本卷是「写完中文网页怎么验、怎么修」的操作手册。规则定义见 SKILL.md §九（每条括注了 T/F 上游 ID）。

## 一、安装（一次）

```bash
# 全局安装，版本锁定 0.1.0（避免未来破坏性升级导致规则漂移）
npm install -g measure-cjk@0.1.0

# 验证
measure-cjk --version     # 应输出 0.1.0
measure-cjk rules         # 列出全部规则与上游 ID
```

- 依赖：纯 Node（htmlparser2 / postcss / css-select / domutils）。**基础档不需要浏览器**。
- 完整档（`--render`）需要 **Playwright**，它是**可选** peerDependency，仅此模式要：`npm install -g playwright` 后 `npx playwright install chromium`。

## 二、两种模式

| 模式 | 命令 | 怎么跑 | 能力边界 |
|---|---|---|---|
| **基础档** | `measure-cjk lint <文件.html>` | 静态分析源码：htmlparser2 解析 DOM、postcss 解析 CSS；`cascade.js` 做**近似层叠** | 只在 1280px（桌面）和 390px（窄屏）两档近似求值；展开 `var()`、视 `@supports` 生效；**不算 `calc()`** |
| **完整档** | `measure-cjk lint <文件.html> --render` | Playwright 驱动无头浏览器，在 **360/390/768/1024/1280/1440** 六宽**实测**，读 `getComputedStyle` 真实计算样式 + 每条 error 截图存 `evidence/` | 以浏览器实测为准，T02/T04–T07/T11 不再靠估算 |

- URL 检查只能用完整档；默认只允许 localhost，远程地址加 `--allow-remote`。
- 输出格式：`--format text|json`，可 `--out <文件>` 落盘，`--config <文件>` 读配置。

## 三、子命令速查

```
measure-cjk lint <路径>...                 # 基础档静态检查
measure-cjk lint <路径/URL>... --render     # 完整档六宽实测 + 截图
measure-cjk fonts <字体名>                  # 查字体授权档（🟢🔵🟡🔴）
measure-cjk rules                           # 列全部规则 + 上游 ID + 是否已实现
measure-cjk card <卡片.html> --out x.png    # 小红书 1080×1440 出图 + 逐元素查字体授权
measure-cjk init [--spacing css|text]       # 生成间距初始化文件
```

## 四、退出码（接 CI / 脚本用）

- `0`：通过，或页面无关中文。
- `1`：有 error。
- `2`：用法或环境错误（如 `--render` 但没装 Playwright）。

## 五、关规则必须写理由（硬约束，机制层面堵死「偷偷关」）

measure-cjk 的 `config.js` 强制：**`disabled` 必须是 `{规则ID: 理由}` 对象，理由为空直接抛 `UsageError`**，没有任何绕过开关。例：

```json
{
  "disabled": {
    "T05": "本页是固定宽度的卡片，行长约束由容器布局保证，不另设 max-width"
  }
}
```

→ 本 skill 的纪律口径：**修不好就如实报告，⛔ 不偷偷关规则凑数**。关任何规则都要在配置里写清理由，且理由要经得起推敲（是「这条不适用本场景」，不是「它报错了嫌烦」）。

## 六、5 轮修复纪律

1. 写完页面 → 跑 `measure-cjk lint`（基础档先过，再 `--render` 完整档）。
2. 拿结果**逐条**修（优先 error，再 warn 里的高优先 P0）。
3. 修完重跑；循环**最多 5 轮**。
4. 5 轮后仍有修不了的，**如实报告**哪些规则未达标、为什么（环境/场景限制），⛔ 不关规则掩盖。
5. 每轮独立记录改了什么、下一轮结果——对应上游「逐轮独立审计」的诚实口径。

## 七、与现有手动三对照的关系

没装校验器时，退回 SKILL.md §五 的手动三对照 + `tools/cjk_spacing.js`（浏览器零依赖，处理中西文间隙/标点挤压）+ `tools/cjk_spacing.py`（服务端出 HTML）。**measure-cjk 不替代这些脚本**——它补的是「AI 网页专属的硬规则（字距不为负/最小字号/防假斜体/字体栈/字体授权）+ 浏览器实测取证」，二者互补。

## 八、规则 ID 一览（0.1.0，部分未实现）

- **T01–T19（排版）**：T01 lang、T02 中英间距、T03 全角标点/引号、T04 行首禁则、T05 行长、T06 行高、T07 字距不为负、T08 不用斜体、T09 text-transform、T10 字重存在、T11 最小字号、T12 首行缩进/段间距二选一（仅完整档）、T13 字体栈、T14 标点挤压、T15 text-wrap、T16 两端对齐慎用、T17 数字/省略号/破折号、T18 竖排、T19 繁体标点。
- **F03–F06（字体授权）**：F03 自托管 webfont 授权、F04 查询授权、F05 体积预算/子集化、F06 出图只用 commercial_image=true（card 检查）。
- **A01–A12（AI 味反模式）**：A01 紫色/蓝紫渐变背景（仅完整档）、A11 每段加粗>15%（仅完整档）；A02–A10/A12 多为「计划中未实现」。

> ● = 已实现（基础+完整档都查）　◐ = 已实现（仅 `--render` 查）　○ = 尚未实现。以 `measure-cjk rules` 实时输出为准。
