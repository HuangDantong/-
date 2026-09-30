# 第二章 图表复刻（Python / matplotlib）

用 Python 逐像素复刻 `第二章 图表(前15).xlsx` 里的图表。所有样式参数都从
xlsx 内部的图表 XML 里解出来，不是目测估计，并用 Excel COM 把原图导出成
PNG 作为比对基准。

| # | 工作表 | 图表 | 脚本 | 输出 | 与原图误差 |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 渐变柱形图 | 渐变填充柱形图 | `chart1_gradient_bar.py` | `chart1_gradient_bar.png` | 3.27/255，一致率 93.1% |
| 2 | 2 带均值柱形图 | 柱形图 + 均值折线 | `chart2_mean_bar.py` | `chart2_mean_bar.png` | 2.38/255，一致率 96.2% |

「误差」指与原图逐像素的平均通道差（0~255），「一致率」指 RGB 各通道
差值之和小于 12 的像素占比。残余误差集中在文字笔画的抗锯齿上——Excel 和
matplotlib 的光栅化器不同，几何位置已经全部对齐。

## 文件说明

```
chart1_gradient_bar.py    图1 复刻脚本
chart2_mean_bar.py        图2 复刻脚本
chart1_gradient_bar.png   图1 输出
chart2_mean_bar.png       图2 输出
compare_reference.py      与原图的像素级比对工具（两个图通用）
reference/
  chart1_excel.png        图1 原始图表（Excel COM 导出，比对基准）
  chart2_excel.png        图2 原始图表
  chart1_side_by_side.png 图1 左右对照（左原图 / 右复刻）
  chart1_overlay.png      图1 两图 50% 叠加，用于检查错位
  chart2_side_by_side.png 图2 左右对照
  chart2_overlay.png      图2 两图 50% 叠加
  cmp_title.png           图1 标题区放大对照
  cmp_cat.png             图1 类别轴标签放大对照
```

## 运行

```bash
pip install matplotlib numpy pillow
python chart1_gradient_bar.py       # 生成 chart1_gradient_bar.png
python chart2_mean_bar.py           # 生成 chart2_mean_bar.png
python compare_reference.py 1       # 图1 与原图比对
python compare_reference.py 2       # 图2 与原图比对
```

## 数据

两张图用的是同一组数据：

| 区域 | 销售量 |
| --- | ---: |
| 华北 | 2354 |
| 华南 | 1902 |
| 东北 | 3524 |
| 西北 | 2698 |
| 西南 | 2896 |
| 华东 | 2563 |

图 2 的均值仍是表里 `D` 列的 `=AVERAGE($C$3:$C$8)`，即 2656.1666…。
原图标注显示为「平均值：2656」，是按四舍五入显示的。

---

## 图 1 · 渐变柱形图

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

**容易做错的地方：渐变作用在单根柱子上**，不是整个系列。每根柱子的渐变都
铺满自身高度，所以 1902 那根矮柱的顶端颜色和 3524 那根高柱一样深，底端
一样浅。若把渐变铺满整个绘图区，矮柱会明显偏浅。

---

## 图 2 · 带均值柱形图

这是一个「柱形图 + 折线图」的组合图。柱形系列是「销售量」，折线系列是
「均值」——一条横贯所有类别的黄色水平线。

| 元素 | XML 中的定义 | matplotlib 实现 |
| --- | --- | --- |
| 图表区背景 | `srgbClr 1A1E43` | `#1A1E43` |
| 绘图区 | `manualLayout x=0.058831 y=0.234382 w=0.904665 h=0.599871` | `figure.add_axes(...)`，另做 0.5px 修正（见下） |
| 柱形系列 | **纯色** `0070C0`，`gapWidth=219%` | `bar(color="#0070C0")` |
| 折线系列 | `FFC000`，线宽 `19050EMU` = 1.5pt，`cap="rnd"`，无标记点 | `plot(..., lw=2.16, solid_capstyle="round")` |
| 数值轴 | `delete="1"` —— **整条轴被删掉** | `set_yticks([])`、`grid(False)` |
| 类别轴 | 轴线 `bg1 lumMod 95% alpha 50%`，0.75pt；标签 `#F2F2F2` 9pt | 底部脊线 50% 透明，1.08pt |
| 数据标签 | `dLblPos="outEnd"`，9pt，`#F2F2F2` | `annotate`，基线距柱顶约 14px |
| 标题 / 副标题 / 脚注 | 同图1 | 同图1 |
| 均值标注 | 「平均值：2656」微软雅黑 8pt，`FFC000` | 11.52pt，`#FFC000` |

### 三个容易做错的地方

1. **数值轴是删除掉的**（`<c:delete val="1"/>`），所以既没有刻度标签也没有
   网格线。这一点从 XML 才能看出来——光看图可能会以为是「网格线设成了
   透明」。纵轴范围 0~4000 是 Excel 自动取整的结果。
2. **华东那根柱子的数据标签被手工拖过**。`chart2.xml` 里第 6 个点
   （`<c:dLbl><c:idx val="5"/>`）带一个 `manualLayout`，因为 2563 那根柱子
   顶端在 y=267，而均值线正好压在 258，按默认位置标签会和黄线重叠，所以
   作者把它拖到了线下方。脚本里的 `MOVED_LABEL` 就是在还原这个手工调整。
3. **绘图区要上移半个像素**。`manualLayout` 存的是小数坐标，Excel 渲染时
   会取整到设备像素，实际画出来的绘图区比标注值高约 0.5px。按标注值直接
   画，底部轴线会低 1px、均值线也会偏 1px。实测上移 0.5px 后绘图区误差从
   8.21 降到 5.93，所以脚本里做了这个小修正（`AXES_TOP`）。

---

## 两图共用的换算

**字号换算系数是 1.44**。画布按 2 px/pt 还原 Excel 图表（416pt 宽的图表
导出成 832px），而坐标轴文字在 XML 里是 9pt，因此 matplotlib 字号
= 9 × 2 × 72/100 = 12.96pt。标题、副标题、脚注同理。

坐标轴与数据标签的拉丁字形继承主题字体（Calibri），中文继承工作簿默认
字体（等线 DengXian），脚本用 matplotlib 的字体回退列表
`["Calibri", "DengXian"]` 实现；标题/副标题/脚注在 XML 里显式写死了
微软雅黑，所以单独指定。

## 比对结果

```
图1   柱体位置高度全部 dx=0 dy=0，网格线 196/277/358/439/520 一致
      平均通道误差 3.27/255，像素一致率 93.06%

图2   柱体横向 dx=0，均值线 y=257~259 一致
      平均通道误差 2.38/255，像素一致率 96.15%
```

两张图的误差热点都落在标题和副标题的笔画上（如 `y=32 x=288`、
`y=96 x=128`），柱体与网格线区域的误差接近 0。
