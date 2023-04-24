from __future__ import annotations
from color import cmap_qual, COLOR_DICT
from wordcloud import WordCloud
from typing import Any, Callable, Dict, List, Tuple, Union, Optional
import matplotlib.font_manager as fm
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator
import math
from adjustText import adjust_text
from itertools import cycle
import scipy.stats as stats
from mpl_toolkits.axes_grid1 import make_axes_locatable
import warnings

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

RANDOM_CMAP = mpl.colors.ListedColormap(np.random.rand(256, 3))


class Plot:
    def __init__(
        self,
        data,  # 原始数
        ax=None,
        fontsize: int = 14,  # 字体大小
        fmt: str = "{:,.0f}",  # 基本数字格式
        style: Dict[str, Any] = {},  # 风格字典
        *args,
        **kwargs,
    ):
        self.data = data
        self.ax = ax or plt.gca()
        self.fontsize = fontsize
        self.figure = self.ax.get_figure()
        self.fmt = fmt
        self._style = style
        self.style = self.Style(self, **self._style)

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

        def xlim(self, xlim: Tuple[Tuple[float, float]]) -> None:
            """设置x轴的边界

            Parameters
            ----------
            xlim : Tuple[Tuple[float, float]]
                包含x轴下界和上界的tuple
            """
            self._plot.ax.set_xlim(xlim[0], xlim[1])

        def ylim(self, ylim: Tuple[Tuple[float, float]]) -> None:
            """设置y轴的边界

            Parameters
            ----------
            ylim : Tuple[Tuple[float, float]]
                包含y轴下界和上界的tuple
            """
            self._plot.ax.set_ylim(ylim[0], ylim[1])

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
                )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
            except:
                by_label = dict(
                    zip(
                        labels[::-1],
                        handles[::-1],
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
        hue: Optional[str] = None,
        x_avg: Optional[float] = None,
        y_avg: Optional[float] = None,
        label_limit: int = 15,
        label_formatter: str = "{index}",
        bubble_scale: float = 1,
        show_reg: bool = False,
        corr: Optional[float] = None,
        **kwargs,
    ) -> PlotBubble:
        """继承基本类，绘制散点图

        Args:
            x (Optional[str], optional): 指定x轴变量字段名，如为None，则x为data第1列. Defaults to None.
            y (Optional[str], optional): 指定y轴变量字段名，如为None，则x为data第2列. Defaults to None.
            z (Optional[str], optional): 指定气泡大小字段名，如为None，则气泡大小为data第3列. Defaults to None.
            hue (Optional[str], optional): 指定气泡颜色字段名. Defaults to None.
            x_avg (Optional[float], optional): x轴平均值或其他分隔值，如提供则绘制x轴分隔竖线. Defaults to None.
            y_avg (Optional[float], optional): y轴平均值或其他分隔值，如提供则绘制y轴分隔水平线. Defaults to None.
            label_limit (int, optional): 限制显示标签的个数. Defaults to 15.
            label_formatter (str, optional): 标签文字的格式，支持{index}, {x}, {y}, {z}, {hue}. Defaults to "{index}".
            bubble_scale (float, optional): 气泡大小系数. Defaults to 1.
            show_reg (bool, optional): 是否显示x,y的拟合趋势及置信区间. Defaults to False.
            corr (Optional[float], optional): 相关系数，如不为None，则显示在ax左上角. Defaults to None.

        Kwargs:
            x_fmt (str, optional): x轴显示数字格式，影响轴刻度标签及分隔线数据标签. Defaults to "{:,.0f}",
            y_fmt (str, optional): y轴显示数字格式，影响轴刻度标签及分隔线数据标签. Defaults to "{:,.0f}",
            alpha (float, optional): 气泡透明度. Defaults to 0.6,
            edgecolor (str, optional): 气泡边框颜色. Defaults to "black",
            avg_linestyle (str, optional): 分隔线样式. Defaults to ":",
            avg_linewidth (float, optional): 分隔线宽度. Defaults to 1,
            avg_color (str, optional): 分隔线及数据标签颜色. Defaults to "black",

        Returns:
            PlotBubble: 返回自身实例
        """

        df = self.data

        # 如果不指定，则分别读取df第1-4列为x,y,z,hue
        x = df.iloc[:, 0] if x is None else df.loc[:, x]
        y = df.iloc[:, 1] if y is None else df.loc[:, y]
        z = df.iloc[:, 2] if z is None else df.loc[:, z]
        if hue is not None:
            hue = df.loc[:, hue]

        # z列标准化并乘以系数以得到一般情况下都合适的气泡大小
        z = (z - z.min()) / (z.max() - z.min())
        z = (z * 100) ** 1.8 * bubble_scale

        # 设置默认风格，并根据kwargs更新
        d_style = {
            "x_fmt": "{:,.0f}",
            "y_fmt": "{:,.0f}",
            "alpha": 0.6,
            "edgecolor": "black",
            "avg_linestyle": ":",
            "avg_linewidth": 1,
            "avg_color": "black",
        }
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        # 确定颜色方案
        if hue is None:
            cmap = RANDOM_CMAP
        else:
            # 如果hue字段是numeric
            if pd.api.types.is_numeric_dtype(hue.dtype):
                cmap = self.figure.cmap_norm
            # 如果hue字段是categorical
            else:
                cmap = self.figure.cmap_qual

        # 根据hue列给bubble着色
        if hue is not None:
            # 如果hue字段是numeric
            if pd.api.types.is_numeric_dtype(hue.dtype):
                colors = hue
            else:  # 如果hue字段是categorical
                levels, categories = pd.factorize(hue)
                colors = [cmap(i) for i in levels]
                # 涉及hue的散点图图例很特殊，按以下方法处理
                if self.style._show_legend is True:
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
                        for i, c in enumerate(categories)
                    ]
                    handles = sorted(handles, key=lambda h: h.get_label())
                    self.ax.legend(
                        handles=handles,
                        title=hue.name,
                        loc=self.style._legend_loc,
                        frameon=False,
                        ncol=self.style._legend_ncol,
                        bbox_to_anchor=(1, 0.5)
                        if self.style._legend_loc == "center left"
                        else (0.5, 1),
                        prop={"family": "Microsoft YaHei", "size": self.fontsize},
                    )
                    self.style._show_legend = False  # 不再使用Plot类的通用方法生成图例
        else:  # 不指定hue，则随机着色
            colors = [cmap(i) for i in range(len(x))]

        # 绘制气泡
        scatter = self.ax.scatter(
            x,
            y,
            z,
            c=colors,
            cmap=cmap,
            alpha=d_style.get("alpha"),
            edgecolors=d_style.get("edgecolor"),
            zorder=3,
        )

        # 如果hue存在并且是连续变量，添加colorbar
        if hue is not None:
            if pd.api.types.is_numeric_dtype(hue.dtype):
                divider = make_axes_locatable(self.ax)
                cax = divider.append_axes("right", size="5%", pad=0.05)
                cbar = self.figure.colorbar(scatter, cax=cax, orientation="vertical")
                cbar.set_label(hue.name)
                cbar.ax.set_zorder(0)
                self.figure.style._label_outer = (
                    False  # color是一个独立的ax，但是不支持label_outer()
                )
                warnings.warn("画布存在colorbar，label_outer风格不生效", UserWarning)

        # 添加系列标签
        np.random.seed(0)
        texts = []
        for i in range(len(df.index[:label_limit])):
            d_label = {
                "x":d_style.get("x_fmt").format(x[i]),
                "y":d_style.get("y_fmt").format(y[i]),
                "z":z[i],
                "hue":hue[i] if hue is not None else None,
                "index":df.index[i]
            }
            texts.append(
                self.ax.text(
                    x[i],
                    y[i],
                    label_formatter.format(**d_label),
                    ha="center",
                    va="center",
                    multialignment="center",
                    fontsize=self.fontsize,
                )
            )

        # 用adjust_text包保证标签互不重叠
        if label_limit > 1:
            adjust_text(
                texts,
                ax=self.ax,
                force_text=0.5,
                arrowprops=dict(arrowstyle="->", color="black"),
            )

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
                d_style.get("y_fmt").format(y_avg),
                ha="right",
                va="top",
                color=d_style.get("avg_color"),
                multialignment="center",
                fontsize=self.fontsize,
                zorder=1,
            )

        """以下部分绘制回归拟合曲线及CI和PI
        参考
        http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/CurveFitting.ipynb
        https://stackoverflow.com/questions/27164114/show-confidence-limits-and-prediction-limits-in-scatter-plot
        """
        if show_reg:
            n = len(x)  # 观察例数
            if n > 2:  # 数据点必须大于cov矩阵的scale
                p, cov = np.polyfit(x, y, 1, cov=True)  # 简单线性回归返回parameter和covariance
                poly1d_fn = np.poly1d(p)  # 拟合方程
                y_model = poly1d_fn(x)  # 拟合的y值
                m = p.size  # 参数个数

                dof = n - m  # degrees of freedom
                t = stats.t.ppf(0.975, dof)  # 显著性检验t值

                # 拟合结果绘图
                self.ax.plot(
                    x,
                    y_model,
                    "-",
                    color="0.1",
                    linewidth=1.5,
                    alpha=0.5,
                    label="Fit",
                )

                # 误差估计
                resid = y - y_model  # 残差
                s_err = np.sqrt(np.sum(resid**2) / dof)  # 标准误差

                # 拟合CI和PI
                x2 = np.linspace(np.min(x), np.max(x), 100)
                y2 = poly1d_fn(x2)

                # CI计算和绘图
                ci = (
                    t
                    * s_err
                    * np.sqrt(
                        1 / n + (x2 - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2)
                    )
                )
                self.ax.fill_between(
                    x2,
                    y2 + ci,
                    y2 - ci,
                    color="#b9cfe7",
                    edgecolor=["none"],
                    alpha=0.5,
                )

                # Pi计算和绘图
                pi = (
                    t
                    * s_err
                    * np.sqrt(
                        1
                        + 1 / n
                        + (x2 - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2)
                    )
                )
                self.ax.fill_between(
                    x2, y2 + pi, y2 - pi, color="None", linestyle="--", linewidth=1
                )
                self.ax.plot(
                    x2, y2 - pi, "--", color="0.5", label="95% Prediction Limits"
                )
                self.ax.plot(x2, y2 + pi, "--", color="0.5")

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


