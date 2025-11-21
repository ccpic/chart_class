"""
Utility functions for plotting.
"""

from __future__ import annotations
from typing import Sequence, List, Optional
import matplotlib as mpl
import numpy as np
import scipy.stats as stats
import pandas as pd
from typing import Callable, Literal
from textalloc import allocate_text


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


def normed_cmap(
    s: pd.Series,
    cmap: mpl.colors.LinearSegmentedColormap,
    num_stds: float = 2.5,
    *args,
    **kwargs,
) -> Callable:
    """Returns a normalized colormap function that takes a float as an argument and
    returns an rgba value.

    Args:
        s (pd.Series):
            a series of numeric values
        cmap (mpl.colors.LinearSegmentedColormap):
            matplotlib Colormap
        num_stds (float, optional):
            vmin and vmax are set to the median ± num_stds.
            Defaults to 2.5.

    Returns:
        Callable: Callable that takes a float as an argument and returns an rgba value.
    """

    # if len(s) == 1:
    #     return lambda x: (238/255, 238/255, 238/255, 1)

    _median = s.median()
    _std = s.std()

    vmin = kwargs.get("vmin")
    if vmin is None:
        vmin = _median - num_stds * _std
    vmax = kwargs.get("vmax")
    if vmax is None:
        vmax = _median + num_stds * _std

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    m = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

    return m.to_rgba


def format_value(
    val: float,
    fmt: str = "{:,.0f}",
    unit: Literal["亿", "百万", "万", "千", None] = None,
    empty_zero: bool = True,
    empty_nan: bool = True,
) -> str:
    """
    格式化数值为指定格式或单位的字符串
    :param val: 数值
    :param fmt: 格式字符串
    :param unit: 单位（亿、百万、万、千）或 None
    :return: 转换后的字符串
    """
    # 如果值不是数值类型（如字符串），直接返回字符串表示
    if not isinstance(val, (int, float, np.number)):
        return str(val) if val is not None else ""

    # 检查是否为 NaN（仅对数值类型）
    if np.isnan(val):
        if empty_nan:
            return ""
        else:
            return "nan"

    if val == 0:
        if empty_zero:
            return ""
        else:
            return fmt.format(val)

    if unit:
        scale = {"亿": 1e8, "百万": 1e6, "万": 1e4, "千": 1e3}.get(unit)
        if scale:
            val /= scale
        else:
            raise ValueError("Invalid unit specified.")
    return fmt.format(val)