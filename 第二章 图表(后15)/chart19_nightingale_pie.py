# -*- coding: utf-8 -*-
"""图 19 · 南丁格尔圆饼图（2021 年各部门人数占比）。

Excel 里是一个 6 系列叠加的饼图（每多一个系列就多涂一层，用于做「逐层减少」
的南丁格尔效果），导出图上是单层饼 + 6 组「圆点 → 斜线 → 横线」引线。
数据标签在 xlsx 的 Chart.Export 里丢失了，但同一套引线在配套 PPT 截图中带
「部门名 + 占比」，这里按引线端点补回。

实测：圆心 (413.5, 367)，半径 217.5；引线端点全部取自 chart4.xml 的
userShapes（锚框拉伸后）。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge

import chartkit as kit

W, H = kit.chart_size(19)
CX, CY, R = 413.5, 367.0, 217.5

VALUES = [0.292, 0.227, 0.175, 0.136, 0.103, 0.067]
COLORS = ["#E74E69", "#F5C353", "#11A7AD", "#0070C0", "#37A2DA", "#7030A0"]
LABELS = [("销售部", "29.2%"), ("采购部", "22.7%"), ("工程部", "17.5%"),
          ("财务部", "13.6%"), ("行政部", "10.3%"), ("人力部", "6.7%")]

# 每组引线：横线 (x0, x1, y)、斜线两端、圆点位置（全部实测）
LEADERS = [
    ((653.9, 773.2, 212.9), (653.1, 213.7, 622.5, 251.9), (622.5, 251.9)),
    ((596.7, 716.0, 528.2), (596.7, 528.2, 573.7, 491.5), (596.7, 528.2)),
    ((164.0, 283.3, 497.2), (164.0, 498.0, 133.5, 536.2), (133.5, 536.2)),
    ((142.7, 262.0, 356.4), (143.5, 355.6, 112.9, 393.9), (112.9, 393.9)),
    ((181.4, 338.9, 288.5), (180.7, 288.5, 157.7, 251.8), (157.7, 251.8)),
    ((276.0, 395.3, 257.0), (276.0, 257.0, 253.1, 220.3), (253.1, 220.3)),
]


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for index, ((x0, x1, y), (dx0, dy0, dx1, dy1), dot) in enumerate(LEADERS):
        color = COLORS[index]
        ax.plot([x0, x1], [y, y], color=color, linewidth=1.0, solid_capstyle="butt")
        ax.plot([dx0, dx1], [dy0, dy1], color=color, linewidth=1.0,
                solid_capstyle="butt")
        ax.add_patch(Circle(dot, 3.6, facecolor=color, edgecolor="none"))

    start = 0.0
    for value, color in zip(VALUES, COLORS):
        sweep = value * 360
        # y 轴向下，Wedge 角度取 a-90；扇区从 start 顺时针扫到 start+sweep
        ax.add_patch(Wedge((CX, CY), R, start - 90, start + sweep - 90,
                           facecolor=color, edgecolor=color, linewidth=0.6))
        start += sweep

    offsets = [(-54, -33), (-54, -33), (-90, -69), (-60, -38),
               (-100, -76), (-100, -76)]
    for index, ((x0, x1, y), _, _) in enumerate(LEADERS):
        outer_x = x0 if abs(x0 - CX) > abs(x1 - CX) else x1
        category, percent = LABELS[index]
        dy_category, dy_percent = offsets[index]
        ax.text(outer_x - 6, y + dy_category, category, color="#F2F2F2",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                ha="right", va="top")
        ax.text(outer_x - 6, y + dy_percent, percent, color=COLORS[index],
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                ha="right", va="top")

    ax.text(54, 32, "2021年各部门人数分布", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(53, 88, "公司总人数1664，销售部人数最多451，占比29.2%", color="white",
            fontsize=12 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(54, 555, "*注：数据来源于公司人力资源系统，统计日期截至2022.01.01",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart19_nightingale_pie.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
