# -*- coding: utf-8 -*-
"""图 18 · 跑道图（各部门人数六层圆环）。

与图 17 同一套构造：6 个系列各 2 个点（人数 + 占位 = 832），holeSize=45，
每条弧从 12 点方向顺时针铺开，弧长 = 人数 / 832 × 360°。

实测：圆心 (373.5, 356.5)，外半径 200.5，内半径 90.2，环带厚 18.4px，
环边线 3pt（6px）深色分隔。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

import chartkit as kit

W, H = kit.chart_size(18)
CX, CY = 373.5, 356.5
OUTER_R = 202.0
INNER_R = OUTER_R * 0.45
BANDS = 6
BAND = (OUTER_R - INNER_R) / BANDS

VALUES = [130, 226, 238, 293, 326, 451]
TOTAL = 832.0
COLORS = ["#7030A0", "#0070C0", "#37A2DA", "#11A7AD", "#F5C353", "#E74E69"]
LABELS = ["销售部 451", "采购部 326", "工程部 293",
          "财务部 238", "行政部 226", "人力部 130"]

TEXT = "#F2F2F2"
FOOT = "#D9D9D9"


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for index, (color, value) in enumerate(zip(COLORS, VALUES)):
        sweep = value / TOTAL * 360
        radius = INNER_R + (index + 1) * BAND
        # y 轴向下，视觉角度需镜像：从 12 点顺时针 sweep 度
        ax.add_patch(Wedge((CX, CY), radius, -90, sweep - 90, width=BAND,
                           facecolor=color, edgecolor=kit.BACKGROUND,
                           linewidth=3 * kit.PX_PER_PT * 0.72, joinstyle="miter"))

    for top, label in zip([156, 175, 193, 211, 229, 247], LABELS):
        ax.text(301, top, label, color=TEXT, fontsize=7 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, va="top", ha="left")

    ax.text(57, 46, "2022年上半年各部门人数", color="white",
            fontsize=20 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(56, 104, "公司总人数1664，销售部人数最多451，占比27%", color="white",
            fontsize=14 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(40, 582, "*注：数据来源于公司人力资源系统，统计日期截止2022.06.30",
            color=FOOT, fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")

    kit.save(fig, "chart18_track_rings.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
