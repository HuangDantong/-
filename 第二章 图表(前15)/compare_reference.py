# -*- coding: utf-8 -*-
"""把复刻图和 Excel 原始导出图做像素级比对，输出几何差异与整体误差。

用法：
    python compare_reference.py 5          # 图5 层叠柱形图
    python compare_reference.py 5 --diff   # 额外把对照图写到系统临时目录

比对图（左右对照 / 50% 叠加）不是复刻产物的一部分，所以默认不落盘；
需要肉眼检查时加 --diff，图片会写到 %TEMP%/chartcmp/ 下。

各图的复刻输出文件名在 CHARTS 里登记；参考图统一叫
reference/chart{N}_excel.png，由 export_reference.py 生成。
"""

import os
import sys

import numpy as np
from PIL import Image

CHARTS = {
    1: ("reference/chart1_excel.png", "chart1_gradient_bar.png"),
    2: ("reference/chart2_excel.png", "chart2_mean_bar.png"),
    3: ("reference/chart3_excel.png", "chart3_rounded_gradient_bar.png"),
    4: ("reference/chart4_excel.png", "chart4_annotated_bar.png"),
    5: ("reference/chart5_excel.png", "chart5_clustered_bar.png"),
    6: ("reference/chart6_excel.png", "chart6_butterfly.png"),
    7: ("reference/chart7_excel.png", "chart7_rept_butterfly.png"),
    8: ("reference/chart8_excel.png", "chart8_percent_stacked.png"),
    9: ("reference/chart9_excel.png", "chart9_compare_column.png"),
    10: ("reference/chart10_excel.png", "chart10_gantt.png"),
    11: ("reference/chart11_excel.png", "chart11_smooth_line.png"),
    12: ("reference/chart12_excel.png", "chart12_diamond_lollipop.png"),
    13: ("reference/chart13_excel.png", "chart13_compare_line.png"),
    14: ("reference/chart14_excel.png", "chart14_doughnut.png"),
    15: ("reference/chart15_excel.png", "chart15_liquid_fill.png"),
}


def load(path):
    return np.array(Image.open(path).convert("RGB")).astype(int)


def align(reference, output):
    """把两张图裁到公共尺寸，便于逐像素比对。"""
    height = min(reference.shape[0], output.shape[0])
    width = min(reference.shape[1], output.shape[1])
    return reference[:height, :width], output[:height, :width]


def report(index, reference, output):
    print("图%-3d %s" % (index, CHARTS[index][1]))
    print("尺寸   ref=%dx%d   out=%dx%d"
          % (reference.shape[1], reference.shape[0],
             output.shape[1], output.shape[0]))
    if reference.shape != output.shape:
        print("       （尺寸不同，按左上角对齐裁到 %dx%d 后比对）"
              % (min(reference.shape[1], output.shape[1]),
                 min(reference.shape[0], output.shape[0])))

    left, right = align(reference, output)
    delta = np.abs(left - right)
    print("平均通道误差 = %.2f / 255      像素近似一致率 = %.2f%%"
          % (delta.mean(), (delta.sum(2) < 12).mean() * 100))

    # 误差热点：32px 分块里误差最大的几块，用来定位没对齐的元素
    error = delta.sum(2)
    block, hotspots = 32, []
    for y in range(0, error.shape[0] - block, block):
        for x in range(0, error.shape[1] - block, block):
            hotspots.append((float(error[y:y + block, x:x + block].mean()), y, x))
    hotspots.sort(reverse=True)
    print("误差热点（32px 分块，前 6）:")
    for value, y, x in hotspots[:6]:
        print("   err=%6.1f  y=%3d x=%3d" % (value, y, x))
    return left, right


def save_diff(index, left, right):
    directory = os.path.join(os.environ.get("TEMP", "."), "chartcmp")
    os.makedirs(directory, exist_ok=True)
    height, width = left.shape[:2]
    canvas = np.full((height, width * 2 + 12, 3), 255, np.uint8)
    canvas[:, :width] = left.astype(np.uint8)
    canvas[:, width + 12:] = right.astype(np.uint8)
    side = os.path.join(directory, "chart%d_side_by_side.png" % index)
    over = os.path.join(directory, "chart%d_overlay.png" % index)
    Image.fromarray(canvas).save(side)
    Image.fromarray(((left * 0.5 + right * 0.5)).astype(np.uint8)).save(over)
    print("对照图已写到 %s" % directory)


def main():
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    reference_path, output_path = CHARTS[index]
    reference, output = load(reference_path), load(output_path)
    left, right = report(index, reference, output)
    if "--diff" in sys.argv:
        save_diff(index, left, right)


if __name__ == "__main__":
    main()