# class PlotBoxWithDots(GridFigure):
#     def plot(
#         self,
#         label_limit: int = 0,
#         label_threshold: float = 0,
#         show_stats: bool = True,
#         order: Union[None, list] = None,
#         dot_size: int = 8,
#     ) -> str:
#         """继承基本类，绘制带数据点的箱型图

#         Parameters
#         ----------
#         label_limit : int, optional
#             展示数据点标签的数量, by default 0
#         label_threshold : float, optional
#             对大于此值的数据点展示标签, by default 0
#         show_stats : bool, optional
#             是否显示统计值，包括最大值、最小值、中位数, by default True
#         order : Union[None, list], optional
#             类别按什么排序，如果为None则按照数据自动排序, by default None
#         dot_size : int, optional
#             数据点大小, by default 8

#         Returns
#         -------
#         str
#             返回绘图保存的路径
#         """
#         for j, ax in enumerate(self.axes):
#             try:
#                 df = self.data[j]
#             except IndexError:
#                 ax.axis("off")
#                 continue

#             x = df.columns[0]
#             y = df.columns[1]

#             ax = sns.stripplot(
#                 x=x,
#                 y=y,
#                 data=df,
#                 edgecolor="black",
#                 alpha=0.5,
#                 s=dot_size,
#                 linewidth=1.0,
#                 jitter=0.2,
#                 ax=ax,
#                 order=order,
#             )
#             ax = sns.boxplot(
#                 x=x,
#                 y=y,
#                 data=df,
#                 whis=np.inf,
#                 boxprops={"facecolor": "None"},
#                 order=order,
#             )

#             ax_xticklabels = [t.get_text() for t in ax.get_xticklabels()]  # 获取x轴标签列表

#             # 添加数据点标签

#             labels = []
#             for category in ax_xticklabels:
#                 df_temp = df[df[x] == category]
#                 for k, idx in enumerate(df_temp.index):
#                     if k == label_limit:
#                         break

#                     point = ax.collections[
#                         ax_xticklabels.index(category)
#                     ].get_offsets()[
#                         k
#                     ]  # 获得散点图的坐标，因为有jitter，不能直接用原始数

#                     if point[1] > label_threshold:  # y值大于某阈值的才显示
#                         labels.append(
#                             plt.text(
#                                 point[0],
#                                 point[1],
#                                 idx,
#                                 size=self.fontsize * 0.8,
#                                 color="black",
#                             )
#                         )

#             adjust_text(
#                 labels,
#                 force_text=0.5,
#                 arrowprops=dict(arrowstyle="->", color="black"),
#             )

#             # 添加最大值， 最小值，中位数标签
#             if show_stats:
#                 df_groupby = df.groupby(x)[y]
#                 maxs = df_groupby.max().reindex(ax_xticklabels)  # 最高值
#                 mins = df_groupby.min().reindex(ax_xticklabels)  # 最低值
#                 medians = df_groupby.median().reindex(ax_xticklabels)  # 中位数

