#!/usr/bin/env python3
"""
cjk_spacing.py — 中西文混排间隙 + 全角标点挤压（服务端，纯文本→HTML）

吸收自 Sivan《赫蹏》(heti-addon.js，MIT)，有扬弃：
  - 同一套挤压规则与"逐文本节点包裹负边距元素"思路，便于生成脚本落盘前处理片段
  - 单遍边界分类，避免 heti 三遍叠跑产生的嵌套 cjk-spacing 元素
  - 保留本 skill 既有规则：紧邻全角标点（引号/括号）内侧不加中西文间隙
    → 间距只发生在"汉字(ideograph)↔西文/数字"边界，引号/括号算标点不算字，
      因此「他说：「OK」」在内层「与 OK 之间不加间隙（与 SKILL.md A 节一致）

配套 CSS（落到使用方样式表）：
  .cjk-spacing-start{margin-inline-end:.25em}
  .cjk-spacing-end{margin-inline-start:.25em}
  .cjk-adjacent-half{margin-inline-end:-.5em}
  .cjk-adjacent-quarter{margin-inline-end:-.25em}
  cjk-spacing,cjk-adjacent{display:inline;unicode-bidi:isolate}
"""
import re

# 汉字/假名（用于"中西文间隙"——不含标点，引号/括号算标点不算字）
IDEO = r'\u3400-\u4dbf\u4e00-\u9fff\u3040-\u309f\u30a0-\u30fa\u30fc-\u30ff\u3100-\u312f\u3200-\u32ff\uF900-\uFAFF'
# 含标点的全角集合（用于"标点挤压"判断相邻关系）
CJK = r'\u3000-\u303f' + IDEO

A = r'A-Za-z\u0080-\u00ff\u0370-\u03ff'
N = r'0-9'
S = r'`~!@#\$%\^&\*\(\)\-_=\+\[\]\{\}\\\|;:\'",<.>/\?'
ANS = A + N + S

BD_STOP = r'。．，、：；！‼？⁇'
BD_SEP = r'·・‧'
BD_OPEN = r'「『（《〈【〖〔［｛'
BD_CLOSE = r'」』）》〉】〗〕］｝'
BD_START = BD_OPEN + BD_CLOSE
BD_END = BD_STOP + BD_OPEN + BD_CLOSE
BD_HALF_OPEN = r'“‘'
BD_HALF_CLOSE = r'”’'
BD_HALF_START = BD_HALF_OPEN + BD_HALF_CLOSE

INNER = rf'[{ANS}]+(?: +[{ANS}]+)*'
# 单遍：捕获可选的"前置汉字 / 西文片段 / 后置汉字"，据此决定间隙落哪一侧
RE_BOUNDARY = re.compile(rf'([{IDEO}]|[{ANS}]+)? *({INNER}) *([{IDEO}])?')
RE_HALF = re.compile(rf'([{BD_STOP}])(?=[{BD_START}])|([{BD_OPEN}])(?=[{BD_OPEN}])|([{BD_CLOSE}])(?=[{BD_END}])')
RE_QUARTER_SEP = re.compile(rf'([{BD_SEP}])(?=[{BD_OPEN}])|([{BD_CLOSE}])(?=[{BD_SEP}])')
RE_QUARTER_HALF = re.compile(rf'([{BD_STOP}])(?=[{BD_HALF_START}])|([{BD_HALF_OPEN}])(?=[{BD_OPEN}])')

SKIP_TAGS = {'pre', 'code', 'sup', 'sub', 'script', 'style', 'cjk-spacing', 'cjk-adjacent'}


def _wrap_spacing(ans, before, after):
    if before and after:
        cls = 'cjk-spacing-start cjk-spacing-end'
    elif before and not after:
        cls = 'cjk-spacing-end'        # 间隙落在西文之前
    elif after and not before:
        cls = 'cjk-spacing-start'      # 间隙落在西文之后
    else:
        return ans                      # 孤立西文片段，不加
    return f'<cjk-spacing class="{cls}">{ans}</cjk-spacing>'


def _wrap_adj(text, kind):
    cls = 'cjk-adjacent-half' if kind == 'half' else 'cjk-adjacent-quarter'
    return f'<cjk-adjacent class="{cls}">{text}</cjk-adjacent>'


def mix_text(text):
    """对单段纯文本应用全部规则。"""
    def _b(m):
        return _wrap_spacing(m.group(2), m.group(1), m.group(3))
    text = RE_BOUNDARY.sub(_b, text)
    text = RE_HALF.sub(lambda m: _wrap_adj(m.group(0), 'half'), text)
    text = RE_QUARTER_SEP.sub(lambda m: _wrap_adj(m.group(0), 'quarter'), text)
    text = RE_QUARTER_HALF.sub(lambda m: _wrap_adj(m.group(0), 'quarter'), text)
    return text


_TAG_RE = re.compile(r'(<!--.*?-->|<[^>]+>)', re.S)


def mix_html(html):
    """把 HTML 切为标签/文本段，只对文本段应用规则（跳过 pre/code/... 内的文本）。"""
    out = []
    for i, part in enumerate(_TAG_RE.split(html)):
        if i % 2 == 1:  # 标签
            out.append(part)
            continue
        out.append(mix_text(part))
    return ''.join(out)


if __name__ == '__main__':
    import sys
    src = sys.stdin.read() if not sys.argv[1:] else sys.argv[1]
    print(mix_html(src))
