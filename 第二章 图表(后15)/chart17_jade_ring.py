# -*- coding: utf-8 -*-
"""图 17 · 玉玦图（年龄分布四层圆环）。

Excel 的构造：4 个系列各 2 个点（占比 + 占位），doughnut holeSize=35。
每个系列先画「占比」，从 12 点方向顺时针铺开，剩余的「占位」为 noFill，
于是四条彩色弧都从顶部起笔、长度按占比。Doughnut 会把每个系列自身归一化，
所以弧长 = 占比 / (占比 + 占位) × 360°。

圆心、半径、角度均从参考图量得：
  圆心 (420.5, 345.5)，外半径 181，hole=35%（内半径 63.35），
  四条弧端点 88.5° / 148.4° / 209.2° / 269.3°（0° 在 12 点、顺时针）。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

import chartkit as kit

W, H = kit.chart_size(17)
CX, CY = 420.5, 345.5
OUTER_R = 181.0
INNER_R = OUTER_R * 0.35
BANDS = 4
BAND = (OUTER_R - INNER_R) / BANDS

# 由内到外：>=50 / [40,50) / [30,40) / [20,30)
COLORS = ["#37A2DA", "#11A7AD", "#F5C353", "#E74E69"]
ENDS = [0.125 / 0.5 * 360, 0.208333 / 0.5 * 360,
        0.291667 / 0.5 * 360, 0.375 / 0.5 * 360]

TEXT = "#F2F2F2"
FOOT = "#D9D9D9"


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for index, (color, sweep) in enumerate(zip(COLORS, ENDS)):
        radius = INNER_R + (index + 1) * BAND
        # y 轴向下，视觉角度需镜像：从 12 点顺时针 sweep 度
        ax.add_patch(Wedge((CX, CY), radius, -90, sweep - 90, width=BAND,
                           facecolor=color, edgecolor=kit.BACKGROUND,
                           linewidth=1.5 * 0.72, joinstyle="miter"))

    for top, label in zip([170, 200, 230, 261],
                          ["[20,30)", "[30,40)", "[40,50)", ">=50"]):
        ax.text(352, top, label, color=TEXT, fontsize=11 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, va="top", ha="left")

    for (x, y), label in [((237, 316), "37.5%"), ((471, 355), "12.5%"),
                          ((429, 438), "20.8%"), ((320, 439), "29.2%")]:
        ax.text(x, y, label, color=TEXT, fontsize=9 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold", va="top", ha="left")

    ax.text(60, 42, "2022年上半年龄分布", color="white",
            fontsize=20 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(57, 100, "公司平均年龄32.5，23-30员工比例最高", color="white",
            fontsize=14 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(53, 555, "*注：数据来源于公司人力资源系统，统计日期截至2022.06.30",
            color=FOOT, fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")

    kit.save(fig, "chart17_jade_ring.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
