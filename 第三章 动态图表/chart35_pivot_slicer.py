# -*- coding: utf-8 -*-
"""图 35 · 透视表 + 切片器（各部门各学历平均月收入）。

工作表 5 是一张以「学历」为行、月收入平均值为值的数据透视表，切片器「部门」
按 7 个部门筛选。这里直接从 `5 人力资源明细` 的 1470 行原始数据现算
每个部门的学历平均月收入，因此每个切片器状态都能独立复现。

值轴固定 0~10000、主刻度 2500；柱子是 0070C0（顶）→ 00B0F0（底）的竖向
渐变，标签在柱顶外侧，保留两位小数。

用法：
    python chart35_pivot_slicer.py                    # 当前 市场拓展
    python chart35_pivot_slicer.py --dept 销售
    python chart35_pivot_slicer.py --gif              # 7 个部门循环
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

import chartkit as kit

W, H = kit.chart_size(35)
X0, X1 = 55.8, 793.9
Y0, Y1 = 152.0, 475.4

EDUS = ["本科", "博士", "高中", "硕士", "专科"]
DEPTS = ["销售", "行政", "人力资源", "市场拓展", "工程", "后勤", "财务"]
DATA = {
    "销售": [7154.78, 8839.20, 5627.30, 7304.73, 6518.84],
    "行政": [6296.69, 10035.31, 6289.34, 5696.10, 5036.50],
    "人力资源": [6760.56, 4990.33, 2776.60, 9711.13, 4489.07],
    "市场拓展": [6138.32, 7187.00, 5853.63, 6739.01, 6908.04],
    "工程": [None, None, 3468.00, None, None],
    "后勤": [None, None, 2693.00, None, None],
    "财务": [6569.11, 4317.00, 3614.25, 7412.70, 3467.60],
}
TOP_COLOR = np.array([0, 112, 192]) / 255.0
BOTTOM_COLOR = np.array([0, 176, 240]) / 255.0
TEXT = "#F2F2F2"


def render(dept):
    values = DATA[dept]
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    def value_y(value):
        return Y1 - value / 10000.0 * (Y1 - Y0)

    for tick in range(0, 10001, 2500):
        y = value_y(tick)
        ax.plot([X0, X1], [y, y], color="#484B69", linewidth=0.72,
                linestyle=(0, (7, 4)), solid_capstyle="butt")
    ax.plot([X0, X1], [Y1, Y1], color="#484B69", linewidth=0.72,
            solid_capstyle="butt")

    cluster = (X1 - X0) / len(EDUS)
    bar_width = cluster / 3.19
    centers = [X0 + (index + 0.5) * cluster for index in range(len(EDUS))]

    # 竖向渐变：顶部 0070C0 → 底部 00B0F0
    gradient = np.linspace(0, 1, 256)[:, None] * (BOTTOM_COLOR - TOP_COLOR) \
        + TOP_COLOR
    gradient = np.repeat(gradient[:, None, :], 2, axis=1)

    for center, value, name in zip(centers, values, EDUS):
        if value is not None:
            top = value_y(value)
            ax.imshow(gradient, extent=(center - bar_width / 2,
                                        center + bar_width / 2, Y1, top),
                      aspect="auto", interpolation="bilinear", zorder=2)
            ax.add_patch(Rectangle((center - bar_width / 2, top), bar_width,
                                   Y1 - top, facecolor="none",
                                   edgecolor="none"))
            ax.text(center, top - 10, "%.2f" % value, color=TEXT,
                    fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                    fontweight="bold", ha="center", va="bottom")
        ax.text(center, 483, name, color=TEXT, fontsize=10 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="center", va="top")

    ax.text(50, 55, "各学历平均工资情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(40, 537,
            "*注：数据来源于人力资源管理系统，统计日期截至2022.03.31",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dept", default="市场拓展", choices=DEPTS)
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()

    fig = render(args.dept)
    kit.save(fig, "chart35_pivot_slicer.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for dept in DEPTS:
            fig = render(dept)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart35_pivot_slicer.gif", duration=1000)


if __name__ == "__main__":
    main()
