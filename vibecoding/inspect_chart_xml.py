# -*- coding: utf-8 -*-
"""把 xlsx 里的图表 XML 压缩成人类可读的样式规格，方便复刻时查参数。

用法：
    python inspect_chart_xml.py 5          # 只看 chart5.xml
    python inspect_chart_xml.py 5 --raw    # 直接打印原始 XML

打印内容依次是：图表类型、标题/副标题/脚注文本、绘图区 manualLayout、
每个系列的图表类型/填充/边框/数据标签/数据范围，以及坐标轴的刻度与格式。
"""

import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第二章 图表(前15).xlsx")

C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def tag(element):
    return element.tag.split("}")[-1]


def fill_of(element):
    """把一个 spPr / txPr 里的填充描述成 '<solid 0070C0>' 这样的字符串。"""
    if element is None:
        return None
    solid = element.find(A + "solidFill")
    if solid is not None:
        scheme = solid.find(A + "schemeClr")
        if scheme is not None:
            mods = " ".join("%s=%s" % (tag(m), m.get("val"))
                            for m in scheme)
            return "scheme %s %s" % (scheme.get("val"), mods)
        srgb = solid.find(A + "srgbClr")
        if srgb is not None:
            return "srgb #%s" % srgb.get("val")
    if element.find(A + "noFill") is not None:
        return "noFill"
    grad = element.find(A + "gradFill")
    if grad is not None:
        stops = []
        for stop in grad.iter(A + "gs"):
            color = stop.find(A + "srgbClr")
            stops.append("%s@%s" % (color.get("val") if color is not None else "?",
                                    stop.get("pos")))
        linear = grad.find(A + "lin")
        angle = linear.get("ang") if linear is not None else "?"
        return "gradFill ang=%s [%s]" % (angle, ",".join(stops))
    patt = element.find(A + "pattFill")
    if patt is not None:
        fg = patt.find(A + "fgClr")
        return "pattFill prst=%s fg=%s" % (patt.get("prst"), fill_of(fg))
    return "(none)"


def line_of(sp_pr):
    if sp_pr is None:
        return None
    ln = sp_pr.find(A + "ln")
    if ln is None:
        return None
    parts = ["fill=%s" % fill_of(ln)]
    if ln.get("w"):
        parts.append("w=%sEMU(%.2fpt)" % (ln.get("w"), int(ln.get("w")) / 12700))
    dash = ln.find(A + "prstDash")
    if dash is not None:
        parts.append("dash=%s" % dash.get("val"))
    return " ".join(parts)


def text_of(node):
    return "".join(t.text or "" for t in node.iter(A + "t"))


def font_of(node):
    if node is None:
        return None
    rpr = node.find(A + "defRPr")
    if rpr is None:
        rpr = node.find(".//" + A + "defRPr")
    if rpr is None:
        return None
    bits = []
    if rpr.get("sz"):
        bits.append("%.1fpt" % (int(rpr.get("sz")) / 100))
    if rpr.get("b"):
        bits.append("bold")
    latin = rpr.find(A + "latin")
    if latin is not None:
        bits.append(latin.get("typeface"))
    bits.append(fill_of(rpr))
    return " ".join(str(b) for b in bits if b)


def dump_title(chart, label):
    node = chart.find(C + label)
    if node is None:
        return
    texts = [text_of(rich) for rich in node.findall(C + "rich")]
    if not texts:
        texts = [text_of(tx) for tx in node.findall(C + "tx")]
    texts = [t for t in texts if t]
    if texts:
        print("  %-10s %r   [%s]" % (label, texts, font_of(node)))


