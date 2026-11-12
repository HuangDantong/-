# -*- coding: utf-8 -*-
"""第四章 销售看板 · Python / matplotlib 复刻

原文件《第四章 销售看板参考.xlsx》的「数据大屏」工作表由 11 张图表、若干
矩形/文本框、一个图标和一个月份下拉框拼成。这里按原图的画布尺寸
(1724 × 1088 px) 逐块重绘，并用「销售明细」「成本明细」两张原始数据表
现算所有指标，因此和 Excel 一样，换个月份整张看板都会跟着变。

用法：
    python dashboard.py                 # 默认 9 月（与原文件 C2=9 一致）
    python dashboard.py --month 3       # 指定 1~12 月
    python dashboard.py --gif           # 生成 12 个月循环 GIF
"""

import argparse
import io
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle, Wedge
from PIL import Image

# ---------------------------------------------------------------------------
# 常量：颜色、画布、字体
# ---------------------------------------------------------------------------

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第四章 销售看板参考.xlsx")

W, H = 1724, 1088          # 看板画布（px，1px = 0.5pt；与 Excel 导出图一致）
DPI = 100

C_BG = "#1A1E43"           # 页面底色
C_PANEL = "#2C3560"        # 面板 / 图表区底色
C_TEXT = "#F2F2F2"         # 图表文字（bg1 lum95%）
C_WHITE = "#FFFFFF"
C_BLUE = "#7BBDD5"         # 浅蓝：区域柱、KPI 环、9 月环比条
C_PINK = "#FC6C9D"         # 粉色：快递柱、办公用品、利润弧
C_INDIGO = "#4A5BD1"       # 靛蓝：家具产品、Top3 高亮块、占比条
C_ORANGE = "#F6A576"       # 橙色：数码电子
C_GRAY = "#535A7D"         # 圆环剩余部分（bg1 20% 叠在面板上）
C_DARKBLUE = "#4454BA"     # 8 月环比条

FONT = "Microsoft YaHei"
plt.rcParams["font.family"] = FONT
plt.rcParams["axes.unicode_minus"] = False


def fs(excel_pt):
    """Excel 字号 -> matplotlib 字号（导出比例 2px/pt，100dpi）。"""
    return excel_pt * 2 * 72 / DPI


# ---------------------------------------------------------------------------
# 数据：直接从工作簿现算（对应 Excel 里的 COUNTIFS / SUMIFS）
# ---------------------------------------------------------------------------

MONTHS = ["%d月" % i for i in range(1, 13)]
REGIONS = ["华北", "华南", "东北", "西北", "西南", "华东"]
COURIERS = ["顺丰", "韵达", "中通", "申通", "圆通", "EMS"]
CATEGORIES = ["办公用品", "家具产品", "数码电子"]
COST_ORDER = ["推广", "其他", "人工", "产品"]   # 与 D27:D30 一致


def load_data():
    from openpyxl import load_workbook

    wb = load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["销售明细"]

    sales = {m: 0.0 for m in MONTHS}
    profit = {m: 0.0 for m in MONTHS}
    qty = {m: 0 for m in MONTHS}
    by_region = {m: defaultdict(int) for m in MONTHS}
    by_courier = {m: defaultdict(int) for m in MONTHS}
    by_category = {m: defaultdict(int) for m in MONTHS}
    by_product = {m: defaultdict(lambda: [0.0, 0]) for m in MONTHS}

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        amount = row[4] or 0.0
        prof = row[6] or 0.0
        region, courier, category, product, month = row[2], row[3], row[7], row[8], row[9]
        if month not in sales:
            continue
        sales[month] += amount
        profit[month] += prof
        qty[month] += 1
        by_region[month][region] += 1
        by_courier[month][courier] += 1
        by_category[month][category] += 1
        by_product[month][product][0] += amount
        by_product[month][product][1] += 1

    costs = {m: {} for m in MONTHS}
    ws = wb["成本明细"]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        costs[row[0]][row[1]] = row[2] or 0.0

    return {
        "sales": sales, "profit": profit, "qty": qty,
        "by_region": by_region, "by_courier": by_courier,
        "by_category": by_category, "by_product": by_product,
        "costs": costs,
    }


