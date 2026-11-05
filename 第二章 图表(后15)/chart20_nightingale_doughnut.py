# -*- coding: utf-8 -*-
"""图 20 · 南丁格尔圆环图（年龄段人数分布）。

5 个系列画同一个圆环（同一组 4 个值），但逐系列减少填充的点数：
  系列 0/1 四点全填，系列 2 填 3 点，系列 3 填 2 点，系列 4 只填 1 点。
于是每块的径向厚度不同——紫色铺满 5 层、蓝色 4 层、青色 3 层、黄色 2 层，
形成「逐层减少」的南丁格尔观感。

实测：圆心 (416.5, 375.2)，外半径 180.5，holeSize=60%（内半径 108.3），
5 层每层厚 14.4px；四条引线的端点从参考图逐像素量得。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge

import chartkit as kit

W, H = kit.chart_size(20)
CX, CY = 416.5, 375.2
OUTER_R = 180.5
INNER_R = OUTER_R * 0.60
BANDS = 5
BAND = (OUTER_R - INNER_R) / BANDS

SLICES = [  # (起点, 终点, 颜色)，0° 在 12 点、顺时针
    (0.0, 135.0, "#512DCB"),
    (135.0, 240.0, "#6073F3"),
    (240.0, 315.0, "#66CBDD"),
    (315.0, 360.0, "#F5C353"),
]
FILL_COUNTS = [4, 4, 3, 2, 1]   # 由内到外每层填充的段数

LEADERS = [
    ((165, 291, 191), (291, 191, 317, 225), (317, 225)),   # >=50
    ((645, 769, 221), (645, 221, 615, 256), (615, 256)),   # [20,30)
    ((78, 246, 379), (246, 379, 267, 340), (267, 340)),    # [40,50)
    ((558, 694, 572), (558, 572, 532, 533), (532, 533)),   # [30,40)
]
LABELS = [
    ((240.5, 143), (240.5, 164), ">=50", "12.5%", "#F2F2F2"),
    ((698.5, 180), (698.5, 202), "[20,30)", "37.5%", "#512DCB"),
    ((151.0, 330), (151.0, 352), "[40,50)", "20.8%", "#66CBDD"),
    ((634.5, 524), (634.5, 546), "[30,40)", "29.2%", "#6073F3"),
]


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    leader_colors = ["#F5C353", "#512DCB", "#66CBDD", "#6073F3"]
    for (line, diagonal, dot), color in zip(LEADERS, leader_colors):
        x0, x1, y = line
        ax.plot([x0, x1], [y, y], color=color, linewidth=1.0, solid_capstyle="butt")
        ax.plot([diagonal[0], diagonal[2]], [diagonal[1], diagonal[3]],
                color=color, linewidth=1.0, solid_capstyle="butt")
        ax.add_patch(Circle(dot, 3.6, facecolor=color, edgecolor="none"))

    for band_index, fill_count in enumerate(FILL_COUNTS):
        radius = INNER_R + (band_index + 1) * BAND
        for start, end, color in SLICES[:fill_count]:
            ax.add_patch(Wedge((CX, CY), radius, start - 90, end - 90,
                               width=BAND, facecolor=color,
                               edgecolor=kit.BACKGROUND, linewidth=0.4))

    for (cx, cy_cat), (px, py), category, percent, color in LABELS:
        ax.text(cx, cy_cat, category, color="#F2F2F2",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")
        ax.text(px, py, percent, color=color, fontsize=9 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="center", va="top")

    ax.text(55, 30, "2022年上半各年龄段人数分布", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(54, 86, "公司平均年龄32.5，20-30员工比例最高占比37.5%", color="white",
            fontsize=12 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(53, 586, "*注：数据来源于公司人力资源系统，统计日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart20_nightingale_doughnut.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
