# -*- coding: utf-8 -*-
"""图 31 · 动态柱形图（选月份看 6 大区域销售额）。

工作表 1 的下拉框（Drop Down 1）链接 J3、列表是 B4:B9（1月~6月）；
C13:H13 用 VLOOKUP 把所选月份的一行数据取到图表数据区，图表再读这一行。
因此切换下拉框时，6 根柱子整体换一组数。

用法：
    python chart31_dynamic_column.py                # 当前状态（5月）
    python chart31_dynamic_column.py --month 3      # 指定月份
    python chart31_dynamic_column.py --gif          # 生成 1~6 月循环 GIF
"""

import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import chartkit as kit

W, H = kit.chart_size(31)
X0, X1 = 101.3, 685.7
Y0, Y1 = 149.0, 439.0

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月"]
REGIONS = ["华北", "华南", "东北", "西北", "西南", "华东"]
DATA = {
    "1月": [259, 247, 705, 513, 463, 384],
    "2月": [235, 266, 529, 324, 579, 282],
    "3月": [330, 342, 705, 540, 492, 308],
    "4月": [282, 342, 599, 270, 492, 384],
    "5月": [282, 323, 705, 486, 405, 308],
    "6月": [965, 380, 282, 567, 463, 897],
}
BLUE = "#0097E0"
TEXT = "#F2F2F2"
GRID = "#454866"


def render(month):
    """把指定月份画成一张图，返回 (figure, 值列表)。"""
    values = DATA[month]
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    def value_y(value):
        return Y1 - value / 800.0 * (Y1 - Y0)

    for tick in range(0, 801, 200):
        y = value_y(tick)
        ax.plot([X0, X1], [y, y], color=GRID, linewidth=0.72,
                linestyle=(0, (4, 4)), solid_capstyle="butt")
    ax.plot([X0, X1], [Y1, Y1], color=GRID, linewidth=0.72,
            solid_capstyle="butt")

    for tick in range(0, 801, 200):
        ax.text(80, value_y(tick), str(tick), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="right", va="center")

    cluster = (X1 - X0) / len(REGIONS)
    bar_width = cluster / 2.5
    centers = [X0 + (index + 0.5) * cluster for index in range(len(REGIONS))]
    for center, value, name in zip(centers, values, REGIONS):
        top = value_y(value)
        ax.add_patch(Rectangle((center - bar_width / 2, top), bar_width,
                               Y1 - top, facecolor=BLUE, edgecolor="none"))
        ax.text(center, 454, name, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")

    ax.text(57, 47, "2022年上半年各区域销售情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(56, 497, "*注：数据来源公司销售系统", color="#D9D9D9",
            fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    return fig, values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default="5月",
                        help="1月~6月（也可写 1~6）")
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()
    month = args.month if args.month.endswith("月") else args.month + "月"

    fig, _ = render(month)
    kit.save(fig, "chart31_dynamic_column.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for month in MONTHS:
            fig, _ = render(month)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart31_dynamic_column.gif")


if __name__ == "__main__":
    main()
