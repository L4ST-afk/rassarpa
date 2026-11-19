#!/usr/bin/env python3
"""数字-量词空格混用检查器（罗蛇Rassarpa §三 A 例外 3 的出件闸）

判据（SKILL.md §三 A 例外 3）：同一份文档内「3 个」（加间隙）与「3个」（窄栏口语）必须二选一，⛔ 混用。
本工具只查**混用**（两种形态同时出现），不判哪种对——那是文档定基调的事。

用法：
  python3 tools/check_spacing_consistency.py <文件.html|md>     # 退出码 0 一致／1 混用／2 用法错误
  python3 tools/check_spacing_consistency.py --self-test        # 变异自证：夹具混用件必红（rc=3 判反失败）

规则：正则找「全角量词紧贴数字」与「全角量词前有空格」两种形态——
  A 形态：[0-9]＋量词（个/位/名/次/段/条/页/字/词/题/句/行/列/格/枚/张/件/套/种/类）
  B 形态：[0-9]＋空格＋量词
同文档 A、B 两种形态都命中 ⇒ 混用，列出各前 3 例与总数。
⛔ 不查「2 位小数」这类数字语义（量词表白名单制，误报看表扩充）。
"""
import re
import sys
import tempfile
from pathlib import Path

CLF = "个位名次段条页字词题句行列格枚张件套种类"

FENCE = re.compile(r"^```[\s\S]*?^```", re.M)     # 围栏代码块整段
INLINE = re.compile(r"`[^`\n]*`")                  # 行内代码


def prose_only(text: str) -> str:
    """剥掉围栏代码块与行内代码：代码示例里的「3个」是样本，不是正文写法。
    顺序不能反：先剥围栏再剥行内，否则围栏的三个反引号会被行内规则切成两截。"""
    return INLINE.sub("", FENCE.sub("", text))


def scan(text: str):
    text = prose_only(text)
    a = re.findall(r"[0-9](?:[,，.][0-9]+)?[" + CLF + r"]", text)
    b = re.findall(r"[0-9] [" + CLF + r"]", text)
    return a, b


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "fixture.md"
        f.write_text("共 25 个词、第 3 段；另页写 25个词、第3段。\n", encoding="utf-8")
        a, b = scan(f.read_text(encoding="utf-8"))
        if not (a and b):
            print("[SELF-TEST] 夹具未同时命中两形态——判据失去区分力"); return 3
        # 阴性对照：单形态文档不得报混用
        g = Path(td) / "clean.md"
        g.write_text("共 25 个词、第 3 段、10 行。\n", encoding="utf-8")
        a2, b2 = scan(g.read_text(encoding="utf-8"))
        if a2 and b2:
            print("[SELF-TEST] 阴性件被误判混用——假红"); return 3
        # 代码块对照：混用只出现在围栏／行内代码里时，不算正文混用（剥掉的必须只是代码）
        h = Path(td) / "code.md"
        h.write_text("正文不含数字量词。\n\n```\n25个词／第 3 段\n```\n另见 `3个`。\n", encoding="utf-8")
        a3, b3 = scan(h.read_text(encoding="utf-8"))
        if a3 or b3:
            print("[SELF-TEST] 代码块里的混用被算进正文——判据越界"); return 3
    print("[SELF-TEST] 混用件红／单形态件绿／代码块不计数 ✓（闸有牙）")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        return 2
    text = Path(args[0]).read_text(encoding="utf-8", errors="replace")
    a, b = scan(text)
    if a and b:
        print(f"❌ 数字-量词空格混用：A 形态（贴）{len(a)} 例、B 形态（空格）{len(b)} 例")
        print("   A 例：", "、".join(a[:3]))
        print("   B 例：", "、".join(b[:3]))
        print("   ⇒ 同一份文档二选一（SKILL.md §三 A 例外 3），⛔ 混用")
        return 1
    print("✅ 无混用（A %d 例／B %d 例，单形态合规）" % (len(a), len(b)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