#                 for l in [maxs, mins, medians]:
#                     for xtick in ax.get_xticks():
#                         if l is medians:
#                             posx = xtick + 0.4
#                         else:
#                             posx = xtick + 0.25

#                         ax.text(
#                             posx,
#                             l[xtick],
#                             self.fmt.format(l[xtick]),
#                             horizontalalignment="left",
#                             verticalalignment="center",
#                             size=self.fontsize,
#                             color="black",
#                             weight="semibold",
#                         )

#         return self.save()


# class PlotWordCloud(GridFigure):
#     def plot(
#         self,
#         mask_shape: str = "rectangle",
#         mask_width: int = 800,
#         mask_height: int = 600,
#     ) -> str:
#         """继承基本类，绘制文字云图

#         Parameters
#         ----------
#         mask_shape : str, optional
#             词云形状类别:circle|rectangle, by default "rectangle"
#         mask_width : int, optional
#             形状为矩形时的矩形宽度, by default 800
#         mask_height : int, optional
#             形状为矩形时的矩形高度, by default 600

#         Returns
#         -------
#         str
#             返回绘图保存的路径
#         """
#         for j, ax in enumerate(self.axes):
#             try:
#                 df = self.data[j]
#             except IndexError:
#                 ax.axis("off")
#                 continue
#             df.dropna(inplace=True)

#             d_words = {}
#             for index, row in df.iterrows():
#                 d_words[index] = row[0]

#             if mask_shape == "circle":
#                 # 产生一个以(150,150)为圆心,半径为130的圆形mask
#                 x, y = np.ogrid[:600, :600]
#                 mask = (x - 300) ** 2 + (y - 300) ** 2 > 260**2
#                 mask = 255 * mask.astype(int)
#                 wordcloud = WordCloud(
#                     width=800,
#                     height=800,
#                     font_path="C:/Windows/Fonts/SimHei.ttf",
#                     background_color="white",
#                     mask=mask,
#                 )
#             elif mask_shape == "rectangle":
#                 wordcloud = WordCloud(
#                     width=mask_width,
#                     height=mask_height,
#                     font_path="C:/Windows/Fonts/SimHei.ttf",
#                     background_color="white",
#                 )

#             wordcloud.generate_from_frequencies(frequencies=d_words)

#             ax.imshow(wordcloud, interpolation="bilinear")
#             ax.axis("off")

#         return self.save()


# class PlotLine(GridFigure):
#     def plot(
#         self,
#         series_showlabel: List[str] = [],
#         endpoint_label_only: bool = False,
#     ) -> str:
#         """继承基本类，绘制线形图

#         Parameters
#         ----------
#         series_showlabel : List[str], optional
#             指定要显示标签的系列, by default []
#         endpoint_label_only : bool, optional
#             标签是全部显示还是只显示首尾节点, by default False

#         Returns
#         -------
#         str
#             返回绘图保存的路径
#         """
#         for j, ax in enumerate(self.axes):
#             df = self.data[j]
#             ITER_COLORS = cycle(COLOR_LIST)
#             # Generate the lines
#             for i, column in enumerate(df.columns):
#                 markerstyle = "o"

#                 # 如果有指定颜色就颜色，否则按预设列表选取
#                 color = COLOR_DICT.get(column, next(ITER_COLORS))

#                 ax.plot(
#                     df.index,
#                     df[column],
#                     color=color,
#                     linewidth=2,
#                     label=column,
#                     marker=markerstyle,
#                     markersize=5,
#                     markerfacecolor="white",
#                     markeredgecolor=color,
#                 )

#                 # 标签
#                 if column in series_showlabel:
#                     for k, idx in enumerate(df.index):
#                         if endpoint_label_only:
#                             if k == 0 or k == len(df.index) - 1:
#                                 t = plt.text(
#                                     idx,
#                                     df.iloc[k, i],
#                                     self.fmt.format(df.iloc[k, i]),
#                                     ha="right" if k == 0 else "left",
#                                     va="center",
#                                     size=self.fontsize,
#                                     color="white",
#                                 )

#                                 t.set_bbox(
#                                     dict(facecolor=color, alpha=0.7, edgecolor=color)
#                                 )
#                         else:
#                             t = plt.text(
#                                 idx,
#                                 df.iloc[k, i],
#                                 self.fmt.format(df.iloc[k, i]),
#                                 ha="center",
#                                 va="center",
#                                 size=self.fontsize,
#                                 color="white",
#                             )
#                             t.set_bbox(
#                                 dict(facecolor=color, alpha=0.7, edgecolor=color)
#                             )

#                 # Customize the major grid
#                 ax.grid(which="major", linestyle=":", linewidth="0.5", color="grey")

#                 # y轴标签格式
#                 ax.yaxis.set_major_formatter(
#                     FuncFormatter(lambda y, _: self.fmt.format(y))
#                 )

#                 # Shrink current axis by 20% and put a legend to the right of the current axis
#                 box = ax.get_position()
#                 # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#                 ax.legend(
#                     loc="center left",
#                     bbox_to_anchor=(1, 0.5),
#                     labelspacing=1.5,
#                     frameon=False,
#                     prop={"family": "SimHei", "size": self.fontsize},
#                 )

#         return self.save()


# # 继承基本类，堆积柱状对比图类
# class PlotStackedBar(GridFigure):
#     def __init__(
#         self,
#         data,  # 原始数
#         savepath: str = "./plots/",  # 保存位置
#         width: int = 15,  # 宽
#         height: int = 6,  # 高
#         fontsize: int = 14,  # 字体大小
#         gs: GridSpec = None,  # GridSpec
#         fmt: str = "{:,.0f}",  # 基本数字格式
#         style: dict = {},  # 风格字典
#         data_line=None,  # 折线图数据
#         fmt_line=None,  # 折线图格式
#         *args,
#         **kwargs,
#     ):
#         super().__init__(
#             data,
#             savepath,
#             width,
#             height,
#             fontsize,
#             gs,
#             fmt,
#             style,
#             *args,
#             **kwargs,
#         )
#         self.data_line = data_to_list(data_line)
#         if fmt_line is not None:
#             self.fmt_line = ["{:%s}" % f for f in fmt_line]
#         else:
#             self.fmt_line = None

#         if self.data_line is not None:
#             check_data_with_axes(self.data_line, self.axes)
#         if self.fmt_line is not None:
#             check_data_with_axes(self.fmt_line, self.axes)

#     def plot(
#         self,
#         stacked: bool = True,
#         show_label: bool = True,
#         show_total_label: bool = False,
#         add_gr_text: bool = False,
#         threshold: float = 0.02,
#         show_legend: bool = True,
#         *args,
#         **kwargs,
#     ) -> str:
#         """继承基本类，绘制堆积柱状图

