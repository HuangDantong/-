# -*- coding: utf-8 -*-
"""图 21 · 南丁格尔玫瑰图（PPT 拼图版）。

这一页不是一张图表对象，而是「图表 + 6 个 Freeform 形状」拼出来的：
图表本身只负责 6 条引线，玫瑰花瓣在 drawing11 的 custGeom 里。参考图用
Excel 导出整页后裁到图表区域，因此能同时看到花瓣和引线。

花瓣路径直接从 drawing11.xml 的 `<a:path>` 取出（贝塞尔控制点原样保留），
再按 组合 8 → 组合 6 → 图表框 的变换链换算到 832×622 画布。填充色依次是
红 / 黄 / 青 / 浅蓝 / 蓝 / 紫。
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path

import chartkit as kit

W, H = kit.chart_size(21)

# 每条花瓣在画布上的贝塞尔路径（实测自 drawing11.xml）
PETALS = [
    ("#E74E69", [1, 4, 4, 4, 4, 4, 4, 2, 2],
     [(404.2, 141.4), (534.9, 141.4), (641.0, 243.6), (641.0, 369.7),
      (641.0, 392.3), (637.5, 414.7), (630.7, 436.3), (404.2, 369.7),
      (404.2, 141.4)]),
    ("#F5C353", [1, 4, 4, 4, 2, 2],
     [(581.9, 421.3), (554.6, 507.7), (464.7, 560.9), (372.4, 545.1),
      (404.8, 369.3), (581.9, 421.3)]),
    ("#11A7AD", [1, 4, 4, 4, 2, 2],
     [(379.5, 503.4), (325.9, 494.3), (282.4, 456.4), (267.5, 405.8),
      (404.4, 368.4), (379.5, 503.4)]),
    ("#37A2DA", [1, 4, 4, 4, 2, 2],
     [(296.7, 398.5), (287.7, 367.9), (293.1, 335.1), (311.5, 308.8),
      (404.0, 369.0), (296.7, 398.5)]),
    ("#0070C0", [1, 4, 4, 4, 2, 2],
     [(336.8, 326.2), (347.1, 311.5), (362.1, 300.5), (379.5, 294.9),
      (405.5, 371.1), (336.8, 326.2)]),
    ("#7030A0", [1, 4, 4, 4, 2, 2],
     [(391.7, 332.2), (395.7, 330.9), (400.0, 330.2), (404.3, 330.2),
      (404.3, 369.1), (391.7, 332.2)]),
]

# 与图 19 同一套引线（chart6.xml 的 userShapes）
LEADERS = [
    ((653.9, 773.2, 212.9), (653.1, 213.7, 622.5, 251.9), (622.5, 251.9), "#E74E69"),
    ((596.7, 716.0, 528.2), (596.7, 528.2, 573.7, 491.5), (596.7, 528.2), "#F5C353"),
    ((164.0, 283.3, 497.2), (164.0, 498.0, 133.5, 536.2), (133.5, 536.2), "#11A7AD"),
    ((142.7, 262.0, 356.4), (143.5, 355.6, 112.9, 393.9), (112.9, 393.9), "#0070C0"),
    ((181.4, 338.9, 288.5), (180.7, 288.5, 157.7, 251.8), (157.7, 251.8), "#37A2DA"),
    ((276.0, 395.3, 257.0), (276.0, 257.0, 253.1, 220.3), (253.1, 220.3), "#7030A0"),
]


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    for color, codes, vertices in PETALS:
        ax.add_patch(PathPatch(Path(vertices, codes), facecolor=color,
                               edgecolor="none"))

    for (x0, x1, y), (dx0, dy0, dx1, dy1), dot, color in LEADERS:
        ax.plot([x0, x1], [y, y], color=color, linewidth=1.0, solid_capstyle="butt")
        ax.plot([dx0, dx1], [dy0, dy1], color=color, linewidth=1.0,
                solid_capstyle="butt")
        ax.add_patch(Circle(dot, 3.6, facecolor=color, edgecolor="none"))

    ax.text(49, 44, "2021年各部门人数分布", color="white",
            fontsize=18 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            fontweight="bold", va="top", ha="left")
    ax.text(48, 104, "公司总人数1664，销售部人数最多451，占比29.2%", color="white",
            fontsize=12 * kit.FONT_SCALE, fontfamily=kit.UI_FONT,
            va="top", ha="left")
    ax.text(41, 584, "*注：数据来源于公司人力资源系统，统计日期截至2022.01.01",
            color="#D9D9D9", fontsize=8 * kit.FONT_SCALE,
            fontfamily=kit.UI_FONT, va="top", ha="left")

    kit.save(fig, "chart21_nightingale_ppt.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
