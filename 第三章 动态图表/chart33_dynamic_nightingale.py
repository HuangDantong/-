# -*- coding: utf-8 -*-
"""图 33 · 动态南丁格尔圆环图（近 7 天 / 近 30 天的流量来源）。

6 个系列叠成同心圆环，每个系列越往外少填一个点，形成层叠的玫瑰效果；
最外层系列的每个点带「类目, 占比」数据标签和引线。

工作表 3 的两个选项按钮链接 I3（1=近7天，2=近30天），图表数据区用
HLOOKUP 取对应一行。

用法：
    python chart33_dynamic_nightingale.py             # 当前 近7天
    python chart33_dynamic_nightingale.py --period 30
    python chart33_dynamic_nightingale.py --gif
"""

import argparse

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge

import chartkit as kit

W, H = kit.chart_size(33)
CX, CY = 369.5, 307.0
OUTER_R = 160.9
INNER_R = OUTER_R * 0.52
BANDS = 6
BAND = (OUTER_R - INNER_R) / BANDS

CATS = ["首页推荐", "关注页面", "搜索", "个人主页", "其他来源"]
COLORS = ["#4A5BD1", "#6073F3", "#11A7AD", "#FFC000", "#E66B4C"]
DATA = {
    7: [0.44, 0.17, 0.15, 0.08, 0.16],
    30: [0.38, 0.21, 0.15, 0.09, 0.17],
}
FILL_COUNTS = [5, 5, 4, 3, 2, 1]
STARTS = [0.0]
for value in DATA[7][:-1]:
    STARTS.append(STARTS[-1] + value * 360)

# 标签锚点（实测）：类目左端、百分比左端
LABELS = [
    ((565, 186), (649, 186)),
    ((407, 475), (491, 475)),
    ((134, 391), (190, 391)),
    ((124, 217), (200, 217)),
    ((166, 151), (250, 151)),
]
# 引线：圆点 → 折点 → 横线终点（实测）
LEADERS = [
    ((526, 225), (555, 188), (662, 188)),
    ((426, 481), (447, 517), (549, 517)),
    ((260, 420), (222, 450), (115, 450)),
    ((240, 290), (209, 257), (108, 257)),
    ((283, 215), (268, 173), (159, 173)),
]


def render(days):
    values = DATA[days]
    sweeps = [value * 360 for value in values]
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for band_index, fill_count in enumerate(FILL_COUNTS):
        radius = INNER_R + (band_index + 1) * BAND
        for point in range(fill_count):
            start = sum(sweeps[:point])
            ax.add_patch(Wedge((CX, CY), radius, start - 90,
                               start + sweeps[point] - 90, width=BAND,
                               facecolor=COLORS[point],
                               edgecolor=COLORS[point], linewidth=0.3))

    # 环带之间只留一圈很淡的分隔线
    for index in range(1, BANDS):
        ax.add_patch(Circle((CX, CY), INNER_R + index * BAND, facecolor="none",
                            edgecolor=kit.BACKGROUND, linewidth=0.5, alpha=0.55))

    for color, (dot, elbow, end) in zip(COLORS, LEADERS):
        ax.plot([dot[0], elbow[0]], [dot[1], elbow[1]], color=color,
                linewidth=1.0, solid_capstyle="butt")
        ax.plot([elbow[0], end[0]], [elbow[1], end[1]], color=color,
                linewidth=1.0, solid_capstyle="butt")
        ax.add_patch(Circle(dot, 3.2, facecolor=color, edgecolor="none"))

    for (cat_xy, pct_xy), cat, color, value in zip(LABELS, CATS, COLORS, values):
        ax.text(cat_xy[0], cat_xy[1], cat + ",", color="#F2F2F2",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="left", va="top")
        ax.text(pct_xy[0], pct_xy[1], "%d%%" % round(value * 100), color=color,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="left", va="top")

    ax.text(54, 47, "2022年6月30日流量来源分布", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(44, 514, "*注：数据来源公司网站", color="#D9D9D9",
            fontsize=8 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", default="7", choices=["7", "30"])
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()
    days = int(args.period)

    fig = render(days)
    kit.save(fig, "chart33_dynamic_nightingale.png")
    plt.close(fig)

    if args.gif:
        frames = []
        for value in (7, 30):
            fig = render(value)
            frames.append(kit.to_image(fig))
            plt.close(fig)
        kit.save_gif(frames, "chart33_dynamic_nightingale.gif", duration=1200)


if __name__ == "__main__":
    main()
