from re import T
from matplotlib import axes
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from matplotlib.gridspec import GridSpec
import os
from numpy.core.arrayprint import str_format
from numpy.lib.function_base import iterable
import pandas as pd
from typing import Any, Callable, Dict, List, Tuple, Union, Optional
import matplotlib.font_manager as fm
import matplotlib as mpl
import seaborn as sns
from matplotlib.ticker import FuncFormatter, StrMethodFormatter
import textwrap
import math
import matplotlib.dates as mdates
import scipy.stats as stats
from adjustText import adjust_text
from itertools import cycle

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

# sns.theme(style="whitegrid")
MYFONT = fm.FontProperties(fname="C:/Windows/Fonts/SimHei.ttf")
NUM_FONT = {"fontname": "Calibri"}


class UnequalDataGridError(Exception):
    def __init__(self, message):
        super().__init__(message)


def data_to_list(data):
    if isinstance(data, dict):
        return [v for k, v in data.items()]
    elif isinstance(data, pd.DataFrame):
        return [data]
    elif isinstance(data, pd.Series):
        return [data.to_frame()]
    elif isinstance(data, tuple):
        return list(data)
    elif isinstance(data, list):
        return data
    else:
        return data


def check_data_with_axes(data: list, axes: axes):
    if len(data) > len(axes):
        message = f"Got {len(data)} pieces of data, while {len(axes)} axes existed."
        raise UnequalDataGridError(message)


