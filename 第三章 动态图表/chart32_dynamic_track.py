# -*- coding: utf-8 -*-
"""图 32 · 动态跑道图（按月份看 6 个部门的环形占比）。

工作表 2 的 Q5 是月份选择格（当前「4月」），H4:I9 用 VLOOKUP 取该月各部门
人数，J 列占位 = 当月总人数的一半 − 本部门人数。于是每个系列的总和都是
「总人数的一半」，彩色弧长 = 人数 /(总人数/2) × 360°。
holeSize=45、6 层，颜色由内到外为紫/蓝/浅蓝/青/黄/红。

用法：
    python chart32_dynamic_track.py               # 当前 4月
    python chart32_dynamic_track.py --month 2     # 指定月份
    python chart32_dynamic_track.py --gif         # 1~4 月循环
"""

import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

import chartkit as kit

W, H = kit.chart_size(32)
CX, CY = 324.5, 182.5
OUTER_R = 181.0
INNER_R = OUTER_R * 0.45
BANDS = 6
BAND = (OUTER_R - INNER_R) / BANDS

MONTHS = ["1月", "2月", "3月", "4月"]
DEPTS = ["人力部", "行政部", "财务部", "工程部", "采购部", "销售部"]
DATA = {
    "1月": [130, 226, 238, 293, 326, 451],
    "2月": [138, 206, 228, 305, 349, 456],
    "3月": [130, 217, 255, 314, 316, 406],
    "4月": [129, 226, 226, 264, 359, 433],
}
COLORS = ["#7030A0", "#0070C0", "#37A2DA", "#11A7AD", "#F5C353", "#E74E69"]


def render(month):
    values = DATA[month]
    half = sum(values) / 2.0
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for index, (value, color) in enumerate(zip(values, COLORS)):
        sweep = value / half * 360.0
        radius = INNER_R + (index + 1) * BAND
        ax.add_patch(Wedge((CX, CY), radius, -90, sweep - 90, width=BAND,
                           facecolor=color, edgecolor=kit.BACKGROUND,
                           linewidth=3 * 0.72, joinstyle="miter"))

    ax.text(60, 380, "*注：数据来源公司人力资源系统", color="#D9D9D9",
            fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", default="4月", help="1月~4月（也可写 1~4）")
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()
    month = args.month if args.month.endswith("月") else args.month + "月"

    fig = render(month)
    kit.save(fig, "chart32_dynamic_track.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for value in MONTHS:
            fig = render(value)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart32_dynamic_track.gif")


if __name__ == "__main__":
    main()
