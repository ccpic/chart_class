"""
Utility functions for plotting.
"""

from __future__ import annotations
from typing import Sequence
import matplotlib as mpl
import numpy as np
import scipy.stats as stats


def scatter_hist(ax: mpl.axes.Axes, x: Sequence, y: Sequence) -> mpl.axes.Axes:
    """在指定scatter ax绘制x,y轴histogram

    Args:
        ax (mpl.axes.Axes): 指定ax
        x (Sequence): scatter的x轴数据
        y (Sequence): scatter的y轴数据

    Returns:
        mpl.axes.Axes: 返回ax_histy，用于后续调整legend位置
    """

    # 创建ax
    ax_histx = ax.inset_axes([0, 1.01, 1, 0.2], sharex=ax)
    ax_histy = ax.inset_axes([1.01, 0, 0.2, 1], sharey=ax)

    # 去除ticklabels
    ax_histx.tick_params(axis="x", labelbottom=False, length=0)
    ax_histx.tick_params(axis="y", length=0)
    ax_histy.tick_params(axis="x", length=0)
    ax_histy.tick_params(axis="y", labelleft=False, length=0)

    ax_histx.hist(x, color="grey")
    ax_histy.hist(y, orientation="horizontal", color="grey")

    # label
    ax_histx.set_ylabel(f"{x.name}分布")
    ax_histy.set_xlabel(f"{y.name}分布")

    return ax_histy


def regression_band(
    ax: mpl.axes.Axes,
    x: Sequence,
    y: Sequence,
    show_ci: bool = True,
    show_pi: bool = False,
) -> None:
    """在指定ax绘制线性拟合区间

    Args:
        ax (mpl.axes.Axes): 指定ax.
        x (Sequence): 自变量.
        y (Sequence): 因变量.
        show_ci (bool, optional): 是否展示confidence interval. Defaults to True.
        show_pi (bool, optional): 是否展示95% prediction limit. Defaults to False.
    """

    n = len(x)
    if n > 2:  # 数据点必须大于cov矩阵的scale
        p, cov = np.polyfit(x, y, 1, cov=True)  # 简单线性回归返回parameter和covariance
        poly1d_fn = np.poly1d(p)  # 拟合方程
        y_model = poly1d_fn(x)  # 拟合的y值
        m = p.size  # 参数个数

        dof = n - m  # degrees of freedom
        t = stats.t.ppf(0.975, dof)  # 显著性检验t值

        # 拟合结果绘图
        ax.plot(
            x,
            y_model,
            ":",
            color="0.1",
            linewidth=1,
            alpha=0.5,
            label="Fit",
            zorder=1,
        )

        # 误差估计
        resid = y - y_model  # 残差
        s_err = np.sqrt(np.sum(resid**2) / dof)  # 标准误差

        # 拟合CI和PI
        x2 = np.linspace(np.min(x), np.max(x), 100)
        y2 = poly1d_fn(x2)

        # CI计算和绘图
        if show_ci:
            ci = (
                t
                * s_err
                * np.sqrt(
                    1 / n + (x2 - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2)
                )
            )
            ax.fill_between(
                x2,
                y2 + ci,
                y2 - ci,
                color="grey",
                edgecolor=["none"],
                alpha=0.1,
                zorder=0,
            )

        # Pi计算和绘图
        if show_pi:
            pi = (
                t
                * s_err
                * np.sqrt(
                    1 + 1 / n + (x2 - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2)
                )
            )
            ax.fill_between(
                x2, y2 + pi, y2 - pi, color="None", linestyle="--", linewidth=1
            )
            ax.plot(x2, y2 - pi, "--", color="0.5", label="95% Prediction Limits")
            ax.plot(x2, y2 + pi, "--", color="0.5")
