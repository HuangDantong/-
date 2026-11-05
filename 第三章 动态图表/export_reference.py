# -*- coding: utf-8 -*-
"""把 `第三章 动态图表.xlsm` 的 7 张图表用 Excel 导出成 PNG，作为比对基准。

用法：
    python export_reference.py

输出（reference/，仅本地比对用，不随复刻成果提交）：
    chart{N}_excel.png      第 N 张图（N = 31..37）对应的图表对象
    chart{N}_meta.txt       图表对象尺寸与位置
"""

import os

import win32com.client

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第三章 动态图表.xlsm")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")
SHEETS = {1: 31, 2: 32, 3: 33, 4: 34, 6: 35, 7: 36, 8: 37}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    workbook = excel.Workbooks.Open(XLSX, ReadOnly=True)
    try:
        for sheet_index, number in SHEETS.items():
            sheet = workbook.Worksheets(sheet_index)
            charts = sheet.ChartObjects()
            meta = ["sheet=%s  chart_objects=%d" % (sheet.Name, charts.Count)]
            for position in range(1, charts.Count + 1):
                obj = charts.Item(position)
                name = "chart%d_excel.png" % number
                obj.Chart.Export(os.path.join(OUT_DIR, name), "PNG")
                meta.append(
                    "  obj%d  w=%.2fpt h=%.2fpt  left=%.2fpt top=%.2fpt  -> %s"
                    % (position, obj.Width, obj.Height, obj.Left, obj.Top, name))
                print(meta[-1])
            with open(os.path.join(OUT_DIR, "chart%d_meta.txt" % number),
                      "w", encoding="utf-8") as handle:
                handle.write("\n".join(meta) + "\n")
    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()


if __name__ == "__main__":
    main()
