# Safari 18.6（本体，非构建）

- UA：`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15`
- 属性支持：`text-autospace` 支持；`text-spacing-trim` 不支持
- 字体：苹方 有｜宋体 有｜黑体 有

| 项 | 读数 |
|---|---|
| 单边界间隙（32px / 64px） | 4px / 8px（0.125 em） |
| 不声明 vs 显式关闭 | 0px |
| 串内已有空格时加 normal | 0px |
| 跨元素边界（两缝） | 4px |
| 每缝包空 span | -4px |
| `.mx` 盒 | 8px（0.25 em） |
| 挤压（苹方／宋体／黑体） | 0／0／0px |

> 这个 Safari 不支持 `text-spacing-trim`，挤压三条读数为 0 是「属性没有」，⛔ 不能和 C7 混着读。

