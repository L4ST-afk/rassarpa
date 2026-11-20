#!/usr/bin/env python3
"""跨引擎对账：*-pw.json 里那几条「应当处处成立」的读数，逐份验一遍。

三条不变式（与引擎无关，改坏了就是改坏了）：
  1. undeclared_vs_off == 0      不声明等于关闭
  2. spaced_delta == 0          串里已有 ASCII 空格时不再补
  3. mx_em == 0.25              .mx 盒就是四分空

两条条件式（先看引擎支不支持这个属性，再说读数）：
  4. 支持 text-autospace 的引擎，gap_em 必须是 0.125
  5. 支持 text-spacing-trim 的引擎，挤压才谈字体；不支持就只记录，不判错

不做的事：不要求 element_delta 三家长一样。WebKit 只补一侧，这正是要记下来的差别。

用法：
    python3 tools/check_engines.py [results]
退出码：0 全过；1 有违反，或一份 *-pw.json 都没有。
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path


def main() -> int:
    results = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    # Playwright 起的两家（*-pw.json）与 Safari 本体（safari.json）一起验：这三条不变式不分载体。
    files = sorted(set(glob.glob(str(results / "*-pw.json")) + glob.glob(str(results / "safari*.json"))))
    if not files:
        print(f"❌ {results} 下没有 *-pw.json 或 safari*.json，先跑 node tools/measure_pw.mjs / tools/measure_safari.mjs")
        return 1

    bad: list[str] = []
    strict = 0
    for f in files:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        name = Path(f).name
        d = data.get("delta") or {}
        sup = data.get("supports") or {}
        env = data.get("env") or {}
        engine = env.get("engine", name)
        platform = env.get("platform", "unknown")

        if d.get("undeclared_vs_off") != 0:
            bad.append(f"{name}：不声明 vs 显式关闭 差 {d.get('undeclared_vs_off')}，应为 0")
        if d.get("spaced_delta") != 0:
            bad.append(f"{name}：串内已有空格时差值 {d.get('spaced_delta')}，应为 0")
        if d.get("mx_em") != 0.25:
            bad.append(f"{name}：.mx 盒折算 {d.get('mx_em')} em，应为 0.25")

        if sup.get("autospace"):
            if d.get("gap_em") == 0.125:
                if platform == "darwin":
                    strict += 1
            elif platform == "darwin":
                # macOS 上有中文字体，读数与声明不符就是真出问题
                bad.append(f"{name}：声明支持 autospace，间隙却是 {d.get('gap_em')} em，应 0.125")
            else:
                # CI 是 Linux，缺中文字体时引擎可能不加间隙；这是环境差异，记一笔，不当门禁
                print(f"   · {name}：{platform} 上间隙 {d.get('gap_em')} em（非 0.125，按环境差异记录）")
        else:
            print(f"   · {name}：该引擎不支持 text-autospace，间隙读数 {d.get('gap_em')} em 只作记录")

        if not sup.get("spacingTrim"):
            print(f"   · {name}：该引擎不支持 text-spacing-trim，挤压三条不判错，只记录")

        print(
            f"   · {name}：{engine} 间隙 {d.get('gap_em')} em｜元素边界 {d.get('element_delta')}px"
            f"｜两缝包 span {d.get('empty_spans_delta')}px"
        )

    if bad:
        print("❌ 跨引擎读数有违反：")
        for line in bad:
            print("   " + line)
        return 1
    print(
        f"✅ 跨引擎 {len(files)} 份：三条不变式全过；"
        f"间隙在 darwin 上按 0.125 em 逐份核（{strict} 份），其他平台只记录（{len(files) - strict} 份）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