# ---------------------------------------------------------------------------
# 绘制小工具
# ---------------------------------------------------------------------------

def panel(ax, rect, color=C_PANEL):
    ax.add_patch(Rectangle((rect[0], rect[1]), rect[2], rect[3],
                           facecolor=color, edgecolor="none", zorder=1))


def text(ax, x, y, s, size, color=C_TEXT, weight="normal", ha="center",
         va="center", zorder=10, **kwargs):
    return ax.text(x, y, s, fontsize=fs(size), color=color, weight=weight,
                   ha=ha, va=va, zorder=zorder, **kwargs)


def gradient_area(ax, xs, ys, baseline, colors, zorder=3, bands=180):
    """按垂直渐变填充面积图，并用多边形裁剪。colors = (top, bottom)。"""
    pts = [(xs[0], baseline)] + list(zip(xs, ys)) + [(xs[-1], baseline)]
    clip = Polygon(pts, closed=True, facecolor="none", edgecolor="none")
    ax.add_patch(clip)
    top = np.array(colors[0], dtype=float)
    bottom = np.array(colors[1], dtype=float)
    y0, y1 = min(ys), baseline
    for i in range(bands):
        t = i / (bands - 1)
        color = (top * (1 - t) + bottom * t) / 255.0
        y = y0 + (y1 - y0) * i / bands
        bar = Rectangle((xs[0], y), xs[-1] - xs[0], (y1 - y0) / bands + 0.7,
                        facecolor=color, edgecolor="none", zorder=zorder)
        ax.add_patch(bar)
        bar.set_clip_path(clip)


# ---------------------------------------------------------------------------
# 各面板
# ---------------------------------------------------------------------------

def draw_bar(ax, rect, title, values, color, ref_w=551, ref_h=265):
    """快递公司销量 / 区域销量：6 根竖向柱子 + 顶部数值。"""
    x0, y0, w, h = rect
    sx, sy = w / ref_w, h / ref_h
    panel(ax, rect)
    text(ax, x0 + 275.5 * sx, y0 + 36 * sy, title, 12)

    centers = [64, 148.5, 233, 317.5, 402, 486.5]
    baseline = 213
    for cx, value in zip(centers, values):
        top = baseline - value * 0.33
        ax.add_patch(Rectangle((x0 + (cx - 13.25) * sx, y0 + top * sy),
                               26.5 * sx, (baseline - top) * sy,
                               facecolor=color, edgecolor="none", zorder=3))
        text(ax, x0 + cx * sx, y0 + (top - 12) * sy, str(value), 8)
    for cx, name in zip(centers, (COURIERS if title == "快递公司销量" else REGIONS)):
        text(ax, x0 + cx * sx, y0 + 247 * sy, name, 8)


def _nice_step(span):
    """给环比条形图挑一个 Excel 风格的刻度（20 对应 680~760 的原图）。"""
    span = max(span, 1)
    base = 10 ** int(np.floor(np.log10(span)))
    for multiple in (1, 2, 5, 10):
        step = multiple * base
        if span / step <= 2.2:
            return step
    return 10 * base