#         Parameters
#         ----------
#         stacked : bool, optional
#             是否堆积, by default True
#         show_label : bool, optional
#             是否显示数字标签, by default True
#         show_total_label : bool, optional
#             是否在最上方显示堆积之和数字标签, by default False
#         add_gr_text : bool, optional
#             是否显示增长率数字, by default False
#         threshold : float, optional
#             显示数字标签的阈值，系列占堆积之和的比例大于此值才显示, by default 0.02
#         show_legend : bool, optional
#             是否显示图例, by default True

#         Returns
#         -------
#         str
#             返回绘图保存的路径
#         """
#         for j, ax in enumerate(self.axes):
#             # 处理绘图数据
#             df = self.data[j]
#             df_gr = self.data[j].pct_change(axis=1)
#             if self.data_line is not None:
#                 df_line = self.data_line[j]

#             # 绝对值bar图和增长率标注
#             for k, index in enumerate(df.index):
#                 bottom_pos = 0
#                 bottom_neg = 0
#                 bottom_gr = 0
#                 bbox_props = None
#                 max_v = df.values.max()
#                 min_v = df.values.min()
#                 ITER_COLORS = cycle(COLOR_LIST)
#                 for i, col in enumerate(df):
#                     v = df.loc[index, col]

#                     if stacked:
#                         if v >= 0:
#                             bottom = bottom_pos
#                         else:
#                             bottom = bottom_neg
#                     else:
#                         bottom = 0

#                     # 如果有指定颜色就颜色，否则按预设列表选取
#                     if stacked:
#                         if col in COLOR_DICT.keys():
#                             color = COLOR_DICT[col]
#                         elif index in COLOR_DICT.keys():
#                             color = COLOR_DICT[index]
#                         else:
#                             color = next(ITER_COLORS)
#                     else:
#                         color = next(ITER_COLORS)

#                     # bar宽度
#                     bar_width = 0
#                     if stacked:
#                         bar_width = 0.5
#                         # if isinstance(
#                         #     df.index, pd.DatetimeIndex
#                         # ):  # 如果x轴是日期，宽度是以“天”为单位的
#                         #     bar_width = 20
#                         # else:
#                         #     bar_width = 0.5
#                     else:
#                         bar_width = 0.8 / df.shape[1]

#                     # bar x轴位置
#                     if stacked:
#                         pos_x = k
#                     else:
#                         pos_x = k + bar_width * i

#                     # 绘制bar图
#                     bar = ax.bar(
#                         pos_x,
#                         v,
#                         width=bar_width,
#                         color=color,
#                         bottom=bottom,
#                         label=col,
#                         zorder=3,
#                     )

#                     if show_label is True:
#                         if stacked is False or df.shape[1] == 1:  # 非堆叠图或只有一列数的情况（非堆叠）
#                             # 根据数据判断标签是否需要微调
#                             if 0 <= v < max_v * 0.05:
#                                 pos_y = v * 1.1
#                                 va = "bottom"
#                                 fontcolor = color
#                             elif min_v * 0.05 < v < 0:
#                                 pos_y = v * 0.9
#                                 va = "top"
#                                 fontcolor = color
#                             else:
#                                 pos_y = v / 2
#                                 va = "center"
#                                 fontcolor = "white"

#                         else:  # 堆叠的情况
#                             pos_y = bottom + v / 2
#                             va = "center"
#                             fontcolor = "white"

#                         if abs(v / ax.get_ylim()[1]) >= threshold:
#                             ax.text(
#                                 pos_x,
#                                 pos_y,
#                                 self.fmt.format(v),
#                                 color=fontcolor,
#                                 va=va,
#                                 ha="center",
#                                 fontsize=self.fontsize,
#                                 zorder=5,
#                                 **NUM_FONT,
#                             )
#                     if v >= 0:
#                         bottom_pos += v
#                     else:
#                         bottom_neg += v

#                     patches = ax.patches
#                     for rect in patches:
#                         height = rect.get_height()
#                         # 负数则添加纹理
#                         if height < 0:
#                             rect.set_hatch("//")

#                     if add_gr_text:
#                         if k > 0:
#                             # 各系列增长率标注
#                             ax.annotate(
#                                 "{:+.1%}".format(df_gr.iloc[k, i]),
#                                 xy=(
#                                     0.5,
#                                     (
#                                         bottom_gr
#                                         + df.iloc[k - 1, i] / 2
#                                         + df.iloc[k, i] / 2
#                                     )
#                                     / 2,
#                                 ),
#                                 ha="center",
#                                 va="center",
#                                 color=color,
#                                 fontsize=self.fontsize,
#                                 bbox=bbox_props,
#                                 zorder=5,
#                             )
#                             bottom_gr += df.iloc[k - 1, i] + df.iloc[k, i]

#                 # 在柱状图顶端添加total值
#                 if show_total_label:
#                     total = df.sum(axis=1)
#                     for p, v in enumerate(total.values):
#                         ax.text(
#                             x=p,
#                             y=v,
#                             s=self.fmt.format(float(v)),
#                             fontsize=self.fontsize,
#                             ha="center",
#                             va="bottom",
#                             zorder=5,
#                         )

#                 # box = ax.get_position()
#                 # ax.set_position([box.x0, box.y0, box.width, box.height * 1.1])

#             # 如果是非堆叠图要手动指定x轴ticks
#             # 解析日期字符串并将其转换为 Matplotlib 内部日期格式
#             if stacked is False:
#                 ax.set_xticks(
#                     np.arange(df.shape[0]) + bar_width / df.shape[1], df.index
#                 )
#             else:
#                 ax.set_xticks(np.arange(df.shape[0]), df.index)

#             # x轴标签
#             ax.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

#             # y轴标签格式
#             ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: self.fmt.format(y)))

#             ax.axhline(0, color="black", linewidth=0.5)  # y轴为0的横线

#             if self.data_line is not None:
#                 # 增加次坐标轴
#                 ax2 = ax.twinx()

#                 if isinstance(df_line, pd.DataFrame):
#                     label = df_line.columns[0]
#                 else:
#                     label = df_line.name

#                 color_line = "darkorange"
#                 line = ax2.plot(
#                     df_line.index,
#                     df_line.values,
#                     label=label,
#                     color=color_line,
#                     linewidth=1,
#                     linestyle="dashed",
#                     marker="o",
#                     markersize=3,
#                     markerfacecolor="white",
#                 )
#                 if "y2lim" in kwargs:
#                     ax2.set_ylim(kwargs["y2lim"][0], kwargs["y2lim"][1])

#                 for i in range(len(df_line)):
#                     if float(df_line.values[i]) <= ax2.get_ylim()[1]:
#                         t = ax2.text(
#                             x=df_line.index[i],
#                             y=df_line.values[i],
#                             s=self.fmt_line[j].format(float(df_line.values[i])),
#                             ha="center",
#                             va="bottom",
#                             fontsize=self.fontsize,
#                             color="white",
#                         )
#                         t.set_bbox(
#                             dict(facecolor=color_line, alpha=0.7, edgecolor=color_line)
#                         )

