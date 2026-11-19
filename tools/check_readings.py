#!/usr/bin/env python3
"""读数对账：README 公布的每个数字，必须在 results/ 的 JSON 里找得到同值。

只做一件事：把「文档说 +4px / 0.125 em」「实测说 +4 / 0.125」这两处对起来，
免得某天改了量具或换机器重量，正文还挂着旧读数。

用法：
    python3 tools/check_readings.py [--results results] [--readme README.md]
退出码：0 全对上；1 有一处对不上（会列出文件与字段）。
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

# README 里的说法 → results/*.json 的 delta 字段。
# 期望值直接从「说法」里读出来，不另抄一份，避免两边一起写错。
CLAIMS = [
    ("0.125 em", "gap_em"),
    ("0.25 em", "mx_em"),
    ("−16px", "trim_pingfang"),
    ("差 0 —— **不声明等于关闭**", "undeclared_vs_off"),
]


def expected_from(needle: str) -> float:
    """从「0.125 em」「−16px」「差 0」里取数。负号是全角减号，先归一。"""
    text = needle.replace("−", "-").replace("＋", "+")
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    if not m:
        raise ValueError(f"没法从「{needle}」里读出期望值")
    return float(m.group(0))


def load_deltas(results_dir: Path) -> list[tuple[str, dict]]:
    out = []
    for f in sorted(glob.glob(str(results_dir / "*.json"))):
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        delta = data.get("delta")
        if isinstance(delta, dict):
            out.append((Path(f).name, delta))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--readme", default="README.md")
    args = ap.parse_args()

    readme = Path(args.readme).read_text(encoding="utf-8")
    sets = load_deltas(Path(args.results))
    if not sets:
        print(f"❌ {args.results} 下没有带 delta 的 JSON，无从对账")
        return 1

    bad = []
    for needle, key in CLAIMS:
        if needle not in readme:
            bad.append(f"README 里找不到「{needle}」——要么改了口径，要么这句被删了")
            continue
        found = [(name, d[key]) for name, d in sets if key in d]
        if not found:
            bad.append(f"README 说了「{needle}」，但没有任何 results JSON 带 {key}")
            continue
        want = expected_from(needle)
        for name, value in found:
            if abs(float(value) - float(want)) > 1e-9:
                bad.append(f"{name} 的 {key} = {value}，README 写的是 {needle}")

    if bad:
        print("❌ 读数对不上：")
        for line in bad:
            print("   " + line)
        return 1
    print(f"✅ 读数对得上：{len(sets)} 份 results，{len(CLAIMS)} 处口径一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
