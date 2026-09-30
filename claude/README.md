# 第二章 图表复刻 · 图1 渐变柱形图

用 Python (matplotlib) 逐像素复刻 `第二章 图表(前15).xlsx` 工作表
「1 渐变柱形图」中的图表。

| 项目 | 内容 |
| --- | --- |
| 数据源 | `'1 渐变柱形图'!$B$3:$C$8` |
| 图表类型 | 簇状柱形图（纵向）+ 线性渐变填充 |
| 输出尺寸 | 832 × 617 px（与原图表 416 × 308.75 pt 等比，2 px/pt） |
| 复刻精度 | 与 Excel 导出图平均通道误差 **3.27 / 255**，像素一致率 **93.1%** |

## 文件说明

```
chart1_gradient_bar.py    复刻脚本（运行入口）
chart1_gradient_bar.png   脚本输出图
compare_reference.py      与原图的像素级比对工具
reference/
  chart1_excel.png        用 Excel COM 从 xlsx 导出的原始图表（比对基准）
  side_by_side.png        左原图 / 右复刻图
  overlay.png             两图 50% 叠加，用于检查是否错位
  cmp_title.png           标题区放大对照（上原图 / 下复刻）
  cmp_cat.png             类别轴标签放大对照
```

## 运行

```bash
pip install matplotlib numpy pillow
python chart1_gradient_bar.py          # 生成 chart1_gradient_bar.png
python compare_reference.py            # 与原图比对，打印几何差异与误差
```

## 数据

| 区域 | 销售量 |
| --- | ---: |
| 华北 | 2354 |
| 华南 | 1902 |
| 东北 | 3524 |
| 西北 | 2698 |
| 西南 | 2896 |
| 华东 | 2563 |

## 样式规格

所有参数直接取自 xlsx 内的图表 XML（`xl/charts/chart1.xml` 与
`xl/drawings/drawing2.xml`），不是目测估计：

| 元素 | XML 中的定义 | matplotlib 实现 |
| --- | --- | --- |
| 图表区背景 | `srgbClr 1A1E43` | `#1A1E43` |
| 绘图区 | `manualLayout x=0.143995 y=0.318858 w=0.760232 h=0.525407` | `figure.add_axes(...)` |
| 柱形渐变 | `gradFill` 线性 `ang=5400000`（自上而下），`pos=0 → 0070C0`，`pos=100000 → 00B0F0` | 逐柱 `imshow` + 柱体作裁剪路径 |
| 柱宽 / 间距 | `gapWidth=219%` → 柱宽 = 类别宽 / 3.19 | `width = 1 / 3.19` |
| 数值轴 | `majorUnit=1000`，0~4000 | `yticks([0,1000,2000,3000,4000])` |
| 数值轴文字 | `bg1 lumMod 95%` | `#F2F2F2`，9pt |
| 网格线 | `tx1 lumMod 15% lumOff 85% alpha 20%`，`9525EMU`(0.75pt)，`prstDash="lgDash"` | `#D9D9D9 @ 20%`，1.08pt，虚线 |
| 数据标签 | `dLblPos="outEnd"`，`showVal=1`，9pt 白色 | `annotate`，基线距柱顶 15px |
| 标题 | 微软雅黑 20pt 加粗，行距 24pt | 28.8pt 加粗 |
| 副标题 | 微软雅黑 14pt，行距 24pt | 20.16pt |
| 脚注 | 微软雅黑 8pt，`bg1 lumMod 85%` | 11.52pt，`#D9D9D9` |

### 两点容易做错的细节

1. **渐变作用在单根柱子上**，而不是整个系列。每根柱子的渐变都铺满
   自身高度，所以 1902 那根矮柱的顶端颜色和 3524 那根高柱一样深，
   底端一样浅。若把渐变铺满整个绘图区，矮柱会明显偏浅。
2. **字号换算系数是 1.44**。画布按 2 px/pt 还原 Excel 图表，而坐标轴
   文字在 XML 里是 9pt，因此 matplotlib 字号 = 9 × 2 × 72/100 = 12.96pt。
   标题、副标题、脚注同理。

坐标轴与数据标签的拉丁字形继承主题字体 (Calibri)，中文继承工作簿
默认字体（等线 DengXian），脚本用 matplotlib 的字体回退列表
`["Calibri", "DengXian"]` 实现；标题/副标题/脚注在 XML 中显式写死了
微软雅黑，因此单独指定。

## 比对结果

```
柱体 (x0,x1,ytop,ybot)      六根柱子位置与高度全部 dx=0 dy=0
网格线 y                    196/277/358/439/520 与原图一致
平均通道误差                3.27 / 255
像素近似一致率              93.06%
```

残余误差集中在文字笔画的抗锯齿上（Excel 与 matplotlib 的
光栅化器不同），几何位置已经完全对齐。误差热点分布：

```
err=130.2  y= 32 x=288   ← 标题笔画
err=112.8  y=576 x=192   ← 脚注笔画
err=100.0  y=256 x=576   ← 数据标签 "2896"
```

柱体与网格线区域的误差接近 0。
