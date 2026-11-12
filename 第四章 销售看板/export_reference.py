# -*- coding: utf-8 -*-
"""用 Excel COM 导出《第四章 销售看板参考.xlsx》的看板整图与 11 张图表，
作为 Python 复刻的比对基准（仅本地使用）。"""
import os
import win32com.client

XLSX = r"D:\大数据分析及数据可视化\《Excel数据可视化 - 从图表到数据大屏》-清华-郭宏远\第四章 销售看板参考.xlsx"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")

def main():
    os.makedirs(OUT, exist_ok=True)
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    wb = excel.Workbooks.Open(XLSX, ReadOnly=True)
    try:
        ws = wb.Worksheets("数据大屏")
        print("used range", ws.UsedRange.Address)
        # 整张看板：复制区域 -> 粘到临时图表 -> 导出
        rng = ws.Range("E1:X40")
        rng.CopyPicture(1, 2)  # xlScreen, xlBitmap
        tmp = ws.ChartObjects().Add(1200, 200, rng.Width, rng.Height)
        tmp.Chart.Paste()
        tmp.Chart.Export(os.path.join(OUT, "dashboard_excel.png"), "PNG")
        tmp.Delete()
        # 逐张图表导出
        for i in range(1, ws.ChartObjects().Count + 1):
            obj = ws.ChartObjects(i)
            name = "chart%d_excel.png" % i
            obj.Chart.Export(os.path.join(OUT, name), "PNG")
            print("chart%d" % i, obj.Name, round(obj.Width,1), round(obj.Height,1), round(obj.Left,1), round(obj.Top,1))
        # 数据大屏展示页也导一张
        try:
            ws2 = wb.Worksheets("数据大屏展示")
            ws2.Range("A1:Z60").CopyPicture(1, 2)
            tmp = ws.ChartObjects().Add(1200, 200, 1400, 800)
            tmp.Chart.Paste()
            tmp.Chart.Export(os.path.join(OUT, "dashboard_show.png"), "PNG")
            tmp.Delete()
        except Exception as e:
            print("show sheet:", e)
    finally:
        wb.Close(SaveChanges=False)
        excel.Quit()

if __name__ == "__main__":
    main()
