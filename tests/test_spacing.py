#!/usr/bin/env python3
"""白盒回归：cjk_spacing.py 的行为断言（离线、无依赖）。

跑法：python3 tests/test_spacing.py   # 期望末行 ALL OK；失败退出 1

覆盖四件事：
  1. 边界两侧都落间隙；
  2. SKIP_TAGS 内的文本一格不动（含 `<code><span>` 这种**嵌套**，只看相邻标签会漏）；
  3. 相邻全角标点挤半字；
  4. 串里已有 ASCII 空格时不重复处理。
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(os.path.dirname(HERE), "tools")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


space = load("cjk_spacing")

CASES = [
    # (说明, 输入, 断言)
    ("中↔西一处西文两侧都落间隙（同一元素带 start+end）", "中a中",
     lambda o: o.count("<cjk-spacing") == 1 and "cjk-spacing-start cjk-spacing-end" in o),
    ("代码块内的字不动", "<code>中a</code>", lambda o: "<cjk-spacing" not in o),
    ("代码块内嵌套一层仍不动", "<code><span>中a</span></code>", lambda o: "<cjk-spacing" not in o),
    ("行内代码内不动、外层两处仍处理", "<p>中a<code>中a</code>中a</p>",
     lambda o: o.count("<cjk-spacing") == 2 and "<code>中a</code>" in o),
    ("script 内不动", "<script>中a</script>", lambda o: "<cjk-spacing" not in o),
    ("相邻全角标点挤半字", "。「", lambda o: "<cjk-adjacent" in o),
    ("已有 ASCII 空格原样保留、不重复处理", "中 a 中",
     lambda o: "<cjk-spacing" not in o and o == "中 a 中"),
    ("纯中文不处理", "中文排版", lambda o: "<cjk-spacing" not in o),
]

failed = 0
for label, src, check in CASES:
    out = space.mix_html(src)
    ok = check(out)
    print(("✓" if ok else "✗"), label, "" if ok else "→ " + out)
    failed += 0 if ok else 1

print("ALL OK" if not failed else f"{failed} 条失败")
sys.exit(0 if not failed else 1)
