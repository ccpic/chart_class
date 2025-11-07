"""
Base Plot class for all chart types.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union, Optional, Literal
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator
from chart.color import Colors


class Plot:
    """所有绘图类的基类，提供通用的绘图工具方法和样式管理。

    Attributes:
        data (pd.DataFrame): 绘图数据
        ax (mpl.axes.Axes): matplotlib axes对象
        fontsize (int): 字体大小
        figure (mpl.figure.Figure): matplotlib figure对象
        fmt (str): 数字格式化字符串
        style (Plot.Style): 样式管理对象
        hue (Optional[pd.Series]): 颜色映射列
        focus (Optional[List[str]]): 重点关注的索引列表
    """

    def __init__(
        self,
        data: Union[pd.DataFrame, pd.Series],
        ax: Optional[mpl.axes.Axes] = None,
        fontsize: int = 14,
        fmt: str = "{:,.0f}",
        style: Dict[str, Any] = {},
        color_dict: Optional[Dict[str, str]] = None,
        cmap_qual: Optional[mpl.colors.Colormap] = None,
        cmap_norm: Optional[mpl.colors.Colormap] = None,
        hue: Optional[str] = None,
        focus: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """初始化Plot基类。

        Args:
            data: 原始数据，支持DataFrame或Series
            ax: matplotlib axes对象，如不提供则使用当前axes
            fontsize: 字体大小，默认14
            fmt: 数字格式化字符串，默认"{:,.0f}"
            style: 风格字典，用于自定义图表样式
            color_dict: 颜色字典，映射名称到颜色
            cmap_qual: 分类变量的colormap
            cmap_norm: 连续变量的colormap
            hue: 颜色映射列名
            focus: 重点关注的index列表
        """
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
                "legend_bbox_to_anchor": (1, 0.5),  # 图例位置
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
                self.legend(
                    self._legend_loc, self._legend_ncol, self._legend_bbox_to_anchor
                )

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
            bbox_to_anchor: Tuple[float, float] = (1, 0.5),
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
                bbox_to_anchor=bbox_to_anchor,
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

    # ==================== Phase 2: 公共工具方法 ====================

    def _merge_style_kwargs(
        self, default_style: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """合并默认样式和用户提供的kwargs

        这个方法消除了所有子类中重复的样式合并逻辑:
        d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}

        Args:
            default_style: 默认样式字典
            **kwargs: 用户提供的参数

        Returns:
            合并后的样式字典

        Example:
            >>> d_style = self._merge_style_kwargs({
            ...     "color": "blue",
            ...     "alpha": 0.5
            ... }, **kwargs)
        """
        return {k: kwargs.get(k, v) for k, v in default_style.items()}

    def _get_color_for_item(
        self,
        item: str,
        stacked: bool = True,
        use_dict: bool = True,
        use_iter: bool = True,
    ) -> str:
        """智能获取单个item的颜色

        统一的颜色获取逻辑，优先级：
        1. color_dict中的自定义颜色
        2. 颜色迭代器中的下一个颜色

        Args:
            item: 数据项名称（通常是列名或index）
            stacked: 是否为堆叠图（影响是否使用color_dict）
            use_dict: 是否使用color_dict
            use_iter: 是否使用颜色迭代器

        Returns:
            颜色值（hex或rgba）

        Example:
            >>> color = self._get_color_for_item("销售额", stacked=True)
        """
        if use_dict and stacked and item in self._color_dict.keys():
            return self._colors.get_color(item)
        elif use_iter:
            return next(self._colors.iter_colors)
        else:
            return self._colors.get_color(item)

    def _reset_color_cycle(self) -> None:
        """重置颜色迭代器到初始状态

        在绘制多个bar或循环绘制时，确保颜色从头开始

        Example:
            >>> for bar in bars:
            ...     self._reset_color_cycle()
            ...     # 绘制bar的各个系列
        """
        from itertools import cycle

        self._colors.iter_colors = cycle(
            self._colors.cmap_qual(i) for i in range(self._colors.cmap_qual.N)
        )

    def _format_axis(
        self, axis: Literal["x", "y", "both"] = "both", formatter: Optional[str] = None
    ) -> None:
        """格式化坐标轴刻度标签

        使用指定的格式化字符串格式化x轴、y轴或两者的刻度标签

        Args:
            axis: 要格式化的轴 ('x', 'y', 或 'both')
            formatter: 格式化字符串，如不指定则使用self.fmt

        Example:
            >>> self._format_axis('y')  # 格式化y轴
            >>> self._format_axis('both', '{:.2f}')  # 自定义格式
        """
        from matplotlib.ticker import FuncFormatter

        fmt = formatter if formatter is not None else self.fmt

        if axis in ("x", "both"):
            self.ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt.format(x)))
        if axis in ("y", "both"):
            self.ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: fmt.format(y)))

    def _get_column(self, col: Optional[str], default_index: int = 0):
        """获取列数据，支持列名或默认索引

        统一的列选择逻辑，如果col为None则使用默认索引

        Args:
            col: 列名，如果为None则使用default_index
            default_index: 默认列索引

        Returns:
            Series: 列数据

        Example:
            >>> x = self._get_column(x, 0)  # x列或第1列
            >>> y = self._get_column(y, 1)  # y列或第2列
        """
        if col is None:
            return self.data.iloc[:, default_index]
        else:
            return self.data.loc[:, col]

    def _calculate_share(self, data, axis: int = 1):
        """计算占比

        Args:
            data: DataFrame或Series
            axis: 计算轴，1为按行，0为按列

        Returns:
            占比数据（0-1之间）

        Example:
            >>> df_share = self._calculate_share(df, axis=1)  # 行占比
            >>> share = self._calculate_share(size)  # Series总占比
        """
        if isinstance(data, pd.Series):
            return data.transform(lambda x: x / x.sum())
        else:
            return data.div(data.sum(axis=axis), axis=1 - axis)

    def _add_colorbar(
        self, scatter, hue_name: str, pad: float = 0.05, show_hist: bool = False
    ) -> None:
        """为scatter图添加colorbar（用于连续型hue变量）

        只在hue为数值型时添加colorbar，并处理相关的布局问题

        Args:
            scatter: scatter plot对象
            hue_name: hue变量的名称
            pad: colorbar与图表的间距
            show_hist: 是否显示了histogram（会影响pad值）

        Example:
            >>> scatter = self.ax.scatter(x, y, c=self.hue, ...)
            >>> self._add_colorbar(scatter, self.hue.name)
        """
        import warnings
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        if self.hue is not None and pd.api.types.is_numeric_dtype(self.hue.dtype):
            divider = make_axes_locatable(self.ax)
            actual_pad = 1.65 if show_hist else pad
            cax = divider.append_axes("right", size="5%", pad=actual_pad)
            cbar = self.figure.colorbar(scatter, cax=cax, orientation="vertical")
            cbar.set_label(hue_name)
            cbar.ax.set_zorder(0)
            self.figure.style._label_outer = False
            warnings.warn("画布存在colorbar，label_outer风格不生效", UserWarning)

    def _create_label_dict(
        self,
        value: Optional[float] = None,
        share: Optional[float] = None,
        gr: Optional[float] = None,
        index: Optional[str] = None,
        col: Optional[str] = None,
        **extra_fields,
    ) -> Dict[str, str]:
        """创建标签格式化字典

        为label_formatter提供格式化字段，支持常见字段和自定义字段

        Args:
            value: 绝对值
            share: 占比
            gr: 增长率
            index: 索引名
            col: 列名
            **extra_fields: 其他自定义字段

        Returns:
            格式化字典，所有值都已转为字符串

        Example:
            >>> d_label = self._create_label_dict(
            ...     value=1000, share=0.25, index="2023"
            ... )
            >>> label = "{abs} ({share})".format(**d_label)
        """
        d_label = {}

        if value is not None:
            d_label["abs"] = self.fmt.format(value)
        if share is not None:
            d_label["share"] = "{:.1%}".format(share)
        if gr is not None:
            d_label["gr"] = "{:+.1%}".format(gr)
        if index is not None:
            d_label["index"] = str(index)
        if col is not None:
            d_label["col"] = str(col)

        # 添加额外字段
        d_label.update(extra_fields)

        return d_label

    def _add_text_with_bbox(
        self,
        x: float,
        y: float,
        text: str,
        color: str = "white",
        bgcolor: Optional[str] = None,
        ha: str = "center",
        va: str = "center",
        fontsize: Optional[int] = None,
        bbox_style: Optional[Dict] = None,
        **kwargs,
    ):
        """添加带背景框的文本标签

        统一的文本标签创建方法，支持自动背景色

        Args:
            x, y: 文本位置
            text: 文本内容
            color: 文本颜色
            bgcolor: 背景颜色，如为None则不添加背景框
            ha, va: 对齐方式
            fontsize: 字体大小，默认使用self.fontsize
            bbox_style: 自定义bbox样式字典
            **kwargs: 传递给ax.text的其他参数

        Returns:
            Text对象

        Example:
            >>> self._add_text_with_bbox(
            ...     x=10, y=20, text="Label", bgcolor="blue"
            ... )
        """
        fontsize = fontsize if fontsize is not None else self.fontsize

        # 默认bbox样式
        if bbox_style is None and bgcolor is not None:
            bbox_style = dict(
                boxstyle="round,pad=0.5",
                facecolor=bgcolor,
                edgecolor=bgcolor,
                alpha=0.7,
            )

        text_obj = self.ax.text(
            x,
            y,
            text,
            color=color,
            ha=ha,
            va=va,
            fontsize=fontsize,
            bbox=bbox_style,
            **kwargs,
        )

        return text_obj
