from __future__ import annotations
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import os
from typing import Any, Dict, List, Tuple, Optional, Literal
import matplotlib as mpl
from plots import (
    PlotBar,  # noqa: F401
    PlotBubble,  # noqa: F401
    PlotLine,  # noqa: F401
    PlotHeatmap,  # noqa: F401
    PlotWordcloud,  # noqa: F401
    PlotStripdot,  # noqa: F401
    PlotHist,  # noqa: F401
    PlotBoxdot,  # noqa: F401
    PlotTreemap,  # noqa: F401
    PlotPie,  # noqa: F401
    PlotArea,  # noqa: F401
    PlotBarh,  # noqa: F401
    PlotWaffle,  # noqa: F401
    PlotFunnel,  # noqa: F401
    PlotVenn2,  # noqa: F401
    PlotVenn3,  # noqa: F401
    PlotTable,  # noqa: F401
)
import pandas as pd
from color import CMAP_QUAL, CMAP_NORM, COLOR_DICT
from components.annotation import Connection
import inspect
import re

mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
mpl.rcParams["font.serif"] = ["Microsoft YaHei"]
mpl.rcParams["axes.unicode_minus"] = False


class GridFigure(Figure):
    def __init__(
        self,
        nrows: int = 1,
        ncols: int = 1,
        width_ratios: Optional[List[float]] = None,
        height_ratios: Optional[List[float]] = None,
        wspace: float = 0.1,
        hspace: float = 0.1,
        sharex: bool = False,
        sharey: bool = False,
        savepath: str = "/plots/",
        width: int = 15,
        height: int = 6,
        fontsize: int = 14,
        color_dict: Dict[str, str] = COLOR_DICT,
        cmap_qual: mpl.colors.Colormap = CMAP_QUAL,
        cmap_norm: mpl.colors.Colormap = CMAP_NORM,
        style: Dict[str, Any] = {},
        *args,
        **kwargs,
    ) -> None:
        """一个matplotlib画布类，用以简化原始matplotlib及应用符合自己日常习惯的一些设置

        Args:
            nrows (int, optional): 子图行数. Defaults to 1.
            ncols (int, optional): 子图列数. Defaults to 1.
            width_ratios (Optional[List[float]], optional): 子图宽度比. Defaults to None.
            height_ratios (Optional[List[float]], optional): 子图高度比. Defaults to None.
            wspace (float, optional): 子图水平间距. Defaults to 0.1.
            hspace (float, optional): 子图垂直间距. Defaults to 0.1.
            sharex (bool, optional): 子图是否共享x轴. Defaults to False.
            sharey (bool, optional): 子图是否共享y轴. Defaults to False.
            savepath (str, optional): 绘图文件保存路径. Defaults to "/plots/".
            width (int, optional): 总宽度. Defaults to 15.
            height (int, optional): 总高度. Defaults to 6.
            fontsize (int, optional): 全局字体大小. Defaults to 14.
            color_dict (Dict[str, str], optional): 颜色字典. Defaults to COLOR_DICT in color.py.
            cmap_qual (mpl.colors.Colormap, optional): 离散的colormap，用于分类变量着色. Defaults to cmap_qual.
            cmap_norm (mpl.colors.Colormap, optional): 连续的colormap，用于连续变量区分表现好坏. Defaults to plt.get_cmap("PiYG").
            style (Dict[str, Any], optional): 风格字典. Defaults to {}.
        """

        super().__init__(*args, **kwargs)

        # 根据nrows, ncols, width_ratios和height_ratios, wspace, hspace生成一个GridSpec
        self.nrows = nrows
        self.ncols = ncols
        width_ratios = [1] * ncols if width_ratios is None else width_ratios
        height_ratios = [1] * nrows if height_ratios is None else height_ratios

        self.gridspec = GridSpec(
            nrows=nrows,
            ncols=ncols,
            width_ratios=width_ratios,
            height_ratios=height_ratios,
            wspace=wspace,
            hspace=hspace,
        )

        self.savepath = savepath
        self.width = width
        self.height = height
        self.fontsize = fontsize
        self._color_dict = color_dict
        self._cmap_qual = cmap_qual
        self._cmap_norm = cmap_norm
        self._style = style
        self.style = self.Style(self, **self._style)  # 应用风格

        # 宽高
        self.set_size_inches(self.width, self.height)

        # Grid
        for i, axes in enumerate(self.gridspec):
            if i == 0:
                main_ax = self.add_subplot(axes)
            else:
                self.add_subplot(
                    axes,
                    sharex=main_ax if sharex else None,  # 多个子图共享x轴
                    sharey=main_ax if sharey else None,  # 多个子图共享y轴
                )

    class Style:
        def __init__(self, figure: mpl.figure.Figure, **kwargs) -> None:
            """初始化风格

            Args:
                figure (mpl.figure.Figure): 所属的画布
            """

            self._figure = figure

            """默认风格字典"""
            d_style = {
                # 整体画布的一些风格
                "title": None,  # 总标题
                "title_fontsize": figure.fontsize * 1.5,  # 总标题字体大小
                "ytitle": None,  # y轴总标题
                "ytitle_fontsize": figure.fontsize * 1.5,  # y轴总标题字体大小
                # GridSpec子图的一些风格
                "label_outer": False,
                # 图例
                "show_legend": False,  # 是否展示画布图例
                "legend_loc": "center left",  # 图例位置
                "legend_ncol": 1,  # 图例列数
                "bbox_to_anchor": (1, 0.5),  # 图例相对位置
            }

            """根据初始化参数更新默认风格字典，并循环生成类属性"""
            d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}
            for key, value in d_style.items():
                self.__setattr__(f"_{key}", value)

        def apply_style(self) -> None:
            """执行一遍风格设置，不能在初始化中进行，因为一些风格在画图后才生效"""

            self.title(self._title, self._title_fontsize)
            self.ytitle(self._ytitle, self._ytitle_fontsize)
            if self._show_legend:
                self.fig_legend(
                    self._bbox_to_anchor, self._legend_loc, self._legend_ncol
                )
            if self._label_outer:
                self.label_outer()

        def title(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            """添加整个画布的标题

            Parameters
            ----------
            title : Optional[str], optional
                标题文字内容, by default None
            fontsize : Optional[float], optional
                标题字体大小, by default None
            """

            self._figure.suptitle(title, fontsize=fontsize)

        def ytitle(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            """添加整个画布的y轴标题

            Parameters
            ----------
            title : Optional[str], optional
                标题文字内容, by default None
            fontsize : Optional[float], optional
                标题字体大小, by default None
            """
            try:
                self._figure.supylabel(title, fontsize=fontsize)
            except AttributeError:
                pass

        def fig_legend(
            self,
            bbox_to_anchor: Tuple[float, float] = (1, 0.5),
            loc: Literal["center left", "lower center"] = "center left",
            ncol: int = 1,
        ) -> None:
            """汇总画布上所有ax的系列，生成一个总图例

            Args:
                bbox_to_anchor (Tuple[float, float], optional): 图例相对位置. Defaults to (1, 0.5).
                loc (Literal["center left", "lower center"], optional): 图例位置. Defaults to "center left".
                ncol (int, optional): 图例列数. Defaults to 1.
            """

            # 删除已经存在的重复图例
            fig_handles, fig_labels = [], []
            for i, _ax in enumerate(self._figure.axes):
                handles, labels = _ax.get_legend_handles_labels()
                for handle, label in zip(handles[::-1], labels[::-1]):
                    if label not in fig_labels:
                        fig_handles.append(handle)
                        fig_labels.append(label)

            self._figure.legend(
                handles=fig_handles,
                labels=fig_labels,
                loc=loc,
                ncol=ncol,
                bbox_to_anchor=bbox_to_anchor,
                labelspacing=1,
                frameon=False,
                prop={"family": "Microsoft YaHei", "size": self._figure.fontsize},
            )

        def label_outer(self) -> None:
            """多个子图时只显示最下方x轴和最左边y轴的刻度标签"""
            for i, _ax in enumerate(self._figure.axes):
                _ax.label_outer()

    def plot(
        self,
        kind: Literal[
            "bar",
            "line",
            "bubble",
            "stripdot",
            "boxdot",
            "hist",
            "heatmap",
            "wordcloud",
            "pie",
            "area",
            "waffle",
            "funnel",
        ],
        data: pd.DataFrame,
        fmt: str = "{:,.0f}",
        ax_index: int = 0,
        fontsize: Optional[float] = None,
        style: Dict[str, any] = {},
        color_dict: Optional[Dict[str, str]] = None,
        cmap_qual: Optional[mpl.colors.Colormap] = None,
        cmap_norm: Optional[mpl.colors.Colormap] = None,
        hue: Optional[str] = None,
        focus: Optional[List[str]] = None,
        **kwargs,
    ) -> mpl.axes.Axes:
        """在当前画布的指定ax绘制网格热力图

        Args:
            kind (Literal["bar", "line", "bubble", "stripdot", "boxdot", "hist", "heatmap", "wordcloud"]): 绘图类型.
            data (pd.DataFrame): 绘图主数据，一个pandas df.
            fmt (str): 主数据格式，用于显示标签等的默认格式. Defaults to "{:,.0f}"
            ax_index (int, optional): ax索引. Defaults to 0.
            fontsize (Optional[float], optional): 绘图字号，如不提供则使用画布字号. Defaults to None.
            style (Optional[Dict[str, any]], optional): 风格字典. Defaults to {}.
            color_dict (Optional[Dict[str,str], optional): 颜色字典，如没有指定则使用默认. Defaults to None.
            hue (Optional[str], optional): 指定颜色映射字段. Defaults to None.

        **kwargs: 其他参数，具体见各绘图类型:
            bar:
                stacked (bool, optional): 是否堆积. Defaults to True.
                show_label (bool, optional): 是否显示数字标签. Defaults to True.
                label_formatter (str, optional): 主标签的格式，支持通配符{abs},{share},{gr},{index},{col}. Defaults to "{abs}".
                show_total_bar (bool, optional): 是否显示一个总体表现外框. Defaults to False.
                show_total_label (bool, optional): 是否在最上方显示堆积之和数字标签. Defaults to False.
                show_gr (bool, optional): 是否显示增长率数字. Defaults to False.
                label_threshold (float, optional): 显示数字标签的阈值，系列占堆积之和的比例大于此值才显示. Defaults to 0.02.
                bar_width (float, optional): 柱宽度，越宽间距越小. Defaults to 0.8.
            line:
                show_label (List[str], optional): 指定要显示标签的系列. Defaults to [].
                endpoint_label_only (bool, optional): 标签是全部显示还是只显示首尾节点. Defaults to False.
                linewidth (int, optional): 线宽. Defaults to 2.
                marker(str,optional): 标记形状. Defaults to "o".
                markersize(int, optional): 标记大小. Defaults to 5.
            bubble:
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
                corr (Optional[float], optional): 相关系数，如不为None，则显示在ax左上角. Defaults to None.
                x_fmt (str, optional): x轴显示数字格式，影响轴刻度标签及分隔线数据标签. Defaults to "{:,.0f}",
                y_fmt (str, optional): y轴显示数字格式，影响轴刻度标签及分隔线数据标签. Defaults to "{:,.0f}",
                alpha (float, optional): 气泡透明度. Defaults to 0.6,
                random_color (bool, optional): 气泡颜色是否随机. Defaults to True,
                edgecolor (str, optional): 气泡边框颜色. Defaults to "black",
                avg_linestyle (str, optional): 分隔线样式. Defaults to ":",
                avg_linewidth (float, optional): 分隔线宽度. Defaults to 1,
                avg_color (str, optional): 分隔线及数据标签颜色. Defaults to "black",
            heatmap:
                cmap (Optional[Union[str, list]], optional): 自定义颜色方案，可以是cmap名或颜色列表. Defaults to None.
                cbar (bool, optional): 是否添加colorbar. Defaults to True.
                show_label (bool, optional): 是否往每个网格添加标签文本. Defaults to True.
            wordcloud:
                col_freq (Optional[str]): 指定频次列，如不指定则默认为df的第一列.
                mask_shape (Literal["rectangle", "circle"], optional): 词云形状类别，默认为矩形. Defaults to "rectangle".
                mask_width (int, optional): 形状为矩形时的矩形宽度. Defaults to 800.
                mask_height (int, optional): 形状为矩形时的矩形高度. Defaults to 600.
            stripdot:
                start (Optional[str], optional): 起始点数据的列名，如不设置则在数据只有1列的情况下默认为None，数据多于1列的情况下默认为第1列. Defaults to None.
                end (Optional[str], optional): 结束点数据的列名，如不设置则在数据只有1列时默认为此列，数据多于1列的情况下默认为第2列. Defaults to None.
                hue (Optional[str], optional): 指定Dot颜色字段名. Defaults to None.
                text_diff (bool, optional): 是否显示差值标签. Defaults to True.
                color_line (str): 横线的颜色. Defaults to "grey".
                color_start (str): 起始点的颜色. Defaults to "grey".
                color_end (str): 结束点的颜色. Defaults to self.figure.cmap_qual.colors[0].
                alpha (float): 透明度. Defaults to 0.3.
            hist:
                bins (int, optional): 直方图柱的个数. Defaults to 100.
                tiles (int, optional): 等分线的个数. Defaults to 10.
                show_kde (bool, optional): 是否显示核密度估计曲线. Defaults to True.
                show_metrics (bool, optional): 是否显示均值和中位数. Defaults to True.
                show_tiles (bool, optional): 是否显示等分线_. Defaults to False.
                ind (Optional[list], optional): 评估点，如为None则为1000个等距点. Defaults to None.
            boxdot:
                x (Optional[str], optional): x轴类别数据的字段名，如不指定则为第1列. Defaults to None.
                y (Optional[str], optional): y轴数值数据的字段名，如不指定则为第2列. Defaults to None.
                label_limit (int, optional): 展示数据点标签的数量. Defaults to 0.
                label_threshold (float, optional): 对大于此值的数据点展示标签. Defaults to 0.
                show_stats (bool, optional): 是否显示统计值，包括最大值、最小值、中位数. Defaults to True.
                order (Optional[Union[None, list]], optional): 类别按什么排序，如果为None则按照数据自动排序. Defaults to None.
                dot_size (float): 散点大小. Defaults to 8.
                jitter (float): 随机散开的间距. Defaults to 0.2
            pie:
                size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
                donut (bool, optional): 甜甜圈图还是饼图. Defaults to False.
                donut_title (Optional[str], optional): 甜甜圈图中间的文字. Defaults to None.
                pct_distance (Optional[float]): 值标签和边界的距离. Defaults to 0.8,
                start_angle (Optional[int]): 饼图的第一片扇叶从哪个角度开始. Defaults to 90,
                counter_clock (Optional[bool]): 饼图扇叶顺序是顺时针还是逆时针. Defaults to False,
                line_width (Optional[float]): 扇叶边线的宽度. Defaults to 3,
                edgecolor (Optional[str]): 扇叶边线的颜色. Defaults to "white",
                label_fontsize (Optional[float]): 值标签的字体大小. Defaults to self.fontsize,
                circle_distance (Optional[float]): 如果生成甜甜圈图，指定宽度. Defaults to 0.7,
            waffle:
                rows (int, optional): 行数. Defaults to 10.
                columns (int, optional): 列数. Defaults to 10.
                size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
                colors (Optional[List[str]], optional): 指定颜色列表，如不指定将使用默认颜色方案. Defaults to None.
                vertical (bool, optional): 分类按垂直发展. Defaults to True.
                block_arranging_style (Literal["snake", "new"], optional): 每个分类如何起始，"snake"为紧接上类末尾，"new-line"为每类新起一行. Defaults to "snake".
                icons (Optional[Union[List[str], str]], optional): 指定矢量图形，为Font Awesome字符串. Defaults to None.
            venn2:
                set1 (Optional[set], optional): 第1组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
                set2 (Optional[set], optional): 第2组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
                set_labels (tuple, optional): 组别标签. Defaults to None.
            venn3:
                set1 (Optional[set], optional): 第1组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
                set2 (Optional[set], optional): 第2组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
                set3 (Optional[set], optional): 第3组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
                set_labels (tuple, optional): 组别标签. Defaults to None.
            table:
                col_defs (Optional[List[ColumnDefinition]]): 列样式定义, defaults to None.

        Returns:
        mpl.axes.Axes: mpl ax
        """
        # 根据kind确定绘图类
        cls = globals()[f"Plot{kind.capitalize()}"]
        # 根据ax_index确定ax
        ax = self.axes[ax_index]

        cls(
            data=data,
            fmt=fmt,
            ax=ax,
            fontsize=self.fontsize if fontsize is None else fontsize,
            style=style,
            color_dict=color_dict,
            cmap_qual=cmap_qual,
            cmap_norm=cmap_norm,
            hue=hue,
            focus=focus,
        ).plot(**kwargs).apply_style()

        return ax

    def annotate(
        self,
        x1: float,
        x2: float,
        text: str,
        offset: Optional[float] = None,
        ax_index: int = 0,
        **kwargs,
    ) -> mpl.axes.Axes:
        """在指定ax画注释文本和线条

        Args:
            ax_index (int, optional): ax索引. Defaults to 0.

        Returns:
            mpl.axes.Axes: mpl ax
        """
        # 根据ax_index确定ax
        ax = self.axes[ax_index]

        plot_data = []
        for artist in ax.containers:
            plot_data.append(artist[0].get_height())
        y1 = plot_data[x1]
        y2 = plot_data[x2]

        Connection(ax, x1, x2, y1, y2, text, offset).draw(**kwargs)

        return ax

    def save(
        self, tight_layout: bool = True, transparent: bool = True, dpi: int = 300
    ) -> str:
        """保存图片

        Args:
            tight_layout (bool, optional): 是否自动调整子图参数，使之填充整个图像区域. Defaults to True.
            transparent (bool, optional): 背景是否透明. Defaults to True.
            dpi (int, optional): _description_. Defaults to 600.

        Returns:
            str: 返回保存图片的路径
        """

        self.style.apply_style()  # 应用风格，一些风格只能在绘图后生效
        if tight_layout:
            self.gridspec.tight_layout(
                self
            )  # 自动调整子图参数，使之填充整个图像区域，但有时不生效

        # 该语句返回chart_class的文件夹而不是引用它的程序的文件夹
        # script_dir = os.path.dirname(__file__)

        # 获取调用当前脚本的脚本路径
        calling_script_dir = os.path.dirname(
            os.path.abspath(inspect.stack()[1].filename)
        )
        plot_dir = f"{calling_script_dir}{self.savepath}"

        # 保存
        if os.path.exists(plot_dir) is False:
            os.makedirs(plot_dir)

        # 根据图表标题设置保存文件名
        path = "%s%s.png" % (
            plot_dir,
            (
                "无标题"
                if self.style._title is None
                else re.sub(r"[\n/]", "_", self.style._title)
            ),
        )
        self.savefig(
            path,
            format="png",
            bbox_inches="tight",
            pad_inches=0.1,
            transparent=transparent,
            dpi=dpi,
        )
        print(path + " has been saved...")

        # Close
        plt.clf()
        plt.cla()
        plt.close()

        return path
