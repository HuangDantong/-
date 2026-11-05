# -*- coding: utf-8 -*-
"""图 23 · 柱形折线图（近六年销售量及增长率）。

主坐标轴 0~6000 画 6 根柱，次坐标轴 -120%~50% 画增长率折线；柱顶与点上方
分别是数值标签，底部是类别和自制图例。

绘图区 manualLayout：x=0.07598, y=0.24882, w=0.84559, h=0.59130，
换算到 832×594 画布即 (63.1, 147.8)~(766.7, 499.0)。柱宽按 gapWidth=219
反推为 36.7px。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

import chartkit as kit

W, H = kit.chart_size(23)
X0, Y0, PW, PH = 63.1, 147.8, 703.6, 351.2
Y1 = Y0 + PH

YEARS = ["2017", "2018", "2019", "2020", "2021", "2022"]
SALES = [1603, 2106, 2406, 3265, 3721, 3921]
GROWTH = [0.27, 0.31378665003119144, 0.14245014245014254,
          0.35702410640066495, 0.1396630934150076, 0.053748992206396062]

BLUE = "#0070C0"
RED = "#E74E69"
TEXT = "#F2F2F2"


def y_value(value):
    return Y1 - value / 6000.0 * PH


def y_percent(value):
    return Y1 - (value + 1.2) / 1.7 * PH


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    cluster = PW / len(YEARS)
    bar_width = cluster / (1 + 219 / 100.0)
    centers = [X0 + (index + 0.5) * cluster for index in range(len(YEARS))]

    for index, (center, value) in enumerate(zip(centers, SALES)):
        top = y_value(value)
        ax.add_patch(Rectangle((center - bar_width / 2, top), bar_width,
                               Y1 - top, facecolor=BLUE, edgecolor="none"))
        # 前 5 根默认外侧标签离柱顶 15px，2022 那根被手工下移（实测 7px）
        label_gap = 3 if index == 5 else 10
        ax.text(center, top - label_gap, str(value), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    points = [(center, y_percent(value)) for center, value in zip(centers, GROWTH)]
    ax.plot([p[0] for p in points], [p[1] for p in points],
            color=RED, linewidth=1.5 * 0.72 * 2, solid_capstyle="round")
    for (x, y), value in zip(points, GROWTH):
        ax.add_patch(Circle((x, y), 4.5, facecolor=RED, edgecolor="none"))
        ax.text(x, y - 15, "%d%%" % round(value * 100), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    for center, year in zip(centers, YEARS):
        ax.text(center, 516, year, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")

    # 自制图例
    ax.add_patch(Rectangle((560, 147), 27, 12, facecolor=BLUE, edgecolor="none"))
    ax.text(590, 153, "销量", color=TEXT, fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, fontweight="bold",
            ha="left", va="center")
    ax.plot([676, 714], [153, 153], color=RED, linewidth=2.16,
            solid_capstyle="round")
    ax.add_patch(Circle((695, 153), 4.5, facecolor=RED, edgecolor="none"))
    ax.text(718, 153, "同比", color=TEXT, fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, fontweight="bold",
            ha="left", va="center")

    ax.text(53, 40, "近六年销售量及增长率", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(52, 96, "平台销量近6年持续增长，但近两年增长率有所放缓", color="white",
            fontsize=11 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(50, 559, "*注：数据来源于公司销售系统", color="#D9D9D9",
            fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")

    kit.save(fig, "chart23_bar_line.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
