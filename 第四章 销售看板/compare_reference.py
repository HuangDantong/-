# -*- coding: utf-8 -*-
"""把复刻结果与 Excel 导出图（reference/dashboard_excel.png）逐像素比对。

Excel 导出图比看板本身多了一圈白边/网格线，先裁到看板卡片区域再比。
运行：python compare_reference.py [--diff]
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "reference", "dashboard_excel.png")
OUT = os.path.join(BASE, "dashboard.png")
# 卡片在看板导出图中的位置（自动检测失败时的兜底）
CARD = (4, 27, 1728, 1115)


def main():
    ours = Image.open(OUT).convert("RGB")
    ref = Image.open(REF).convert("RGB").crop(CARD)
    ref = ref.resize(ours.size, Image.LANCZOS)

    a = np.asarray(ours).astype(int)
    b = np.asarray(ref).astype(int)
    diff = np.abs(a - b)
    mean_err = diff.mean()
    close = (diff.sum(2) < 12).mean() * 100
    print("尺寸        :", ours.size)
    print("平均通道误差: %.2f/255" % mean_err)
    print("像素一致率  : %.2f%%" % close)

    if "--diff" in sys.argv:
        Image.fromarray(np.abs(a - b).astype(np.uint8) * 2).save(
            os.path.join(BASE, "reference", "diff.png"))
        blend = Image.blend(ours, ref, 0.5)
        blend.save(os.path.join(BASE, "reference", "blend.png"))
        print("saved: reference/diff.png, reference/blend.png")


if __name__ == "__main__":
    main()
