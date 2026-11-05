# -*- coding: utf-8 -*-
"""图 34 · 动态组合图（勾选销售额 / 利润 / 利润率）。

工作表 4 的三个复选框链接 C13/D13/E13；图表数据区 B17:F20 用
IF(勾选, 原值, 负哨兵) 隐藏系列（销售额 -100、利润 -200、利润率 -2），
负值落在坐标轴之外，于是整个系列消失。

主值轴 0~4000 画两组柱：销售额（蓝）与利润（红），标签在柱内顶部；
次值轴 -100%~100% 画利润率折线（黄），标签在折线上方。

用法：
    python chart34_dynamic_combo.py                     # 三个系列全开
    python chart34_dynamic_combo.py --hide profit       # 隐藏利润
    python chart34_dynamic_combo.py --gif               # 8 种组合循环
"""

import argparse
import itertools

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import chartkit as kit

W, H = kit.chart_size(34)
X0, X1 = 35.6, 786.9
Y0, Y1 = 147.6, 490.0

CATS = ["口红", "面膜", "隔离", "粉底液"]
SALES = [2800, 2564, 2282, 2353]
PROFIT = [1896, 1563, 986, 1324]
RATE = [0.6771428571428572, 0.609594383775351,
        0.43207712532865905, 0.5626859328516787]

BLUE = "#0070C0"
RED = "#E74E69"
YELLOW = "#FFC000"
TEXT = "#F2F2F2"


def render(show_sales=True, show_profit=True, show_rate=True):
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    def value_y(value):
        return Y1 - value / 4000.0 * (Y1 - Y0)

    def rate_y(value):
        return Y1 - (value + 1.0) / 2.0 * (Y1 - Y0)

    ax.plot([X0, X1], [Y1, Y1], color="#454866", linewidth=0.72,
            solid_capstyle="butt")

    cluster = (X1 - X0) / len(CATS)
    bar_width = cluster / (2 + 0.27 + 2.19)
    offset = (bar_width + 0.27 * bar_width) / 2.0
    centers = [X0 + (index + 0.5) * cluster for index in range(len(CATS))]

    for center, sales, profit in zip(centers, SALES, PROFIT):
        series = [(center - offset, sales, BLUE, show_sales),
                  (center + offset, profit, RED, show_profit)]
        for x, value, color, visible in series:
            if not visible:
                continue
            top = value_y(value)
            ax.add_patch(Rectangle((x - bar_width / 2, top), bar_width,
                                   Y1 - top, facecolor=color, edgecolor="none"))
            ax.text(x, top + 5, str(value), color="white",
                    fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                    fontweight="bold", ha="center", va="top")

    if show_rate:
        points = [(center, rate_y(value)) for center, value in zip(centers, RATE)]
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=YELLOW, linewidth=1.5 * 2 * 0.72, solid_capstyle="round")
        for (x, y), value in zip(points, RATE):
            ax.text(x, y - 14, "%d%%" % round(value * 100), color=TEXT,
                    fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                    fontweight="bold", ha="center", va="bottom")

    for center, name in zip(centers, CATS):
        ax.text(center, 506, name, color=TEXT, fontsize=10 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="center", va="top")

    ax.text(68, 42, "2022年化妆品销售情况", color="white",
            fontsize=19 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(59, 555, "*注：数据来源公司销售系统", color="#D9D9D9",
            fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hide", nargs="*", default=[],
                        choices=["sales", "profit", "rate"])
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()

    states = {"sales": True, "profit": True, "rate": True}
    for name in args.hide:
        states[name] = False

    fig = render(show_sales=states["sales"], show_profit=states["profit"], show_rate=states["rate"])
    kit.save(fig, "chart34_dynamic_combo.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for sales, profit, rate in itertools.product([False, True], repeat=3):
            fig = render(show_sales=sales, show_profit=profit, show_rate=rate)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart34_dynamic_combo.gif", duration=900)


if __name__ == "__main__":
    main()
