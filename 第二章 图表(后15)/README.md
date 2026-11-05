# 第二章 图表(后15) · Python / matplotlib 复刻

复刻 `第二章 图表(后15).xlsx` 里的图 16~30。每张图一个脚本、一张 PNG；
样式和几何参数都从 xlsx 的图表 XML 与导出图上量得，不靠目测。

| # | 工作表 | 图表 | 脚本 | 输出 |
| --- | --- | --- | --- | --- |
| 16 | 16 波浪水球图 | 水球 + 波浪水面 | `chart16_water_ball.py` | `chart16_water_ball.png` |
| 17 | 17 玉玦图 | 四层圆环（年龄分布） | `chart17_jade_ring.py` | `chart17_jade_ring.png` |
| 18 | 18 跑道图 | 六层圆环（部门人数） | `chart18_track_rings.py` | `chart18_track_rings.png` |
| 19 | 19 南丁格尔圆饼图 | 饼图 + 引线标签 | `chart19_nightingale_pie.py` | `chart19_nightingale_pie.png` |
| 20 | 20 南丁格尔圆环图 | 五层递减圆环 | `chart20_nightingale_doughnut.py` | `chart20_nightingale_doughnut.png` |
| 21 | 20 南丁格尔（PPT） | Freeform 花瓣 + 引线 | `chart21_nightingale_ppt.py` | `chart21_nightingale_ppt.png` |
| 22 | 22 仪表盘图 | 三层圆环 + 指针 | `chart22_gauge.py` | `chart22_gauge.png` |
| 23 | 23 柱形折线图 | 柱形 + 增长率折线 | `chart23_bar_line.py` | `chart23_bar_line.png` |
| 24 | 24 目标柱形图 | 目标框 + 实际柱 | `chart24_target_bar.py` | `chart24_target_bar.png` |
| 25 | 25 子弹图 | 区间背景 + 实际柱 + 目标线 | `chart25_bullet.py` | `chart25_bullet.png` |
| 26 | 26 柱形圆 | 柱形 + 变径圆珠 | `chart26_bar_circle.py` | `chart26_bar_circle.png` |
| 27 | 27 簇状柱形折线图 | 双柱 + 同比折线 | `chart27_clustered_bar_line.py` | `chart27_clustered_bar_line.png` |
| 28 | 28 复合柱形图 | 季度汇总块 + 月柱 | `chart28_compound_bar.py` | `chart28_compound_bar.png` |
| 29 | 29 滑珠图 | 胶囊进度条 + 圆珠 | `chart29_lollipop.py` | `chart29_lollipop.png` |
| 30 | 30 对比滑珠图 | 双圆珠对比 | `chart30_compare_lollipop.py` | `chart30_compare_lollipop.png` |

## 运行

```bash
pip install matplotlib numpy pillow

python chart16_water_ball.py
# ... 或逐个运行 chart17 ~ chart30
```

`chartkit.py` 是公共部件：画布换算、主题色解析、userShapes（含嵌套组合）
展开、从导出图量文字墨迹。脚本里的常数都注明「实测」。

## 文件说明

```
chartkit.py               公共部件（画布、字体、主题色、userShapes 坐标展开）
chartN_*.py               15 张图的脚本
chartN_*.png              15 张复刻输出
export_reference.py       可选：用 Excel COM 重新导出比对基准（需要本机 Excel）
compare_reference.py      可选：复刻图与原图做像素比对
inspect_chart_xml.py      可选：把 chartN.xml 压成可读的样式规格
inspect_usershapes.py     可选：列出图表 userShapes 里的标注框
```

`reference/`（Excel 导出的原图）只在本地用于校核，已在 `.gitignore` 中排除。
