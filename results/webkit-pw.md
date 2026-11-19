# webkit（Playwright 构建）

- 引擎：webkit 27.2 · darwin
- UA：`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.2 Safari/605.1.15`
- 属性支持：`text-autospace` 支持；`text-spacing-trim` 不支持
- 字体：苹方 有｜宋体 有｜黑体 有｜Noto CJK 有

| 项 | 读数 |
|---|---|
| 单边界间隙（32px） | 4px |
| 单边界间隙（64px） | 8px |
| 折算 | 0.125 em |
| 不声明 vs 显式关闭 | 0px |
| 串内已有空格时加 normal | 0px |
| 跨元素边界（normal − 无声明） | 4px |
| 每缝包空 span | -4px |
| `.mx` 盒（32px） | 8px（0.25 em） |
| 挤压（苹方／宋体／黑体） | 0／0／0px |

> 这个引擎不支持 `text-spacing-trim`，挤压三条读数为 0 是「属性没有」，不是「字体没 halt」，⛔ 不能和 C7 混着读。

