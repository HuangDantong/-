# -*- coding: utf-8 -*-
"""图 27 · 簇状柱形折线图（2022 vs 2021 各月销量同比）。

主值轴 0~5000：2022（蓝）与 2021（红）两根柱，overlap=-27%（两柱之间留
27% 柱宽的缝）；次值轴 -110%~30%：黄色增长率折线。右上角的 2022/2021
小方块是 userShapes 里的两个文本框（不是图例）。

绘图区 (67.5, 163.4)~(770.0, 520.5)。柱宽按 gapWidth=219 + 两系列 + 27%
间隙反推：cluster / 4.46 = 26.25px。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

import chartkit as kit

W, H = kit.chart_size(27)
X0, Y1, PW, PH = 67.5, 520.5, 702.5, 357.1

CATS = ["华北", "华南", "东北", "西北", "西南", "华东"]
V2022 = [2354, 1902, 3524, 2698, 2896, 2563]
V2021 = [2021, 1563, 3213, 2531, 2631, 2361]
GROWTH = [0.16, 0.22, 0.10, 0.07, 0.10, 0.09]

BLUE = "#0070C0"
RED = "#E74E69"
YELLOW = "#FFC000"
TEXT = "#F2F2F2"


def value_y(value):
    return Y1 - value / 5000.0 * PH


def percent_y(value):
    return Y1 - (value + 1.1) / 1.4 * PH


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    cluster = PW / len(CATS)
    bar_width = cluster / (2 + 0.27 + 2.19)
    offset = (bar_width + 0.27 * bar_width) / 2.0
    centers = [X0 + (index + 0.5) * cluster for index in range(len(CATS))]

    ax.plot([X0, X0 + PW], [Y1, Y1], color="#454866", linewidth=1.0,
            solid_capstyle="butt")

    for center, v22, v21 in zip(centers, V2022, V2021):
        for x, value, color in [(center - offset, v22, BLUE),
                                (center + offset, v21, RED)]:
            top = value_y(value)
            ax.add_patch(Rectangle((x - bar_width / 2, top), bar_width,
                                   Y1 - top, facecolor=color, edgecolor="none"))
            ax.text(x, top - 10, str(value), color=TEXT,
                    fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                    fontweight="bold", ha="center", va="bottom")

    points = [(center, percent_y(value))
              for center, value in zip(centers, GROWTH)]
    ax.plot([p[0] for p in points], [p[1] for p in points],
            color=YELLOW, linewidth=1.5 * 2 * 0.72, solid_capstyle="round")
    for (x, y), value in zip(points, GROWTH):
        ax.add_patch(Circle((x, y), 5.0, facecolor=YELLOW, edgecolor="none"))
        ax.text(x, y - 16, "%d%%" % round(value * 100), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    for center, name in zip(centers, CATS):
        ax.text(center, 535, name, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")

    # 右上角两个年份小方块（userShapes 文本框）
    for (x0, y0, x1, y1, color, label) in [
            (682, 407, 758, 436, BLUE, "2022"),
            (689, 450, 761, 478, RED, "2021")]:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                               facecolor=kit.BACKGROUND, edgecolor=color,
                               linewidth=1.5 * 0.72))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, label, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                ha="center", va="center")

    ax.text(45, 39, "上半年各月商品销量同比去年情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(45, 96, "2022年相比于2021年销量都有提升，半年整体提升17%",
            color="white", fontsize=12 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    ax.text(38, 578, "*注：数据来源于公司销售系统，统计日期截至2022.06,30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart27_clustered_bar_line.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
