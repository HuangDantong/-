# -*- coding: utf-8 -*-
"""图 37 · 动态对比滑珠图（按月份 / 按区域切换视角）。

工作表 8 的选项按钮链接 K2：1=按月份（下拉选月份，图上是 6 个区域），
2=按区域（下拉选区域，图上是 6 个月）。图表数据区 B15:F20 用
IF/VLOOKUP/HLOOKUP 把另一个维度取出来。

每行是一条横向滑珠：蓝色到完成率、灰色（白 30%）补到 100%，完成率处压
一颗白边蓝珠（marker size=15），「32%」写在珠子右侧。

用法：
    python chart37_dynamic_lollipop.py                 # 当前：1月 × 6区域
    python chart37_dynamic_lollipop.py --mode region --index 2
    python chart37_dynamic_lollipop.py --gif           # 6月 + 6区域
"""

import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

import chartkit as kit

W, H = kit.chart_size(37)
X0, X1 = 85.0, 669.0
Y0, Y1 = 136.2, 462.2

REGIONS = ["华北", "华南", "东北", "西北", "西南", "华东"]
MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月"]
RATES = {
    "华北": [0.32, 0.45, 0.66, 0.52, 0.69, 0.7710],
    "华南": [0.49, 0.36, 0.54, 0.39, 0.4150, 0.4030],
    "东北": [0.65, 0.53, 0.58, 0.48, 0.4450, 0.3990],
    "西北": [0.73, 0.63, 0.61, 0.53, 0.4700, 0.4080],
    "西南": [0.536, 0.498, 0.527, 0.708, 0.7035, 0.7580],
    "华东": [0.32, 0.49, 0.65, 0.73, 0.5360, 0.7468],
}
BLUE = "#0070C0"
TRACK_GRAY = "#5F627C"
TEXT = "#F2F2F2"


def render(mode, index):
    if mode == "month":
        rates = [RATES[region][index - 1] for region in REGIONS]
        labels = REGIONS
    else:
        # 按区域模式：mode 是区域名，横轴换成 6 个月
        rates = [RATES[mode][month - 1] for month in range(1, 7)]
        labels = MONTHS

    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    cluster = (Y1 - Y0) / 6.0
    bar_height = 19.0
    # 横向条形图的第一类在最下面
    rows = [Y0 + (5 - i + 0.5) * cluster for i in range(6)]

    def x_of(rate):
        return X0 + rate * (X1 - X0)

    for y, rate, label in zip(rows, rates, labels):
        ax.add_patch(Rectangle((X0, y - bar_height / 2), X1 - X0, bar_height,
                               facecolor=TRACK_GRAY, edgecolor="none"))
        ax.add_patch(Rectangle((X0, y - bar_height / 2), x_of(rate) - X0,
                               bar_height, facecolor=BLUE, edgecolor="none"))
        ax.add_patch(Circle((x_of(rate), y), 15.0, facecolor=BLUE,
                            edgecolor="white", linewidth=1.5 * 0.72))
        ax.text(x_of(rate) + 27, y, "%d%%" % round(rate * 100), color="white",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="left", va="center")
        ax.text(70, y, label, color=TEXT, fontsize=9 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="right", va="center")

    ax.text(40, 34, "2022年上半年区域销量目标达成率情况", color="white",
            fontsize=17.5 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(36, 481, "*注：数据来源公司销售系统,日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="month", choices=["month", "region"])
    parser.add_argument("--index", type=int, default=1)
    parser.add_argument("--region", default="华北", choices=REGIONS)
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()

    if args.mode == "month":
        fig = render("month", args.index)
    else:
        fig = render(args.region, args.index)
    kit.save(fig, "chart37_dynamic_lollipop.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for index in range(1, 7):
            fig = render("month", index)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        for region in REGIONS:
            fig = render(region, 1)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart37_dynamic_lollipop.gif", duration=900)


if __name__ == "__main__":
    main()