def main():
    number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    with zipfile.ZipFile(XLSX) as archive:
        raw = archive.read("xl/charts/chart%d.xml" % number).decode("utf-8")
        if "--raw" in sys.argv:
            print(raw)
            return
        root = ET.fromstring(raw)

    plot = root.find(C + "chart").find(C + "plotArea")
    print("=" * 72)
    print("chart%d.xml" % number)

    kinds = sorted({tag(child) for child in plot
                    if tag(child).endswith("Chart")})
    print("图表类型:", ", ".join(kinds))
    for title in root.iter(C + "title"):
        print("有独立的 chart 标题节点")
        break

    chart = root.find(C + "chart")
    for label in ("title", "autoTitleDeleted"):
        pass
    dump_title(chart, "title")
    for sub in ("subtitle", "footnote"):
        node = chart.find(C + sub)
        if node is not None:
            print("  %-10s %r   [%s]" % (sub, text_of(node), font_of(node)))

    layout = plot.find(C + "layout")
    if layout is not None:
        manual = layout.find(C + "manualLayout")
        if manual is not None:
            vals = {tag(child): child.get("val") for child in manual}
            print("绘图区 manualLayout:", vals)
    else:
        print("绘图区 layout: (自动)")

    print("-" * 72)
    for index, series in enumerate(plot.iter(C + "ser")):
        print("系列 %d" % index)
        for tag_name in ("idx", "order", "tx"):
            node = series.find(C + tag_name)
            if node is not None:
                if tag_name == "tx":
                    print("  名称      %r" % text_of(node))
                else:
                    print("  %-9s %s" % (tag_name, node.get("val")))
        for kind in ("barChart", "lineChart", "doughnutChart"):
            pass
        sp_pr = series.find(C + "spPr")
        if sp_pr is not None:
            print("  填充      %s" % fill_of(sp_pr))
            print("  边框      %s" % line_of(sp_pr))
        marker = series.find(C + "marker")
        if marker is not None:
            print("  标记      symbol=%s size=%s  %s" % (
                (marker.find(C + "symbol").get("val")
                 if marker.find(C + "symbol") is not None else "?"),
                (marker.find(C + "size").get("val")
                 if marker.find(C + "size") is not None else "?"),
                fill_of(marker.find(C + "spPr"))))
        smooth = series.find(C + "smooth")
        if smooth is not None:
            print("  平滑      %s" % smooth.get("val"))
        labels = series.find(C + "dLbls")
        if labels is not None:
            shown = [tag(n) for n in labels if tag(n).startswith("show")]
            pos = labels.find(C + "dLblPos")
            print("  数据标签  %s pos=%s numFmt=%s font=%s" % (
                shown, pos.get("val") if pos is not None else "-",
                (labels.find(C + "numFmt").get("formatCode")
                 if labels.find(C + "numFmt") is not None else "-"),
                font_of(labels)))
        for name in ("cat", "val", "xVal", "yVal", "bubbleSize"):
            node = series.find(C + name)
            if node is None:
                continue
            formula = node.find(C + "f")
            points = [p.text for p in node.iter(C + "pt")]
            points = [p for p in points if p is not None]
            print("  %-9s f=%s" % (name, formula.text if formula is not None else "-"))
            if points:
                print("  %-9s 缓存值 %s" % ("", points))
            literal = node.find(C + "numLit")
            if literal is not None:
                print("  %-9s 字面值 %s" % ("", [v.text for v in literal.iter(C + "pt")]))
            str_lit = node.find(C + "strLit")
            if str_lit is not None:
                print("  %-9s 字面值 %s" % ("", [v.text for v in str_lit.iter(C + "pt")]))
        print()

    for axis in plot.iter():
        if tag(axis) in ("catAx", "valAx", "dateAx", "serAx"):
            print("%s" % tag(axis))
            for child in axis:
                name = tag(child)
                if name in ("delete", "majorTickMark", "minorTickMark",
                            "tickLblPos", "crosses", "crossesAt"):
                    print("  %-14s %s" % (name, child.get("val")))
                elif name in ("scaling", "majorUnit", "numFmt", "title", "txPr"):
                    if name == "scaling":
                        vals = {tag(c): c.get("val") for c in child}
                        print("  %-14s %s" % (name, vals))
                    elif name == "numFmt":
                        print("  %-14s %s" % (name, child.get("formatCode")))
                    elif name == "majorUnit":
                        print("  %-14s %s" % (name, child.get("val")))
            print()

    for legend in root.iter(C + "legend"):
        pos = legend.find(C + "legendPos")
        print("图例  pos=%s  %s" % (pos.get("val") if pos is not None else "-",
                                   font_of(legend)))
        print()

    for node in root.iter():
        if tag(node) in ("gapWidth", "overlap", "barDir", "grouping",
                         "varyColors", "holeSize", "firstSliceAng", "radarStyle"):
            print("  %-14s %s" % (tag(node), node.get("val")))


if __name__ == "__main__":
    main()
