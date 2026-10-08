# -*- coding: utf-8 -*-
"""列出图表 userShapes 里的所有覆盖元素（标题 / 副标题 / 脚注 / 标注框等）。

图表里那些不属于绘图区的文字和形状——标题、副标题、脚注，以及像图3 那样
手工拖到柱顶的数值圆角框——都放在图表的 userShapes 部分，而不是 chart XML。
这个脚本把它们的位置、填充、文字和字号摊平打印出来。

用法：
    python inspect_usershapes.py 3
    python inspect_usershapes.py 3 --raw     # 打印原始 XML

坐标说明：cdr:from / cdr:to 是相对图表区的比例（0~1），a:xfrm 里的
off / ext 是 EMU 绝对坐标（1 pt = 12700 EMU）。复刻时用比例坐标更省事，
因为画布就是整个图表区。
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第二章 图表(前15).xlsx")

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
CDR = "{http://schemas.openxmlformats.org/drawingml/2006/chartDrawing}"
EMU_PER_PT = 12700


def tag(element):
    return element.tag.split("}")[-1]


def color_of(node):
    """把 solidFill / noFill 描述成 '#RRGGBB@alpha' 或 'scheme:xxx'。"""
    if node is None:
        return "-"
    solid = node.find(A + "solidFill")
    if solid is None and tag(node) == "solidFill":
        solid = node
    if solid is not None:
        srgb = solid.find(A + "srgbClr")
        if srgb is not None:
            alpha = srgb.find(A + "alpha")
            suffix = "@%s%%" % (int(alpha.get("val")) / 1000) if alpha is not None else ""
            return "#%s%s" % (srgb.get("val"), suffix)
        scheme = solid.find(A + "schemeClr")
        if scheme is not None:
            mods = " ".join("%s=%s" % (tag(m), m.get("val")) for m in scheme)
            return "scheme:%s %s" % (scheme.get("val"), mods)
    if node.find(A + "noFill") is not None:
        return "noFill"
    if node.find(A + "gradFill") is not None:
        grad = node.find(A + "gradFill")
        stops = []
        for stop in grad.iter(A + "gs"):
            color = stop.find(A + "srgbClr")
            stops.append("%s@%s" % (color.get("val") if color is not None else "?",
                                    stop.get("pos")))
        return "grad[%s]" % ",".join(stops)
    return "-"


def runs_of(tx_body):
    """返回 [(文本, 字号pt, 粗体, 颜色, 字体)]，字体是 latin 的 typeface。"""
    out = []
    for para in tx_body.findall(A + "p"):
        pieces = []
        for run in list(para.findall(A + "r")) + list(para.findall(A + "fld")):
            rpr = run.find(A + "rPr")
            text = "".join(t.text or "" for t in run.iter(A + "t"))
            size = int(rpr.get("sz")) / 100 if (rpr is not None and rpr.get("sz")) else None
            bold = rpr is not None and rpr.get("b") == "1"
            latin = rpr.find(A + "latin") if rpr is not None else None
            face = latin.get("typeface") if latin is not None else None
            color = color_of(rpr) if rpr is not None else "-"
            pieces.append((text, size, bold, color, face))
        if pieces:
            out.append(pieces)
    return out


def main():
    number = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    with zipfile.ZipFile(XLSX) as archive:
        rels = archive.read("xl/charts/_rels/chart%d.xml.rels" % number).decode("utf-8")
        match = re.search(r'Target="\.\./drawings/(drawing\d+\.xml)"', rels)
        if not match:
            print("chart%d 没有 userShapes" % number)
            return
        name = match.group(1)
        raw = archive.read("xl/drawings/" + name).decode("utf-8")

    if "--raw" in sys.argv:
        print(raw)
        return

    print("=" * 78)
    print("chart%d.xml -> %s" % (number, name))
    root = ET.fromstring(raw)

    for index, anchor in enumerate(root):
        kind = tag(anchor)
        if kind not in ("relSizeAnchor", "absSizeAnchor", "oneCellAnchor",
                        "twoCellAnchor", "absoluteAnchor"):
            continue
        start = anchor.find(CDR + "from")
        end = anchor.find(CDR + "to")
        for child in anchor:
            child_kind = tag(child)
            if child_kind not in ("sp", "pic", "graphicFrame", "cxnSp", "grpSp"):
                continue
            name_node = child.find(".//" + CDR + "cNvPr")
            label = name_node.get("name") if name_node is not None else "?"
            sp_pr = child.find(CDR + "spPr")
            off = size = geom = "-"
            if sp_pr is not None:
                xfrm = sp_pr.find(A + "xfrm")
                if xfrm is not None:
                    o, e = xfrm.find(A + "off"), xfrm.find(A + "ext")
                    if o is not None:
                        off = "%.1f,%.1fpt" % (int(o.get("x")) / EMU_PER_PT,
                                               int(o.get("y")) / EMU_PER_PT)
                    if e is not None:
                        size = "%.1fx%.1fpt" % (int(e.get("cx")) / EMU_PER_PT,
                                                int(e.get("cy")) / EMU_PER_PT)
                geo = sp_pr.find(A + "prstGeom")
                if geo is not None:
                    geom = geo.get("prst")
            fill = color_of(sp_pr.find(A + "solidFill")) if sp_pr is not None else "-"
            ln = sp_pr.find(A + "ln") if sp_pr is not None else None
            line = color_of(ln) if ln is not None else "-"

            if start is not None and end is not None:
                rel = "rel (%.5f,%.5f)-(%.5f,%.5f)" % (
                    float(start.find(CDR + "x").text), float(start.find(CDR + "y").text),
                    float(end.find(CDR + "x").text), float(end.find(CDR + "y").text))
            else:
                rel = "-"

            print("-" * 78)
            print("[%d] %-14s %s" % (index, label, child_kind))
            print("    几何 %-12s 尺寸 %-16s %s" % (geom, size, rel))
            print("    绝对 %-18s 填充 %-22s 边框 %s" % (off, fill, line))
            body = child.find(CDR + "txBody")
            if body is None:
                body = child.find(".//" + A + "txBody")
            if body is not None:
                body_pr = body.find(A + "bodyPr")
                if body_pr is not None:
                    print("    排版 anchor=%s rot=%s ins(l,t,r,b)=%s,%s,%s,%s" % (
                        body_pr.get("anchor"), body_pr.get("rot"),
                        body_pr.get("lIns"), body_pr.get("tIns"),
                        body_pr.get("rIns"), body_pr.get("bIns")))
                for para in runs_of(body):
                    for text, size_pt, bold, color, face in para:
                        print("    文字 %r  %spt %s %s %s" % (
                            text, size_pt, "bold" if bold else "", color, face))


if __name__ == "__main__":
    main()