class GridFigure(Figure):
    """
    一个matplotlib图表类，用以简化原始matplotlib及应用符合自己日常习惯的一些设置:
    数据预处理，
    grid,
    宽高设置，
    字体大小，
    总标题
    保存
    """

    def __init__(
        self,
        data: Union[list, tuple, pd.DataFrame, pd.Series],  # 原始数
        savepath: str = "/plots/",  # 保存位置
        width: int = 15,  # 宽
        height: int = 6,  # 高
        fontsize: int = 14,  # 字体大小
        gs: GridSpec = None,  # GridSpec
        fmt: str = "{:,.0f}",  # 基本数字格式
        style: Dict[str, Any] = {},  # 风格字典
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.savepath = savepath
        self.width = width
        self.height = height
        self.fontsize = fontsize
        self.gs = gs
        self.fmt = fmt
        self._style = style

        # 所有数据处理成列表格式
        self.data = data_to_list(data)

        # 宽高
        self.set_size_inches(self.width, self.height)

        # Grid
        if gs is not None:
            for axes in gs:
                self.add_subplot(axes)
        else:
            self.add_subplot(111)

        # 检查grid大小和数据是否匹配
        check_data_with_axes(self.data, self.axes)

        self.style = self.Style(self, **style)

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
                "gs_titles": None,  # GridSpec标题
                "gs_titles_fontsize": figure.fontsize,  # GridSpec标题字体大小
                "major_grid": None,  # 主网格线
                "minor_grid": None,  # 次网格线
                "hide_top_right_spines": False,  # 是否隐藏上/右边框
                "last_xticks_only": False,  # 多个子图情况下只显示最下方图片的x轴ticks
                "first_yticks_only": False,  # 多个子图情况下只显示最左侧图片的y轴ticks
                "same_xlim": False,  # 多个子图是否x轴边界一致
                "same_ylim": False,  # 多个子图是否y轴边界一致
                # 坐标轴相关的风格
                "xlabel": None,  # x轴标题
                "xlabel_fontsize": figure.fontsize,  # x轴标题字体大小
                "ylabel": None,  # y轴标题
                "ylabel_fontsize": figure.fontsize,  # y轴标题字体大小
                "xlim": None,  # x轴边界(最小值, 最大值)
                "ylim": None,  # y轴边界(最小值, 最大值)
                "y2lim": None,  # y轴次坐标轴边界(最小值, 最大值)
                # 刻度相关的风格
                "xticklabel_fontsize": figure.fontsize,  # x轴刻度标签字体大小
                "yticklabel_fontsize": figure.fontsize,  # y轴刻度标签字体大小
                "xticklabel_rotation": None,  # x抽刻度标签旋转角度
                "yticklabel_rotation": None,  # y抽刻度标签旋转角度
                "remove_xticks": False,  # 是否移除x轴刻度
                "remove_yticks": False,  # 是否移除y轴刻度
            }

            """根据初始化参数更新默认风格字典，并循环生成类属性"""
            d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}
            for key, value in d_style.items():
                self.__setattr__(f"_{key}", value)

            """初始化自动执行一遍风格设置"""
            self.title(self._title, self._title_fontsize)
            self.ytitle(self._ytitle, self._ytitle_fontsize)
            self.gs_titles(self._gs_titles, self._gs_titles_fontsize)
            self.xlabel(self._xlabel, self._xlabel_fontsize)
            self.ylabel(self._ylabel, self._ylabel_fontsize)
            self.tick_params(
                self._xticklabel_fontsize,
                self._yticklabel_fontsize,
                self._xticklabel_rotation,
                self._yticklabel_rotation,
            )
            if self._remove_xticks:
                self.remove_xticks()
            if self._remove_yticks:
                self.remove_yticks()
            if self._hide_top_right_spines:
                self.hide_top_right_spines()
            if self._last_xticks_only:
                self.last_xticks_only()
            if self._first_yticks_only:
                self.first_yticks_only()
            if self._xlim is not None:
                self.xlim(self._xlim)
            if self._ylim is not None:
                self.ylim(self._ylim)
            if self._y2lim is not None:
                self.y2lim(self._y2lim)
            if self._same_xlim:
                self.same_xlim()
            if self._same_ylim:
                self.same_ylim()
            if self._major_grid is not None:
                self.major_grid(**self._major_grid)
            if self._minor_grid is not None:
                self.minor_grid(**self._minor_grid)

        def title(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            self._figure.suptitle(title, fontsize=fontsize)

        def ytitle(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            self._figure.supylabel(title, fontsize=fontsize)

        def gs_titles(
            self, titles: Optional[List[str]], fontsize: Optional[float] = None
        ) -> None:
            if titles is not None:
                for i, _ax in enumerate(self._figure.axes):
                    try:
                        _ax.title(titles[i], fontsize=fontsize)
                    except:
                        continue

        def tick_params(
            self,
            xticklabel_fontsize: Optional[float] = None,
            yticklabel_fontsize: Optional[float] = None,
            xticklabel_rotation: Optional[float] = None,
            yticklabel_rotation: Optional[float] = None,
        ) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.tick_params(
                    axis="x",
                    labelsize=xticklabel_fontsize,
                    labelrotation=xticklabel_rotation,
                )  # 设置x轴刻度标签字体大小
                _ax.tick_params(
                    axis="y",
                    labelsize=yticklabel_fontsize,
                    labelrotation=yticklabel_rotation,
                )  # 设置y轴刻度标签字体大小

        def remove_xticks(self) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.get_xaxis().set_ticks([])

        def remove_yticks(self) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.get_yaxis().set_ticks([])

        def xlabel(
            self, label: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.set_xlabel(label, fontsize=fontsize)

        def ylabel(
            self, label: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.set_ylabel(label, fontsize=fontsize)

        def hide_top_right_spines(self) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.spines["right"].set_visible(False)
                _ax.spines["top"].set_visible(False)
                _ax.yaxis.set_ticks_position("left")
                _ax.xaxis.set_ticks_position("bottom")

        def last_xticks_only(self) -> None:
            for i, _ax in enumerate(self._figure.axes):
                if (i % self._figure.gs.nrows) != self._figure.gs.nrows - 1:
                    _ax.get_xaxis().set_visible(False)

        def first_yticks_only(self) -> None:
            for i, _ax in enumerate(self._figure.axes):
                if (i % self.gs.ncols) != 0:
                    _ax.get_yaxis().set_visible(False)

        def xlim(self, xlim: Tuple[Tuple[float, float]]) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.set_xlim(xlim[i][0], xlim[i][1])

        def ylim(self, ylim: Tuple[Tuple[float, float]]) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax.set_ylim(ylim[i][0], ylim[i][1])

        def y2lim(self, y2lim: Tuple[Tuple[float, float]]) -> None:
            for i, _ax in enumerate(self._figure.axes):
                _ax2 = _ax.get_shared_x_axes().get_siblings(_ax)[0]
                _ax2.set_ylim(y2lim[i][0], y2lim[i][1])

        def same_xlim(self) -> None:
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

        def major_grid(self, **kwargs) -> None:
            d_grid = {
                "color": "grey",
                "axis": "both",
                "linestyle": ":",
                "linewidth": 0.3,
                "zorder": 0,
            }
            d_grid = {k: kwargs[k] if k in kwargs else v for k, v in d_grid.items()}

            for i, _ax in enumerate(self._figure.axes):
                _ax.grid(
                    which="major",
                    color=d_grid["color"],
                    axis=d_grid["axis"],
                    linestyle=d_grid["linestyle"],
                    linewidth=d_grid["linewidth"],
                    zorder=d_grid["zorder"],
                )

        def minor_grid(self, **kwargs) -> None:
            d_grid = {
                "color": "grey",
                "axis": "both",
                "linestyle": ":",
                "linewidth": 0.3,
                "zorder": 0,
            }
            d_grid = {k: kwargs[k] if k in kwargs else v for k, v in d_grid.items()}
            for i, _ax in enumerate(self._figure.axes):
                _ax.minorticks_on()
                _ax.grid(
                    which="both",
                    color=d_grid["color"],
                    axis=d_grid["axis"],
                    linestyle=d_grid["linestyle"],
                    linewidth=d_grid["linewidth"],
                    zorder=d_grid["zorder"],
                )

    def save(self):
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
