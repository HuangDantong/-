# -*- coding: utf-8 -*-
"""导出《第四章 人力资源可视化看板.xlsx》的比对基准。

Excel 里图表是浮在单元格上的，Range.CopyPicture 抓不到它们；所以整张看板
先用 PageSetup 把打印区域设为 P1:Z25，导出 PDF，再用 PyMuPDF 渲染成 PNG。
6 张图表另外单独导出，方便逐张核对。

用法：
    pip install pywin32 pymupdf
    python export_reference.py
"""
import os
import win32com.client
import pymupdf

XLSX = (r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》"
        r"-清华-郭宏远\第四章 人力资源可视化看板.xlsx")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")


def main():
    os.makedirs(OUT, exist_ok=True)
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    wb = excel.Workbooks.Open(XLSX, ReadOnly=True)
    try:
        ws = wb.Worksheets(1)
        # 整张看板：打印区域 P1:Z25 -> PDF -> PNG
        ws.PageSetup.PrintArea = "$P$1:$Z$25"
        ws.PageSetup.Orientation = 2          # 横向
        ws.PageSetup.Zoom = False
        ws.PageSetup.FitToPagesWide = 1
        ws.PageSetup.FitToPagesTall = 1
        pdf = os.path.join(OUT, "dashboard.pdf")
        ws.ExportAsFixedFormat(0, pdf)
        doc = pymupdf.open(pdf)
        doc[0].get_pixmap(dpi=200).save(os.path.join(OUT, "dashboard_excel.png"))
        doc.close()

        # 逐张图表导出
        for i in range(1, ws.ChartObjects().Count + 1):
            ws.ChartObjects(i).Chart.Export(
                os.path.join(OUT, "chart%d_excel.png" % i), "PNG")
    finally:
        wb.Close(SaveChanges=False)
        excel.Quit()


if __name__ == "__main__":
    main()
