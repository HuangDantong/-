# -*- coding: utf-8 -*-
"""图 28 · 复合柱形图（2021 各月化妆品销量走势）。

类别轴其实有 15 个槽位：12 个月 + 每季度后插 1 个空槽。空槽让四个季度的
柱子自然分开：每季度 3 根月柱（宽 17.8px，默认 gapWidth=150），后面跟一根
通栏季度汇总柱（gapWidth=0，宽 44.5px，20% 不透明度），构成深色背景块。

绘图区 (81.5, 103.5)~(750.1, 500.8)，值轴 0~12000。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import chartkit as kit

W, H = kit.chart_size(28)
X0, Y1, PW, PH = 81.5, 500.8, 668.6, 397.3

MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月",
          "7月", "8月", "9月", "10月", "11月", "12月"]
VALUES = [2354, 1902, 3524, 2698, 2896, 2563,
          3156, 2896, 3621, 2635, 2963, 2789]
QUARTER_TOTALS = [7780, 8157, 9673, 8387]
QUARTER_COLORS = ["#4A5BD1", "#FC6C0F", "#F6A50B", "#A2417B"]
TEXT = "#F2F2F2"


def value_y(value):
    return Y1 - value / 12000.0 * PH


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    slot = PW / 15.0
    month_slots = [index + index // 3 for index in range(12)]
    month_centers = [X0 + (slot_index + 0.5) * slot for slot_index in month_slots]
    bar_width = slot / 2.5

    # 季度汇总背景块（先画，压在月柱后面）
    for quarter, (total, color) in enumerate(zip(QUARTER_TOTALS, QUARTER_COLORS)):
        start = quarter * 4
        left = X0 + start * slot
        top = value_y(total)
        ax.add_patch(Rectangle((left, top), 3 * slot, Y1 - top,
                               facecolor=color, alpha=0.20, edgecolor="none"))
        ax.text(left + 1.5 * slot, top - 10, str(total), color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    # 月柱
    for index, (center, value) in enumerate(zip(month_centers, VALUES)):
        top = value_y(value)
        color = QUARTER_COLORS[index // 3]
        ax.add_patch(Rectangle((center - bar_width / 2, top), bar_width,
                               Y1 - top, facecolor=color, edgecolor="none"))
        ax.text(center, top - 10, str(value), color=TEXT,
                fontsize=8 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="bottom")

    for center, name in zip(month_centers, MONTHS):
        ax.text(center, 516, name, color=TEXT,
                fontsize=9 * kit.FONT_SCALE, fontfamily=kit.AXIS_FONTS,
                fontweight="bold", ha="center", va="top")

    ax.text(59, 41, "2021年各月化妆品销量走势", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(58, 97, "2021年第三季度销量最多9673，9月单月销量最大3621",
            color="white", fontsize=11 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")
    ax.text(49, 567, "*注：数据来源于公司销售系统，统计日期截至2021.12.31",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart28_compound_bar.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
