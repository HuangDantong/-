# 第三章 动态图表 · Python / matplotlib 复刻

> [← 返回总目录](../README.md)


复刻 `第三章 动态图表.xlsm` 里的 7 张动态图表。每张图一个脚本，可指定控件
状态生成对应 PNG；加 `--gif` 会遍历所有状态生成循环动画，直接展示“动起来”
的效果。

| # | 工作表 | 图表 | 驱动方式 | 脚本 / 输出 |
| --- | --- | --- | --- | --- |
| 31 | 1 动态柱形图 | 6 区域销量柱形 | 下拉框选月份（J3） | `chart31_dynamic_column.py/.png/.gif` |
| 32 | 2 动态跑道图 | 6 部门同心跑道 | Q5 选月份 | `chart32_dynamic_track.py/.png/.gif` |
| 33 | 3 动态南丁格尔圆环图 | 流量来源层叠圆环 | 选项按钮选 7/30 天（I3） | `chart33_dynamic_nightingale.py/.png/.gif` |
| 34 | 4 动态组合图 | 销售额/利润/利润率 | 3 个复选框（C13:E13） | `chart34_dynamic_combo.py/.png/.gif` |
| 35 | 5 透视表切片器 | 各学历平均月收入 | 部门切片器 | `chart35_pivot_slicer.py/.png/.gif` |
| 36 | 6 VBA动态玉玦图 | 流量来源四层玉玦 | 2 个 VBA 按钮改 H3 | `chart36_vba_jade_ring.py/.png/.gif` |
| 37 | 7 动态滑珠图 | 区域/月份达成率滑珠 | 选项按钮 + 下拉框（K2/K3） | `chart37_dynamic_lollipop.py/.png/.gif` |

## 运行

```bash
pip install matplotlib numpy pillow

python chart31_dynamic_column.py                  # 默认状态
python chart31_dynamic_column.py --month 3        # 指定月份
python chart31_dynamic_column.py --gif            # 生成 6 个月循环动画

python chart33_dynamic_nightingale.py --period 30
python chart34_dynamic_combo.py --hide profit rate
python chart35_pivot_slicer.py --dept 销售
python chart36_vba_jade_ring.py --period 7
python chart37_dynamic_lollipop.py --mode region --region 华南
```

## 动态机制对应关系

- **图 31**：源数据 `B4:H9` 为 6 个月 × 6 区域；下拉框链接 `J3`，`B13:H13`
  用 `INDEX/VLOOKUP` 取所选月份一行。
- **图 32**：`H4:I9` 用 `MATCH($Q$5,...)+1` 取月份列；占位列
  `J = 总人数/2 − 本部门人数`，所以每条弧都是 `人数/(总人数/2)` 圈。
- **图 33**：`I3` 是选项按钮的值（1/2），`B13:G13` 用 `HLOOKUP` 取
  「近7天/近30天」一行；6 个同心系列逐层少填一个点。
- **图 34**：`C13/D13/E13` 三个复选框；隐藏时对应系列写入负哨兵
  （-100/-200/-2），落在坐标轴外。
- **图 35**：透视表按「学历」行字段、月收入平均值；切片器筛选「部门」。
  脚本直接从 `5 人力资源明细` 的 1470 行原始数据现算 7 个部门的均值。
- **图 36**：两个按钮的 VBA 只做一件事——把 `H3` 写成「近7天/近30天」；
  `B11:F12` 用 `VLOOKUP` 取值，占位 = 50% − 占比。
- **图 37**：`K2` 选「按月份/按区域」，`K3` 选具体项；`B15:F20` 用
  `IF + VLOOKUP/HLOOKUP` 把另一个维度铺成 6 行。

## 文件说明

```
chartkit.py             公共部件（画布换算、字体、主题色、userShapes）
chartN_*.py             7 张图的脚本（每个都有 --gif）
chartN_*.png            各图默认状态的复刻结果
chartN_*.gif            动态循环演示
export_reference.py     可选：用 Excel COM 重新导出比对基准（需要本机 Excel）
compare_reference.py    可选：复刻图与原图做像素比对
```

`reference/`（Excel 导出的原图）只在本地校核，已在 `.gitignore` 中排除。
