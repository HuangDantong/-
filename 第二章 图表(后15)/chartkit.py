# -*- coding: utf-8 -*-
"""复刻 `第二章 图表(后15).xlsx`（图 16~30）时反复用到的公共部件。

与前一组的 chartkit 相同，画布按 2px/pt 还原 Excel 图表导出尺寸，字号
按 1.44 倍放大（2 × 72 / 100）。这一组多了三件事：

1. 工作簿里的图表 XML 文件名与「图 16~30」不是一一对应的（图 24/25 各有
   两个图表对象），用 CHART_PARTS 查表；
2. userShapes 里的标注大量用「组合」嵌套，需要按 grpSp 的 xfrm 逐层换算成
   画布像素坐标；
3. 主题色 schemeClr 带 lumMod / lumOff / alpha，按 HSL 亮度公式还原。
"""

import os
import re
import zipfile
from xml.etree import ElementTree as ET

import numpy as np
from matplotlib import font_manager
from PIL import Image

DPI = 100
PX_PER_PT = 2.0
FONT_SCALE = PX_PER_PT * 72 / DPI          # 9pt -> 12.96pt
BACKGROUND = "#1A1E43"
EMU_PER_PT = 12700.0
EMU_PER_PX = EMU_PER_PT / PX_PER_PT        # 6350

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
CDR = "{http://schemas.openxmlformats.org/drawingml/2006/chartDrawing}"

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第二章 图表(后15).xlsx")

HERE = os.path.dirname(os.path.abspath(__file__))

# 图号 -> chartN.xml 的 N。图 24/25 的第二个对象才是画面上可见的图表，
# 第一个是挪到工作表右侧的辅助图（导出为空），这里按可见对象登记。
CHART_PARTS = {
    16: [1], 17: [2], 18: [3], 19: [4], 20: [5], 21: [6], 22: [7],
    23: [8], 24: [10], 25: [12], 26: [13], 27: [14], 28: [15],
    29: [16], 30: [17],
}

# 导出画布尺寸（px），由图表对象的 pt 尺寸 × 2 得到；写死在代码里，
# 这样交付的脚本不依赖 reference/ 下的比对图也能运行。
CHART_SIZES = {
    16: (405, 400), 17: (834, 594), 18: (832, 622), 19: (832, 622),
    20: (835, 624), 21: (832, 622), 22: (832, 638), 23: (832, 594),
    24: (844, 589), 25: (842, 589), 26: (831, 591), 27: (832, 616),
    28: (844, 603), 29: (844, 593), 30: (831, 593),
}

# 主题色（theme1.xml，Office 配色）
THEME = {
    "dk1": "000000", "lt1": "FFFFFF", "dk2": "44546A", "lt2": "E7E6E6",
    "accent1": "5B9BD5", "accent2": "ED7D31", "accent3": "A5A5A5",
    "accent4": "FFC000", "accent5": "4472C4", "accent6": "70AD47",
    "hlink": "0563C1", "folHlink": "954F72",
}
SCHEME_ALIAS = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2"}


# --------------------------------------------------------------------------
# 字体
# --------------------------------------------------------------------------


def pick_font(candidates, fallback="DejaVu Sans"):
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            return name
    return fallback


UI_FONT = pick_font(["Microsoft YaHei", "微软雅黑", "SimHei", "DengXian"])
AXIS_FONTS = [pick_font(["Calibri"]),
              pick_font(["DengXian", "等线", "SimSun", "Microsoft YaHei"])]


# --------------------------------------------------------------------------
# 颜色
# --------------------------------------------------------------------------


def _rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _to_hls(rgb):
    import colorsys
    return colorsys.rgb_to_hls(*[v / 255.0 for v in rgb])


def _from_hls(h, l, s):
    import colorsys
    return tuple(int(round(v * 255)) for v in colorsys.hls_to_rgb(h, l, s))


def resolve_color(scheme_or_srgb_node):
    """把一个 solidFill 的子节点（srgbClr/schemeClr）解成 (r,g,b,a)。

    lumMod/lumOff 作用在 HSL 的 L 上（Excel 的算法：L' = L*lumMod + lumOff），
    alpha 取 0~100000 的千分比。
    """
    if scheme_or_srgb_node is None:
        return None
    node = scheme_or_srgb_node
    color = node.get("val")
    if node.tag == A + "schemeClr":
        color = THEME[SCHEME_ALIAS.get(color, color)]
    rgb = _rgb(color)
    mods = {child.tag.split("}")[-1]: int(child.get("val")) / 100000.0
            for child in node}
    if "lumMod" in mods or "lumOff" in mods:
        h, l, s = _to_hls(rgb)
        l = l * mods.get("lumMod", 1.0) + mods.get("lumOff", 0.0)
        rgb = _from_hls(h, max(0.0, min(1.0, l)), s)
    return rgb + (mods.get("alpha", 1.0),)