#                 # 次坐标轴标签格式
#                 ax2.yaxis.set_major_formatter(
#                     FuncFormatter(lambda y, _: self.fmt_line[j].format(y))
#                 )
#                 ax2.get_yaxis().set_ticks([])

#                 # # x轴标签
#                 # ax2.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

#             # 图例
#             if show_legend:
#                 box = ax.get_position()
#                 # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

#                 handles, labels = ax.get_legend_handles_labels()
#                 if self.data_line is not None:
#                     handles2, labels2 = ax2.get_legend_handles_labels()
#                     by_label = dict(
#                         zip(
#                             labels[::-1] + labels2[::-1],
#                             handles[::-1] + handles2[::-1],
#                         )
#                     )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
#                 else:
#                     by_label = dict(
#                         zip(
#                             labels[::-1],
#                             handles[::-1],
#                         )
#                     )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
#                 ax.legend(
#                     by_label.values(),
#                     by_label.keys(),
#                     loc="center left",
#                     ncol=1,
#                     bbox_to_anchor=(1, 0.5),
#                     labelspacing=1,
#                     frameon=False,
#                     prop={"family": "SimHei", "size": self.fontsize},
#                 )

#         return self.save()


# 继承基本类，堆积柱状对比图类
class PlotBar(Plot):
    def __init__(
        self,
        data,  # 原始数
        ax=None,
        width: int = 15,  # 宽
        height: int = 6,  # 高
        fontsize: int = 14,  # 字体大小
        fmt: str = "{:,.0f}",  # 基本数字格式
        # 以下为PlotStackedBar特有参数
        data_line=None,  # 折线图数据
        fmt_line="{:,.0%}",  # 折线图格式
        *args,
        **kwargs,
    ):
        self.data_line = data_line
        self.fmt_line = fmt_line
        super().__init__(
            data=data,
            ax=ax,
            width=width,
            height=height,
            fontsize=fontsize,
            fmt=fmt,
            *args,
            **kwargs,
        )

    def plot(
        self,
        stacked: bool = True,
        show_label: bool = True,
        label_formatter: str = "{abs}",
        show_total_bar: bool = False,
        show_total_label: bool = False,
        add_gr_text: bool = False,
        threshold: float = 0.02,
        *args,
        **kwargs,
    ) -> PlotBar:
        """继承基本Plot类，绘制柱状图

        Args:
            stacked (bool, optional): 是否堆积. Defaults to True.
            show_label (bool, optional): 是否显示数字标签. Defaults to True.
            label_formatter (str, optional): 主标签的格式，支持通配符{abs},{share},{gr},{index},{col}. Defaults to "{abs}".
            show_total_bar (bool, optional): 是否显示一个总体表现外框. Defaults to False.
            show_total_label (bool, optional): 是否在最上方显示堆积之和数字标签. Defaults to False.
            add_gr_text (bool, optional): 是否显示增长率数字. Defaults to False.
            threshold (float, optional): 显示数字标签的阈值，系列占堆积之和的比例大于此值才显示. Defaults to 0.02.

        Returns:
            self: 返回自身plot实例
        """
        df = self.data
        df_share = self.data.apply(lambda x: x / x.sum())
        df_gr = self.data.pct_change(axis=0)
        if self.data_line is not None:
            df_line = self.data_line

        # 绝对值bar图和增长率标注
        for k, index in enumerate(df.index):
            bottom_pos = 0
            bottom_neg = 0
            bottom_gr = 0

            max_v = df.values.max()
            min_v = df.values.min()

            iter_colors = cycle(cmap_qual(i) for i in range(cmap_qual.N))
            for i, col in enumerate(df):
                # 计算出的指标
                v = df.loc[index, col]
                share = df_share.loc[index, col]
                gr = df_gr.loc[index, col]
                total_gr = df.iloc[k, :].sum() / df.iloc[k - 1, :].sum() - 1
                d_label = {
                    "abs": kwargs.get("fmt_abs", self.fmt).format(v),
                    "share": kwargs.get("fmt_share", "{:.1%}").format(share),
                    "gr": kwargs.get("fmt_gr", "{:+.1%}").format(gr),
                    "total_gr": kwargs.get("fmt_gr", "{:+.1%}").format(total_gr),
                    "index": index,
                    "col": col,
                }

                # 如果有指定颜色就颜色，否则按预设列表选取
                if stacked:
                    if col in COLOR_DICT.keys():
                        color = COLOR_DICT[col]
                    elif index in COLOR_DICT.keys():
                        color = COLOR_DICT[index]
                    else:
                        color = next(iter_colors)
                else:
                    color = next(iter_colors)

                if stacked:
                    if v >= 0:
                        bottom = bottom_pos
                    else:
                        bottom = bottom_neg
                else:
                    bottom = 0

                # bar宽度
                bar_width = 0
                if stacked:
                    bar_width = 0.5
                    # if isinstance(
                    #     df.index, pd.DatetimeIndex
                    # ):  # 如果x轴是日期，宽度是以“天”为单位的
                    #     bar_width = 20
                    # else:
                    #     bar_width = 0.5
                else:
                    bar_width = 0.8 / df.shape[1]

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
                    self._style._hide_top_right_spines = True

                    # for index in df.index:
                    #     ax.text(
                    #         index,
                    #         df.loc[index, :].sum() * (H_INDEX + 0.02),
                    #         "{:,.0f}".format(df.loc[index, :].sum()),
                    #         ha="center",
                    #         fontsize=self.fontsize,
                    #     )

                if show_label is True:
                    if stacked is False or df.shape[1] == 1:  # 非堆叠图或只有一列数的情况（非堆叠）
                        # 根据数据判断标签是否需要微调
                        if 0 <= v < max_v * 0.05:
                            pos_y = v * 1.1
                            va = "bottom"
                            fontcolor = color
                        elif min_v * 0.05 < v < 0:
                            pos_y = v * 0.9
                            va = "top"
                            fontcolor = color
                        else:
                            pos_y = v / 2
                            va = "center"
                            fontcolor = "white"

                    else:  # 堆叠的情况
                        pos_y = bottom + v / 2
                        va = "center"
                        fontcolor = "white"

                    if abs(v / self.ax.get_ylim()[1]) >= threshold:
                        self.ax.text(
                            x=pos_x,
                            y=pos_y,
                            s=label_formatter.format(**d_label),
                            color=fontcolor,
                            va=va,
                            ha="center",
                            fontsize=self.fontsize,
                            zorder=5,
                        )
                if v >= 0:
                    bottom_pos += v
                else:
                    bottom_neg += v

                patches = self.ax.patches
                for rect in patches:
                    height = rect.get_height()
                    # 负数则添加纹理
                    if height < 0:
                        rect.set_hatch("//")

                if add_gr_text:
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
                            fontsize=self.fontsize,
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
                                fontsize=self.fontsize,
                            )

            # 在柱状图顶端添加total值
            if show_total_label:
                total = df.sum(axis=1)
                for p, v in enumerate(total.values):
                    self.ax.text(
                        x=p,
                        y=v * 1.05 if show_total_bar else v,  # 如果绘制整体外框则优化total值文本的位置
                        s=self.fmt.format(float(v)),
                        fontsize=self.fontsize,
                        ha="center",
                        va="bottom",
                        zorder=5,
                    )

            # box = ax.get_position()
            # ax.set_position([box.x0, box.y0, box.width, box.height * 1.1])

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

        if self.data_line is not None:
            # 增加次坐标轴
            ax2 = self.ax.twinx()

            if isinstance(df_line, pd.DataFrame):
                label = df_line.columns[0]
            else:
                label = df_line.name

            color_line = "darkorange"
            line = ax2.plot(
                df_line.index,
                df_line.values,
                label=label,
                color=color_line,
                linewidth=1,
                linestyle="dashed",
                marker="o",
                markersize=3,
                markerfacecolor="white",
            )
            if "y2lim" in kwargs:
                ax2.set_ylim(kwargs["y2lim"][0], kwargs["y2lim"][1])

            for i in range(len(df_line)):
                if float(df_line.values[i]) <= ax2.get_ylim()[1]:
                    t = ax2.text(
                        x=df_line.index[i],
                        y=df_line.values[i],
                        s=self.fmt_line.format(float(df_line.values[i])),
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

        return self


# # 继承基本类，Histgram分布图类
# class PlotHist(GridFigure):
#     def plot(
#         self,
#         bins: int = 100,
#         tiles: int = 10,
#         show_kde: bool = True,
#         show_metrics: bool = True,
#         show_tiles: bool = False,
#         ind: list = None,
#     ):
#         for j, ax in enumerate(self.axes):
#             df = self.data[j]
#             df.plot(
#                 kind="hist",
#                 density=True,
#                 bins=bins,
#                 ax=ax,
#                 color="grey",
#                 legend=None,
#                 alpha=0.5,
#             )
#             if show_kde:
#                 ax_new = ax.twinx()
#                 df.plot(kind="kde", ax=ax_new, color="darkorange", legend=None, ind=ind)
#                 # ax_new.get_legend().remove()
#                 ax_new.set_yticks([])  # 删除y轴刻度
#                 ax_new.set_ylabel(None)

#             # ax.set_title(title)
#             # ax.set_xlabel(xlabel)
#             # ax.set_yticks([])  # 删除y轴刻度
#             # ax.set_ylabel(ylabel)

#             # 添加百分位信息
#             if show_tiles:
#                 # 计算百分位数据
#                 percentiles = []
#                 for i in range(tiles):
#                     percentiles.append(
#                         [df.quantile((i) / tiles), "D" + str(i + 1)]
#                     )  # 十分位Decile

#                 # 在hist图基础上绘制百分位
#                 for i, percentile in enumerate(percentiles):
#                     ax.axvline(percentile[0], color="crimson", linestyle=":")  # 竖分隔线
#                     ax.text(
#                         percentile[0],
#                         ax.get_ylim()[1] * 0.97,
#                         int(percentile[0]),
#                         ha="center",
#                         color="crimson",
#                         fontsize=self.fontsize,
#                     )
#                     if i < tiles - 1:
#                         ax.text(
#                             percentiles[i][0]
#                             + (percentiles[i + 1][0] - percentiles[i][0]) / 2,
#                             ax.get_ylim()[1],
#                             percentile[1],
#                             ha="center",
#                         )
#                     else:
#                         ax.text(
#                             percentiles[tiles - 1][0]
#                             + (ax.get_xlim()[1] - percentiles[tiles - 1][0]) / 2,
#                             ax.get_ylim()[1],
#                             percentile[1],
#                             ha="center",
#                         )

#             # 添加均值、中位数等信息
#             if show_metrics:
#                 median = np.median(df.values)  # 计算中位数
#                 mean = np.mean(df.values)  # 计算平均数
#                 # if self.text_diff is not None:
#                 #     median_diff = self.text_diff[j]["中位数"]  # 计算对比中位数
#                 #     mean_diff = self.text_diff[j]["平均数"]  # 计算对比平均数

#                 if median > mean:
#                     yindex_median = 0.95
#                     yindex_mean = 0.9
#                     pos_median = "left"
#                     pos_mean = "right"
#                 else:
#                     yindex_mean = 0.95
#                     yindex_median = 0.9
#                     pos_median = "right"
#                     pos_mean = "left"

#                 ax.axvline(median, color="crimson", linestyle=":")
#                 ax.text(
#                     median,
#                     ax.get_ylim()[1] * yindex_median,
#                     f"中位数：{self.fmt.format(median)}",
#                     ha=pos_median,
#                     color="crimson",
#                     fontsize=self.fontsize,
#                 )

#                 ax.axvline(mean, color="purple", linestyle=":")
#                 ax.text(
#                     mean,
#                     ax.get_ylim()[1] * yindex_mean,
#                     f"平均数：{self.fmt.format(mean)}",
#                     ha=pos_mean,
#                     color="purple",
#                     fontsize=self.fontsize,
#                 )

#             # 去除ticks
#             ax.get_yaxis().set_ticks([])

#             # 轴标题
#             ax.set_ylabel("频次", fontsize=self.fontsize)

#         return self.save()


# # 继承基本类，算珠图类
# class PlotStripDot(GridFigure):
#     def __init__(
#         self,
#         data,  # 原始数
#         savepath: str = "./plots/",  # 保存位置
#         width: int = 15,  # 宽
#         height: int = 6,  # 高
#         fontsize: int = 14,  # 字体大小
#         title: str = None,  # 图表标题
#         ytitle: str = None,  # y轴标题
#         gs: GridSpec = None,  # GridSpec
#         gs_title: list = None,  # 每个Grid的标题
#         fmt: list = [",.0f"],  # 每个grid的数字格式
#         text_diff=None,  # 差异数据
#         *args,
#         **kwargs,
#     ):
#         super().__init__(
#             data,
#             savepath,
#             width,
#             height,
#             fontsize,
#             title,
#             ytitle,
#             gs,
#             gs_title,
#             fmt,
#             *args,
#             **kwargs,
#         )
#         self.text_diff = data_to_list(text_diff)
#         check_data_with_axes(self.text_diff, self.axes)

#     def plot(
#         self,
#         color: list = ["crimson"],
#     ):
#         check_data_with_axes(color, self.axes)

#         fmt_diff = [fmt[:2] + "+" + fmt[2:] for fmt in self.fmt]

#         for j, ax in enumerate(self.axes):
#             df = self.data[j]
#             index_range = range(1, len(df.index) + 1)
#             ax.hlines(
#                 y=index_range,
#                 xmin=df.iloc[:, 0],
#                 xmax=df.iloc[:, 1],
#                 color="grey",
#                 alpha=0.3,
#             )  # 连接线
#             ax.scatter(
#                 df.iloc[:, 0],
#                 index_range,
#                 color="grey",
#                 alpha=0.3,
#                 label=df.columns[0],
#             )  # 起始端点
#             ax.scatter(
#                 df.iloc[:, 1],
#                 index_range,
#                 color=color[j],
#                 alpha=0.4,
#                 label=df.columns[1],
#             )  # 结束端点

#             # 添加最新时点的数据标签
#             text_gap = (ax.get_xlim()[1] - ax.get_xlim()[0]) / 50
#             for i in index_range:
#                 ax.text(
#                     df.iloc[i - 1, 1] + text_gap,
#                     i,
#                     self.fmt.format(df.iloc[i - 1, 1]),
#                     ha="left",
#                     va="center",
#                     color=color[j],
#                     fontsize=self.fontsize,
#                     zorder=20,
#                     **NUM_FONT,
#                 )
#             # 添加间隔线
#             list_range = list(index_range)
#             list_range.append(max(list_range) + 1)
#             ax.hlines(
#                 y=[i - 0.5 for i in list_range],
#                 xmin=ax.get_xlim()[0],
#                 xmax=ax.get_xlim()[1],
#                 color="grey",
#                 linestyle="--",
#                 linewidth=0.5,
#                 alpha=0.2,
#             )
#             ax.set_yticks(index_range, labels=df.index)  # 添加y轴标签
#             ax.tick_params(
#                 axis="y", which="major", labelsize=self.fontsize
#             )  # 调整y轴标签字体大小
#             # if j != 0 and j != 2:  # 多图的情况，除第一张图以外删除y轴信息
#             #     ax.get_yaxis().set_ticks([])

#             if self.text_diff is not None:
#                 if self.text_diff[j] is not None and self.text_diff[j].empty is False:
#                     for i in index_range:
#                         idx = df.index[i - 1]
#                         try:
#                             v_diff = self.text_diff[j].loc[idx].values[0]
#                         except:
#                             v_diff = 0

#                         # 正负色
#                         if v_diff < 0:
#                             fontcolor = "crimson"
#                         else:
#                             fontcolor = "black"

#                         if v_diff > 0:
#                             edgecolor_diff = "green"
#                         elif v_diff < 0:
#                             edgecolor_diff = "red"
#                         else:
#                             edgecolor_diff = "darkorange"

#                         if v_diff != 0 and math.isnan(v_diff) is False:
#                             t = ax.text(
#                                 ax.get_xlim()[1] * 1.1,
#                                 i,
#                                 fmt_diff[j].format(v_diff),
#                                 ha="center",
#                                 va="center",
#                                 color=fontcolor,
#                                 fontsize=self.fontsize,
#                                 zorder=20,
#                                 **NUM_FONT,
#                             )
#                             # t.set_bbox(
#                             #     dict(
#                             #         facecolor=edgecolor_diff,
#                             #         alpha=0.25,
#                             #         edgecolor=edgecolor_diff,
#                             #         zorder=20,
#                             #     )
#                             # )

#             ax.invert_yaxis()  # 翻转y轴，最上方显示排名靠前的序列

#             # 图例
#             ax.legend(
#                 # df.columns,
#                 loc="lower right",
#                 # ncol=4,
#                 # bbox_to_anchor=(0.5, -0.1),
#                 # labelspacing=1,
#                 # frameon=False,
#                 prop={"family": "SimHei", "size": self.fontsize},
#             )

#         return self.save()


# # 继承基本类，网格热力图类
# class PlotHeatGrid(GridFigure):
#     def __init__(
#         self,
#         *args,
#         **kwargs,
#     ):
#         super().__init__(*args, **kwargs)

#     def plot(self, cbar: bool = True, cmap: list = ["bwr"], fmt: list = [",.0f"]):
#         check_data_with_axes(cmap, self.axes)
#         check_data_with_axes(fmt, self.axes)

#         for j, ax in enumerate(self.axes):
#             df = self.data[j]
#             sns.heatmap(
#                 df,
#                 ax=ax,
#                 annot=True,
#                 cbar=cbar,
#                 cmap=cmap[j],
#                 fmt=fmt[j],
#                 annot_kws={"fontsize": self.fontsize},
#             )

#             ax.set(ylabel=None)  # 去除y轴标题

#         return self.save()


# # 继承基本类，堆积柱状对比图类
# class PlotBarLine(GridFigure):
#     def plot(self, add_gr_text: bool = False, threshold: float = 0):
#         for j, ax in enumerate(self.axes):
#             # 处理绘图数据
#             df = self.data[j].transpose()
#             df_gr = self.data[j].pct_change(axis=1).transpose()

#             # 绝对值bar图和增长率标注
#             for k, index in enumerate(df.index):
#                 bottom_pos = 0
#                 bottom_neg = 0
#                 bottom_gr = 0
#                 bbox_props = None
#                 for i, col in enumerate(df):
#                     if df.loc[index, col] >= 0:
#                         bottom = bottom_pos
#                     else:
#                         bottom = bottom_neg
#                     # 如果有指定颜色就颜色，否则按预设列表选取
#                     if col in COLOR_DICT.keys():
#                         color = COLOR_DICT[col]
#                     else:
#                         color = COLOR_LIST[i]

#                     # 绝对值bar图
#                     ax.bar(
#                         index,
#                         df.loc[index, col],
#                         width=0.5,
#                         color=color,
#                         bottom=bottom,
#                         label=col,
#                     )
#                     if abs(df.loc[index, col]) >= threshold:
#                         ax.text(
#                             index,
#                             bottom + df.loc[index, col] / 2,
#                             self.fmt.format(df.loc[index, col]),
#                             color="white",
#                             va="center",
#                             ha="center",
#                             fontsize=self.fontsize,
#                         )
#                     if df.loc[index, col] >= 0:
#                         bottom_pos += df.loc[index, col]
#                     else:
#                         bottom_neg += df.loc[index, col]

#                     patches = ax.patches
#                     for rect in patches:
#                         height = rect.get_height()
#                         # 负数则添加纹理
#                         if height < 0:
#                             rect.set_hatch("//")

#                     if add_gr_text:
#                         if k > 0:
#                             # 各系列增长率标注
#                             ax.annotate(
#                                 "{:+.1%}".format(df_gr.iloc[k, i]),
#                                 xy=(
#                                     0.5,
#                                     (
#                                         bottom_gr
#                                         + df.iloc[k - 1, i] / 2
#                                         + df.iloc[k, i] / 2
#                                     )
#                                     / 2,
#                                 ),
#                                 ha="center",
#                                 va="center",
#                                 color=color,
#                                 fontsize=self.fontsize,
#                                 bbox=bbox_props,
#                             )
#                             bottom_gr += df.iloc[k - 1, i] + df.iloc[k, i]
#             # 图例
#             box = ax.get_position()
#             ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#             handles, labels = ax.get_legend_handles_labels()
#             by_label = dict(
#                 zip(
#                     labels[::-1],
#                     handles[::-1],
#                 )
#             )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
#             ax.legend(
#                 by_label.values(),
#                 by_label.keys(),
#                 loc="center left",
#                 ncol=1,
#                 bbox_to_anchor=(1, 0.5),
#                 labelspacing=1,
#                 frameon=False,
#                 prop={"family": "SimHei", "size": self.fontsize},
#             )

#             ax.axhline(0, color="black", linewidth=0.5)  # y轴为0的横线
#             ax.get_yaxis().set_ticks([])  # 去除y ticks

#             ax.tick_params(axis="x", labelrotation=0)  # x轴标签旋转

#         return self.save()


# # 继承基本类，堆积柱状对比图（增强型）类
# class PlotStackedBarPlus(GridFigure):
#     def plot(self):
#         H_INDEX = 1.03  # 外框对比bar的高度系数
#         for j, ax in enumerate(self.axes):
#             # 处理绘图数据
#             df = self.data[j].transpose()
#             df_share = self.data[j].apply(lambda x: x / x.sum()).transpose()
#             df_gr = self.data[j].pct_change(axis=1).transpose()

#             # 绝对值bar图和增长率标注
#             for k, index in enumerate(df.index):
#                 bottom = 0
#                 bottom_gr = 0
#                 bbox_props = None
#                 for i, col in enumerate(df):
#                     # 如果有指定颜色就颜色，否则按预设列表选取
#                     if col in COLOR_DICT.keys():
#                         color = COLOR_DICT[col]
#                     else:
#                         color = COLOR_LIST[i]

#                     # 绝对值bar图
#                     ax.bar(
#                         index,
#                         df.loc[index, col],
#                         width=0.5,
#                         color=color,
#                         bottom=bottom,
#                         label=col,
#                     )
#                     ax.text(
#                         index,
#                         bottom + df.loc[index, col] / 2,
#                         "{:,.0f}".format(df.loc[index, col])
#                         + "("
#                         + "{:.1%}".format(df_share.loc[index, col])
#                         + ")",
#                         color="white",
#                         va="center",
#                         ha="center",
#                         fontsize=self.fontsize,
#                     )
#                     bottom += df.loc[index, col]

#                     if k > 0:
#                         # 各系列增长率标注
#                         ax.annotate(
#                             "{:+.1%}".format(df_gr.iloc[k, i]),
#                             xy=(
#                                 0.5,
#                                 (bottom_gr + df.iloc[k - 1, i] / 2 + df.iloc[k, i] / 2)
#                                 / 2,
#                             ),
#                             ha="center",
#                             va="center",
#                             color=color,
#                             fontsize=self.fontsize,
#                             bbox=bbox_props,
#                         )
#                         bottom_gr += df.iloc[k - 1, i] + df.iloc[k, i]

#                 # 绘制总体增长率
#                 if k > 0:
#                     gr = df.iloc[k, :].sum() / df.iloc[k - 1, :].sum() - 1

#                     ax.annotate(
#                         "{:+.1%}".format(gr),
#                         xy=(
#                             0.5,
#                             (df.iloc[k, :].sum() + df.iloc[k - 1, :].sum())
#                             / 2
#                             * (H_INDEX + 0.02),
#                         ),
#                         ha="center",
#                         va="center",
#                         color="black",
#                         fontsize=self.fontsize,
#                         bbox=bbox_props,
#                     )
#             # 绘制总体表现外框
#             ax.bar(
#                 df.index,
#                 df.sum(axis=1) * H_INDEX,
#                 width=0.6,
#                 linewidth=1,
#                 linestyle="--",
#                 facecolor=(1, 0, 0, 0.0),
#                 edgecolor=(0, 0, 0, 1),
#             )
#             for index in df.index:
#                 ax.text(
#                     index,
#                     df.loc[index, :].sum() * (H_INDEX + 0.02),
#                     "{:,.0f}".format(df.loc[index, :].sum()),
#                     ha="center",
#                     fontsize=self.fontsize,
#                 )

#             # 因为有总体数量标签，增加一些图表高度
#             box = ax.get_position()
#             ax.set_position(
#                 [box.x0, box.y0 - box.height * 0.1, box.width, box.height * 1.1]
#             )

#             # 图例
#             if len(self.axes) > 1:  # 平行多图时的情况
#                 ax.legend(
#                     df.columns,
#                     loc="upper center",
#                     ncol=4,
#                     bbox_to_anchor=(0.5, -0.1),
#                     labelspacing=1,
#                     frameon=False,
#                     prop={"family": "SimHei", "size": self.fontsize},
#                 )
#             else:  # 单图时的情况
#                 box = ax.get_position()
#                 ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#                 handles, labels = ax.get_legend_handles_labels()
#                 by_label = dict(
#                     zip(
#                         labels[::-1],
#                         handles[::-1],
#                     )
#                 )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
#                 ax.legend(
#                     by_label.values(),
#                     by_label.keys(),
#                     loc="center left",
#                     ncol=1,
#                     bbox_to_anchor=(1, 0.5),
#                     labelspacing=1,
#                     frameon=False,
#                     prop={"family": "SimHei", "size": self.fontsize},
#                 )
#             # 去除ticks
#             # ax.get_xaxis().set_ticks([])
#             ax.get_yaxis().set_ticks([])

#         return self.save()


if __name__ == "__main__":
    # df = pd.DataFrame(
    #     {"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]}, index=["a", "b", "c"]
    # )
    # print(df)
    fig, axes = plt.subplots(1, 2, figsize=(8, 3))
    # axes = axes.ravel()

    for k, ax in enumerate(axes):
        np.random.seed(0)
        x, y = np.random.random((2, 30))
        ax.plot(x, y, "bo")

        texts = []
        for i in range(len(x)):
            t = ax.text(x[i], y[i], "Text%s" % i, ha="center", va="center")
            texts.append(t)
        adjust_text(texts, ax=ax)

    fig.savefig("test.png")
