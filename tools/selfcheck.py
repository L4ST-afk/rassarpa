#!/usr/bin/env python3
"""罗蛇Rassarpa · 最小自检器（2026-11-15 全批批三新增）

只读。三断言＋变异自证，退出码：0 全绿／1 有红／2 跑不成。

  A1  API 名一致：SKILL.md 里 `new Xxx(` 形态的调用，真名必须存在于 tools/ 源码
      （2026-11-14 三方交叉评审判「不过」的死承诺：正文调用名与 tools 真名不一致。2026-11-15 洗名后本 skill 自有命名 CJKSpacing/cjk-*，A1 守「调用名＝真名」这条契约）
  A2  引用在盘：SKILL.md 点名的 references/*.md 与 tools/*.py|js 全部存在
  A3  编号有落点：SKILL.md §九展开的 T/F 编号（**T01** 等粗体形态）逐一有正文小节
  A4  开箱样式红线：cjk-typo.css 无负 letter-spacing（T07）、font-size ≥12px（T11）、
      正文基线行高 ≥1.5（T06）；A2 已覆盖其在盘与被点名

  python3 tools/selfcheck.py            # 三断言＋C1
  python3 tools/selfcheck.py --self-test  # 变异自证：临时副本改坏 API 名，A1 必红（判反 rc=3）
⛔ 变异只在临时副本做，⛔ 本脚本不写库内任何文件。
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # skills/罗蛇Rassarpa


def a1_api_names(skill_md: str) -> list:
    """SKILL.md 里 `new Xxx(` 的调用名，必须在 tools/ 源码里有同名定义。"""
    called = set(re.findall(r"new\s+([A-Z][A-Za-z]+)\s*\(", skill_md))
    src = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "tools").glob("*") if p.suffix in {".js", ".py"})
    missing = [n for n in sorted(called) if not re.search(r"(function\s+%s\b|%s\s*[:=]\s*function|class\s+%s\b|def\s+%s\b)" % (n, n, n, n), src)]
    return missing


def a2_refs(skill_md: str) -> list:
    """SKILL.md 点名的 references/*.md 与 tools/* 全部在盘。"""
    named = set(re.findall(r"`(references/[^`]+?\.md|tools/[^`]+?\.(?:py|js))`", skill_md))
    return [n for n in sorted(named) if not (ROOT / n).exists()]


def a3_rule_ids(skill_md: str) -> list:
    """§九 粗体展开的 T/F 编号，必须各有展开落点。
    口径：落点行＝含该编号且行内 T/F 编号总数 <4 的非空行（≥4 个编号的行是索引/括注行，不算落点），
    且行长 ≥50 字符（保证有实质说明，⛔ 只出现编号不算）。"""
    sec9 = skill_md.split("## 九", 1)[-1].split("## 生成背景", 1)[0]
    pat = re.compile(r"\*\*(T\d+b?|F\d+)\b")
    missing = []
    for rid in sorted(set(pat.findall(sec9))):
        hit = False
        for line in sec9.splitlines():
            ids_in_line = set(pat.findall(line))
            if rid in ids_in_line and len(ids_in_line) < 4 and len(line.strip()) >= 50:
                hit = True
                break
        if not hit:
            missing.append(rid)
    return missing



def a4_typo_css() -> list:
    """tools/cjk-typo.css 的 T07/T11/T06 值红线（装配层不得违反自家规则）。"""
    css = (ROOT / "tools" / "cjk-typo.css").read_text(encoding="utf-8")
    bad = []
    if re.search(r"letter-spacing\s*:\s*-", css):
        bad.append("T07：出现负 letter-spacing")
    for m in re.finditer(r"font-size\s*:\s*(\d+)px", css):
        if int(m.group(1)) < 12:
            bad.append(f"T11：font-size {m.group(0)} <12px")
    # T06 只管正文：标题块（选择器含 h1–h6）的行高豁免；.cjk--annotation 的 2.25 是行间注加宽不涉红
    for block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = block[0].strip(), block[1]
        if re.search(r"\bh[1-6]\b", sel):
            continue
        for m in re.finditer(r"line-height\s*:\s*([0-9.]+)", body):
            v = float(m.group(1))
            if 0 < v < 1.5:
                bad.append(f"T06：正文行高 {v} <1.5（选择器：{sel[:40]}）")
    return bad


def main() -> int:
    skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    problems = []
    a1 = a1_api_names(skill_md)
    if a1:
        problems.append(f"A1 API 名死承诺（SKILL.md 调用了 tools/ 里不存在的名字）：{a1}")
    a2 = a2_refs(skill_md)
    if a2:
        problems.append(f"A2 点名文件不在盘：{a2}")
    a3 = a3_rule_ids(skill_md)
    if a3:
        problems.append(f"A3 §九编号无展开落点：{a3}")
    a4 = a4_typo_css()
    if a4:
        problems.append(f"A4 开箱样式红线：{a4}")
    checker = ROOT / "tools" / "check_spacing_consistency.py"
    if not checker.exists():
        problems.append("C1 check_spacing_consistency.py 不在盘")
    else:
        r = subprocess.run([sys.executable, str(checker), "--self-test"], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            problems.append(f"C1 混用检查器 --self-test 判反失败 rc={r.returncode}（闸没牙）")

    if "--self-test" in sys.argv:
        # 变异臂：临时副本把 CJKSpacing 改成坏名，A1 必须能抓到
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "SKILL.md"
            # 变异必须落在真正的调用点上：第一个 CJKSpacing 出现在说明文字里，改它
            # 会让 A1 什么也看不见，自检变「永远绿」——那闸就白装了。
            bad = skill_md.replace("new CJKSpacing(", "new NoSuchSpacing(", 1)
            if bad == skill_md:
                print("[SELF-TEST] 变异失败：未找到 CJKSpacing 可改"); return 3
            tmp.write_text(bad, encoding="utf-8")
            m1 = a1_api_names(bad)
            if not m1 or "NoSuchSpacing" not in m1:
                print("[SELF-TEST] A1 变异判反失败：改坏 API 名后仍绿"); return 3
        print("[SELF-TEST] A1 变异件判红 ✓（闸有牙）")

    if problems:
        print("❌ 自检不过：")
        for p in problems:
            print("  -", p)
        return 1
    print("✅ A1 API 名一致｜A2 引用在盘｜A3 §九编号有落点｜A4 开箱样式红线｜C1 混用检查器有牙")
    return 0


if __name__ == "__main__":
    sys.exit(main())
