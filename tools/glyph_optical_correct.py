#!/usr/bin/env python3
"""
逐字光学修正 (Per-glyph Optical Correction)
==========================================
罗蛇Rassarpa skill 工具：基于字体真实度量，为单个字形计算光学修正参数，
用于做「灰度平衡 / 墨迹居中」微调。

原理（来自 skill 知识地图 A.1 字面率·重心 / A.4 四个基础形状）：
  同一字号的字形，墨迹面积（字面率）与墨迹中心各不相同——"1" 轻、"8" 重；
  字形在 advance 字身框里也未必居中。直接以 advance 框居中，会让轻字发飘、
  重字显大、偏左字显歪。逐字光学修正即把"墨迹几何中心"对齐到目标点。

两种模式：
  fixed  —— 不改变字号：仅横向墨迹居中（单字）+ 两位数按"合墨跨度"居中
             并保留字间死隙收紧。这是"灰度平衡"在固定字号下的唯一纯量杠杆。
  size   —— 改变字号：按墨迹面积把轻数字放大、重数字缩小，逼近均匀灰度。
             仅作参考；样张通常不建议全量等灰度（会失真、扭曲字面）。

局限（务必告知用户）：
  * 纯 <text> 节点无法改单字"黑度/字重"。要真动墨色，只能：变量字体 weight 轴 /
    给轻字换 Bold 字面 / 转轮廓后加 stroke——三者都超出 text 结构，需重写管线。
  * 纵向：数字共用 cap height，墨迹纵向跨度一致，cap-height 偏移已统居中，无需逐字纵向修正。

依赖：fontTools
"""
import argparse
import json
import sys

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.areaPen import AreaPen
except ImportError:  # 可选依赖：只有这个工具需要，缺了要说人话，⛔ 不要抛一屏 traceback
    sys.exit("缺 fontTools：python3 -m pip install fonttools（本仓只有逐字光学修正用它，"
             "其余工具零依赖）")



def load_metrics(font_path, face=0, digits="0123456789"):
    f = TTFont(font_path, fontNumber=face)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    glyf = f["glyf"]
    hmtx = f["hmtx"]
    out = {}
    for d in digits:
        if ord(d) not in cmap:
            continue
        gname = cmap[ord(d)]
        g = glyf[gname]
        adv = hmtx[gname][0] / upm
        xMin, xMax, yMin, yMax = (v / upm for v in (g.xMin, g.xMax, g.yMin, g.yMax))
        pen = AreaPen()
        g.draw(pen, glyf)
        area = pen.value / upm / upm
        inkW = xMax - xMin
        inkCx = (xMin + xMax) / 2
        out[d] = dict(adv=adv, xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax,
                      inkW=inkW, inkCx=inkCx, area=area)
    return out


def enrich(M, size):
    areas = {d: m["area"] for d, m in M.items()}
    mean = sum(areas.values()) / len(areas) if areas else 0
    for d, m in M.items():
        gap_em = m["inkCx"] - m["adv"] / 2          # 墨迹中心相对字身框中心
        m["inkCxGap_em"] = gap_em
        m["inkCxGap_px"] = gap_em * size
        m["areaRatio"] = m["area"] / mean if mean else 1
        # 面积等灰度所需的整字号缩放
        m["sizeComp_pct"] = ((mean / m["area"]) ** 0.5 - 1) * 100 if m["area"] else 0
        # 温和钳制 ±8%（避免样张失真）
        c = m["sizeComp_pct"]
        m["mildSize_pct"] = max(-8.0, min(8.0, c))
        # fixed 模式：text-anchor=middle 下，x = cx - gap_px
        m["fixed_xshift_px"] = -m["inkCxGap_px"]
    return M


def pair_layout(d1, d2, cx, size, tighten, M, r=45, stroke=5, edge_margin=4.0):
    """两位数：按"合墨跨度"居中于 cx，并保留 (1-tighten) 比例的字间死隙。

    灰度平衡前提（用户硬性约束）：左数字尽量不贴左边、右数字尽量不贴右边——
    即两字可向内（左字右移、右字左移）收紧以让出圆内边距。当合墨跨度逼近圆边时，
    自动加大 tighten 直到满足 edge_margin；若即使零间隙仍放不下，则退化为零间隙
    （保持 t<=0.97，字身不重叠）。

    返回两字形的 advance 左缘 x（配合 text-anchor=start 的 <tspan x=>）。"""
    m1, m2 = M[d1], M[d2]
    adv = m1["adv"]
    inkA = m1["inkW"] * size
    inkB = m2["inkW"] * size
    xMinA = m1["xMin"] * size
    xMinB = m2["xMin"] * size
    natural_gap = (2 * adv - m1["inkW"] - m2["inkW"]) * size
    inner = r - stroke / 2.0
    half_max = inner - edge_margin                # 合墨半跨度允许上限
    # 先按用户 tighten 算跨度
    span = inkA + (1 - tighten) * natural_gap + inkB
    t = tighten
    if span / 2.0 > half_max:
        # 逼近圆边：解 (1-t)*natural_gap = 2*half_max - inkA - inkB，求更紧的 t
        avail = 2 * half_max - inkA - inkB
        if avail <= 0:
            t = 1.0                               # 零间隙（仍不重叠）
        else:
            t = 1.0 - avail / natural_gap
            t = min(t, 0.97)                       # 保底留 3% 死隙，字身不相叠
        span = inkA + (1 - t) * natural_gap + inkB
    eff_gap = (1 - t) * natural_gap
    cursor = cx - span / 2.0                      # A 墨迹左缘
    x1 = cursor - xMinA                           # A advance 左缘
    cursor += inkA + eff_gap
    x2 = cursor - xMinB                           # B advance 左缘
    return round(x1, 2), round(x2, 2)


def main():
    ap = argparse.ArgumentParser(description="逐字光学修正：字体真实度量 -> 灰度平衡/墨迹居中参数")
    ap.add_argument("--font", required=True, help="字体路径（含 .ttc 也可）")
    ap.add_argument("--face", type=int, default=0, help=".ttc 内的字面序号")
    ap.add_argument("--size", type=float, default=75, help="参考字号(px)")
    ap.add_argument("--digits", default="0123456789")
    ap.add_argument("--mode", choices=["fixed", "size"], default="fixed")
    ap.add_argument("--tighten", type=float, default=0.7, help="两位数收紧比例(0-1): 吃掉死隙的比例")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    M = enrich(load_metrics(args.font, args.face, args.digits), args.size)

    if args.json:
        print(json.dumps(M, ensure_ascii=False, indent=2))
        return

    print(f"{'d':>2} {'adv':>6} {'inkW':>6} {'inkCx':>7} {'area':>7} {'ratio':>6} "
          f"{'gap_px':>7} {'fixedΔx':>7} {'sizeComp%':>9} {'mild%':>7}")
    for d, m in M.items():
        print(f"{d:>2} {m['adv']:6.3f} {m['inkW']:6.3f} {m['inkCx']:7.3f} {m['area']:7.3f} "
              f"{m['areaRatio']:6.3f} {m['inkCxGap_px']:7.2f} {m['fixed_xshift_px']:7.2f} "
              f"{m['sizeComp_pct']:9.2f} {m['mildSize_pct']:7.2f}")
    if args.mode == "fixed":
        print("\n[fixed 模式] 不改字号，仅横向墨迹居中：单字 x = cx + fixedΔx (text-anchor=middle)")
    else:
        print("\n[size 模式] 按面积等比缩放：size' = size*(1+mild%/100)（参考，慎用于样张）")


if __name__ == "__main__":
    main()
