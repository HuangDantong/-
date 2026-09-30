# -*- coding: utf-8 -*-
"""对比复刻图与 Excel 原始导出图，输出逐项几何差异。"""

import numpy as np
from PIL import Image

REF = "reference/chart1_excel.png"
OUT = "chart1_gradient_bar.png"


def bands(mask, rows_min=1, gap=3):
    rows = mask.sum(1)
    ys = np.where(rows >= rows_min)[0]
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
    bright = a.sum(2) > 420
    bars = (a[:, :, 2] > 150) & (a[:, :, 0] < 60) & (a[:, :, 1] > 90) & (a[:, :, 1] < 200)

    info = {"size": a.shape[1::-1]}

    # 柱体几何
    cols = np.where(bars.sum(0) > 5)[0]
    groups = []
    if len(cols):
        s = p = cols[0]
        for x in cols[1:]:
            if x > p + 3:
                groups.append((int(s), int(p)))
                s = x
            p = x
        groups.append((int(s), int(p)))
    info["bars"] = [
        (g[0], g[1], int(np.where(bars[:, (g[0] + g[1]) // 2])[0].min()),
         int(np.where(bars[:, (g[0] + g[1]) // 2])[0].max()))
        for g in groups
    ]

    # 文本条带（排除柱体所在列）
    text = bright.copy()
    for g in groups:
        text[:, g[0]:g[1] + 1] = False
    info["text_bands"] = []
    for y0, y1 in bands(text, rows_min=1):
        cs = np.where(text[y0:y1 + 1].sum(0) > 0)[0]
        if len(cs) == 0:
            continue
        info["text_bands"].append((y0, y1, int(cs.min()), int(cs.max())))

    # 网格线
    gl = (np.abs(a - np.array([64, 67, 97])).sum(2) < 30)
    rows = gl.sum(1)
    info["grid_y"] = [int(y) for y in np.where(rows > 50)[0]]
    return info, a


def main():
    ri, ra = analyse(REF)
    oi, oa = analyse(OUT)

    print("size        ref=%s out=%s" % (ri["size"], oi["size"]))
    print()
    print("柱体 (x0,x1,ytop,ybot):")
    for r, o in zip(ri["bars"], oi["bars"]):
        print("   ref %-24s out %-24s  dx=%s dy=%s" % (r, o, o[0] - r[0], o[2] - r[2]))
    print()
    print("网格线 y:")
    print("   ref", ri["grid_y"])
    print("   out", oi["grid_y"])
    print()
    print("水平/垂直条带 (y0,y1,xmin,xmax):")
    print("  ref:")
    for b in ri["text_bands"]:
        print("    ", b)
    print("  out:")
    for b in oi["text_bands"]:
        print("    ", b)

    diff = np.abs(ra - oa).mean()
    same = (np.abs(ra - oa).sum(2) < 12).mean()
    print()
    print("平均通道误差 = %.2f / 255    像素近似一致率 = %.2f%%" % (diff, same * 100))

    # 叠加对比图
    h = max(ra.shape[0], oa.shape[0])
    w = ra.shape[1] + oa.shape[1] + 12
    canvas = np.full((h, w, 3), 255, np.uint8)
    canvas[:ra.shape[0], :ra.shape[1]] = ra
    canvas[:oa.shape[0], ra.shape[1] + 12:ra.shape[1] + 12 + oa.shape[1]] = oa
    Image.fromarray(canvas).save("reference/side_by_side.png")

    blend = (ra * 0.5 + oa * 0.5).astype(np.uint8)
    Image.fromarray(blend).save("reference/overlay.png")
    print("已输出 reference/side_by_side.png 与 reference/overlay.png")


if __name__ == "__main__":
    main()
