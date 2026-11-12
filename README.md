# 大数据分析及数据可视化 · 课程实验仓库

把《Excel 数据可视化——从图表到数据大屏》（清华·郭宏远）里的 **30 张静态图表、
7 张动态图表和 2 张数据大屏**全部迁移成 Python / matplotlib 实现。每张图都有
独立脚本、PNG 输出；动态图额外带 GIF；数据大屏支持按月份联动。

> 复刻不是“看着像”，而是从 xlsx 内部的 `chartN.xml`、`drawingN.xml` 里解析
> 颜色、字号、manualLayout 和 userShapes，再用 Excel COM 导出原图做逐像素比对。

## 成果一览

| 章节 | 内容 | 数量 | 入口 |
| --- | --- | ---: | --- |
| 第二章（前 15） | 渐变柱、均值线、蝴蝶图、甘特图、水球图等 | 15 | [查看](<第二章 图表(前15)/>) |
| 第二章（后 15） | 玉玦、跑道、南丁格尔、仪表盘、子弹图、滑珠图等 | 15 | [查看](<第二章 图表(后15)/>) |
| 第三章 | 下拉框 / 选项按钮 / 复选框 / VBA 驱动的动态图表 | 7 | [查看](<第三章 动态图表/>) |
| 第四章 | 销售数据大屏（11 个图表 + 4 个 KPI 环） | 1 | [查看](<第四章 销售看板/>) |
| 第四章 | 人力资源结构看板（6 个图表） | 1 | [查看](<第四章 人力资源可视化看板/>) |

合计 **39 个实验**：30 张静态图 + 7 张动态图（每张附循环 GIF）+ 2 张看板。

## 预览

<table>
<tr>
<td align="center"><img src="第二章%20图表(前15)/chart3_rounded_gradient_bar.png" width="360"><br><sub>渐变圆角柱形图</sub></td>
<td align="center"><img src="第二章%20图表(后15)/chart19_nightingale_pie.png" width="360"><br><sub>南丁格尔圆饼图</sub></td>
<td align="center"><img src="第三章%20动态图表/chart34_dynamic_combo.gif" width="360"><br><sub>复选框动态组合图</sub></td>
</tr>
<tr>
<td align="center" colspan="1"><img src="第四章%20销售看板/dashboard.png" width="360"><br><sub>销售数据大屏（可切换月份）</sub></td>
<td align="center" colspan="1"><img src="第四章%20人力资源可视化看板/dashboard.png" width="360"><br><sub>人力资源结构看板</sub></td>
<td align="center"><img src="第二章%20图表(前15)/chart1_gradient_bar.png" width="360"><br><sub>渐变填充柱形图</sub></td>
</tr>
</table>

## 快速开始

```bash
pip install -r requirements.txt

# 静态图：进入对应章节，运行任意脚本
cd "第二章 图表(前15)"
python chart1_gradient_bar.py
python chart5_clustered_bar.py

# 动态图：--month / --period / --dept 等参数可切换控件状态
cd "../第三章 动态图表"
python chart31_dynamic_column.py --month 3
python chart31_dynamic_column.py --gif

# 数据大屏：默认 9 月，--gif 生成 12 个月循环动画
cd "../第四章 销售看板"
python dashboard.py
python dashboard.py --month 3
python dashboard.py --gif

cd "../第四章 人力资源可视化看板"
python dashboard.py
```

仓库内已附带离线数据（`第四章 销售看板/data/summary.json`、
`第四章 人力资源可视化看板/data/summary.json`、`第二章 图表(前15)/data/chart_meta.json`），
**没有原始课程 xlsx 也能直接运行**。若本机有源文件，脚本会优先从 xlsx 现算。

## 复刻方法与质量

1. **解样式**：从 xlsx（zip）里读图表 XML，取系列颜色、字号、数据标签、坐标轴、
   绘图区 manualLayout；从 drawing XML 取标题、副标题、标注框等 userShapes。
2. **导出原图**：Windows + Excel COM 把每张图导出成 PNG 作为比对基准；
   大屏的图表浮在单元格上，改用“打印区域 → PDF → PNG”。
3. **逐像素比对**：`compare_reference.py` 计算平均通道误差和像素一致率，
   残余误差主要来自 Excel 与 matplotlib 的文字抗锯齿差异。

| 部分 | 平均通道误差 | 像素一致率 |
| --- | ---: | ---: |
| 第二章 30 张静态图 | 1.6 – 5.8 / 255 | 87% – 96% |
| 第四章 销售看板 | 5.34 / 255 | 91.07% |
| 第四章 人力资源看板 | 3.28 / 255 | 94.38% |

## 仓库结构

```
README.md                         本文件
requirements.txt                  Python 依赖
第二章 图表(前15)/                 图 1–15：脚本 + PNG + data/chart_meta.json
第二章 图表(后15)/                 图 16–30：脚本 + PNG
第三章 动态图表/                   图 31–37：脚本 + PNG + GIF
第四章 销售看板/                   销售数据大屏：dashboard.py/.png/.gif + data/
第四章 人力资源可视化看板/          人员结构看板：dashboard.py/.png + data/
```

每个章节目录里都有自己的 `README.md`，说明该章的图表清单、数据口径、运行参数
和复刻要点；`reference/` 为本地比对基准，已被 `.gitignore` 排除。

## 说明

- 原始课程文件（xlsx / xlsm / PDF / zip）未纳入本仓库；需要重新导出比对基准时，
  按各章 README 的说明运行 `export_reference.py`（依赖 Windows + Excel）。
- 旧版 `可视化代码/` 已从 git 索引移除，本地文件保留在 `.gitignore` 中。
- `olist-analysis/` 是独立的 Olist 商业分析项目，有自己的仓库，未混入本仓库。

## 链接

- GitHub: <https://github.com/HuangDantong/->
- Gitee: 待补充（仓库地址确认后更新）
