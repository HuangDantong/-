# -*- coding: utf-8 -*-
"""对比复刻图与 Excel 原始导出图，输出逐项几何差异与整体误差。

用法：
    python compare_reference.py 1     # 图1 渐变柱形图
    python compare_reference.py 2     # 图2 带均值柱形图
"""

import sys

import numpy as np
from PIL import Image

CHARTS = {
    1: ("reference/chart1_excel.png", "chart1_gradient_bar.png"),
    2: ("reference/chart2_excel.png", "chart2_mean_bar.png"),
}


def bands(mask, gap=3):
    rows = mask.sum(1)
    ys = np.where(rows > 0)[0]
    if len(ys) == 0:
        return []
    out = []
    start = prev = ys[0]
    for y in ys[1:]:
        if y > prev + gap:
            out.append((int(start), int(prev)))
            start = y
        prev = y
    out.append((int(start), int(prev)))
    return out


def analyse(path):
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    bg = np.array([26, 30, 67])
    info = {"size": a.shape[1::-1], "arr": a}

    # 柱体：偏蓝的实心像素（对渐变柱取两端之外的中段也能命中）
    bars = (a[:, :, 2] > 150) & (a[:, :, 0] < 60) & (90 < a[:, :, 1]) & (a[:, :, 1] < 200)
    cols = np.where(bars.sum(0) > 10)[0]
    groups = []
    if len(cols):
        s = p = cols[0]
        for x in cols[1:]:
            if x > p + 3:
                groups.append((int(s), int(p)))
                s = x
            p = x
        groups.append((int(s), int(p)))
    info["bars"] = []
    for x0, x1 in groups:
        cx = (x0 + x1) // 2
        ys = np.where(bars[:, cx])[0]
        info["bars"].append((x0, x1, int(ys.min()), int(ys.max())))

    # 文本条带：亮且接近中性灰（排除黄色均值线）
    neutral = (np.abs(a[:, :, 0] - a[:, :, 1]) < 25) & (np.abs(a[:, :, 1] - a[:, :, 2]) < 25)
    bright = neutral & (a.sum(2) > 330)
    info["bands"] = []
    for y0, y1 in bands(bright):
        cs = np.where(bright[y0:y1 + 1].sum(0) > 0)[0]
        if len(cs):
            info["bands"].append((y0, y1, int(cs.min()), int(cs.max())))

    # 黄色元素（均值线 / 均值标注）
    yellow = (a[:, :, 0] > 200) & (a[:, :, 1] > 150) & (a[:, :, 2] < 80)
    info["yellow"] = [(int(y), int(yellow[y].sum())) for y in np.where(yellow.sum(1) > 40)[0]]
    return info


def overlay_ink(info, x0, x1):
    """给定期望的 x 区间，返回该区间内文本墨迹的 y 范围。"""
    a = info["arr"]
    neutral = (np.abs(a[:, :, 0] - a[:, :, 1]) < 25) & (np.abs(a[:, :, 1] - a[:, :, 2]) < 25)
    m = neutral & (a.sum(2) > 330)
    sub = m[:, x0:x1]
    ys = np.where(sub.sum(1) > 0)[0]
    return (int(ys.min()), int(ys.max())) if len(ys) else None


def main():
    key = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ref_path, out_path = CHARTS[key]
    ri, oi = analyse(ref_path), analyse(out_path)

    print("图%d   %s  vs  %s" % (key, ref_path, out_path))
    print("尺寸        ref=%s   out=%s" % (ri["size"], oi["size"]))
    print()
    print("柱体 (x0,x1,ytop,ybot):")
    for r, o in zip(ri["bars"], oi["bars"]):
        print("   ref %-24s out %-24s  dx=%+d dy=%+d dw=%+d"
              % (r, o, o[0] - r[0], o[2] - r[2], (o[1] - o[0]) - (r[1] - r[0])))
    print()
    if ri["yellow"] or oi["yellow"]:
        print("黄色均值线 y (像素数>40 的行):")
        print("   ref", [y for y, _ in ri["yellow"]])
        print("   out", [y for y, _ in oi["yellow"]])
        print()
    print("文本条带 (y0,y1,xmin,xmax):")
    print("   ref:")
    for b in ri["bands"]:
        print("      ", b)
    print("   out:")
    for b in oi["bands"]:
        print("      ", b)

    ra, oa = ri["arr"], oi["arr"]
    if ra.shape != oa.shape:
        print("\n尺寸不同，无法逐像素比对")
        return
    d = np.abs(ra - oa)
    print()
    print("平均通道误差 = %.2f / 255    像素近似一致率 = %.2f%%"
          % (d.mean(), (d.sum(2) < 12).mean() * 100))

    h, w = ra.shape[:2]
    canvas = np.full((h, w * 2 + 12, 3), 255, np.uint8)
    canvas[:, :w] = ra.astype(np.uint8)
    canvas[:, w + 12:] = oa.astype(np.uint8)
    Image.fromarray(canvas).save("reference/chart%d_side_by_side.png" % key)
    Image.fromarray(((ra * 0.5 + oa * 0.5)).astype(np.uint8)).save(
        "reference/chart%d_overlay.png" % key)

    # 误差热点
    err = d.sum(2)
    bs, blocks = 32, []
    for y in range(0, h - bs, bs):
        for x in range(0, w - bs, bs):
            blocks.append((float(err[y:y + bs, x:x + bs].mean()), y, x))
    blocks.sort(reverse=True)
    print("误差热点（32px 分块，前 6）:")
    for v, y, x in blocks[:6]:
        print("   err=%6.1f  y=%3d x=%3d" % (v, y, x))
    print("\n已输出 reference/chart%d_side_by_side.png 与 chart%d_overlay.png" % (key, key))


if __name__ == "__main__":
    main()
