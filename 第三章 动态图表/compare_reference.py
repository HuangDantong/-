# -*- coding: utf-8 -*-
"""把复刻图和 Excel 原始导出图做像素级比对，输出整体误差与误差热点。

用法：
    python compare_reference.py 16          # 图16
    python compare_reference.py 16 --diff   # 对照图写到 %TEMP%/chartcmp/

比对图不是复刻产物，默认不落盘。
"""

import os
import sys

import numpy as np
from PIL import Image

CHARTS = {
    31: ("chart31_excel.png", "chart31_dynamic_column.png"),
    32: ("chart32_excel.png", "chart32_dynamic_track.png"),
    33: ("chart33_excel.png", "chart33_dynamic_nightingale.png"),
    34: ("chart34_excel.png", "chart34_dynamic_combo.png"),
    35: ("chart35_excel.png", "chart35_pivot_slicer.png"),
    36: ("chart36_excel.png", "chart36_vba_jade_ring.png"),
    37: ("chart37_excel.png", "chart37_dynamic_lollipop.png"),
}

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    return np.array(Image.open(os.path.join(HERE, path)).convert("RGB")).astype(int)


def main():
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    reference, output = load("reference/" + CHARTS[index][0]), load(CHARTS[index][1])
    print("图%-3d %s" % (index, CHARTS[index][1]))
    print("尺寸   ref=%dx%d   out=%dx%d"
          % (reference.shape[1], reference.shape[0],
             output.shape[1], output.shape[0]))
    height = min(reference.shape[0], output.shape[0])
    width = min(reference.shape[1], output.shape[1])
    left, right = reference[:height, :width], output[:height, :width]
    delta = np.abs(left - right)
    print("平均通道误差 = %.2f / 255      像素近似一致率 = %.2f%%"
          % (delta.mean(), (delta.sum(2) < 12).mean() * 100))

    error = delta.sum(2)
    block, hotspots = 32, []
    for y in range(0, error.shape[0] - block, block):
        for x in range(0, error.shape[1] - block, block):
            hotspots.append((float(error[y:y + block, x:x + block].mean()), y, x))
    hotspots.sort(reverse=True)
    print("误差热点（32px 分块，前 6）:")
    for value, y, x in hotspots[:6]:
        print("   err=%6.1f  y=%3d x=%3d" % (value, y, x))

    if "--diff" in sys.argv:
        directory = os.path.join(os.environ.get("TEMP", "."), "chartcmp")
        os.makedirs(directory, exist_ok=True)
        canvas = np.full((height, width * 2 + 12, 3), 255, np.uint8)
        canvas[:, :width] = left.astype(np.uint8)
        canvas[:, width + 12:] = right.astype(np.uint8)
        Image.fromarray(canvas).save(
            os.path.join(directory, "chart%d_side_by_side.png" % index))
        Image.fromarray(((left * 0.5 + right * 0.5)).astype(np.uint8)).save(
            os.path.join(directory, "chart%d_overlay.png" % index))
        print("对照图已写到 %s" % directory)


if __name__ == "__main__":
    main()
