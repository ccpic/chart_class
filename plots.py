from __future__ import annotations
from wordcloud import WordCloud
from typing import Any, Dict, List, Tuple, Union, Optional, Sequence, Literal
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from adjustText import adjust_text
import scipy.stats as stats
from mpl_toolkits.axes_grid1 import make_axes_locatable
import warnings
import math
from itertools import cycle
import squarify
from color import Colors
from pywaffle import Waffle
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles
from plottable import ColumnDefinition, Table


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

    # # 令histy的宽度等于histx的高度
    # pos_x = ax_histx.get_position()
    # pos_y = ax_histy.get_position()
    # pos_y.x1 = pos_y.x0 + pos_x.y1 - pos_x.y0
    # ax_histy.set_position(pos_y)

    # 去除ticklabels
    ax_histx.tick_params(axis="x", labelbottom=False, length=0)
    ax_histx.tick_params(axis="y", length=0)
    ax_histy.tick_params(axis="x", length=0)
    ax_histy.tick_params(axis="y", labelleft=False, length=0)

    # # 根据binwidth计算lim
    # binwidth = 0.25
    # xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    # lim = (int(xymax / binwidth) + 1) * binwidth
    # bins = np.arange(-lim, lim + binwidth, binwidth)

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
    # n: int,
    show_ci: bool = True,
    show_pi: bool = False,
) -> None:
    """在指定ax绘制线性拟合区间

    Args:
        ax (mpl.axes.Axes): 指定ax.
        x (Sequence): 自变量.
        y (Sequence): 因变量.
        n (int): 观察例数.
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


class Plot:
    def __init__(
        self,
        data,  # 原始数
        ax=None,
        fontsize: int = 14,  # 字体大小
        fmt: str = "{:,.0f}",  # 基本数字格式
        style: Dict[str, Any] = {},  # 风格字典
        color_dict: Optional[Dict[str, str]] = None,  # 颜色字典
        cmap_qual: Optional[mpl.colors.Colormap] = None,  # 分类颜色映射
        cmap_norm: Optional[mpl.colors.Colormap] = None,  # 正态分布颜色映射
        hue: Optional[str] = None,  # 颜色映射列名
        focus: Optional[List[str]] = None,  # 重点关注的index，可依此做后续操作
        *args,
        **kwargs,
    ):
        self.data = (
            data.to_frame() if isinstance(data, pd.Series) else data
        )  # 把pd.Series也转化为pd.Dataframe处理
        self.ax = ax or plt.gca()
        self.fontsize = fontsize
        self.figure = self.ax.get_figure()
        self.fmt = fmt
        self._style = style
        self.style = self.Style(self, **self._style)
        self._color_dict = (
            {**self.figure._color_dict, **color_dict}
            if color_dict
            else self.figure._color_dict
        )
        self._cmap_qual = self.figure._cmap_qual if cmap_qual is None else cmap_qual
        self._cmap_norm = self.figure._cmap_norm if cmap_norm is None else cmap_norm
        self._colors = Colors(
            color_dict=self._color_dict,
            cmap_qual=self._cmap_qual,
            cmap_norm=self._cmap_norm,
        )
        if hue is not None:
            self.hue = self.data.loc[:, hue]
        else:
            self.hue = None
        self.focus = focus

    class Style:
        def __init__(self, plot, **kwargs) -> None:
            self._plot = plot

            """默认风格字典"""
            d_style = {
                # 图表的一些风格
                "title": None,  # 图表标题
                "title_fontsize": plot.fontsize,  # 图表标题字体大小
                "major_grid": None,  # 主网格线
                "minor_grid": None,  # 次网格线
                "hide_top_right_spines": False,  # 是否隐藏上/右边框
                # 坐标轴相关的风格
                "xlabel": None,  # x轴标题
                "xlabel_fontsize": plot.fontsize,  # x轴标题字体大小
                "ylabel": None,  # y轴标题
                "ylabel_fontsize": plot.fontsize,  # y轴标题字体大小
                "xlim": None,  # x轴边界(最小值, 最大值)
                "ylim": None,  # y轴边界(最小值, 最大值)
                "y2lim": None,  # y轴次坐标轴边界(最小值, 最大值)
                # 刻度相关的风格
                "all_xticks": False,  # 显示所有x轴刻度
                "xticklabel_fontsize": plot.fontsize,  # x轴刻度标签字体大小
                "yticklabel_fontsize": plot.fontsize,  # y轴刻度标签字体大小
                "xticklabel_rotation": None,  # x抽刻度标签旋转角度
                "yticklabel_rotation": None,  # y抽刻度标签旋转角度
                "remove_xticks": False,  # 是否移除x轴刻度
                "remove_yticks": False,  # 是否移除y轴刻度
                "xticks_interval": None,  # x轴刻度间隔
                "yticks_interval": None,  # y轴刻度间隔
                "xticks_length": 0,  # x轴刻度长度
                "yticks_length": 0,  # y轴刻度长度
                # 图例
                "show_legend": True,  # 是否展示ax图例
                "legend_loc": "center left",  # 图例位置
                "legend_ncol": 1,  # 图例列数
            }

            """根据初始化参数更新默认风格字典，并循环生成类属性"""
            d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}
            for key, value in d_style.items():
                self.__setattr__(f"_{key}", value)

        def apply_style(self) -> None:
            """执行一遍风格设置，不能放在初始化阶段因为一些风格在绘图后才生效"""
            self.title(self._title, self._title_fontsize)
            self.xlabel(self._xlabel, self._xlabel_fontsize)
            self.ylabel(self._ylabel, self._ylabel_fontsize)
            self.tick_params(
                self._xticklabel_fontsize,
                self._yticklabel_fontsize,
                self._xticklabel_rotation,
                self._yticklabel_rotation,
                self._xticks_length,
                self._yticks_length,
            )
            if self._all_xticks:
                self.all_xticks()
            if self._xticks_interval is not None:
                self.xticks_interval(self._xticks_interval)
            if self._yticks_interval is not None:
                self.yticks_interval(self._yticks_interval)
            if self._remove_xticks:
                self.remove_xticks()
            if self._remove_yticks:
                self.remove_yticks()
            if self._hide_top_right_spines:
                self.hide_top_right_spines()
            if self._xlim is not None:
                self.xlim(self._xlim)
            if self._ylim is not None:
                self.ylim(self._ylim)
            if self._y2lim is not None:
                self.y2lim(self._y2lim)
            if self._major_grid is not None:
                self.major_grid(**self._major_grid)
            if self._minor_grid is not None:
                self.minor_grid(**self._minor_grid)
            if self._show_legend:
                self.legend(self._legend_loc, self._legend_ncol)

        def title(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            """添加图表的标题

            Parameters
            ----------
            title : Optional[str], optional
                标题文字内容, by default None
            fontsize : Optional[float], optional
                标题字体大小, by default None
            """
            self._plot.ax.set_title(title, fontsize=fontsize)

        def all_xticks(self):
            self._plot.ax.set(xticks=self._plot.data.index)

        def tick_params(
            self,
            xticklabel_fontsize: Optional[float] = None,
            yticklabel_fontsize: Optional[float] = None,
            xticklabel_rotation: Optional[float] = None,
            yticklabel_rotation: Optional[float] = None,
            xticks_length: float = 0,
            yticks_length: float = 0,
        ) -> None:
            """设置刻度标签样式

            Parameters
            ----------
            xticklabel_fontsize : Optional[float], optional
                x轴刻度标签字体大小, by default None
            yticklabel_fontsize : Optional[float], optional
                y轴刻度标签字体大小, by default None
            xticklabel_rotation : Optional[float], optional
                x轴刻度标签旋转角度, by default None
            yticklabel_rotation : Optional[float], optional
                y轴刻度标签旋转角度, by default None
            """
            self._plot.ax.tick_params(
                axis="x",
                labelsize=xticklabel_fontsize,
                labelrotation=xticklabel_rotation,
                length=xticks_length,
            )
            self._plot.ax.tick_params(
                axis="y",
                labelsize=yticklabel_fontsize,
                labelrotation=yticklabel_rotation,
                length=yticks_length,
            )

        def remove_xticks(self) -> None:
            """移除x轴刻度"""
            self._plot.ax.get_xaxis().set_ticks([])

        def remove_yticks(self) -> None:
            """移除y轴刻度"""
            self._plot.ax.get_yaxis().set_ticks([])

        def xticks_interval(self, interval: float) -> None:
            """设置x轴刻度间隔

            Args:
                interval (float): 刻度间隔
            """
            self._plot.ax.xaxis.set_major_locator(MultipleLocator(interval))

        def yticks_interval(self, interval: float) -> None:
            """设置y轴刻度间隔

            Args:
                interval (float,): 刻度间隔
            """
            self._plot.ax.yaxis.set_major_locator(MultipleLocator(interval))

        def xlabel(
            self, label: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            """设置x轴标题

            Parameters
            ----------
            label : Optional[str], optional
                x轴标题内容, by default None
            fontsize : Optional[float], optional
                x轴标题字体大小, by default None
            """
            self._plot.ax.set_xlabel(label, fontsize=fontsize)

        def ylabel(
            self, label: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            """设置y轴标题

            Parameters
            ----------
            label : Optional[str], optional
                y轴标题内容, by default None
            fontsize : Optional[float], optional
                y轴标题字体大小, by default None
            """
            self._plot.ax.set_ylabel(label, fontsize=fontsize)

        def hide_top_right_spines(self) -> None:
            """隐藏上/右边框，可以解决一些图表标签与边框重叠的问题"""
            self._plot.ax.spines["right"].set_visible(False)
            self._plot.ax.spines["top"].set_visible(False)
            self._plot.ax.yaxis.set_ticks_position("left")
            self._plot.ax.xaxis.set_ticks_position("bottom")

        def xlim(self, xlim: Tuple[Union[float, str], Union[float, str]]) -> None:
            """设置x轴的边界

            Parameters
            ----------
            xlim : Tuple[Union[float,str], Union[float,str]]
                包含x轴下界和上界的tuple，如果填"-"则保持当前不变
            """
            current_xlim = self._plot.ax.get_xlim()
            if xlim[0] == "-":
                self._plot.ax.set_xlim(current_xlim[0], xlim[1])
            elif xlim[1] == "-":
                self._plot.ax.set_xlim(xlim[0], current_xlim[1])
            else:
                self._plot.ax.set_xlim(current_xlim[0], xlim[1])

        def ylim(self, ylim: Tuple[Union[float, str], Union[float, str]]) -> None:
            """设置y轴的边界

            Parameters
            ----------
            ylim : Tuple[Union[float,str], Union[float,str]]
                包含y轴下界和上界的tuple，如果填"-"则保持当前不变
            """
            current_ylim = self._plot.ax.get_ylim()
            if ylim[0] == "-":
                self._plot.ax.set_ylim(current_ylim[0], ylim[1])
            elif ylim[1] == "-":
                self._plot.ax.set_ylim(ylim[0], current_ylim[1])
            else:
                self._plot.ax.set_ylim(current_ylim[0], ylim[1])

        def y2lim(self, y2lim: Tuple[Tuple[float, float]]) -> None:
            """设置y轴次坐标轴的边界

            Parameters
            ----------
            y2lim : Tuple[Tuple[float, float]]
                包含y轴次坐标轴下界和上界的tuple
            """
            _ax2 = self._plot.ax.get_shared_x_axes().get_siblings(self._plot.ax)[0]
            _ax2.set_ylim(y2lim[0], y2lim[1])

        def major_grid(self, **kwargs) -> None:
            """显示主网格线"""
            d_grid = {
                "color": "grey",
                "axis": "both",
                "linestyle": ":",
                "linewidth": 0.3,
                "zorder": 0,  # 图层
            }
            d_grid = {k: kwargs[k] if k in kwargs else v for k, v in d_grid.items()}

            self._plot.ax.grid(
                which="major",
                color=d_grid["color"],
                axis=d_grid["axis"],
                linestyle=d_grid["linestyle"],
                linewidth=d_grid["linewidth"],
                zorder=d_grid["zorder"],
            )

        def minor_grid(self, **kwargs) -> None:
            """显示次网格线，比主网格线更密集"""
            d_grid = {
                "color": "grey",
                "axis": "both",
                "linestyle": ":",
                "linewidth": 0.3,
                "zorder": 0,  # 图层
            }
            d_grid = {k: kwargs[k] if k in kwargs else v for k, v in d_grid.items()}

            self._plot.ax.minorticks_on()  # 注意该语句，只显示major_grid不需要
            self._plot.ax.grid(
                which="both",
                color=d_grid["color"],
                axis=d_grid["axis"],
                linestyle=d_grid["linestyle"],
                linewidth=d_grid["linewidth"],
                zorder=d_grid["zorder"],
            )

        def legend(
            self,
            loc: Literal["center left", "lower center"] = "center left",
            ncol: int = 1,
        ):
            """生成ax图例

            Args:
                loc (Literal["center left", "lower center"], optional): 图例位置. Defaults to "center left".
                ncol (int, optional): 图例列数. Defaults to 1.
            """
            # 添加图例后原ax是否缩放
            # box = self.ax.get_position()
            # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            handles, labels = self._plot.ax.get_legend_handles_labels()
            try:
                ax2 = self._plot.ax.get_shared_x_axes().get_siblings(self._plot.ax)[0]
                handles2, labels2 = ax2.get_legend_handles_labels()
                by_label = dict(
                    zip(
                        labels[::-1] + labels2[::-1],
                        handles[::-1] + handles2[::-1],
                    )
                    if self._plot.__class__.__name__
                    in ["PlotBar", "PlotArea"]  # 柱状图则图例顺序倒序
                    else zip(
                        labels + labels2,
                        handles + handles2,
                    )
                )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
            except Exception:
                by_label = dict(
                    zip(
                        labels[::-1],
                        handles[::-1],
                    )
                    if self._plot.__class__.__name__
                    in ["PlotBar", "PlotArea"]  # 柱状图则图例顺序倒序
                    else zip(
                        labels,
                        handles,
                    )
                )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
            self._plot.ax.legend(
                by_label.values(),
                by_label.keys(),
                loc=loc,
                ncol=ncol,
                bbox_to_anchor=(1, 0.5) if loc == "center left" else (0.5, 1),
                frameon=False,
                prop={"family": "Microsoft YaHei", "size": self._plot.fontsize},
            )

    def apply_style(self):
        """应用风格，不适合在初始化应用，因为有些风格要在绘图后才生效

        Returns:
            self: 返回实例
        """

        self.style.apply_style()

        return self


# 继承基本类, 气泡图
class PlotBubble(Plot):
    def plot(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        z: Optional[str] = None,
        xlim: Optional[Tuple[float, float]] = None,
        ylim: Optional[Tuple[float, float]] = None,
        x_avg: Optional[float] = None,
        y_avg: Optional[float] = None,
        label_limit: int = 15,
        label_formatter: str = "{index}",
        label_topy: int = 0,
        label_mustshow: List[str] = [],
        bubble_scale: float = 1,
        show_reg: bool = False,
        show_hist: bool = False,
        corr: Optional[float] = None,
        **kwargs,
    ) -> PlotBubble:
        """继承基本类，绘制散点图

        Args:
            x (Optional[str], optional): 指定x轴变量字段名，如为None，则x为data第1列. Defaults to None.
            y (Optional[str], optional): 指定y轴变量字段名，如为None，则x为data第2列. Defaults to None.
            z (Optional[str], optional): 指定气泡大小字段名，如为None，则气泡大小为data第3列. Defaults to None.
            xlim (Optional[Tuple[float, float]]): 手动指定x轴边界. Defaults to None.
            ylim (Optional[Tuple[float, float]]): 手动指定y轴边界. Defaults to None.
            x_avg (Optional[float], optional): x轴平均值或其他分隔值，如提供则绘制x轴分隔竖线. Defaults to None.
            y_avg (Optional[float], optional): y轴平均值或其他分隔值，如提供则绘制y轴分隔水平线. Defaults to None.
            label_limit (int, optional): 限制显示标签的个数. Defaults to 15.
            label_formatter (str, optional): 标签文字的格式，支持{index}, {x}, {y}, {z}, {hue}. Defaults to "{index}".
            label_topy (int, optional): 如>0则强制显示y轴值最高的n个item的标签. Defaults to 0.
            label_mustshow (List[str], optional): 强制显示该列表中的标签. Defaults to [].
            bubble_scale (float, optional): 气泡大小系数. Defaults to 1.
            show_reg (bool, optional): 是否显示x,y的拟合趋势及置信区间. Defaults to False.
            show_reg (bool, optional): 是否显示x,y的分布histogram Defaults to False.
            corr (Optional[float], optional): 相关系数，如不为None，则显示在ax左上角. Defaults to None.

        Kwargs:
            x_fmt (str, optional): x轴显示数字格式，影响轴刻度标签及分隔线数据标签. Defaults to "{:,.0f}",
            y_fmt (str, optional): y轴显示数字格式，影响轴刻度标签及分隔线数据标签. Defaults to "{:,.0f}",
            alpha (float, optional): 气泡透明度. Defaults to 0.6,
            random_color (bool, optional): 气泡颜色是否随机. Defaults to True,
            edgecolor (str, optional): 气泡边框颜色. Defaults to "black",
            avg_linestyle (str, optional): 分隔线样式. Defaults to ":",
            avg_linewidth (float, optional): 分隔线宽度. Defaults to 1,
            avg_color (str, optional): 分隔线及数据标签颜色. Defaults to "black",

        Returns:
            PlotBubble: 返回自身实例
        """

        df = self.data

        # 如果不指定，则分别读取df第1-3列为x,y,z
        x = df.iloc[:, 0] if x is None else df.loc[:, x]
        y = df.iloc[:, 1] if y is None else df.loc[:, y]
        z = df.iloc[:, 2] if z is None else df.loc[:, z]

        # z列标准化并乘以系数以得到一般情况下都合适的气泡大小
        # max_normed = 1
        # min_normed = z.min() / z.max()
        # if z.max() != z.min():
        #     z = min_normed + (z - z.min()) * (max_normed - min_normed) / (z.max() - z.min())
        z = (z / z.max() * 100) ** 1.8 * bubble_scale

        # 设置默认风格，并根据kwargs更新
        d_style = {
            "x_fmt": "{:,.0f}",
            "y_fmt": "{:,.0f}",
            "alpha": 0.6,
            "random_color": True,
            "edgecolor": "black",
            "avg_linestyle": ":",
            "avg_linewidth": 1,
            "avg_color": "black",
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        # 设置x,y轴边界
        if ylim is not None:
            self.ax.set_ylim(ymin=ylim[0], ymax=ylim[1])
        if xlim is not None:
            self.ax.set_xlim(xmin=xlim[0], xmax=xlim[1])

        # 添加histogram，在前半步执行因为涉及到legend位置的问题
        if show_hist:
            ax_legend = scatter_hist(ax=self.ax, x=x, y=y)
        else:
            ax_legend = self.ax

        cmap, colors = self._colors.get_colors(
            labels=df.index, hue=self.hue, random_color=d_style["random_color"]
        )

        if self.style._show_legend is True and self.hue is not None:
            if pd.api.types.is_numeric_dtype(self.hue) is False:
                levels, categories = pd.factorize(self.hue)
                handles = [
                    Line2D(
                        [0],
                        [0],
                        marker="o",
                        markerfacecolor=self._color_dict.get(c, cmap(i)),
                        markersize=10,
                        color="white",
                        label=c,
                    )
                    for i, c in enumerate(categories)
                ]
                handles = sorted(handles, key=lambda h: h.get_label())
                ax_legend.legend(
                    handles=handles,
                    title=self.hue.name,
                    loc=self.style._legend_loc,
                    frameon=False,
                    ncol=self.style._legend_ncol,
                    bbox_to_anchor=(
                        (1, 0.5)
                        if self.style._legend_loc == "center left"
                        else (0.5, 1)
                    ),
                    prop={"family": "Microsoft YaHei", "size": self.fontsize},
                )
                self.style._show_legend = False  # 不再使用Plot类的通用方法生成图例

        # 绘制气泡
        scatter = self.ax.scatter(
            x,
            y,
            z,
            c=self.hue if pd.api.types.is_numeric_dtype(self.hue) else colors,
            cmap=cmap,
            alpha=d_style.get("alpha"),
            edgecolors=d_style.get("edgecolor"),
            zorder=3,
        )

        # 如果hue存在并且是连续变量，添加colorbar
        if self.hue is not None:
            if pd.api.types.is_numeric_dtype(self.hue.dtype):
                divider = make_axes_locatable(self.ax)
                cax = divider.append_axes(
                    "right", size="5%", pad=1.65 if show_hist else 0.05
                )
                cbar = self.figure.colorbar(scatter, cax=cax, orientation="vertical")
                cbar.set_label(self.hue.name)
                cbar.ax.set_zorder(0)
                self.figure.style._label_outer = (
                    False  # color是一个独立的ax，但是不支持label_outer()
                )
                warnings.warn("画布存在colorbar，label_outer风格不生效", UserWarning)

        # 添加系列标签
        texts = []
        x_shown = x if xlim is None else x[x.between(xlim[0], xlim[1])]
        y_shown = y if ylim is None else y[y.between(ylim[0], ylim[1])]
        index_shown = x_shown.index.intersection(y_shown.index)

        for i in range(len(index_shown)):
            # print(index_shown[i])
            if (
                i < label_limit
                or (index_shown[i] in y.loc[index_shown].nlargest(label_topy).index)
                or (index_shown[i] in label_mustshow)
                or (self.focus and index_shown[i] in self.focus)
            ):  # 在label_limit内或者强制要求展示y值最大item的标签或者在特别关注列表时
                d_label = {
                    "x": d_style.get("x_fmt").format(x.loc[index_shown].iloc[i]),
                    "y": d_style.get("y_fmt").format(y.loc[index_shown].iloc[i]),
                    "z": z.loc[index_shown].iloc[i],
                    "hue": (
                        self.hue.loc[index_shown].iloc[i] if self.hue is not None else None
                    ),
                    "index": index_shown[i],
                }
                texts.append(
                    self.ax.text(
                        x.loc[index_shown].iloc[i],
                        y.loc[index_shown].iloc[i],
                        label_formatter.format(**d_label),
                        ha="center",
                        va="center",
                        multialignment="center",
                        fontsize=self.fontsize,
                    )
                )

        # 用adjust_text包保证标签互不重叠
        if label_limit > 1:
            np.random.seed(0)
            adjust_text(
                texts,
                ax=self.ax,
                # force_text=0.5,
                arrowprops=dict(arrowstyle="->", color="black"),
            )

        # 添加轴label
        if self.style._xlabel is None:
            self.style._xlabel = x.name
        if self.style._ylabel is None:
            self.style._ylabel = y.name

        # 设置坐标轴格式
        self.ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, _: d_style.get("x_fmt").format(x))
        )
        self.ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: d_style.get("y_fmt").format(y))
        )

        # 绘制平均线
        if x_avg is not None:
            self.ax.axvline(
                x_avg,
                linestyle=d_style.get("avg_linestyle"),
                linewidth=d_style.get("avg_linewidth"),
                color=d_style.get("avg_color"),
            )
            self.ax.text(
                x_avg,
                self.ax.get_ylim()[1],
                d_style.get("x_fmt").format(x_avg),
                ha="left",
                va="top",
                color=d_style.get("avg_color"),
                multialignment="center",
                fontsize=self.fontsize,
                zorder=1,
            )
        if y_avg is not None:
            self.ax.axhline(
                y_avg,
                linestyle=d_style.get("avg_linestyle"),
                linewidth=d_style.get("avg_linewidth"),
                color=d_style.get("avg_color"),
            )
            self.ax.text(
                self.ax.get_xlim()[1],
                y_avg,
                kwargs.get("y_avg_label", d_style.get("y_fmt").format(y_avg)),
                ha="right",
                va="top",
                color=d_style.get("avg_color"),
                multialignment="center",
                fontsize=self.fontsize,
                zorder=1,
            )

        # 添加线性拟合曲线
        if show_reg:
            regression_band(ax=self.ax, x=x, y=y)

        # Add corr
        if corr is not None:
            self.ax.text(
                0.02,
                0.96,
                "x,y相关系数：" + str(corr),
                horizontalalignment="left",
                verticalalignment="center",
                transform=self.ax.transAxes,
                fontsize=10,
            )

        return self


class PlotBoxdot(Plot):
    def plot(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        label_limit: int = 0,
        label_threshold: float = 0,
        show_stats: bool = True,
        order: Optional[Union[None, list]] = None,
        **kwargs,
    ) -> PlotBoxdot:
        """继承基本类，绘制带数据点的箱型图

        Args:
            x (Optional[str], optional): x轴类别数据的字段名，如不指定则为第1列. Defaults to None.
            y (Optional[str], optional): y轴数值数据的字段名，如不指定则为第2列. Defaults to None.
            label_limit (int, optional): 展示数据点标签的数量. Defaults to 0.
            label_threshold (float, optional): 对大于此值的数据点展示标签. Defaults to 0.
            show_stats (bool, optional): 是否显示统计值，包括最大值、最小值、中位数. Defaults to True.
            order (Optional[Union[None, list]], optional): 类别按什么排序，如果为None则按照数据自动排序. Defaults to None.

        Returns:
            PlotBoxWithDots: 返回一个自身实例
        """

        df = self.data

        x = df.columns[0] if x is None else x
        y = df.columns[1] if y is None else y

        d_style = {"dot_size": 8, "jitter": 0.2}
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        ax = sns.stripplot(
            x=x,
            y=y,
            data=df,
            edgecolor="black",
            alpha=0.5,
            s=d_style.get("dot_size"),
            linewidth=1.0,
            jitter=d_style.get("jitter"),
            ax=self.ax,
            order=order,
            hue=self.hue,
        )
        ax = sns.boxplot(
            x=x,
            y=y,
            data=df,
            whis=np.inf,
            boxprops={"facecolor": "None"},
            order=order,
        )

        # 确保绘制完成后获取 x 轴标签
        self.figure.canvas.draw()
        ax_xticklabels = [t.get_text() for t in ax.get_xticklabels()]  # 获取x轴标签列表

        # 添加数据点标签

        labels = []
        for category in ax_xticklabels:
            df_temp = df[df[x] == category]
            for k, idx in enumerate(df_temp.index):
                if k == label_limit:
                    break

                point = ax.collections[ax_xticklabels.index(category)].get_offsets()[
                    k
                ]  # 获得散点图的坐标，因为有jitter，不能直接用原始数

                if point[1] > label_threshold:  # y值大于某阈值的才显示

                    labels.append(
                        plt.text(
                            point[0],
                            point[1],
                            idx,
                            size=self.fontsize * 0.8,
                            color="black",
                        )
                    )
        if len(labels) > 0:
            adjust_text(
                labels,
                arrowprops=dict(arrowstyle="->", color="black"),
            )

        # 添加最大值， 最小值，中位数标签
        if show_stats:
            df_groupby = df.groupby(x)[y]
            maxs = df_groupby.max().reindex(ax_xticklabels)  # 最高值
            mins = df_groupby.min().reindex(ax_xticklabels)  # 最低值
            medians = df_groupby.median().reindex(ax_xticklabels)  # 中位数

            for metric in [maxs, mins, medians]:
                for xtick in ax.get_xticks():
                    if metric is medians:
                        posx = xtick + 0.4
                    else:
                        posx = xtick + 0.25

                    ax.text(
                        posx,
                        metric[xtick],
                        self.fmt.format(metric[xtick]),
                        horizontalalignment="left",
                        verticalalignment="center",
                        size=self.fontsize,
                        color="black",
                        weight="semibold",
                    )

        return self


class PlotWordcloud(Plot):
    def plot(
        self,
        col_freq: Optional[str] = None,
        mask_shape: Literal["rectangle", "circle"] = "rectangle",
        mask_width: int = 800,
        mask_height: int = 600,
    ) -> PlotWordcloud:
        """继承基本类，绘制文字云图

        Args:
            col_freq (Optional[str]): 指定频次列，如不指定则默认为df的第一列.
            mask_shape (Literal["rectangle", "circle"], optional): 词云形状类别，默认为矩形. Defaults to "rectangle".
            mask_width (int, optional): 形状为矩形时的矩形宽度. Defaults to 800.
            mask_height (int, optional): 形状为矩形时的矩形高度. Defaults to 600.

        Returns:
            PlotWordcloud: 返回自身实例
        """

        df = self.data

        df = df.loc[:, col_freq] if col_freq is not None else df.iloc[:, 0]

        df.dropna(inplace=True)
        d_words = df.to_dict()

        font_path = "C:/Windows/Fonts/msyh.ttc"  # 字体路径

        if mask_shape == "circle":
            # 产生一个以(150,150)为圆心,半径为130的圆形mask
            x, y = np.ogrid[:600, :600]
            mask = (x - 300) ** 2 + (y - 300) ** 2 > 260**2
            mask = 255 * mask.astype(int)
            wordcloud = WordCloud(
                width=800,
                height=800,
                font_path=font_path,
                background_color="white",
                mask=mask,
            )
        elif mask_shape == "rectangle":
            wordcloud = WordCloud(
                width=mask_width,
                height=mask_height,
                font_path=font_path,
                background_color="white",
            )

        wordcloud.generate_from_frequencies(frequencies=d_words)

        self.ax.imshow(wordcloud, interpolation="bilinear")
        self.ax.axis("off")

        return self


class PlotLine(Plot):
    def plot(
        self,
        show_label: List[str] = [],
        endpoint_label_only: bool = False,
        **kwargs,
    ) -> PlotLine:
        """继承基本类，绘制线形图

        Args:
            show_label (List[str], optional): 指定要显示标签的系列. Defaults to [].
            endpoint_label_only (bool, optional): 标签是全部显示还是只显示首尾节点. Defaults to False.

        Kwargs:
            adjust_labels (bool, optional): 是否自动调整标签位置. Defaults to True.
            linewidth (int, optional): 线宽. Defaults to 2.
            linestyle(str, optional): 线型. Defaults to "-".
            marker(str,optional): 标记形状. Defaults to "o".
            markersize(int, optional): 标记大小. Defaults to 5.

        Returns:
            PlotLine: 返回自身实例
        """

        df = self.data

        d_style = {
            "adjust_labels": True,
            "linewidth": 2,  # 线条粗细
            "linestyle": "-",  # 线条样式
            "marker": "o",  # 标记点样式
            "markersize": 5,  # 标记点大小
            "line_color": None,  # 线条颜色
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        lines = []
        texts = []
        for i, column in enumerate(df.columns):
            # 如果有指定颜色就颜色，否则按预设列表选取
            color = (
                self._colors.get_color(column)
                if d_style.get("line_color") is None
                else d_style.get("line_color")
            )

            # 生成折线图
            lines.append(
                self.ax.plot(
                    df.index,
                    df[column],
                    color=color,
                    linestyle=d_style.get("linestyle"),
                    linewidth=(
                        2
                        if self.focus is not None and column in self.focus
                        else d_style.get("linewidth")
                    ),
                    label=column,
                    marker=d_style.get("marker"),
                    markersize=d_style.get("markersize"),
                    markerfacecolor="white",
                    markeredgecolor=color,
                    zorder=(
                        100 if self.focus is not None and column in self.focus else 10
                    ),
                )
            )

            # 标签
            if column in show_label:
                for k, idx in enumerate(df.index):
                    if endpoint_label_only:
                        if k == 0 or k == len(df.index) - 1:
                            texts.append(
                                self.ax.text(
                                    idx,
                                    df.iloc[k, i],
                                    self.fmt.format(df.iloc[k, i]),
                                    ha="right" if k == 0 else "left",
                                    va="center",
                                    size=self.fontsize,
                                    color="white",
                                    bbox=dict(
                                        facecolor=color, alpha=0.7, edgecolor=color
                                    ),
                                    zorder=(
                                        100
                                        if self.focus is not None
                                        and column in self.focus
                                        else 10
                                    ),
                                )
                            )
                    else:
                        texts.append(
                            self.ax.text(
                                idx,
                                df.iloc[k, i],
                                self.fmt.format(df.iloc[k, i]),
                                ha="center",
                                va="center",
                                size=self.fontsize,
                                color="white",
                                bbox=dict(facecolor=color, alpha=0.7, edgecolor=color),
                                zorder=(
                                    100
                                    if self.focus is not None and column in self.focus
                                    else 10
                                ),
                            )
                        )

        # 优化标签位置
        if d_style.get("adjust_labels") is True:
            np.random.seed(0)
            adjust_text(
                texts,
                ax=self.ax,
                only_move={"text": "y", "static": "y", "explode": "y", "pull": "y"},
                arrowprops=dict(arrowstyle="-"),
                max_move=(1, 1),
            )

        # y轴标签格式
        self.ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: self.fmt.format(y))
        )

        return self


class PlotArea(Plot):
    def plot(
        self,
        stacked: bool = True,
        show_label: List[str] = [],
        endpoint_label_only: bool = False,
        **kwargs,
    ) -> PlotLine:
        """继承基本类，绘制区域图

        Args:
            stacked (bool, optional): 是否堆积. Defaults to True.
            show_label (List[str], optional): 指定要显示标签的系列. Defaults to [].
            endpoint_label_only (bool, optional): 标签是全部显示还是只显示首尾节点. Defaults to False.

        Kwargs:
            linewidth (int, optional): 线宽. Defaults to 2.
            marker(str,optional): 标记形状. Defaults to "o".
            markersize(int, optional): 标记大小. Defaults to 5.
            alpha (float, optional): 透明度. Defaults to 1.

        Returns:
            PlotLine: 返回自身实例
        """

        df = self.data

        d_style = {
            "linewidth": 2,
            "alpha": 1,
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        for i, column in enumerate(df.columns):
            # 如果有指定颜色就颜色，否则按预设列表选取
            color = self._colors.get_color(column)

            if (
                stacked or i == 0
            ):  # 仅在 stacked 为 True 或是第一个列时使用 fill_between
                # 生成区域图
                self.ax.fill_between(
                    df.index,
                    df.iloc[:, :i].sum(axis=1),
                    df.iloc[:, : i + 1].sum(axis=1),
                    label=column,
                    alpha=d_style.get("alpha"),
                    color=color,
                )

                # # 生成折线图
                # self.ax.plot(
                #     df.index,
                #     df.iloc[:, : i + 1].sum(axis=1),
                #     color=color,
                #     linewidth=d_style.get("linewidth"),
                #     label=column,
                # )
            else:
                # 生成区域图
                self.ax.fill_between(
                    df.index,
                    df[column],
                    label=column,
                    alpha=d_style.get("alpha"),
                    color=color,
                )

                # 生成折线图
                self.ax.plot(
                    df.index,
                    df[column],
                    color=color,
                    linewidth=d_style.get("linewidth"),
                    label=column,
                )
            # 标签
            if column in show_label:
                for k, idx in enumerate(df.index):
                    if stacked is True:
                        # 如果堆积，标签要挪到面积图中间
                        position_y = (
                            df.iloc[k, :i].sum() + df.iloc[k, : i + 1].sum()
                        ) / 2
                    else:
                        position_y = df.iloc[k, i]
                    if endpoint_label_only:
                        if k == 0 or k == len(df.index) - 1:
                            t = self.ax.text(
                                idx,
                                position_y,
                                self.fmt.format(df.iloc[k, i]),
                                ha="center",
                                # ha="right" if k == 0 else "left",
                                va="center",
                                size=self.fontsize,
                                color="white",
                            )
                    else:
                        t = self.ax.text(
                            idx,
                            position_y,
                            self.fmt.format(df.iloc[k, i]),
                            ha="center",
                            va="center",
                            size=self.fontsize,
                            color="white",
                        )
                    t.set_bbox(dict(facecolor=color, alpha=0.7, edgecolor=color))

            # y轴标签格式
            self.ax.yaxis.set_major_formatter(
                FuncFormatter(lambda y, _: self.fmt.format(y))
            )

        return self


class PlotBar(Plot):
    def plot(
        self,
        stacked: bool = True,
        show_label: bool = True,
        label_formatter: str = "{abs}",
        show_total_bar: bool = False,
        show_total_label: bool = False,
        show_gr_text: bool = False,
        show_gr_line: bool = False,
        show_avg_line: bool = False,
        label_threshold: float = 0.02,
        period_change: int = 1,
        **kwargs,
    ) -> PlotBar:
        """继承基本Plot类，绘制柱状图

        Args:
            stacked (bool, optional): 是否堆积. Defaults to True.
            show_label (bool, optional): 是否显示数字标签. Defaults to True.
            label_formatter (str, optional): 主标签的格式，支持通配符{abs},{share},{gr},{index},{col}. Defaults to "{abs}".
            show_total_bar (bool, optional): 是否显示一个总体表现外框. Defaults to False.
            show_total_label (bool, optional): 是否在最上方显示堆积之和数字标签. Defaults to False.
            show_gr_text (bool, optional): 是否显示增长率数字. Defaults to False.
            show_gr_line (bool, optional): 是否显示增长率线形图. Defaults to False.
            label_threshold (float, optional): 显示数字标签的阈值，系列占堆积之和的比例大于此值才显示. Defaults to 0.02.
            period_change (float, optional): 计算增长率同比的期数. Defaults to 1.

        Returns:
            self: 返回自身plot实例
        """
        df = self.data
        df_share = df.div(df.sum(axis=1), axis=0)
        df_gr = self.data.pct_change(axis=0, periods=period_change)
        if df.shape[1] == 1:
            avg = df.mean().values[0]

        d_style = {
            "bar_width": 0.8,  # 柱宽
            "bar_color": None,  # 柱指定颜色
            "label_fontsize": self.fontsize,  # 标签字体大小
            "bbox": None,  # 标签背景
            "fmt_abs": self.fmt,  # 绝对值标签格式
            "fmt_share": "{:.1%}",  # 占比标签格式
            "fmt_gr": "{:+.1%}",  # 增长率标签格式
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        # 绝对值bar图和增长率标注

        # bar宽度
        bar_width = d_style.get("bar_width")
        for k, index in enumerate(df.index):
            bottom_pos = 0
            bottom_neg = 0
            bottom_gr = 0

            max_v = np.nanmax(df.values)
            min_v = np.nanmin(df.values)
            range_v = max_v - min_v

            self._colors.iter_colors = cycle(
                self._colors.cmap_qual(i) for i in range(self._colors.cmap_qual.N)
            )  # reset colors cycle between bars
            for i, col in enumerate(df):
                # 计算出的指标
                v = df.loc[index, col]
                share = df_share.loc[index, col]
                gr = df_gr.loc[index, col]
                total_gr = df.iloc[k, :].sum() / df.iloc[k - 1, :].sum() - 1
                d_label = {
                    "abs": d_style.get("fmt_abs").format(v),
                    "share": d_style.get("fmt_share").format(share),
                    "gr": d_style.get("fmt_gr").format(gr),
                    "total_gr": d_style.get("fmt_gr").format(total_gr),
                    "index": index,
                    "col": col,
                }

                # 如果有指定颜色就颜色，否则按预设列表选取
                if d_style.get("bar_color"):
                    color = d_style.get("bar_color")
                else:
                    if stacked:
                        if (
                            self._color_dict is not None
                            and col in self._color_dict.keys()
                        ):
                            color = self._colors.get_color(col)
                        elif (
                            self._color_dict is not None
                            and index in self._color_dict.keys()
                        ):
                            color = self._colors.get_color(index)
                        else:
                            color = next(self._colors.iter_colors)
                    else:
                        color = next(self._colors.iter_colors)

                # # 如果是关注的index，则特定着色
                # if index == focus:
                #     color = "red"

                if stacked:
                    if v >= 0:
                        bottom = bottom_pos
                    else:
                        bottom = bottom_neg
                else:
                    bottom = 0

                # bar x轴位置
                if stacked:
                    pos_x = k
                else:
                    pos_x = k + bar_width * i

                # 绘制bar图
                self.ax.bar(
                    pos_x,
                    v,
                    width=bar_width,
                    color=color,
                    bottom=bottom,
                    label=col,
                    zorder=3,
                )
                # 绘制总体表现外框
                if show_total_bar:
                    self.ax.bar(
                        df.index,
                        df.sum(axis=1) * 1.03,
                        width=0.6,
                        linewidth=1,
                        linestyle="--",
                        facecolor=(1, 0, 0, 0.0),
                        edgecolor=(0, 0, 0, 1),
                    )

                    # 因为多了总体表现外框，移除右、上边框
                    self.style._hide_top_right_spines = True

                if show_label is True:
                    if (
                        stacked is False or df.shape[1] == 1
                    ):  # 非堆叠图或只有一列数的情况（非堆叠）
                        # 根据数据判断标签是否需要微调
                        if abs(v) <= range_v * 0.2:
                            pos_y = v * 1.1
                            va = "bottom" if v >= 0 else "top"
                            fontcolor = (
                                color if d_style.get("bbox") is None else "white"
                            )

                        # if 0 <= v < max_v * 0.05:
                        #     pos_y = v * 1.1
                        #     va = "bottom"
                        #     fontcolor = (
                        #         color if d_style.get("bbox") is None else "white"
                        #     )
                        # elif min_v * 0.05 < v < 0:
                        #     pos_y = v * 0.9
                        #     va = "top"
                        #     fontcolor = (
                        #         color if d_style.get("bbox") is None else "white"
                        #     )
                        else:
                            pos_y = v / 2
                            va = "center"
                            fontcolor = "white"

                    else:  # 堆叠的情况
                        pos_y = bottom + v / 2
                        va = "center"
                        fontcolor = "white"

                    if abs(v / self.ax.get_ylim()[1]) >= label_threshold:
                        self.ax.text(
                            x=pos_x,
                            y=pos_y,
                            s=label_formatter.format(**d_label),
                            color=fontcolor,
                            va=va,
                            ha="center",
                            fontsize=d_style.get("label_fontsize"),
                            zorder=5,
                            bbox=d_style.get("bbox"),
                        )
                if v >= 0:
                    bottom_pos += v
                else:
                    bottom_neg += v

                # patches = self.ax.patches
                # for rect in patches:
                #     height = rect.get_height()
                #     # 负数则添加纹理
                #     if height < 0 or (focus and index in focus):
                #         rect.set_hatch("//")

                if show_gr_text:
                    if k > 0:
                        # 各系列增长率标注
                        self.ax.text(
                            x=k - 0.5,
                            y=(bottom_gr + df.iloc[k - 1, i] / 2 + df.iloc[k, i] / 2)
                            / 2,
                            s=d_label["gr"],
                            ha="center",
                            va="center",
                            color=color,
                            fontsize=d_style.get("label_fontsize"),
                            zorder=5,
                        )
                        bottom_gr += df.iloc[k - 1, i] + df.iloc[k, i]

                        # 绘制总体增长率
                        if show_total_label:
                            self.ax.text(
                                x=k - 0.5,
                                y=(df.iloc[k, :].sum() + df.iloc[k - 1, :].sum())
                                / 2
                                * 1.05,
                                s=d_label["total_gr"],
                                ha="center",
                                va="bottom",
                                color="black",
                                fontsize=d_style.get("label_fontsize"),
                            )

            # 在柱状图顶端添加total值
            if show_total_label:
                total = df.sum(axis=1)
                for p, v in enumerate(total.values):
                    self.ax.text(
                        x=p,
                        y=(
                            v * 1.05 if show_total_bar else v
                        ),  # 如果绘制整体外框则优化total值文本的位置
                        s=self.fmt.format(float(v)),
                        fontsize=d_style.get("label_fontsize"),
                        ha="center",
                        va="bottom",
                        zorder=5,
                    )

        # 如果是非堆叠图要手动指定x轴ticks
        # 解析日期字符串并将其转换为 Matplotlib 内部日期格式
        if stacked is False:
            self.ax.set_xticks(
                np.arange(df.shape[0]) + bar_width / df.shape[1], df.index
            )
        else:
            self.ax.set_xticks(np.arange(df.shape[0]), df.index)

        # x轴标签
        self.ax.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

        # y轴标签格式
        self.ax.yaxis.set_major_formatter(
            FuncFormatter(lambda y, _: self.fmt.format(y))
        )

        self.ax.axhline(0, color="black", linewidth=0.5)  # y轴为0的横线

        if show_gr_line:
            # 增加次坐标轴
            ax2 = self.ax.twinx()

            color_line = "darkorange"
            ax2.plot(
                df_gr.index,
                df_gr.values,
                label="GR(y-1)",
                color=color_line,
                linewidth=1,
                linestyle="dashed",
                marker="o",
                markersize=3,
                markerfacecolor="white",
            )
            # if "y2lim" in kwargs:
            #     ax2.set_ylim(kwargs["y2lim"][0], kwargs["y2lim"][1])

            for i in range(len(df_gr)):
                if float(df_gr.values[i]) <= ax2.get_ylim()[1]:
                    t = ax2.text(
                        x=df_gr.index[i],
                        y=df_gr.values[i],
                        s="{:+.0%}".format(float(df_gr.values[i])),
                        ha="center",
                        va="bottom",
                        fontsize=self.fontsize,
                        color="white",
                    )
                    t.set_bbox(
                        dict(facecolor=color_line, alpha=0.7, edgecolor=color_line)
                    )

            # 次坐标轴标签格式
            ax2.yaxis.set_major_formatter(
                FuncFormatter(lambda y, _: self.fmt_line.format(y))
            )
            ax2.get_yaxis().set_ticks([])

            # # x轴标签
            # ax2.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

        if show_avg_line and df.shape[1] == 1:
            self.ax.axhline(
                avg,
                linestyle="dashed",
                linewidth=0.5,
                color="red",
                zorder=100,
            )
            self.ax.text(
                self.ax.get_xlim()[1],
                avg,
                f"平均：{self.fmt.format(avg)}",
                ha="right",
                va="bottom",
                color="red",
                fontsize=self.fontsize,
                zorder=100,
            )

        return self


class PlotBarh(Plot):
    def plot(
        self,
        stacked: bool = True,
        show_label: bool = True,
        label_formatter: str = "{abs}",
        label_threshold: float = 0.02,
        label_pos: Literal["smart", "center", "outer"] = "smart",
        **kwargs,
    ) -> PlotBar:
        """继承基本Plot类，绘制柱状图

        Args:
            stacked (bool, optional): 是否堆积. Defaults to True.
            show_label (bool, optional): 是否显示数字标签. Defaults to True.
            label_formatter (str, optional): 主标签的格式，支持通配符{abs},{share},{gr},{index},{col}. Defaults to "{abs}".
            show_total_bar (bool, optional): 是否显示一个总体表现外框. Defaults to False.
            show_total_label (bool, optional): 是否在最上方显示堆积之和数字标签. Defaults to False.
            show_gr_text (bool, optional): 是否显示增长率数字. Defaults to False.
            show_gr_line (bool, optional): 是否显示增长率线形图. Defaults to False.
            label_threshold (float, optional): 显示数字标签的阈值，系列占堆积之和的比例大于此值才显示. Defaults to 0.02.
            label_pos (Literal["smart", "center", "outer"], optional): 标签位置，smart为自动判断，center为居中，outer为外侧. Defaults to "smart".

        Returns:
            self: 返回自身plot实例
        """
        df = self.data
        df_share = df.div(df.sum(axis=1), axis=0)
        df_share_total = df.div(df.sum())

        d_style = {
            "bar_height": 0.8,  # bar高度
            "bar_color": None,  # 柱指定颜色
            "label_fontsize": self.fontsize,  # 标签字体大小
            "bbox": None,  # 标签背景
            "fmt_abs": self.fmt,  # 绝对值标签格式
            "fmt_share": "{:.1%}",  # 占比标签格式
            "fmt_gr": "{:+.1%}",  # 增长率标签格式
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        # 绝对值bar图和增长率标注
        max_v = np.nanmax(df.values)
        min_v = np.nanmin(df.values)
        for k, index in enumerate(df.index):
            left_pos = 0
            left_neg = 0

            self._colors.iter_colors = cycle(
                self._colors.cmap_qual(i) for i in range(self._colors.cmap_qual.N)
            )  # reset colors cycle between bars
            for i, col in enumerate(df):
                # 计算出的指标
                v = df.loc[index, col]
                share = df_share.loc[index, col]
                share_total = df_share_total.loc[index, col]

                d_label = {
                    "abs": d_style.get("fmt_abs").format(v),
                    "share": d_style.get("fmt_share").format(share),
                    "share_total": d_style.get("fmt_share").format(share_total),
                    "index": index,
                    "col": col,
                }

                # 如果有指定颜色就颜色，否则按预设列表选取
                # 如果有指定颜色就颜色，否则按预设列表选取
                if d_style.get("bar_color"):
                    color = d_style.get("bar_color")
                else:
                    if stacked:
                        if col in self._color_dict.keys():
                            color = self._colors.get_color(col)
                        elif index in self._color_dict.keys():
                            color = self._colors.get_color(index)
                        else:
                            color = next(self._colors.iter_colors)
                    else:
                        color = next(self._colors.iter_colors)

                if stacked:
                    if v >= 0:
                        left = left_pos
                    else:
                        left = left_neg
                else:
                    left = 0

                # bar宽度
                bar_height = d_style.get("bar_height")

                # bar y轴位置
                if stacked:
                    pos_y = k
                else:
                    pos_y = k + bar_height * i

                # 绘制bar图
                self.ax.barh(
                    pos_y,
                    v,
                    height=bar_height,
                    color=color,
                    left=left,
                    label=col,
                    zorder=3,
                )

                if show_label is True:
                    margin = self.ax.get_xlim()[1] * 0.02
                    if label_pos == "smart":
                        if (
                            stacked is False or df.shape[1] == 1
                        ):  # 非堆叠图或只有一列数的情况（非堆叠）
                            # 根据数据判断标签是否需要微调
                            if 0 <= v < max_v * 0.2:
                                pos_x = v + margin
                                ha = "left"
                                fontcolor = (
                                    color if d_style.get("bbox") is None else "white"
                                )
                            elif min_v * 0.2 < v < 0:
                                pos_x = v - margin
                                ha = "right"
                                fontcolor = (
                                    color if d_style.get("bbox") is None else "white"
                                )
                            else:
                                pos_x = v / 2
                                ha = "center"
                                fontcolor = "white"

                        else:  # 堆叠的情况
                            pos_x = left + v / 2
                            ha = "center"
                            fontcolor = "white"
                    elif label_pos == "outer":
                        pos_x = v + margin
                        ha = "left"
                        fontcolor = color
                    elif label_pos == "center":
                        pos_x = left + v / 2
                        ha = "center"
                        fontcolor = "white"

                    if abs(v / self.ax.get_ylim()[1]) >= label_threshold:
                        self.ax.text(
                            x=pos_x,
                            y=pos_y,
                            s=label_formatter.format(**d_label),
                            color=fontcolor,
                            va="center",
                            ha=ha,
                            fontsize=d_style.get("label_fontsize"),
                            zorder=5,
                        )
                if v >= 0:
                    left_pos += v
                else:
                    left_neg += v

                patches = self.ax.patches
                for rect in patches:
                    height = rect.get_height()
                    # 负数则添加纹理
                    if height < 0:
                        rect.set_hatch("//")

        # 如果是非堆叠图要手动指定x轴ticks
        # 解析日期字符串并将其转换为 Matplotlib 内部日期格式
        if stacked is False:
            self.ax.set_yticks(
                np.arange(df.shape[0]) + bar_height / df.shape[1], df.index
            )
        else:
            self.ax.set_yticks(np.arange(df.shape[0]), df.index)

        # y轴标签
        self.ax.get_yaxis().set_ticks(range(0, len(df.index)), labels=df.index)

        # x轴标签格式
        self.ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, _: self.fmt.format(x))
        )
        self.ax.axvline(0, color="black", linewidth=0.5)  # x轴为0的竖线

        self.ax.invert_yaxis()  # 翻转y轴，最上方显示排名靠前的序列

        return self


class PlotHist(Plot):
    def plot(
        self,
        bins: int = 10,
        tiles: int = 10,
        show_kde: bool = True,
        show_metrics: bool = True,
        show_tiles: bool = False,
        ind: Optional[list] = None,
        **kwargs,
    ) -> PlotHist:
        """继承基本类，绘制histogram直方图

        Args:
            bins (int, optional): 直方图柱的个数. Defaults to 10.
            tiles (int, optional): 等分线的个数. Defaults to 10.
            show_kde (bool, optional): 是否显示核密度估计曲线. Defaults to True.
            show_metrics (bool, optional): 是否显示均值和中位数. Defaults to True.
            show_tiles (bool, optional): 是否显示等分线_. Defaults to False.
            ind (Optional[list], optional): 评估点，如为None则为1000个等距点. Defaults to None.

        Returns:
            PlotHist: 返回一个自身的实例
        """

        df = self.data

        # 设置默认风格，并根据kwargs更新
        d_style = {
            "color_hist": "grey",
            "color_kde": "darkorange",
            "color_mean": "purple",
            "color_median": "crimson",
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        df.plot(
            kind="hist",
            density=True,
            bins=bins,
            ax=self.ax,
            color=d_style.get("color_hist"),
            legend=None,
            alpha=0.5,
        )
        if show_kde:
            ax_kde = self.ax.twinx()
            df.plot(
                kind="kde",
                ax=ax_kde,
                color=d_style.get("color_kde"),
                legend=None,
                ind=ind,
            )
            # ax_kde.get_legend().remove()
            ax_kde.set_yticks([])  # 删除y轴刻度
            ax_kde.set_ylabel(None)

        # 添加百分位信息
        if show_tiles:
            # 计算每个子区间的长度
            interval_length = 1.0 / tiles

            # 初始化结果列表，包含第一个边界值
            boundaries = [0.0]

            # 计算并添加每个子区间的边界值
            for i in range(1, tiles):
                boundary_value = i * interval_length
                boundaries.append(boundary_value)

            print(boundaries)
            # 计算百分位数据
            percentiles = df.quantile(boundaries).reset_index()
            print(percentiles, type(percentiles))

            # 在hist图基础上绘制百分位
            self.ax.set_xlim(self.style._xlim[0], self.style._xlim[1])
            for i, (index, row) in enumerate(percentiles.iterrows()):
                self.ax.axvline(row[1], color="crimson", linestyle=":")  # 竖分隔线
                self.ax.text(
                    row[1],
                    self.ax.get_ylim()[1] * 0.97,
                    int(row[1]),
                    ha="center",
                    color="crimson",
                    fontsize=self.fontsize,
                )
                if i < tiles - 1:
                    self.ax.text(
                        percentiles.iloc[i, 1]
                        + (percentiles.iloc[i + 1, 1] - percentiles.iloc[i, 1]) / 2,
                        self.ax.get_ylim()[1],
                        "D" + str(i + 1),
                        ha="center",
                        va="bottom",
                    )
                else:
                    self.ax.text(
                        percentiles.iloc[tiles - 1, 1]
                        + (self.ax.get_xlim()[1] - percentiles.iloc[tiles - 1, 1]) / 2,
                        self.ax.get_ylim()[1],
                        "D" + str(i + 1),
                        ha="center",
                        va="bottom",
                    )

        # 添加均值、中位数等信息
        if show_metrics:
            median = np.nanmedian(df.values)  # 计算中位数
            mean = np.nanmean(df.values)  # 计算平均数
            # if self.text_diff is not None:
            #     median_diff = self.text_diff[j]["中位数"]  # 计算对比中位数
            #     mean_diff = self.text_diff[j]["平均数"]  # 计算对比平均数

            if median > mean:
                yindex_median = 0.95
                yindex_mean = 0.9
                pos_median = "left"
                pos_mean = "right"
            else:
                yindex_mean = 0.95
                yindex_median = 0.9
                pos_median = "right"
                pos_mean = "left"

            self.ax.axvline(median, color=d_style.get("color_median"), linestyle=":")
            self.ax.text(
                median,
                self.ax.get_ylim()[1] * yindex_median,
                f"中位数：{self.fmt.format(median)}",
                ha=pos_median,
                color="white",
                fontsize=self.fontsize,
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor=d_style.get("color_median"),
                    edgecolor=d_style.get("color_median"),
                    linewidth=1,
                    alpha=0.7,
                ),
                zorder=100,
            )

            self.ax.axvline(mean, color=d_style.get("color_mean"), linestyle=":")
            self.ax.text(
                mean,
                self.ax.get_ylim()[1] * yindex_mean,
                f"平均数：{self.fmt.format(mean)}",
                ha=pos_mean,
                color="white",
                fontsize=self.fontsize,
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor=d_style.get("color_mean"),
                    edgecolor=d_style.get("color_mean"),
                    linewidth=1,
                    alpha=0.7,
                ),
                zorder=100,
            )

        # 去除ticks
        self.ax.get_yaxis().set_ticks([])
        # self.ax.xaxis.set_major_formatter(ticker.StrMethodFormatter(self.fmt))

        # 轴标题
        self.ax.set_ylabel("频次", fontsize=self.fontsize)

        # x轴显示范围
        if isinstance(df, pd.DataFrame):
            self.ax.set_xlim(df.min().min(), df.max().max())
        else:
            self.ax.set_xlim(df.min(), df.max())

        ax_kde.spines["right"].set_visible(False)
        ax_kde.spines["top"].set_visible(False)
        ax_kde.yaxis.set_ticks_position("left")
        ax_kde.xaxis.set_ticks_position("bottom")

        return self


class PlotStripdot(Plot):
    def plot(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        text_diff: bool = True,
        **kwargs,
    ) -> PlotStripdot:
        """继承基本Plot类，绘制算珠图（也称点线图，泡泡糖图）

        Args:
            start (Optional[str], optional): 起始点数据的列名，如不设置则在数据只有1列的情况下默认为None，数据多于1列的情况下默认为第1列. Defaults to None.
            end (Optional[str], optional): 结束点数据的列名，如不设置则在数据只有1列时默认为此列，数据多于1列的情况下默认为第2列. Defaults to None.
            text_diff (bool, optional): 是否显示差值标签. Defaults to True.

        Kwargs:
            color_line (str): 横线的颜色. Defaults to "grey".
            color_start (str): 起始点的颜色. Defaults to "grey".
            color_end (str): 结束点的颜色. Defaults to self.figure.cmap_qual.colors[0].
            alpha (float): 透明度. Defaults to 0.3.

        Returns:
            PlotStripdot: 返回一个自身实例
        """

        df = self.data

        if df.shape[1] == 1:  # 如果df只有1列，默认没有start，唯一列是end数据
            start = None
            end = df.iloc[:, 0]
        else:  # 如果df多于1列不指定，则分别读取df第1-2列为start, end
            start = df.iloc[:, 0] if start is None else df.loc[:, start]
            end = df.iloc[:, 1] if end is None else df.loc[:, end]
            diff = end.subtract(start)
            fmt_diff = self.fmt[:2] + "+" + self.fmt[2:]

        d_style = {
            "color_line": "grey",
            "color_start": "grey",
            "color_end": self._colors.cmap_qual.colors[0],
            "random_color": True,
            "alpha": 0.3,
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}
        # 颜色方案，如果有hue则按hue着色，如果没有则使用self.itercolors的

        cmap, colors = self._colors.get_colors(
            labels=df.index,
            hue=self.hue,
            color=d_style.get("color_end"),
            random_color=d_style["random_color"],
        )

        if self.style._show_legend is True and self.hue is not None:
            if pd.api.types.is_numeric_dtype(self.hue) is False:
                handles = [
                    Line2D(
                        [0],
                        [0],
                        marker="o",
                        markerfacecolor=cmap(i),
                        markersize=10,
                        color="white",
                        label=c,
                    )
                    for i, c in enumerate(pd.factorize(self.hue)[1])
                ]
                handles = sorted(handles, key=lambda h: h.get_label())
                hue_legend = plt.legend(
                    handles=handles,
                    title=self.hue.name,
                    loc=self.style._legend_loc,
                    frameon=False,
                    ncol=self.style._legend_ncol,
                    bbox_to_anchor=(
                        (1, 0.5)
                        if self.style._legend_loc == "center left"
                        else (0.5, 1)
                    ),
                    prop={"family": "Microsoft YaHei", "size": self.fontsize},
                )
                self.ax.add_artist(hue_legend)
                # self.style._show_legend = False  # 不再使用Plot类的通用方法生成图例

        index_range = range(1, len(df.index) + 1)
        self.ax.hlines(
            y=index_range,
            xmin=start,
            xmax=end,
            color=d_style.get("color_line"),
            alpha=d_style.get("alpha"),
        )  # 连接线
        if start is not None:
            self.ax.scatter(
                start,
                index_range,
                color=d_style.get("color_start"),
                alpha=d_style.get("alpha"),
                label=start.name,
            )  # 起始端点
        scatter_end = self.ax.scatter(
            end,
            index_range,
            c=self.hue if pd.api.types.is_numeric_dtype(self.hue) else colors,
            cmap=cmap,
            alpha=d_style.get("alpha"),
            label=end.name,
        )  # 结束端点

        # 如果hue存在并且是连续变量，添加colorbar
        if self.hue is not None:
            if pd.api.types.is_numeric_dtype(self.hue.dtype):
                divider = make_axes_locatable(self.ax)
                cax = divider.append_axes("right", size="5%", pad=0.05)
                cbar = self.figure.colorbar(
                    scatter_end, cax=cax, orientation="vertical"
                )
                cbar.set_label(self.hue.name)
                cbar.ax.set_zorder(0)
                self.figure.style._label_outer = (
                    False  # color是一个独立的ax，但是不支持label_outer()
                )
                warnings.warn("画布存在colorbar，label_outer风格不生效", UserWarning)

        # 添加最新时点的数据标签
        text_gap = (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) / 50
        for i in index_range:
            v_diff = diff[i - 1]

            self.ax.text(
                end[i - 1] + text_gap if v_diff >= 0 else end[i - 1] - text_gap,
                i,
                self.fmt.format(end[i - 1]),
                ha="left" if v_diff >= 0 else "right",
                va="center",
                color=colors[i - 1],
                fontsize=self.fontsize,
                zorder=20,
            )
        # 添加间隔线
        list_range = list(index_range)
        list_range.append(max(list_range) + 1)
        self.ax.hlines(
            y=[i - 0.5 for i in list_range],
            xmin=self.ax.get_xlim()[0],
            xmax=self.ax.get_xlim()[1],
            color="grey",
            linestyle="--",
            linewidth=0.5,
            alpha=0.2,
        )

        self.ax.set_yticks(index_range, labels=df.index)  # 添加y轴标签
        self.ax.tick_params(
            axis="y", which="major", labelsize=self.fontsize
        )  # 调整y轴标签字体大小

        # 如果hue存在，将y轴的ticklabels也着色
        if self.hue is not None or d_style["random_color"]:
            for i, label in enumerate(self.ax.get_yticklabels(which="both")):
                label.set_color(colors[i])

        if text_diff and df.shape[1] > 1:
            for i in index_range:
                v_diff = diff[i - 1]

                # 正负色
                if v_diff < 0:
                    fontcolor = "crimson"
                else:
                    fontcolor = (
                        colors[i - 1]
                        if self.hue is not None or d_style["random_color"]
                        else "black"
                    )

                if v_diff != 0 and math.isnan(v_diff) is False:
                    self.ax.text(
                        self.ax.get_xlim()[1] * 0.99,
                        i,
                        fmt_diff.format(v_diff),
                        ha="right",
                        va="center",
                        color=fontcolor,
                        fontsize=self.fontsize,
                        zorder=20,
                    )
                    # t.set_bbox(
                    #     dict(
                    #         facecolor=edgecolor_diff,
                    #         alpha=0.25,
                    #         edgecolor=edgecolor_diff,
                    #         zorder=20,
                    #     )
                    # )

        self.ax.invert_yaxis()  # 翻转y轴，最上方显示排名靠前的序列

        self.style._legend_loc = "lower center"
        self.style._legend_ncol = 2

        return self


class PlotHeatmap(Plot):
    def plot(
        self,
        cmap: Optional[Union[str, list]] = None,
        cbar: bool = True,
        show_label: bool = True,
        **kwargs,
    ) -> PlotHeatmap:
        """继承基本类，生成网格热力图类

        Args:
            cmap (Optional[Union[str, list]], optional): 自定义颜色方案，可以是cmap名或颜色列表. Defaults to None.
            cbar (bool, optional): 是否添加colorbar. Defaults to True.
            show_label (bool, optional): 是否往每个网格添加标签文本. Defaults to True.

        Returns:
            PlotHeatmap: 返回自身实例
        """
        sns.heatmap(
            data=self.data,
            ax=self.ax,
            annot=show_label,
            cbar=cbar,
            cmap=self._colors.cmap_norm if cmap is None else cmap,
            fmt=self.fmt[2:-1],  # seaborn格式会自己加{:}
            annot_kws={"fontsize": self.fontsize},
        )

        return self


# 继承基本类, 矩形Treemap
class PlotTreemap(Plot):
    def plot(
        self,
        level1: str,
        size: str,
        level2: Optional[str] = None,
        **kwargs,
    ) -> PlotTreemap:
        """使用squarify包生成矩形Treemap

        Args:
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.

        Returns:
            PlotTreemap: 返回自身实例
        """

        df = self.data

        colors = self._colors.get_colors(labels=df.index, hue=self.hue)[1]

        df_size1 = pd.pivot_table(
            data=df, index=level1, columns=None, values=size, aggfunc=sum
        ).sort_values(by=size, ascending=False)

        # # 合并名称和值为Labels
        # list_index = df.index.tolist()
        # list_name = []
        # for name in list_index:
        #     if len(name) > 8:
        #         name = name[:8] + "..."  # 防止太长的标签，在之后的可视化中会出界
        #     list_name.append(name)
        # list_size = df.iloc[:, 0].tolist()
        # list_diff = df.iloc[:, 1].tolist()
        # list_labels = [
        #     m + "\n" + str("{:,.0f}".format(n)) + "\n" + str("{:+,.0f}".format(p))
        #     for m, n, p in zip(list_name, list_size, list_diff)
        # ]

        # # 创造和同比净增长关联的颜色方案
        # min_diff = min(list_diff)
        # max_diff = max(list_diff)
        # if min_diff > 0:
        #     cmap = mpl.cm.Greens
        #     norm = mpl.colors.Normalize(vmin=min_diff, vmax=max_diff)
        # elif max_diff < 0:
        #     cmap = mpl.cm.Reds
        #     norm = mpl.colors.Normalize(vmin=min_diff, vmax=max_diff)
        # else:
        #     cmap = mpl.cm.RdYlGn  # 绿色为正，红色为负
        #     norm = mpl.colors.TwoSlopeNorm(
        #         vmin=min_diff, vcenter=0, vmax=max_diff
        #     )  # 强制0为中点的正太分布渐变色

        # colors = [cmap(norm(value)) for value in list_diff]

        # 使用Squarify导出矩形数据，以数据手动画图，可以控制更多元素
        list_size = df_size1[size].tolist()
        list_size = squarify.normalize_sizes(
            list_size, self.figure.width, self.figure.height
        )  # 根据设置的总体宽高正态化数据
        rects_data = squarify.squarify(
            list_size, 0, 0, self.figure.width, self.figure.height
        )  # Squarify算法计算出所有矩形的数据

        # 根据数据循环创建矩形并添加标签
        for i, r in enumerate(rects_data):
            color = self._colors.get_color(df.index[i])

            rect = patches.Rectangle(
                (r["x"], r["y"]),
                r["dx"],
                r["dy"],
                linewidth=10,
                edgecolor="#222222",
                facecolor=color,
            )  # 创建四边形
            self.ax.add_patch(rect)  # Add patch到轴
            # 动态添加标签并设置标签字体大小
            if r["dx"] > 0.02 * (self.figure.width * self.figure.height) or r["dx"] * r[
                "dy"
            ] > 0.01 * (self.figure.width * self.figure.height):
                plt.text(
                    (
                        r["x"] + r["dx"] / 2
                        if level2 is None
                        else r["x"] + r["dx"] * 0.05
                    ),  # 如无level2，则rect的水平中心，否则rect的left稍往右偏移
                    (
                        r["y"] + r["dy"] / 2
                        if level2 is None
                        else r["y"] + r["dy"] - r["dx"] * 0.05
                    ),  # 如无level2，则rect的垂直中心，否则rect的Top稍往下偏移
                    df_size1.index[i],
                    ha="center" if level2 is None else "left",
                    va="center",
                    multialignment="center",
                    fontsize=(self.fontsize * r["dx"])
                    ** 0.5,  # / (self.width * self.height),
                    color="black" if level2 is None else "grey",
                )
            # # 前十名左上角添加Rank
            # if i < 10:
            #     plt.text(
            #         r["x"] + r["dx"] * 0.1,  # rect的left稍往右偏移
            #         r["y"] + r["dy"] - r["dx"] * 0.1,  # rect的Top稍往下偏移
            #         i + 1,
            #         ha="center",
            #         va="center",
            #         multialignment="center",
            #         # fontproperties=MYFONT,
            #         fontsize=(self.fontsize * r["dx"])
            #         ** 0.5,  # / (self.width * self.height),
            #     )

            # 绘制Level2
            if level2 is not None:
                df_size2 = pd.pivot_table(
                    data=df[df[level1] == df_size1.index[i]],
                    index=level2,
                    columns=None,
                    values=size,
                    aggfunc=sum,
                ).sort_values(by=size, ascending=False)
                list_size2 = df_size2[size].tolist()
                list_size2 = squarify.normalize_sizes(
                    list_size2, r["dx"], r["dy"]
                )  # 根据设置的总体宽高正态化数据
                rects_data = squarify.squarify(
                    list_size2, r["x"], r["y"], r["dx"], r["dy"]
                )  # Squarify算法计算出所有矩形的数据

                for j, r2 in enumerate(rects_data):
                    rect2 = patches.Rectangle(
                        (r2["x"], r2["y"]),
                        r2["dx"],
                        r2["dy"],
                        linewidth=2,
                        edgecolor="#222222",
                        facecolor=color if self.hue is None else colors[i],
                    )  # 创建四边形
                    self.ax.add_patch(rect2)  # Add patch到轴
                    # 动态添加标签并设置标签字体大小
                    if r2["dx"] > 0.02 * (self.figure.width * self.figure.height) or r2[
                        "dx"
                    ] * r["dy"] > 0.01 * (self.figure.width * self.figure.height):
                        plt.text(
                            r2["x"] + r2["dx"] / 2,  # rect的水平中心
                            r2["y"] + r2["dy"] / 2,  # rect的垂直中心
                            df_size2.index[j],
                            ha="center",
                            va="center",
                            multialignment="center",
                            fontsize=(self.fontsize * r2["dx"])
                            ** 0.5,  # / (self.width * self.height),
                        )

        # 去除边框的刻度
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Squarify包要求width和height的乘积等于上方主数据的和，所以要如此设置
        self.ax.set_xlim(0, self.figure.width)
        self.ax.set_ylim(0, self.figure.height)

        return self


# 继承基本类, 绘制饼图
class PlotPie(Plot):
    def plot(
        self,
        size: Optional[str] = None,
        label_formatter: str = "{abs}",
        donut: bool = False,
        donut_title: Optional[str] = None,
        **kwargs,
    ) -> PlotPie:
        """继承基本类，绘制饼图

        Args:
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
            donut (bool, optional): 甜甜圈图还是饼图. Defaults to False.
            donut_title (Optional[str], optional): 甜甜圈图中间的文字. Defaults to None.

        Returns:
            PlotPie: 返回一个自身实例
        """
        df = self.data

        # 如果不指定，则分别读取df第1列为size
        size = df.iloc[:, 0] if size is None else df.loc[:, size]
        share = size.transform(lambda x: x / x.sum())

        df_mask = []
        for index, value in share.items():
            df_mask.append(abs(value))  # 加abs是为了防止项目有负数

        d_style = {
            "pct_distance": 0.8,
            "start_angle": 90,
            "counter_clock": False,
            "line_width": 1,
            "edgecolor": "white",
            "label_fontsize": self.fontsize,
            "circle_distance": 0.7,
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        # Draw the pie chart
        wedges, texts, autotexts = self.ax.pie(
            df_mask,
            labels=df.index,
            autopct="%1.1f%%",
            pctdistance=d_style.get("pct_distance"),
            startangle=d_style.get("start_angle"),
            counterclock=d_style.get("counter_clock"),
            wedgeprops={
                "linewidth": d_style.get("line_width"),
                "edgecolor": d_style.get("edgecolor"),
            },
            textprops={"fontsize": d_style.get("label_fontsize")},
        )

        for i, pie_wedge in enumerate(wedges):
            # 如果有指定颜色就颜色，否则按预设列表选取
            color = self._colors.get_color(pie_wedge.get_label())
            pie_wedge.set_facecolor(color)

            if size.iloc[i] < 0:
                pie_wedge.set_facecolor("white")

        for k, autotext in enumerate(autotexts):
            d_label = {
                "abs": kwargs.get("fmt_abs", self.fmt).format(size.iloc[k]),
                "share": kwargs.get("fmt_share", "{:.1%}").format(share.iloc[k]),
                "index": index,
            }
            autotext.set_color("white")
            autotext.set_fontsize(self.fontsize)
            autotext.set_text(label_formatter.format(**d_label))
            if size.iloc[k] < 0:
                autotext.set_color("r")

        if donut:
            # Prepare the white center circle for Donat shape
            my_circle = plt.Circle(
                (0, 0), d_style.get("circle_distance"), color="white"
            )
            self.ax.text(
                0,
                0,
                donut_title,
                horizontalalignment="center",
                verticalalignment="center",
                size=self.fontsize,
            )
            self.ax.add_artist(my_circle)  # 用白色圆圈覆盖饼图，变成圈图

        self.style._show_legend = False  # Pie图默认不显示图例

        return self


# 继承基本类, 绘制华夫图waffle plot
class PlotWaffle(Plot):
    def plot(
        self,
        rows: int = 10,
        columns: int = 10,
        size: Optional[str] = None,
        colors: Optional[List[str]] = None,
        vertical: bool = True,
        block_arranging_style: Literal["snake", "new-line"] = "snake",
        icons: Optional[Union[List[str], str]] = None,
        **kwargs,
    ) -> PlotWaffle:
        """继承基本类，绘制华夫图

        Args:
            rows (int, optional): 行数. Defaults to 10.
            columns (int, optional): 列数. Defaults to 10.
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
            colors (Optional[List[str]], optional): 指定颜色列表，如不指定将使用默认颜色方案. Defaults to None.
            vertical (bool, optional): 分类按垂直发展. Defaults to True.
            block_arranging_style (Literal["snake", "new"], optional): 每个分类如何起始，"snake"为紧接上类末尾，"new-line"为每类新起一行. Defaults to "snake".
            icons (Optional[Union[List[str], str]], optional): 指定矢量图形，为Font Awesome字符串. Defaults to None.

        Returns:
            PlotWaffle: 返回一个自身实例
        """
        df = self.data

        # 如果不指定，则分别读取df第1列为size
        size = df.iloc[:, 0] if size is None else df.loc[:, size]
        share = (
            size.transform(lambda x: x / x.sum()).mul(100).astype(int).values.tolist()
        )

        if colors is None:
            colors = []
            for idx in size.index:
                if idx in self._color_dict.keys():
                    colors.append(self._colors.get_color(idx))
                else:
                    colors.append(next(self._colors.iter_colors))

        self.ax.set_aspect(aspect="equal")
        # self.style._show_legend = False  # 不再使用Plot类的通用方法生成图例

        Waffle.make_waffle(
            ax=self.ax,  # pass axis to make_waffle
            rows=rows,
            columns=columns,
            values=share,
            colors=colors,
            rounding_rule="ceil",
            vertical=vertical,
            block_arranging_style=block_arranging_style,
            icons=icons,
            # legend={
            #     "labels": [k for k in size.index],
            #     "loc": "lower left",
            #     "bbox_to_anchor": (0, -0.4),
            #     "fontsize": self.fontsize,
            # },
            **kwargs,
        )

        return self


# 继承基本类, 绘制漏斗图
class PlotFunnel(Plot):
    def plot(
        self, size: Optional[str] = None, height: Optional[float] = 0.7, **kwargs
    ) -> PlotFunnel:
        df = self.data

        # 设置默认风格，并根据kwargs更新
        d_style = {
            "color": "navy",
            "bbox": dict(
                boxstyle="round,pad=0.5",
                facecolor="grey",
                edgecolor="black",
                linewidth=1,
                alpha=0.5,
            ),
            "label_ha": "center",  # "center", "right", "left
            "show_label": True,
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        labels = df.index
        size = df.iloc[:, 0] if size is None else df.loc[:, size]
        max = size[0]
        dummy1 = [max / 2 - i / 2 for i in size]  # 为了形成漏斗两侧的留白
        dummy2 = [
            i + j for i, j in zip(size, dummy1)
        ]  # 原始值+留白，使漏斗bar出现在图片中间

        self.ax.barh(
            labels[::-1], dummy2[::-1], color=d_style.get("color"), height=height
        )
        self.ax.barh(labels[::-1], dummy1[::-1], color="white", height=height)
        self.ax.axis("off")

        polygons = []
        for i in range(len(size)):
            # 标签
            if d_style.get("show_label"):
                self.ax.text(
                    max * (-0.1),
                    i,
                    labels[::-1][i],
                    ha=d_style.get("label_ha"),
                    va="center",
                    multialignment="center",
                    fontsize=self.fontsize * 1.2,
                    bbox=d_style.get("bbox"),
                )

            # 数量
            self.ax.text(
                dummy2[0] / 2,
                i,
                self.fmt.format(size[::-1][i]),
                ha="center",
                va="center",
                multialignment="center",
                fontsize=self.fontsize,
                color="white",
            )

            # 转化率
            if i < (len(size) - 1):
                self.ax.text(
                    dummy2[0] / 2,
                    len(size) - 1.5 - i,
                    "{:.1%}".format(size[i + 1] / size[i]),
                    ha="center",
                    va="center",
                    multialignment="center",
                    fontsize=self.fontsize,
                )

                polygons.append(
                    patches.Polygon(
                        xy=np.array(
                            [
                                (dummy1[i + 1], len(size) - 2 + height / 2 - i),
                                (dummy2[i + 1], len(size) - 2 + height / 2 - i),
                                (dummy2[i], len(size) - 1 - height / 2 - i),
                                (dummy1[i], len(size) - 1 - height / 2 - i),
                            ]
                        )
                    )
                )
        self.ax.add_collection(
            PatchCollection(polygons, facecolor=d_style.get("color"), alpha=0.5)
        )
        return self


# 继承基本类, 绘制2组数据的Venn图
class PlotVenn2(Plot):

    def plot(
        self,
        set1: Optional[set] = None,
        set2: Optional[set] = None,
        set_labels: tuple = None,
        **kwargs,
    ) -> PlotVenn2:
        """继承基本类，绘制2组数据的Venn图

        Args:
            set1 (Optional[set], optional): 第1组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set2 (Optional[set], optional): 第2组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set_labels (tuple, optional): 组别标签. Defaults to None.

        Returns:
            PlotVenn2: 返回一个自身实例
        """
        if all((set1, set2)):
            v = venn2(subsets=(set1, set2), set_labels=set_labels, ax=self.ax)
            venn2_circles(subsets=(set1, set2), ax=self.ax)
        else:
            v = venn2(subsets=self.data, set_labels=set_labels, ax=self.ax)
            venn2_circles(subsets=self.data, ax=self.ax)

        # 获取并设置所有文本对象的字体大小
        for text in self.ax.texts:
            text.set_fontsize(self.fontsize)

        # 颜色
        if color := kwargs.get("color"):
            for i, id in enumerate(["10", "01", "11"]):
                v.get_patch_by_id(id).set_color(color[i])

        return self


class PlotVenn3(Plot):

    def plot(
        self,
        set1: Optional[set] = None,
        set2: Optional[set] = None,
        set3: Optional[set] = None,
        set_labels: tuple = None,
        **kwargs,
    ) -> PlotVenn2:
        """继承基本类，绘制2组数据的Venn图

        Args:
            set1 (Optional[set], optional): 第1组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set2 (Optional[set], optional): 第2组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set3 (Optional[set], optional): 第3组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set_labels (tuple, optional): 组别标签. Defaults to None.

        Returns:
            PlotVenn3: 返回一个自身实例
        """
        if all((set1, set2, set3)):
            v = venn3(subsets=(set1, set2, set3), set_labels=set_labels, ax=self.ax)
            venn3_circles(subsets=(set1, set2, set3), ax=self.ax)
        else:
            v = venn3(subsets=self.data, set_labels=set_labels, ax=self.ax)
            venn3_circles(subsets=self.data, ax=self.ax)

        # 获取并设置所有文本对象的字体大小
        for text in self.ax.texts:
            text.set_fontsize(self.fontsize)

        # 颜色
        if color := kwargs.get("color"):
            for i, id in enumerate(["100", "010", "110", "001", "101", "011", "111"]):
                try:
                    v.get_patch_by_id(id).set_color(color[i])
                except IndexError:
                    pass
                
        return self


class PlotTable(Plot):
    def plot(
        self, col_defs: Optional[List[ColumnDefinition]] = None, **kwargs
    ) -> PlotTable:
        """继承基本类，使用Plottable库绘制表格

        Args:
            col_defs (Optional[List[ColumnDefinition]]): 列样式定义, defaults to None.

        Returns:
            PlotTable: 返回一个自身实例
        """
        df = self.data

        table = Table(
            df=df,
            ax=self.ax,
            column_definitions=col_defs,
            row_dividers=True,
            footer_divider=True,
            textprops={
                "fontsize": self.fontsize,
            },
            even_row_color="#eeeeee",
            row_divider_kw={"linewidth": 1, "linestyle": (0, (1, 5))},
            col_label_divider_kw={"linewidth": 1, "linestyle": "-"},
            col_label_cell_kw={"height": 2},
            column_border_kw={"linewidth": 1, "linestyle": "-"},
        ).autoset_fontcolors(colnames=df.columns)
        
        # 指定行背景色
        if kwargs.get("row_facecolors") is not None:
            row_facecolors = kwargs.get("row_facecolors")
            for i, row in enumerate(df.index):
                if row in row_facecolors.keys():
                    table.rows[i].set_facecolor(row_facecolors[row])
        
        # 指定行字体色
        if kwargs.get("row_fontcolors") is not None:
            row_fontcolors = kwargs.get("row_fontcolors")
            for i, row in enumerate(df.index):
                if row in row_fontcolors.keys():
                    table.rows[i].set_fontcolor(row_fontcolors[row])

        return self
