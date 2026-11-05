# -*- coding: utf-8 -*-
"""图 30 · 对比滑珠图（2022 vs 2021 目标达成率）。

一根蓝色进度条 + 灰色剩余轨道（宽 13px 的胶囊），上面两颗滑珠：蓝珠是
2022 完成率、灰珠是 2021 完成率（scatter marker size=10）。完成率数字写在
蓝珠正上方。

实测：轨道 0%→124px、100%→660px；条中心 y=197/270.5/344.5/418.5/492.5；
图例用两个带白边的圆点 + 11pt 文字。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

import chartkit as kit

W, H = kit.chart_size(30)
X_ZERO, X_ONE = 124.0, 660.0
BAR_Y = [197.0, 270.5, 344.5, 418.5, 492.5]
CATS = ["华南", "华北", "东北", "西北", "华东"]
RATE_2022 = [0.86, 0.74, 0.62, 0.51, 0.35]
RATE_2021 = [0.92, 0.69, 0.53, 0.39, 0.45]
TRACK_HEIGHT = 13.0

BLUE = "#0070C0"
GRAY_TRACK = "#717389"
GRAY_BEAD = "#A6A6A6"
TEXT = "#F2F2F2"


def x_of(rate):
    return X_ZERO + rate * (X_ONE - X_ZERO)


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    radius = TRACK_HEIGHT / 2.0
    for y, r22, r21, cat in zip(BAR_Y, RATE_2022, RATE_2021, CATS):
        ax.plot([X_ZERO + radius, X_ONE - radius], [y, y], color=GRAY_TRACK,
                linewidth=TRACK_HEIGHT * 0.72, solid_capstyle="round")
        ax.plot([X_ZERO + radius, x_of(r22)], [y, y], color=BLUE,
                linewidth=TRACK_HEIGHT * 0.72, solid_capstyle="round")
        ax.add_patch(Circle((x_of(r21), y), 9.5, facecolor=GRAY_BEAD,
                            edgecolor="white", linewidth=1.5 * 0.72))
        ax.add_patch(Circle((x_of(r22), y), 9.5, facecolor=BLUE,
                            edgecolor="white", linewidth=1.5 * 0.72))
        ax.text(x_of(r22), y - 16, "%d%%" % round(r22 * 100), color="white",
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")
        ax.text(105, y, cat, color=TEXT, fontsize=9 * kit.FONT_SCALE,
                fontfamily=kit.AXIS_FONTS, fontweight="bold",
                ha="right", va="center")

    # 图例
    ax.add_patch(Circle((73.5, 152), 9.5, facecolor=BLUE,
                        edgecolor="white", linewidth=1.5 * 0.72))
    ax.text(92, 152, "2022完成率", color=TEXT, fontsize=9 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, ha="left", va="center")
    ax.add_patch(Circle((179, 152), 9.5, facecolor=GRAY_BEAD,
                        edgecolor="white", linewidth=1.5 * 0.72))
    ax.text(196, 152, "2021完率", color=TEXT, fontsize=9 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, ha="left", va="center")

    ax.text(60, 42, "2022年上半年销量目标达成率同比去年情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(59, 98, "华南完成率最高达到86%，华东最低35%，其中华南和华东不及2021年",
            color="white", fontsize=11 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    ax.text(69, 553, "*注：数据来源于公司销售系统，统计日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart30_compare_lollipop.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
