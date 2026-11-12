# -*- coding: utf-8 -*-
"""第四章 人力资源可视化看板 · Python / matplotlib 复刻

原文件《第四章 人力资源可视化看板.xlsx》的「202203人员基础信息」工作表右侧
是一张 2×3 的人员结构看板：年龄、性别、婚姻状况三个圆环，学历、部门两个
横向条形图，以及入转调柱形图。这里按原图的画布尺寸 (1598 × 808 px) 逐块
重绘，人数直接从工作表的统计区读取。

用法：
    python dashboard.py
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第四章 人力资源可视化看板.xlsx")

W, H = 1598, 808
DPI = 100

C_OUTER = "#2C3A79"        # 看板外框
C_PANEL = "#1D2349"        # 六个图表面板
C_TEXT = "#F2F2F2"
C_WHITE = "#FFFFFF"
C_LBLUE = "#7AD5FE"        # 条形图 / 圆环浅蓝
C_ORANGE = "#EDA530"
C_BLUE = "#0070C0"
C_BLUE2 = "#00B0F0"
C_ORANGE2 = "#ED7D31"

FONT = "Microsoft YaHei"
plt.rcParams["font.family"] = FONT
plt.rcParams["axes.unicode_minus"] = False


def fs(excel_pt):
    """Excel 字号 -> matplotlib 字号。

    看板图里 1 Excel pt 约渲染成 2.78 px；matplotlib 的 1pt = 100/72 px，
    所以字号直接乘 2.0 即可对齐。
    """
    return excel_pt * 2.0


# ---------------------------------------------------------------------------
# 数据：读取工作簿统计区（J/K 与 M/N 列）
# ---------------------------------------------------------------------------

def load_data():
    # 仓库内附带了统计结果 data/summary.json，没有课程 xlsx 也能运行
    summary = os.path.join(BASE, "data", "summary.json")
    if not os.path.exists(XLSX) and os.path.exists(summary):
        with open(summary, encoding="utf-8") as handle:
            return json.load(handle)

    from openpyxl import load_workbook

    wb = load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb.active

    def col(letter, first, last):
        return [ws["%s%d" % (letter, r)].value for r in range(first, last + 1)]

    return {
        "total": ws["N2"].value,
        "age": {"labels": col("J", 11, 15), "values": col("K", 11, 15)},
        "gender": {"labels": col("J", 19, 20), "values": col("K", 19, 20)},
        "education": {"labels": col("J", 24, 28), "values": col("K", 24, 28)},
        "marriage": {"labels": col("M", 11, 13), "values": col("N", 11, 13)},
        "join": {"labels": col("M", 17, 19), "values": col("N", 17, 19)},
        "department": {"labels": col("M", 24, 29), "values": col("N", 24, 29)},
    }


# ---------------------------------------------------------------------------
# 绘制部件
# ---------------------------------------------------------------------------

def text(ax, x, y, s, size, color=C_TEXT, weight="normal", ha="center",
         va="center", zorder=10):
    return ax.text(x, y, s, fontsize=fs(size), color=color, weight=weight,
                   ha=ha, va=va, zorder=zorder)


def ring_arcs(ax, cx, cy, r, width, fractions, colors, zorder=4):
    """从 12 点方向顺时针画圆环扇区（y 轴向下，角度做镜像）。"""
    angle = -90.0
    for fraction, color in zip(fractions, colors):
        ax.add_patch(Wedge((cx, cy), r, angle, angle + 360.0 * fraction,
                           width=width, facecolor=color, edgecolor="none",
                           zorder=zorder))
        angle += 360.0 * fraction


def doughnut(ax, panel, chart, colors, pct_labels, legend, labels, title_xy):
    x0, y0, w, h = panel
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=C_PANEL,
                           edgecolor="none", zorder=1))
    text(ax, title_xy[0], title_xy[1], chart["title"], 10, weight="bold")

    cx, cy, r = chart["cx"], chart["cy"], chart["r"]
    values = chart["values"]
    total = sum(values)
    ring_arcs(ax, cx, cy, r, r * 0.25,
              [v / total for v in values], colors, zorder=3)

    for (lx, ly), s in pct_labels:
        text(ax, lx, ly, s, 7)

    marker_x, marker_ys = legend
    for ly, name, color in zip(marker_ys, labels, colors):
        ax.add_patch(Rectangle((marker_x, ly - 5), 11, 10, facecolor=color,
                               edgecolor="none", zorder=4))
        text(ax, marker_x + 16, ly, name, 7, ha="left")


def hbar(ax, panel, title_xy, bars, values, labels, colors=C_LBLUE,
         bar_h=17):
    """横向条形图：bars=(起点x, 行中心ys, 缩放px/单位, 值文字x偏移)。"""
    x0, y0, w, h = panel
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=C_PANEL,
                           edgecolor="none", zorder=1))
    text(ax, title_xy[0], title_xy[1], title_xy[2], 10, weight="bold")

    left, ys, scale, value_gap = bars
    for yy, value, name in zip(ys, values, labels):
        length = value * scale
        ax.add_patch(Rectangle((left, yy - bar_h / 2), max(length, 2), bar_h,
                               facecolor=colors, edgecolor="none", zorder=3))
        text(ax, left - 22, yy, name, 7, ha="right")
        text(ax, left + length + value_gap, yy, str(value), 7, ha="left")


# ---------------------------------------------------------------------------
# 整张看板
# ---------------------------------------------------------------------------

def render(data):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(C_OUTER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_facecolor(C_OUTER)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, H, facecolor=C_OUTER,
                           edgecolor="none", zorder=0))

    text(ax, 798, 46.5, "公司人员结构看板", 14, color=C_TEXT, weight="bold")

    # 六个面板：上排 年龄 / 性别 / 婚姻，下排 学历 / 入转调 / 部门
    P1, P2, P3 = (30, 86, 481, 273), (548, 86, 490, 273), (1075, 86, 480, 273)
    P4, P5, P6 = (33, 387, 481, 388), (546, 387, 490, 388), (1074, 387, 480, 388)

    age = data["age"]
    doughnut(ax, P1, {
        "title": "年龄", "cx": 215, "cy": 258, "r": 56.5,
        "values": age["values"],
    }, [C_BLUE2, C_ORANGE2, C_LBLUE, C_ORANGE, C_BLUE],
        [((237, 176), "7%"), ((289, 210), "16%"), ((295, 298), "22%"),
         ((184, 330), "20%"), ((130, 219), "35%")],
        (403, [170.5, 209, 247.5, 286, 324]), age["labels"],
        (270.5, 133))

    gender = data["gender"]
    doughnut(ax, P2, {
        "title": "性别", "cx": 754.5, "cy": 258, "r": 56.5,
        "values": gender["values"],
    }, [C_ORANGE, C_BLUE],
        [((842, 297), "60%"), ((666, 225), "40%")],
        (975, [237, 279]), gender["labels"], (792, 133))

    marriage = data["marriage"]
    doughnut(ax, P3, {
        "title": "婚姻状况", "cx": 1266.5, "cy": 258.5, "r": 56.5,
        "values": marriage["values"],
    }, [C_ORANGE, C_BLUE, C_LBLUE],
        [((1360, 216), "32%"), ((1217, 334), "46%"), ((1195, 197), "22%")],
        (1473, [216, 258, 300]), marriage["labels"], (1314.5, 133))

    edu = data["education"]
    hbar(ax, P4, (273.5, 434.5, "学历"),
         (168, [515, 566, 617, 668, 718.5], 226 / 572.0, 12),
         edu["values"][::-1], edu["labels"][::-1], bar_h=17)

    dep = data["department"]
    hbar(ax, P6, (1313, 435, "部门"),
         (1209, [511, 553.5, 595.5, 637.5, 680.5, 723], 251 / 799.0, 12),
         dep["values"][::-1], dep["labels"][::-1], bar_h=14)

    # 入转调：柱形图 + 顶部总人数
    ax.add_patch(Rectangle((P5[0], P5[1]), P5[2], P5[3], facecolor=C_PANEL,
                           edgecolor="none", zorder=1))
    text(ax, 802, 442.5, "总人数：%d" % data["total"], 11, color=C_WHITE,
         weight="bold")
    text(ax, 800, 505, "入转调", 10, weight="bold")
    join = data["join"]
    centers = [648.5, 790.5, 933.5]
    baseline = 714
    for cx, value, name in zip(centers, join["values"], join["labels"]):
        top = baseline - value * 3.475
        ax.add_patch(Rectangle((cx - 22, top), 44, baseline - top,
                               facecolor=C_LBLUE, edgecolor="none", zorder=3))
        text(ax, cx, top - 29, str(value), 7)
        text(ax, cx, 746.5, name, 7)

    return fig


def main():
    fig = render(load_data())
    path = os.path.join(BASE, "dashboard.png")
    fig.savefig(path, dpi=DPI, facecolor=C_OUTER)
    print("saved:", path)


if __name__ == "__main__":
    main()
