# -*- coding: utf-8 -*-
"""图 24 · 目标柱形图（各商品销量完成情况）。

两个柱形系列叠在同一绘图区：目标系列 noFill + 灰描边（宽 29.8px），实际系列
蓝色实心（宽 21.7px），前者被后者盖住中间，只剩两侧的「目标框」。数值轴
0~1000，绘图区 (63.2, 155.6)~(778.8, 475.6)。

口红、防晒两个标签在 XML 里被手工上移，实测离柱顶分别是 27px / 25px，
其余四个是 15px。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import chartkit as kit

W, H = kit.chart_size(24)
X0, Y0, PW, PH = 63.2, 155.6, 715.6, 320.0
Y1 = Y0 + PH

CATS = ["口红", "面膜", "隔离", "防晒", "精华", "面霜"]
ACTUAL = [653, 523, 648, 856, 714, 785]
TARGET = [700, 500, 600, 900, 600, 600]
LABEL_GAPS = [27, 15, 15, 25, 15, 14]

BLUE = "#0070C0"
OUTLINE = "#86889A"
TEXT = "#F2F2F2"


def value_y(value):
    return Y1 - value / 1000.0 * PH


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    cluster = PW / len(CATS)
    target_width = cluster / (1 + 300 / 100.0)
    actual_width = cluster / (1 + 450 / 100.0)
    centers = [X0 + (index + 0.5) * cluster for index in range(len(CATS))]

    ax.plot([X0, X0 + PW], [Y1, Y1], color="#152E5C", linewidth=2.0,
            solid_capstyle="butt")

    for center, target, actual, gap in zip(centers, TARGET, ACTUAL, LABEL_GAPS):
        top = value_y(target)
        ax.add_patch(Rectangle((center - target_width / 2, top), target_width,
                               Y1 - top, facecolor="none", edgecolor=OUTLINE,
                               linewidth=1.5 * 0.72))
        top = value_y(actual)
        ax.add_patch(Rectangle((center - actual_width / 2, top), actual_width,
                               Y1 - top, facecolor=BLUE, edgecolor="none"))
        ax.text(center, top - gap + 5, str(actual), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    for center, name in zip(centers, CATS):
        ax.text(center, 490, name, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                ha="center", va="top")

    # 图例（Excel 图例被排到绘图区上方）
    ax.add_patch(Rectangle((87, 149), 11, 11, facecolor="none",
                           edgecolor=OUTLINE, linewidth=1.2))
    ax.text(105, 154.5, "目标销量", color=TEXT, fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, ha="left", va="center")
    ax.add_patch(Rectangle((178, 149), 11, 11, facecolor=BLUE, edgecolor="none"))
    ax.text(195, 154.5, "实际销量", color=TEXT, fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.AXIS_FONTS, ha="left", va="center")

    ax.text(63, 39, "2022年上半年各商品销量完成情况", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(63, 95, "防晒整体销量最好，达到856，面霜远超目标，超额完成30%",
            color="white", fontsize=11 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    ax.text(61, 548, "*注：数据来源于公司销售系统，统计日期截至2022.06.30",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart24_target_bar.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
