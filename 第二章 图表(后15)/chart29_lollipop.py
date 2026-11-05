# -*- coding: utf-8 -*-
"""图 29 · 滑珠图（产品销量目标达成率）。

两根横向堆积条拼成「轨道 + 进度」：蓝色到完成率，灰色占到 100%，都是
30px 高的圆头胶囊（series 用图片填充，导出后是纯色）。完成率位置再压一个
白边蓝心的圆珠（scatter marker size=15）。

实测：轨道 0%→136px、100%→611px，条中心 y=188/262/336/410/484，
胶囊高 30px，圆珠半径 16px。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

import chartkit as kit

W, H = kit.chart_size(29)
X_ZERO, X_ONE = 136.0, 611.0
BAR_Y = [188, 262, 336, 410, 484]
CATS = ["华南", "华北", "东北", "西北", "华东"]
RATES = [0.86, 0.74, 0.62, 0.51, 0.35]
TRACK_HEIGHT = 30.0

BLUE = "#0070C0"
GRAY = "#717389"
TEXT = "#F2F2F2"


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    radius = TRACK_HEIGHT / 2.0
    for y, rate, cat in zip(BAR_Y, RATES, CATS):
        end = X_ZERO + rate * (X_ONE - X_ZERO)
        ax.plot([X_ZERO + radius, X_ONE - radius], [y, y], color=GRAY,
                linewidth=TRACK_HEIGHT * 0.72, solid_capstyle="round")
        ax.plot([X_ZERO + radius, end], [y, y], color=BLUE,
                linewidth=TRACK_HEIGHT * 0.72, solid_capstyle="round")
        ax.add_patch(Circle((end, y), 16.5, facecolor=BLUE,
                            edgecolor="white", linewidth=2.0 * 0.72))
        ax.text(end - 20, y, "%d%%" % round(rate * 100), color="white",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="right", va="center")
        ax.text(118, y, cat, color=TEXT, fontsize=9 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="right", va="center")

    ax.text(65, 36, "2022年上半年产品销量目标达成率情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(64, 92, "华南完成率最高达到86%，华东最低35%", color="white",
            fontsize=11 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(65, 551, "*注：数据来源于公司销售系统，统计日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart29_lollipop.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
