# -*- coding: utf-8 -*-
"""图 16 · 波浪水球图（2022 上半年完成率 65%）。

Excel 里其实是一张单柱柱形图：两根系列的柱子都用图片填充（实心圆 + 圆环），
再按 65% 裁切。导出图上看到的就是「圆环 + 蓝色水体 + 波浪水面 + 40pt 的
65%」。这里直接按导出图逐像素还原几何：

- 外环：userShapes 的椭圆，锚框拉伸后圆心 (200.3, 197.9)，半径 192×190px，
  #0070C0、1.5pt；
- 水面：对参考图逐列量出水面纵坐标，最小二乘拟合出周期 180px、振幅 11.8px
  的余弦（实测），水体 #0070C0，用外圆裁剪；
- 文字：40pt 微软雅黑白色，墨迹范围 x=144~275、y=156~208（实测）。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon

import chartkit as kit

W, H = kit.chart_size(16)
CX, CY = 200.5, 198.5
RX, RY = 191.0, 189.0
WATER_CX, WATER_CY, WATER_R = 202.0, 197.5, 174.0
BLUE = "#0070C0"

# 水面：y(x) = 162.6 + 11.8·cos(2πx/180 + 0.811)（对参考图水面逐列测量后拟合）
WAVE_MEAN, WAVE_AMP, WAVE_PERIOD, WAVE_PHASE = 162.6, 11.8, 180.0, 0.811


def wave_y(x):
    return WAVE_MEAN + WAVE_AMP * np.cos(2 * np.pi * x / WAVE_PERIOD + WAVE_PHASE)


def main():
    fig = kit.new_figure(W, H)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")

    circle = Ellipse((CX, CY), 2 * RX, 2 * RY, facecolor="none", edgecolor="none")
    ax.add_patch(circle)
    water_circle = Ellipse((WATER_CX, WATER_CY), 2 * WATER_R, 2 * WATER_R,
                           facecolor="none", edgecolor="none")
    ax.add_patch(water_circle)

    xs = np.linspace(0, W, 600)
    surface = np.column_stack([np.r_[xs, W, 0], np.r_[wave_y(xs), H, H]])
    water = Polygon(surface, closed=True, facecolor=BLUE, edgecolor="none")
    water.set_clip_path(water_circle)
    ax.add_patch(water)

    ax.add_patch(Ellipse((CX, CY), 2 * RX - 3, 2 * RY - 3, facecolor="none",
                         edgecolor=BLUE, linewidth=3 * 0.72))

    ax.text(209.5, 188.0, "65%", color="white", fontsize=40 * kit.FONT_SCALE,
            fontfamily="Calibri", ha="center", va="center")

    kit.save(fig, "chart16_water_ball.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
