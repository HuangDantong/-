# -*- coding: utf-8 -*-
"""图 36 · VBA 动态玉玦图（近 7 天 / 近 30 天流量来源）。

工作表 6 的两个按钮（Button 1 / Button 2）把 H3 写成「近7天」/「近30天」，
图表数据区 B11:F12 用 VLOOKUP 取对应周期，占位列 = 50% − 占比，于是每个
系列的总和都是 50%，彩色弧长 = 占比 / 50% × 360°。

holeSize=35、4 层，颜色由内到外：00B0F0 / 11A7AD / FFC000 / E74E69。

用法：
    python chart36_vba_jade_ring.py                # 当前 近30天
    python chart36_vba_jade_ring.py --period 7
    python chart36_vba_jade_ring.py --gif
"""

import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

import chartkit as kit

W, H = kit.chart_size(36)
CX, CY = 351.0, 295.0
OUTER_R = 173.0
INNER_R = OUTER_R * 0.35
BANDS = 4
BAND = (OUTER_R - INNER_R) / BANDS

COLORS = ["#00B0F0", "#11A7AD", "#FFC000", "#E74E69"]
DATA = {
    7: [0.13, 0.19, 0.32, 0.36],
    30: [0.09, 0.24, 0.29, 0.38],
}
CENTER_LABELS = ["首页推荐", "关注页面", "搜索", "个人主页"]
PCT_POS = [(388, 265), (440, 285), (465, 325), (447, 409)]


def render(days):
    values = DATA[days]
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for index, (value, color) in enumerate(zip(values, COLORS)):
        sweep = value / 0.5 * 360.0
        radius = INNER_R + (index + 1) * BAND
        ax.add_patch(Wedge((CX, CY), radius, -90, sweep - 90, width=BAND,
                           facecolor=color, edgecolor=kit.BACKGROUND,
                           linewidth=1.5 * 0.72, joinstyle="miter"))
        ax.text(PCT_POS[index][0], PCT_POS[index][1],
                "%d%%" % round(value * 100), color="white",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="left", va="top")

    for top, label in zip([122, 153, 182, 212], CENTER_LABELS):
        ax.text(339, top, label, color="#F2F2F2",
                fontsize=10 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                ha="right", va="top")

    ax.text(184, 42, "流量来源分布", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(46, 497, "*注：数据来源公司网站", color="#D9D9D9",
            fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", default="30", choices=["7", "30"])
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()
    days = int(args.period)

    fig = render(days)
    kit.save(fig, "chart36_vba_jade_ring.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for value in (7, 30):
            fig = render(value)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart36_vba_jade_ring.gif", duration=1200)


if __name__ == "__main__":
    main()