def draw_chart7(ax, rect, current, previous, change, current_label="9月", previous_label="8月"):
    """销量环比：横向条形图 + 同比（实为环比）标注。"""
    x0, y0, w, h = rect
    sx, sy = w / 554, h / 236
    panel(ax, rect)
    text(ax, x0 + 277 * sx, y0 + 36 * sy, "销量环比", 12)

    text(ax, x0 + 34 * sx, y0 + 115 * sy, current_label, 9, ha="right")
    text(ax, x0 + 34 * sx, y0 + 180 * sy, previous_label, 9, ha="right")

    # 条形长度 = 在 Excel 自动坐标轴里的位置；9 月对应 680~760 的轴，
    # 和原图的 349px / 162px 完全一致
    step = _nice_step(abs(current - previous))
    axis_min = (min(current, previous) // step) * step - step
    axis_max = -(-max(current, previous) // step) * step   # ceil to step
    if axis_max <= axis_min:
        axis_max = axis_min + step
    span_px = 436 - 54

    def bar_px(value):
        return (value - axis_min) / (axis_max - axis_min) * span_px

    ax.add_patch(Rectangle((x0 + 54 * sx, y0 + 106 * sy),
                           bar_px(current) * sx, 22 * sy,
                           facecolor=C_BLUE, edgecolor="none", zorder=3))
    ax.add_patch(Rectangle((x0 + 54 * sx, y0 + 170 * sy),
                           bar_px(previous) * sx, 23 * sy,
                           facecolor=C_DARKBLUE, edgecolor="none", zorder=3))

    text(ax, x0 + (54 + bar_px(current) + 12) * sx, y0 + 115 * sy,
         str(current), 8, ha="left")
    text(ax, x0 + (54 + bar_px(previous) + 12) * sx, y0 + 181 * sy,
         str(previous), 8, ha="left")
    text(ax, x0 + 436 * sx, y0 + 114 * sy, "%.2f%%" % (change * 100), 12,
         weight="bold", ha="left")
    text(ax, x0 + 498 * sx, y0 + 173 * sy, "同比", 9, ha="right")


def draw_chart8(ax, rect, monthly_sales, ref_w=553, ref_h=324):
    """各月销售额：渐变面积图。"""
    x0, y0, w, h = rect
    sx, sy = w / ref_w, h / ref_h
    panel(ax, rect)
    text(ax, x0 + 276 * sx, y0 + 37 * sy, "各月销售额(万)", 12)

    # 面积图从第一个分类点（1 月）画到最后一个（12 月），不是整条绘图区
    left, right = 80, 513
    bottom, top = 272, 80.5

    def y_of(value):
        return bottom - (value / 200.0) * (bottom - top)

    xs = [left + i * (right - left) / 11 for i in range(12)]
    values = [monthly_sales[m] for m in MONTHS]
    ys = [y_of(v) for v in values]
    gradient_area(ax,
                  [x0 + x * sx for x in xs], [y0 + y * sy for y in ys],
                  y0 + bottom * sy,
                  ((74, 91, 209), (50, 61, 119)), zorder=3)

    for value, y in zip([200, 150, 100, 50, 0],
                        [80.5, 128.5, 175.5, 223.5, 271.5]):
        text(ax, x0 + 56 * sx, y0 + y * sy, "%.2f" % value, 8, ha="right")
    for cx, m in zip(xs, MONTHS):
        text(ax, x0 + cx * sx, y0 + 298 * sy, m, 8)


def draw_chart9(ax, rect, counts, total, ref_w=548, ref_h=383):
    """产品类别销量：圆环 + 中心总销量 + 右侧图例。"""
    x0, y0, w, h = rect
    sx, sy = w / ref_w, h / ref_h
    panel(ax, rect)
    text(ax, x0 + 274 * sx, y0 + 37 * sy, "产品类别销量", 12)

    cx, cy = x0 + 191 * sx, y0 + 229.5 * sy
    r = 111 * min(sx, sy)
    width = r * 0.15
    fractions = [counts[c] / total for c in CATEGORIES]
    colors = [C_PINK, C_INDIGO, C_ORANGE]
    ring_arcs(ax, cx, cy, r, width, fractions, colors, zorder=4)

    text(ax, cx - 1 * sx, cy - 8 * sy, str(total), 24, color=C_WHITE,
         fontfamily="SimSun",
         path_effects=[path_effects.withStroke(linewidth=0.7, foreground=C_WHITE)])
    text(ax, cx - 11.5 * sx, cy + 52 * sy, "总销", 10, color=C_WHITE)
    text(ax, cx - 16 * sx, cy + 88 * sy, "量", 10, color=C_WHITE)

    # 百分比标签在 Excel 里是手工拖到固定位置的，不随圆环角度移动
    labels = [(333, 257), (74, 313), (88, 127)]
    for (lx, ly), fraction in zip(labels, fractions):
        text(ax, x0 + lx * sx, y0 + ly * sy, "%.0f%%" % (fraction * 100), 8)

    for (ly, name, color), count in zip(
            [(167, "办公用品", C_PINK), (231, "家具产品", C_INDIGO),
             (295, "数码电子", C_ORANGE)], [counts[c] for c in CATEGORIES]):
        ax.add_patch(Rectangle((x0 + 413 * sx, y0 + (ly - 5) * sy), 9 * sx,
                               9 * sy, facecolor=color, edgecolor="none", zorder=5))
        text(ax, x0 + 426 * sx, y0 + ly * sy, name, 8, ha="left")


def draw_chart10(ax, rect, top_products, ref_w=553, ref_h=293):
    """商品销售额 Top3：透明图表 + 手工表格。"""
    x0, y0, w, h = rect
    sx, sy = w / ref_w, h / ref_h
    panel(ax, rect)
    text(ax, x0 + 275 * sx, y0 + 37 * sy, "商品销售额Top3", 12)

    text(ax, x0 + 190 * sx, y0 + 93 * sy, "产品", 8)
    text(ax, x0 + 385 * sx, y0 + 93 * sy, "销售额(万)", 8)
    text(ax, x0 + 454 * sx, y0 + 93 * sy, "销量", 8)

    rows_y = [136, 193, 250]
    medals = ["medal_gold.png", "medal_silver.png", "medal_bronze.png"]
    for i, ((name, amount, count), ry) in enumerate(zip(top_products, rows_y)):
        if i < 3:
            image = plt.imread(os.path.join(BASE, "assets", medals[i]))
            ax.imshow(image, extent=(x0 + 60.7 * sx, x0 + 99.7 * sx,
                                     y0 + (ry + 23) * sy, y0 + (ry - 19) * sy),
                      zorder=5, interpolation="lanczos")
        text(ax, x0 + 151 * sx, y0 + ry * sy, name, 8, ha="left",
             color=C_WHITE)
        ax.add_patch(Rectangle((x0 + 343 * sx, y0 + (ry - 16) * sy), 52 * sx,
                               32 * sy, facecolor=C_INDIGO, edgecolor="none",
                               zorder=4))
        text(ax, x0 + 369 * sx, y0 + ry * sy, "%.2f" % amount, 9, color=C_WHITE)
        text(ax, x0 + 441 * sx, y0 + ry * sy, str(count), 9, color=C_WHITE)


def draw_chart11(ax, rect, profit, sales, ref_w=553, ref_h=324):
    """利润额占比销售额：单值圆环 + 右侧数值 + 底部标题框。"""
    x0, y0, w, h = rect
    sx, sy = w / ref_w, h / ref_h
    panel(ax, rect)

    margin = profit / sales if sales else 0.0
    cx, cy = x0 + 154 * sx, y0 + 137 * sy
    r = 91.5 * min(sx, sy)
    width = r * 0.15
    ring_arcs(ax, cx, cy, r, width, [margin, 1 - margin], [C_PINK, C_GRAY],
              zorder=3)

    text(ax, cx + 4 * sx, cy - 2 * sy, "%.2f%%" % (margin * 100), 20,
         color=C_WHITE)
    text(ax, cx + 1 * sx, cy + 36 * sy, "利润率", 9)

    text(ax, x0 + 313 * sx, y0 + 111 * sy, "利润额(万)", 8, ha="left")
    text(ax, x0 + 406 * sx, y0 + 111 * sy, "%.2f" % profit, 12, weight="bold",
         color=C_PINK, ha="left")
    text(ax, x0 + 340 * sx, y0 + 141 * sy, "/", 8)
    text(ax, x0 + 313 * sx, y0 + 169 * sy, "销售额(万)", 8, ha="left")
    text(ax, x0 + 406 * sx, y0 + 172 * sy, "%.2f" % sales, 12, weight="bold",
         color=C_PINK, ha="left")

    ax.add_patch(FancyBboxPatch((x0 + 161 * sx, y0 + 251 * sy), 215 * sx,
                                57 * sy, boxstyle="round,pad=0,rounding_size=%f" % (12 * min(sx, sy)),
                                facecolor="none", edgecolor=C_INDIGO,
                                linewidth=2.2, zorder=4))
    text(ax, x0 + 276 * sx, y0 + 279 * sy, "利润额占比销售额", 12)


def char_width(s, size_pt):
    """粗估字符串宽度（px），用于模拟 Excel 文本框的自动换行。"""
    em = size_pt * 2.0  # 2px/pt
    total = 0.0
    for ch in s:
        if "一" <= ch <= "鿿":
            total += em
        elif ch == "%":
            total += em * 0.82
        elif ch == ".":
            total += em * 0.30
        elif ch in "()":
            total += em * 0.38
        else:
            total += em * 0.58
    return total


def ring_arcs(ax, cx, cy, r, width, fractions, colors, zorder=4,
              start_screen=90.0):
    """从 12 点方向顺时针画圆环扇区。

    画布 y 轴向下，matplotlib 的 Wedge 角度需要做一次镜像，否则蓝/橙
    两段会左右颠倒（Excel 的 firstSliceAng=0 也是从 12 点顺时针）。
    """
    angle = -90.0          # 12 点方向在 y 轴向下的画布上对应 -90°
    for fraction, color in zip(fractions, colors):
        ax.add_patch(Wedge((cx, cy), r, angle, angle + 360.0 * fraction,
                           width=width, facecolor=color, edgecolor="none",
                           zorder=zorder))
        angle += 360.0 * fraction


def draw_kpi(ax, rect, fraction, label_lines, value, pct, boxes):
    """四个成本圆环：圆角边框 + 单值环 + 百分比 / 名称 / 金额。"""
    x0, y0, w, h = rect
    sx, sy = w / 245.0, h / 194.0
    ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                                boxstyle="round,pad=0,rounding_size=%f" % (8 * min(w / 245, h / 194)),
                                facecolor="none", edgecolor=C_BLUE,
                                linewidth=1.1, zorder=5))

    # 图表标题（如“推广”“人工”），标题布局取自 chart XML
    tx, ty = boxes["title"]
    text(ax, x0 + (tx * w + 8 * sx), y0 + (ty * h + 21 * sy),
         boxes["name"], 10, ha="left")

    # 绘图区中心与半径来自 chart XML 的 manualLayout
    px, py, pw, ph = boxes["plot"]
    cx, cy = x0 + (px + pw / 2) * w, y0 + (py + ph / 2) * h
    r = min(pw * w, ph * h) / 2
    width = r * 0.15
    ring_arcs(ax, cx, cy, r, width, [fraction, 1 - fraction],
              [C_BLUE, C_GRAY], zorder=6)

    # 名称：两行，左对齐
    lx = boxes["label"][0] + 0.058
    for line, ly in zip(label_lines, boxes["label_y"]):
        text(ax, x0 + lx * w, y0 + ly * sy, line, 8, ha="left")

    # 金额：框不够宽时 Excel 会把最后一位折到第二行
    vx = boxes["value"][0] + 0.058
    value_s = "%.2f" % value
    avail = boxes["value"][2] * w - 2 * 14.4
    if char_width(value_s, 10) > avail:
        lines = [value_s[:-1], value_s[-1]]
    else:
        lines = [value_s]
    for line, ly in zip(lines, boxes["value_y"]):
        text(ax, x0 + vx * w, y0 + ly * sy, line, 10, ha="left")

    # 百分比：同理，窄框会把“%”折行
    bx = boxes["pct"][0] + 0.058
    pct_s = "%.2f%%" % (fraction * 100)
    avail = boxes["pct"][2] * w - 2 * 14.4
    if char_width(pct_s, 9) > avail:
        lines = [pct_s[:-1], "%"]
    else:
        lines = [pct_s]
    for line, ly in zip(lines, boxes["pct_y"]):
        text(ax, x0 + bx * w, y0 + ly * sy, line, 9, ha="left")


