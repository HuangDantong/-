# -*- coding: utf-8 -*-
"""图 26 · 柱形圆（各区域销量与同比）。

红色柱画销量，4500 处一条无连线折线只保留 6 个圆形标记；每个点的标记
在 XML 里单独覆盖了 size（12/25/16/21/18/25），所以圆的大小正好等于
百分比数值（1pt ≈ 2px），百分数就写在圆心上。

绘图区 (66.9, 147.7)~(752.9, 500.8)，值轴 0~5000（值轴本身 delete）。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

import chartkit as kit

W, H = kit.chart_size(26)
X0, Y1, PW, PH = 66.9, 500.8, 686.0, 353.1

CATS = ["华北", "华南", "东北", "西北", "西南", "华东"]
VALUES = [2354, 1902, 3524, 2698, 2896, 2563]
PERCENTS = [12, 25, 16, 21, 18, 25]

RED = "#E74E69"
BLUE = "#0070C0"
TEXT = "#F2F2F2"


def value_y(value):
    return Y1 - value / 5000.0 * PH


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    cluster = PW / len(CATS)
    bar_width = cluster / (1 + 219 / 100.0)
    centers = [X0 + (index + 0.5) * cluster for index in range(len(CATS))]

    for center, value in zip(centers, VALUES):
        top = value_y(value)
        ax.add_patch(Rectangle((center - bar_width / 2, top), bar_width,
                               Y1 - top, facecolor=RED, edgecolor="none"))
        ax.text(center, top - 10, str(value), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    circle_y = value_y(4500)
    for center, percent in zip(centers, PERCENTS):
        radius = percent * kit.PX_PER_PT / 2.0   # size=percent pt → 直径 2×percent px
        ax.add_patch(Circle((center, circle_y), radius,
                            facecolor=BLUE, edgecolor="none"))
        ax.text(center, circle_y, "%d%%" % percent, color="white",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="center")

    for center, name in zip(centers, CATS):
        ax.text(center, 515, name, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")

    ax.text(52, 36, "各区域上半年销量以同比", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(51, 92, "东北区域销量持续保持第一，华东和华南同比去年增长最多",
            color="white", fontsize=11 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    ax.text(36, 550, "*注：数据来源于公司销售系统，统计日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart26_bar_circle.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
