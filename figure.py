from re import T
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import os
from typing import Any, Callable, Dict, List, Tuple, Union, Optional
import matplotlib as mpl
from plots import PlotBar
import pandas as pd

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
mpl.rcParams["font.serif"] = ["Microsoft YaHei"]
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams.update({"font.size": 16})
mpl.rcParams["hatch.linewidth"] = 0.5
mpl.rcParams["hatch.color"] = "grey"


class GridFigure(Figure):
    """
    一个matplotlib画布类，用以简化原始matplotlib及应用符合自己日常习惯的一些设置:
    grid,
    宽高设置，
    字体大小，
    总标题
    保存
    """

    def __init__(
        self,
        nrows: int = 1,
        ncols: int = 1,
        width_ratios: Optional[List[float]] = None,
        height_ratios: Optional[List[float]] = None,
        wspace: float = 0.1,
        hspace: float = 0.1,
        savepath: str = "/plots/",  # 保存位置
        width: int = 15,  # 宽
        height: int = 6,  # 高
        fontsize: int = 14,  # 字体大小
        fmt: str = "{:,.0f}",  # 基本数字格式
        style: Dict[str, Any] = {},  # 风格字典
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        # 根据nrows, ncols, width_ratios和height_ratios, wspace, hspace返回一个GridSpec
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
        self.fmt = fmt
        self._style = style

        # 宽高
        self.set_size_inches(self.width, self.height)

        # Grid
        if self.gridspec is not None:
            for axes in self.gridspec:
                self.add_subplot(axes)
        else:
            self.add_subplot(111)

    class Style:
        def __init__(self, figure, **kwargs) -> None:
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
                "same_xlim": False,  # 多个子图是否x轴边界一致
                "same_ylim": False,  # 多个子图是否y轴边界一致
                # 图例
                "show_legend": True,  # 是否展示画布图例
                "legend_loc": "center left",  # 图例位置
                "legend_ncol": 1,  # 图例列数
            }

            """根据初始化参数更新默认风格字典，并循环生成类属性"""
            d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}
            for key, value in d_style.items():
                self.__setattr__(f"_{key}", value)

            """初始化自动执行一遍风格设置"""
            self.title(self._title, self._title_fontsize)
            self.ytitle(self._ytitle, self._ytitle_fontsize)
            if self._same_xlim:
                self.same_xlim()
            if self._same_ylim:
                self.same_ylim()
            if self._show_legend:
                self.fig_legend(self._legend_loc, self._legend_ncol)
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
            self._figure.supylabel(title, fontsize=fontsize)

        def fig_legend(
            self,
            loc: Literal["center left", "lower center"] = "center left",
            ncol: int = 1,
        ) -> None:
            """汇总画布上所有ax的系列，生成一个总图例

            Args:
                loc (Literal["center left", "lower center"], optional): 图例位置. Defaults to "center left".
                ncol (int, optional): 图例列数. Defaults to 1.
            """
            # 删除已经存在的重复图例
            handles, labels = [], []
            for i, _ax in enumerate(self._figure.axes):
                h, l = _ax.get_legend_handles_labels()
                for hh, ll in zip(h[::-1], l[::-1]):
                    if ll not in labels:
                        handles.append(hh)
                        labels.append(ll)

            self._figure.legend(
                handles=handles,
                labels=labels,
                loc=loc,
                ncol=ncol,
                bbox_to_anchor=(0.9, 0.5) if loc == "center left" else (0.5, 1),
                labelspacing=1,
                frameon=False,
                prop={"family": "Microsoft YaHei", "size": self._figure.fontsize},
            )

        def same_xlim(self) -> None:
            """多个子图时保持x轴边界一致"""
            for i, _ax in enumerate(self._figure.axes):
                xlim_min, xlim_max = _ax.get_xlim()
                if i == 0:
                    xlim_range = [xlim_min, xlim_max]
                else:
                    if xlim_min < xlim_range[0]:
                        xlim_range = [xlim_min, xlim_range[1]]
                    if xlim_max > xlim_range[1]:
                        xlim_range = [xlim_range[0], xlim_max]
                _ax.set_xlim(xlim_range[0], xlim_range[1])

        def same_ylim(self) -> None:
            """多个子图时保持y轴边界一致"""
            for i, _ax in enumerate(self._figure.axes):
                ylim_min, ylim_max = _ax.get_ylim()
                if i == 0:
                    ylim_range = [ylim_min, ylim_max]
                else:
                    if ylim_min < ylim_range[0]:
                        ylim_range = [ylim_min, ylim_range[1]]
                    if ylim_max > ylim_range[1]:
                        ylim_range = [ylim_range[0], ylim_max]
                _ax.ylim(ylim_range[0], ylim_range[1])

        def label_outer(self) -> None:
            """多个子图时只显示最下方x轴和最左边y轴的刻度标签"""
            for i, _ax in enumerate(self._figure.axes):
                _ax.label_outer()

    def plot_bar(
        self,
        data: pd.DataFrame,
        fmt: str = "{:,.0f}",
        ax_index: int = 0,
        fontsize: Optional[float] = None,
        style: Dict[str, any] = {},
        data_line: Optional[pd.DataFrame] = None,
        fmt_line: Optional[str] = "{:+,.0%}",
        **kwargs,
    ) -> mpl.axes.Axes:
        """在当前画布的指定ax绘制柱状图

        Args:
            data (pd.DataFrame): 绘图主数据
            fmt (str): 主数据格式，用于显示标签等的默认格式. Defaults to "{:,.0f}"
            ax_index (int, optional): ax索引. Defaults to 0.
            fontsize (Optional[float], optional): 绘图字号. Defaults to None.
            style (Dict[str, any], optional): 风格字典. Defaults to {}.
            data_line (Optional[pd.DataFrame], optional): 次坐标轴折线图数据. Defaults to None.
            fmt_line (Optional[str], optional): 次坐标轴折线图数据格式. Defaults to "{:+,.0%}".

        **kwargs:
            stacked (bool, optional): 是否堆积. Defaults to True.
            show_label (bool, optional): 是否显示数字标签. Defaults to True.
            show_total_bar (bool, optional): 是否显示一个总体表现外框. Defaults to False.
            show_total_label (bool, optional): 是否在最上方显示堆积之和数字标签. Defaults to False.
            add_gr_text (bool, optional): 是否显示增长率数字. Defaults to False.
            threshold (float, optional): 显示数字标签的阈值，系列占堆积之和的比例大于此值才显示. Defaults to 0.02.

        Returns:
            mpl.axes.Axes: 返回ax
        """
        ax = self.axes[ax_index]

        PlotBar(
            data=data,
            fmt=fmt,
            ax=ax,
            fontsize=self.fontsize if fontsize is None else fontsize,
            style=style,
            data_line=data_line,
            fmt_line=fmt_line,
        ).plot(**kwargs).apply_style()

        return ax

    def save(self) -> None:
        self.style = self.Style(self, **self._style)  # 应用风格
        """保存图片"""
        script_dir = os.path.dirname(__file__)
        plot_dir = f"{script_dir}{self.savepath}"

        # 保存
        if os.path.exists(plot_dir) is False:
            os.makedirs(plot_dir)

        path = "%s%s.png" % (
            plot_dir,
            "test"
            if self.style._title is None
            else self.style._title.replace("/", "_"),
        )
        self.savefig(
            path,
            format="png",
            bbox_inches="tight",
            transparent=True,
            dpi=600,
        )
        print(path + " has been saved...")

        # Close
        plt.clf()
        plt.cla()
        plt.close()

        return path