# 每个 KPI 图的布局参数（取自 chart1~4 XML 的 plotArea / userShapes）
KPI_BOXES = {
    1: {"plot": (0.12656, 0.36513, 0.34809, 0.48521),
        "title": (0.20091, 0.06414), "name": "推广",
        "label": (0.5052, 0.25122, 0.35932, 0.35011),
        "value": (0.49657, 0.58529, 0.43522, 0.2726),
        "pct": (0.13421, 0.49576, 0.3662, 0.27394),
        "label_y": [69, 97], "value_y": [139], "pct_y": [120.5, 147]},
    2: {"plot": (0.09588, 0.38651, 0.34809, 0.48521),
        "title": (0.11655, 0.06414), "name": "其他",
        "label": (0.46494, 0.23118, 0.35932, 0.33407),
        "value": (0.45631, 0.55188, 0.35932, 0.33407),
        "pct": (0.08532, 0.5158, 0.43522, 0.2726),
        "label_y": [65, 95], "value_y": [133, 167], "pct_y": [124.5]},
    3: {"plot": (0.10355, 0.38651, 0.34809, 0.48521),
        "title": (0.10121, 0.06414), "name": "人工",
        "label": (0.50808, 0.23919, 0.35932, 0.38218),
        "value": (0.5052, 0.53318, 0.35932, 0.24052),
        "pct": (0.11695, 0.51179, 0.36045, 0.28597),
        "label_y": [69, 97], "value_y": [127, 158], "pct_y": [123, 152]},
    4: {"plot": (0.12656, 0.41858, 0.34809, 0.48521),
        "title": (0.20857, 0.06414), "name": "产品",
        "label": (0.50232, 0.22717, 0.35932, 0.35812),
        "value": (0.4937, 0.57326, 0.35932, 0.22851),
        "pct": (0.15722, 0.53986, 0.32018, 0.2726),
        "label_y": [69, 97], "value_y": [136, 170], "pct_y": [128.5, 155]},
}
KPI_RECTS = {
    1: (42.0, 593.4, 244.8, 194.0),
    2: (309.8, 805.2, 248.8, 194.0),
    3: (310.6, 595.0, 248.8, 194.0),
    4: (42.2, 803.8, 244.8, 194.0),
}


