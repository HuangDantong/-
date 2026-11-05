# -*- coding: utf-8 -*-
"""把 `第二章 图表(前15).xlsx` 里的图表用 Excel 导出成 PNG，作为复刻的比对基准。

用法：
    python export_reference.py

输出：
    reference/chart{N}_excel.png   第 N 张工作表里的图表对象（原图）
    reference/chart{N}_meta.txt    图表对象的尺寸/位置，用于核对画布大小

第 7 张工作表「7 蝴蝶图」不是图表对象（用单元格+条件格式做的），
导出会跳过，它的目标图由 sheet7 的单元格渲染自行还原。
"""

import os

import win32com.client

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第二章 图表(前15).xlsx")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    workbook = excel.Workbooks.Open(XLSX)
    try:
        for index in range(1, workbook.Worksheets.Count + 1):
            sheet = workbook.Worksheets(index)
            charts = sheet.ChartObjects()
            meta = ["sheet=%s  chart_objects=%d" % (sheet.Name, charts.Count)]
            for position in range(1, charts.Count + 1):
                obj = charts.Item(position)
                path = os.path.join(OUT_DIR, "chart%d_excel.png" % index)
                obj.Chart.Export(path, "PNG")
                meta.append(
                    "  obj%d  w=%.2fpt h=%.2fpt  left=%.2fpt top=%.2fpt  -> %s"
                    % (position, obj.Width, obj.Height, obj.Left, obj.Top,
                       os.path.basename(path))
                )
                print(meta[-1])
            with open(os.path.join(OUT_DIR, "chart%d_meta.txt" % index),
                      "w", encoding="utf-8") as handle:
                handle.write("\n".join(meta) + "\n")
            if charts.Count == 0:
                print("  sheet%d %s: 无图表对象" % (index, sheet.Name))
    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()


if __name__ == "__main__":
    main()
