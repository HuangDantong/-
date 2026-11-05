# -*- coding: utf-8 -*-
"""图 25 · 子弹图（销量完成情况）。

三层堆叠背景条画「及格 / 良好 / 优秀」区间（0-600 / 600-800 / 800-1000），
上面盖一根更窄的深蓝实际值柱；目标值用黄色短横线（lineChart 的 dash 标记）。

绘图区 (107.5, 171.4)~(800.7, 490.0)，主值轴 0~1200。区间柱宽 33px
（gapWidth=250），实际柱宽 19.25px（gapWidth=500）。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import chartkit as kit

W, H = kit.chart_size(25)
X0, Y1, PW, PH = 107.5, 490.0, 693.2, 319.0

CATS = ["口红", "面膜", "隔离", "防晒", "精华", "面霜"]
ACTUAL = [653, 523, 648, 856, 714, 785]
TARGET = [700, 500, 600, 900, 600, 600]

BASE = "#82ADD7"
MID = "#0885BC"
TOP = "#0070C0"
ACTUAL_COLOR = "#0E5DFF"
TARGET_COLOR = "#FFC000"
TEXT = "#F2F2F2"


def value_y(value):
    return Y1 - value / 1200.0 * PH


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    cluster = PW / len(CATS)
    range_width = cluster / (1 + 250 / 100.0)
    actual_width = cluster / (1 + 500 / 100.0)
    centers = [X0 + (index + 0.5) * cluster for index in range(len(CATS))]

    ax.plot([X0, X0 + PW], [Y1, Y1], color="#454866", linewidth=1.0,
            solid_capstyle="butt")

    for center in centers:
        for low, high, color in [(0, 600, BASE), (600, 800, MID),
                                 (800, 1000, TOP)]:
            ax.add_patch(Rectangle((center - range_width / 2, value_y(high)),
                                   range_width, value_y(low) - value_y(high),
                                   facecolor=color, edgecolor="none"))

    for center, actual in zip(centers, ACTUAL):
        top = value_y(actual)
        ax.add_patch(Rectangle((center - actual_width / 2, top), actual_width,
                               Y1 - top, facecolor=ACTUAL_COLOR, edgecolor="none"))

    for center, target in zip(centers, TARGET):
        y = value_y(target)
        ax.plot([center - 10, center + 10], [y, y], color=TARGET_COLOR,
                linewidth=4 * 0.72, solid_capstyle="butt")

    for value in range(0, 1201, 200):
        ax.text(90, value_y(value), str(value), color="#BFBFBF",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="right", va="center")

    for center, name in zip(centers, CATS):
        ax.text(center, 505, name, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")

    # 图例
    legend = [(152, BASE, "及格"), (228, MID, "良好"), (300, TOP, "优秀"),
              (370, ACTUAL_COLOR, "实际")]
    for x, color, label in legend:
        ax.add_patch(Rectangle((x, 166), 10, 10, facecolor=color, edgecolor="none"))
        ax.text(x + 15, 171, label, color=TEXT, fontsize=9 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="left", va="center")
    ax.plot([433, 453], [171, 171], color=TARGET_COLOR, linewidth=4 * 0.72,
            solid_capstyle="butt")
    ax.text(458, 171, "目标", color=TEXT, fontsize=9 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, fontweight="bold",
            ha="left", va="center")

    ax.text(54, 36, "2022年上半年各商品销量完成情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(53, 92, "防晒整体销量最好，达到856，面霜远超目标，超额完成30%",
            color="white", fontsize=11 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    ax.text(53, 550, "*注：数据来源于公司销售系统，统计日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart25_bullet.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