# ---------------------------------------------------------------------------
# 整张看板
# ---------------------------------------------------------------------------

def render(data, month):
    m = "%d月" % month
    prev = 12 if month == 1 else month - 1

    qty = data["qty"][m]
    prev_qty = data["qty"]["%d月" % prev]
    sales = data["sales"][m] / 10000.0
    profit = data["profit"][m] / 10000.0
    change = qty / prev_qty - 1 if prev_qty else 0.0

    categories = {c: data["by_category"][m][c] for c in CATEGORIES}
    regions = {r: data["by_region"][m][r] for r in REGIONS}
    couriers = {c: data["by_courier"][m][c] for c in COURIERS}
    monthly = {k: v / 10000.0 for k, v in data["sales"].items()}

    products = data["by_product"][m]
    top = sorted(products.items(), key=lambda kv: kv[1][0], reverse=True)[:3]
    top_products = [(name, amount / 10000.0, count) for name, (amount, count) in top]

    costs = data["costs"][m]
    total_cost = sum(costs.values())

    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(C_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    # 面板底板
    for rect in [(25, 130, 546, 382), (25, 528, 546, 482),
                 (587, 130, 551, 235), (587, 378, 551, 293),
                 (587, 687, 551, 323), (1149, 130, 551, 323),
                 (1149, 467, 551, 265), (1149, 746, 551, 264)]:
        panel(ax, rect)

    # 顶部标题栏 / 底部装饰栏
    panel(ax, (27, 13, 1674, 105))
    panel(ax, (27, 1021, 1674, 58))

    text(ax, 49, 61.5, "公司销售数据可视化看板", 18, color=C_WHITE,
         weight="bold", ha="left")

    # 日历图标 + 月份下拉框（原文件是窗体控件 Drop Down 1，C2=9）
    calendar = plt.imread(os.path.join(BASE, "assets", "calendar.png"))
    ax.imshow(calendar, extent=(1478, 1517, 106, 66), zorder=5,
              interpolation="lanczos")
    ax.add_patch(FancyBboxPatch((1543, 69), 88, 33,
                                boxstyle="round,pad=0,rounding_size=2",
                                facecolor=C_WHITE, edgecolor="#9A9A9A",
                                linewidth=0.8, zorder=5))
    ax.plot([1609, 1609], [71, 100], color="#C0C0C0", linewidth=0.8, zorder=6)
    ax.add_patch(Polygon([[1614, 83], [1625, 83], [1619.5, 90]],
                         closed=True, facecolor="#333333", edgecolor="none",
                         zorder=6))
    text(ax, 1552, 85.5, m, 10, color="#222222", ha="left", zorder=7)

    # 各图
    draw_chart9(ax, (25, 130, 546, 382), categories, qty)
    text(ax, 299.5, 560.5, "成本费用", 12, color=C_WHITE)

    draw_kpi(ax, KPI_RECTS[1], costs["推广"] / total_cost,
             ["推广费", "用合计"], costs["推广"],
             costs["推广"] / total_cost, KPI_BOXES[1])
    draw_kpi(ax, KPI_RECTS[3], costs["人工"] / total_cost,
             ["人工费", "用合计"], costs["人工"],
             costs["人工"] / total_cost, KPI_BOXES[3])
    draw_kpi(ax, KPI_RECTS[4], costs["产品"] / total_cost,
             ["产品费", "用合计"], costs["产品"],
             costs["产品"] / total_cost, KPI_BOXES[4])
    draw_kpi(ax, KPI_RECTS[2], costs["其他"] / total_cost,
             ["其他费", "用合计"], costs["其他"],
             costs["其他"] / total_cost, KPI_BOXES[2])

    draw_chart7(ax, (587, 130, 551, 235), qty, prev_qty, change,
                m, "%d月" % prev)
    draw_chart10(ax, (587, 378, 551, 293), top_products)
    draw_chart11(ax, (587, 687, 551, 323), profit, sales)

    draw_chart8(ax, (1149, 130, 551, 323), monthly)
    draw_bar(ax, (1149, 467, 551, 265), "区域销量",
             [regions[r] for r in REGIONS], C_BLUE)
    draw_bar(ax, (1149, 746, 551, 264), "快递公司销量",
             [couriers[c] for c in COURIERS], C_PINK)

    return fig


def save_png(fig, name="dashboard.png"):
    path = os.path.join(BASE, name)
    fig.savefig(path, dpi=DPI, facecolor=C_BG)
    print("saved:", path)
    return path


def save_gif(data, name="dashboard_months.gif", scale=0.5):
    frames = []
    for month in range(1, 13):
        fig = render(data, month)
        buffer = io.BytesIO()
        fig.canvas.draw()
        fig.savefig(buffer, format="png", dpi=DPI, facecolor=C_BG)
        plt.close(fig)
        buffer.seek(0)
        image = Image.open(buffer).convert("RGB")
        image = image.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
        frames.append(image)
    path = os.path.join(BASE, name)
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=900, loop=0, optimize=True)
    print("saved:", path)
    return path


def main():
    parser = argparse.ArgumentParser(description="复刻第四章销售看板")
    parser.add_argument("--month", type=int, default=9, choices=range(1, 13))
    parser.add_argument("--gif", action="store_true", help="生成 12 个月循环动画")
    parser.add_argument("--out", default=None, help="输出文件名")
    args = parser.parse_args()

    data = load_data()
    if args.gif:
        save_gif(data)
        return
    fig = render(data, args.month)
    save_png(fig, args.out or "dashboard.png")


if __name__ == "__main__":
    main()
