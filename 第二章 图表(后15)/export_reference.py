# -*- coding: utf-8 -*-
"""把 `第二章 图表(后15).xlsx` 的图表用 Excel 导出成 PNG，作为复刻比对基准。

用法：
    python export_reference.py

输出（reference/，仅本地比对用，不随复刻成果提交）：
    chart{N}_excel.png      第 N 张图（N = 16..30）对应的图表对象
    chart{N}_excel_1.png    同一张工作表里有多个图表对象时按对象顺序编号
    chart{N}_meta.txt       图表对象数量、尺寸与位置
"""

import os

import win32com.client

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第二章 图表(后15).xlsx")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    workbook = excel.Workbooks.Open(XLSX)
    try:
        for position, index in enumerate(range(1, workbook.Worksheets.Count + 1)):
            number = 15 + index
            sheet = workbook.Worksheets(index)
            charts = sheet.ChartObjects()
            meta = ["sheet=%s  chart_objects=%d" % (sheet.Name, charts.Count)]
            for object_position in range(1, charts.Count + 1):
                obj = charts.Item(object_position)
                if charts.Count == 1:
                    name = "chart%d_excel.png" % number
                else:
                    name = "chart%d_excel_%d.png" % (number, object_position)
                path = os.path.join(OUT_DIR, name)
                obj.Chart.Export(path, "PNG")
                meta.append(
                    "  obj%d  w=%.2fpt h=%.2fpt  left=%.2fpt top=%.2fpt  -> %s"
                    % (object_position, obj.Width, obj.Height, obj.Left, obj.Top,
                       name)
                )
                print(meta[-1])
            with open(os.path.join(OUT_DIR, "chart%d_meta.txt" % number),
                      "w", encoding="utf-8") as handle:
                handle.write("\n".join(meta) + "\n")
            if charts.Count == 0:
                print("  chart%d %s: 无图表对象" % (number, sheet.Name))
    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()


if __name__ == "__main__":
    main()