def fill_of(node):
    """solidFill / noFill / gradFill / blipFill -> (r,g,b,a) | 'none' | dict。"""
    if node is None:
        return None
    solid = node.find(A + "solidFill")
    if solid is not None:
        for child in solid:
            if child.tag in (A + "srgbClr", A + "schemeClr"):
                return resolve_color(child)
    if node.find(A + "noFill") is not None:
        return "none"
    grad = node.find(A + "gradFill")
    if grad is not None:
        stops = []
        for stop in grad.iter(A + "gs"):
            child = list(stop)[0] if len(stop) else None
            if child is not None:
                stops.append((int(stop.get("pos")) / 100000.0,
                              resolve_color(child)))
        lin = grad.find(A + "lin")
        return {"type": "grad", "angle": int(lin.get("ang")) / 60000.0
                if lin is not None else 0.0, "stops": stops}
    blip = node.find(A + "blipFill")
    if blip is not None:
        embed = blip.find(A + "blip")
        return {"type": "image",
                "rid": embed.get(
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                if embed is not None else None}
    return None


def line_of(sp_pr):
    if sp_pr is None:
        return None
    ln = sp_pr.find(A + "ln")
    if ln is None:
        return None
    return {
        "color": fill_of(ln),
        "width_px": int(ln.get("w")) / EMU_PER_PX if ln.get("w") else 0.0,
        "dash": (ln.find(A + "prstDash").get("val")
                 if ln.find(A + "prstDash") is not None else None),
        "head": (ln.find(A + "headEnd").get("type")
                 if ln.find(A + "headEnd") is not None else None),
        "tail": (ln.find(A + "tailEnd").get("type")
                 if ln.find(A + "tailEnd") is not None else None),
    }


# --------------------------------------------------------------------------
# 读 workbook / chart XML
# --------------------------------------------------------------------------


def _read(part):
    with zipfile.ZipFile(XLSX) as archive:
        return archive.read(part).decode("utf-8")


def chart_root(number, part=None):
    part = part or CHART_PARTS[number][0]
    return ET.fromstring(_read("xl/charts/chart%d.xml" % part))


def chart_size(number):
    """导出 PNG 的 (宽, 高) 像素。"""
    return CHART_SIZES[number]


REF_SUFFIX = {24: "_2", 25: "_2"}


def reference_path(number, suffix=None):
    if suffix is None:
        suffix = REF_SUFFIX.get(number, "")
    name = "chart%d_excel%s.png" % (number, suffix)
    return os.path.join(HERE, "reference", name)


# --------------------------------------------------------------------------
# userShapes（含嵌套组合）
# --------------------------------------------------------------------------


def _paragraphs(tx_body):
    if tx_body is None:
        return []
    out = []
    for para in tx_body.findall(A + "p"):
        ppr = para.find(A + "pPr")
        align = ppr.get("algn") if ppr is not None else None
        runs = []
        for run in list(para.findall(A + "r")) + list(para.findall(A + "fld")):
            rpr = run.find(A + "rPr")
            latin = rpr.find(A + "latin") if rpr is not None else None
            color = None
            if rpr is not None and rpr.find(A + "solidFill") is not None:
                color = fill_of(rpr.find(A + "solidFill"))
            runs.append({
                "text": "".join(t.text or "" for t in run.iter(A + "t")),
                "size_pt": int(rpr.get("sz")) / 100
                if (rpr is not None and rpr.get("sz")) else None,
                "bold": rpr is not None and rpr.get("b") == "1",
                "color": color,
                "face": latin.get("typeface") if latin is not None else None,
            })
        if runs:
            out.append({"align": align, "runs": runs})
    return out


def _xfrm(sp_pr):
    if sp_pr is None:
        return None
    xfrm = sp_pr.find(A + "xfrm")
    if xfrm is None:
        return None
    off, ext = xfrm.find(A + "off"), xfrm.find(A + "ext")
    data = {}
    if off is not None:
        data["x"], data["y"] = int(off.get("x")), int(off.get("y"))
    if ext is not None:
        data["cx"], data["cy"] = int(ext.get("cx")), int(ext.get("cy"))
    data["rot"] = int(xfrm.get("rot", 0)) / 60000.0
    data["flipH"] = xfrm.get("flipH") == "1"
    data["flipV"] = xfrm.get("flipV") == "1"
    return data


def _group_xfrm(grp):
    grp_pr = grp.find(CDR + "grpSpPr")
    xfrm = grp_pr.find(A + "xfrm") if grp_pr is not None else None
    if xfrm is None:
        return None
    off, ext = xfrm.find(A + "off"), xfrm.find(A + "ext")
    ch_off, ch_ext = xfrm.find(A + "chOff"), xfrm.find(A + "chExt")
    if None in (off, ext, ch_off, ch_ext):
        return None
    return {
        "x": int(off.get("x")), "y": int(off.get("y")),
        "cx": int(ext.get("cx")), "cy": int(ext.get("cy")),
        "chx": int(ch_off.get("x")), "chy": int(ch_off.get("y")),
        "chcx": int(ch_ext.get("cx")), "chcy": int(ch_ext.get("cy")),
    }


def _apply(matrix, x, y):
    return matrix[0] * x + matrix[1] * y + matrix[2], \
        matrix[3] * x + matrix[4] * y + matrix[5]


def _group_matrix(parent, g):
    scale_x = g["cx"] / g["chcx"] if g["chcx"] else 1.0
    scale_y = g["cy"] / g["chcy"] if g["chcy"] else 1.0
    local = (scale_x, 0.0, g["x"] - g["chx"] * scale_x,
             0.0, scale_y, g["y"] - g["chy"] * scale_y)
    return (
        parent[0] * local[0] + parent[1] * local[3],
        parent[0] * local[1] + parent[1] * local[4],
        parent[0] * local[2] + parent[1] * local[5] + parent[2],
        parent[3] * local[0] + parent[4] * local[3],
        parent[3] * local[1] + parent[4] * local[4],
        parent[3] * local[2] + parent[4] * local[5] + parent[5],
    )


def user_shapes(number, part=None):
    """把图表 userShapes 展开成绝对像素坐标的元素列表。

    每个元素：
      kind       sp / pic / cxnSp / graphicFrame
      name       形状名
      geom       预设几何（rect / ellipse / line ...）
      box        (x0, y0, x1, y1) 画布像素
      fill, line
      paragraphs [{'align', 'runs'}]，run 带字号/粗体/颜色/字体
      flipH/flipV（连接符方向用）
    """
    part = part or CHART_PARTS[number][0]
    rels = _read("xl/charts/_rels/chart%d.xml.rels" % part)
    match = re.search(r'Target="\.\./drawings/(drawing\d+\.xml)"', rels)
    if not match:
        return []
    root = ET.fromstring(_read("xl/drawings/" + match.group(1)))
    width_px, height_px = chart_size(number)
    identity = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    out = []
    mapper = [lambda x, y: (x, y)]

    def walk(node, matrix):
        kind = node.tag.split("}")[-1]
        if kind == "grpSp":
            g = _group_xfrm(node)
            child_matrix = _group_matrix(matrix, g) if g else matrix
            for child in node:
                if child.tag.split("}")[-1] in (
                        "sp", "pic", "cxnSp", "graphicFrame", "grpSp"):
                    walk(child, child_matrix)
            return
        if kind not in ("sp", "pic", "cxnSp", "graphicFrame"):
            return
        sp_pr = node.find(CDR + "spPr")
        xfrm = _xfrm(sp_pr)
        name_node = node.find(".//" + CDR + "cNvPr")
        info = {
            "kind": kind,
            "name": name_node.get("name") if name_node is not None else "",
            "geom": None, "box": None, "fill": None, "line": None,
            "paragraphs": [], "flipH": False, "flipV": False, "rot": 0.0,
        }
        if xfrm and "x" in xfrm:
            x0, y0 = _apply(matrix, xfrm["x"], xfrm["y"])
            x1, y1 = _apply(matrix, xfrm["x"] + xfrm.get("cx", 0),
                            xfrm["y"] + xfrm.get("cy", 0))
            x0, y0 = mapper[0](x0 / EMU_PER_PX, y0 / EMU_PER_PX)
            x1, y1 = mapper[0](x1 / EMU_PER_PX, y1 / EMU_PER_PX)
            info["box"] = (min(x0, x1), min(y0, y1),
                           max(x0, x1), max(y0, y1))
            info["flipH"], info["flipV"] = xfrm["flipH"], xfrm["flipV"]
            info["rot"] = xfrm["rot"]
        if sp_pr is not None:
            geom = sp_pr.find(A + "prstGeom")
            info["geom"] = geom.get("prst") if geom is not None else None
            info["fill"] = fill_of(sp_pr)
            info["line"] = line_of(sp_pr)
        info["paragraphs"] = _paragraphs(node.find(CDR + "txBody"))
        out.append(info)

    for anchor in root:
        if anchor.tag.split("}")[-1] != "relSizeAnchor":
            continue
        start, end = anchor.find(CDR + "from"), anchor.find(CDR + "to")
        if start is None or end is None:
            continue
        ax0 = float(start.find(CDR + "x").text) * width_px
        ay0 = float(start.find(CDR + "y").text) * height_px
        ax1 = float(end.find(CDR + "x").text) * width_px
        ay1 = float(end.find(CDR + "y").text) * height_px
        for child in anchor:
            kind = child.tag.split("}")[-1]
            if kind not in ("sp", "pic", "cxnSp", "graphicFrame", "grpSp"):
                continue
            # 锚框会按比例拉伸其内容（Excel 的 relSizeAnchor 语义）
            if kind == "grpSp":
                g = _group_xfrm(child)
                box = None
                if g:
                    box = (g["x"] / EMU_PER_PX, g["y"] / EMU_PER_PX,
                           (g["x"] + g["cx"]) / EMU_PER_PX,
                           (g["y"] + g["cy"]) / EMU_PER_PX)
            else:
                xf = _xfrm(child.find(CDR + "spPr"))
                box = None
                if xf and "x" in xf:
                    box = (xf["x"] / EMU_PER_PX, xf["y"] / EMU_PER_PX,
                           (xf["x"] + xf.get("cx", 0)) / EMU_PER_PX,
                           (xf["y"] + xf.get("cy", 0)) / EMU_PER_PX)
            if box and box[2] > box[0] and box[3] > box[1]:
                sx = (ax1 - ax0) / (box[2] - box[0])
                sy = (ay1 - ay0) / (box[3] - box[1])
                mapper[0] = (lambda x, y, ax0=ax0, ay0=ay0, bx0=box[0],
                             by0=box[1], sx=sx, sy=sy:
                             (ax0 + (x - bx0) * sx, ay0 + (y - by0) * sy))
            else:
                mapper[0] = lambda x, y: (x, y)
            walk(child, identity)
    return out


def text_of(paragraphs):
    return "".join(run["text"] for para in paragraphs for run in para["runs"])


# --------------------------------------------------------------------------
# 画布与量测
# --------------------------------------------------------------------------


def new_figure(width_px, height_px, facecolor=BACKGROUND):
    import matplotlib.pyplot as plt
    figure = plt.figure(figsize=(width_px / DPI, height_px / DPI), dpi=DPI)
    figure.patch.set_facecolor(facecolor)
    return figure


def save(figure, name):
    path = os.path.join(HERE, name)
    figure.savefig(path, dpi=DPI, facecolor=figure.get_facecolor())
    print("saved:", path)
    return path


def as_array(image):
    if isinstance(image, str):
        return np.array(Image.open(image).convert("RGB")).astype(int)
    return np.asarray(image).astype(int)


def pixel(image, x, y):
    return tuple(as_array(image)[int(y), int(x)])


def ink_bbox(image, top, bottom, left, right, brightness=250,
             background=BACKGROUND):
    array = as_array(image)
    sub = array[top:bottom, left:right]
    mask = sub.sum(2) > brightness
    rows = np.where(mask.sum(1) > 0)[0]
    cols = np.where(mask.sum(0) > 0)[0]
    if not len(rows) or not len(cols):
        return None
    return (top + int(rows.min()), top + int(rows.max()),
            left + int(cols.min()), left + int(cols.max()))


def band_rows(image, top, bottom, left, right, brightness=250, gap=3):
    array = as_array(image)
    sub = array[top:bottom, left:right]
    mask = sub.sum(2) > brightness
    rows = np.where(mask.sum(1) > 0)[0]
    if not len(rows):
        return []
    bands, start, previous = [], rows[0], rows[0]
    for row in rows[1:]:
        if row > previous + gap:
            bands.append((top + int(start), top + int(previous)))
            start = row
        previous = row
    bands.append((top + int(start), top + int(previous)))
    return bands


def runs_in_row(image, row, background=BACKGROUND, tolerance=0):
    array = as_array(image)
    background = (np.array(_rgb(background)) if isinstance(background, str)
                  else np.asarray(background))
    out, start = [], None
    for x in range(array.shape[1]):
        differs = np.any(np.abs(array[row, x] - background) > tolerance)
        if differs and start is None:
            start = x
        elif not differs and start is not None:
            out.append((start, x - 1, tuple(array[row, (start + x - 1) // 2])))
            start = None
    if start is not None:
        out.append((start, array.shape[1] - 1,
                    tuple(array[row, (start + array.shape[1] - 1) // 2])))
    return out
