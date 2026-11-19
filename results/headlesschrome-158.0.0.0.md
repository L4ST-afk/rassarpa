<!-- 由 run.mjs 生成于 2026-11-19T19:16:52.592Z · Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/158.0.0.0 Safari/537.36 -->
| 项 | 量到的值 |
|---|---|
| 单边界间隙（32px） | +4px = 0.125 em |
| 单边界间隙（64px） | +8px = 0.125 em |
| 无声明 vs `no-autospace` | 0（0 = 无声明即关闭） |
| 已含 ASCII 空格的串 | 0（0 = 不再补） |
| 跨元素边界（`中<abbr>a</abbr>中`） | +8px |
| 每缝空 span 叠在 normal 上 | 0（负值 = 把原生间隙打掉了） |
| `.mx` 盒（32px） | +8px = 0.25 em |
| 挤压 · PingFang SC | −16px |
| 挤压 · Songti SC | 0 |
| 挤压 · Heiti SC | 0 |

CSS.supports：`text-autospace: normal` = true｜`no-autospace` = true｜`text-spacing-trim: normal` = true
