# -*- coding: utf-8 -*-
"""图 22 · 仪表盘图（2022-06-29 运营指数 76）。

三个同心圆环叠出来：
- 系列 0（order=2）蓝色 #0070C0，画最外圈，270° 弧；
- 系列 2（order=1）彩色的 10 段 27°，3 青 + 4 黄 + 3 红；
- 系列 1（order=0）用背景色 #1A1E43，形成内侧暗环和刻度分隔。
白色指针是一条饼图的零宽扇区边界（firstSliceAng=225，70.2° 处）。

实测：圆心 (430.5, 393.5)，外半径 196.5，holeSize=70%，三层各厚 19.65px；
指针从圆心指到 (290, 328)；刻度标签 50..150 打在半径 153 处。
"""

import math

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

import chartkit as kit

W, H = kit.chart_size(22)
CX, CY = 430.5, 393.5
OUTER_R = 196.5
INNER_R = OUTER_R * 0.70
BAND = (OUTER_R - INNER_R) / 3

BLUE = "#0070C0"
TEAL = "#087E8B"
YELLOW = "#FFC54D"
RED = "#F94C66"
SEGMENT_COLORS = [TEAL] * 3 + [YELLOW] * 4 + [RED] * 3
START = 225.0          # 第一个刻度在左下（12 点顺时针 225°）
STEP = 27.0


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    # 最外圈蓝环是整圈（系列 0 把 90° 的空档也填成了蓝色）
    ax.add_patch(Wedge((CX, CY), OUTER_R, 0, 360, width=BAND,
                       facecolor=BLUE, edgecolor="none"))

    # 中间彩色分段环
    for index, color in enumerate(SEGMENT_COLORS):
        start = START + index * STEP
        ax.add_patch(Wedge((CX, CY), INNER_R + 2 * BAND, start - 90,
                           start + STEP - 90, width=BAND,
                           facecolor=color, edgecolor="none"))

    # 刻度分隔线（12 条）
    for index in range(12):
        angle = math.radians(START + index * STEP)
        x_in = CX + INNER_R * math.sin(angle)
        y_in = CY - INNER_R * math.cos(angle)
        x_out = CX + OUTER_R * math.sin(angle)
        y_out = CY - OUTER_R * math.cos(angle)
        ax.plot([x_in, x_out], [y_in, y_out], color=kit.BACKGROUND,
                linewidth=2 * 0.72, solid_capstyle="butt")

    # 刻度标签 50..150（半径 153）
    for index in range(11):
        value = 50 + index * 10
        angle = math.radians(START + index * STEP)
        x = CX + 153 * math.sin(angle)
        y = CY - 153 * math.cos(angle)
        ax.text(x, y, str(value), color="#F2F2F2",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                ha="center", va="center")

    # 指针（76 → 225 + (76-50)/10*27 = 295.2°）
    angle = math.radians(295.2)
    ax.plot([CX, CX + 155 * math.sin(angle)],
            [CY, CY - 155 * math.cos(angle)],
            color="#F2F2F2", linewidth=2.0, solid_capstyle="round")

    ax.text(431.5, 503.0, "76", color="#BFBFBF",
            fontsize=24 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
            ha="center", va="center")

    ax.text(124, 62, "2022年6月29公司整体运营指数良好", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")

    kit.save(fig, "chart22_gauge.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
