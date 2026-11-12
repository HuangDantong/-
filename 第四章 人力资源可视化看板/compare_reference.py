# -*- coding: utf-8 -*-
"""把复刻结果与 Excel 导出的看板图逐像素比对。

Excel 导出图（PDF 渲染）四周有白边，先自动裁到看板卡片再比。
运行：python compare_reference.py [--diff]
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "reference", "dashboard_excel.png")
OUT = os.path.join(BASE, "dashboard.png")


def main():
    ours = Image.open(OUT).convert("RGB")
    ref_full = np.asarray(Image.open(REF).convert("RGB"))
    mask = np.abs(ref_full.astype(int) - 255).sum(2) > 20
    ys, xs = np.where(mask)
    ref = Image.fromarray(ref_full[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    ref = ref.resize(ours.size, Image.LANCZOS)

    a = np.asarray(ours).astype(int)
    b = np.asarray(ref).astype(int)
    diff = np.abs(a - b)
    print("尺寸        :", ours.size)
    print("平均通道误差: %.2f/255" % diff.mean())
    print("像素一致率  : %.2f%%" % ((diff.sum(2) < 12).mean() * 100))

    if "--diff" in sys.argv:
        Image.fromarray(np.abs(a - b).astype(np.uint8) * 2).save(
            os.path.join(BASE, "reference", "diff.png"))
        Image.blend(ours, ref, 0.5).save(
            os.path.join(BASE, "reference", "blend.png"))
        print("saved: reference/diff.png, reference/blend.png")


if __name__ == "__main__":
    main()
