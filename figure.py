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
from matplotlib.ticker import FuncFormatter
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

# sns.set_theme(style="whitegrid")
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
                ax = self.add_subplot(axes)
        else:
            ax = self.add_subplot(111)

        # 检查grid大小和数据是否匹配
        check_data_with_axes(self.data, self.axes)

        self.style = self.Style(self, **style)

    class Style:
        def __init__(self, figure, **kwargs) -> None:
            self._figure = figure

            """整体画布的一些风格"""
            self._title = kwargs.get("title")  # 总标题
            self._title_fontsize = (
                kwargs.get("title_fontsize") or figure.fontsize * 1.5
            )  # 总标题字体大小
            self._ytitle = kwargs.get("yitle")  # y轴总标题
            self._ytitle_fontsize = (
                kwargs.get("ytitle_fontsize") or figure.fontsize * 1.5
            )  # y轴总标题字体大小

            """GridSpec画布的一些风格"""
            self._gs_titles = kwargs.get("gs_titles")  # GridSpec标题
            self._gs_titles_fontsize = (
                kwargs.get("gs_titles_fontsize") or figure.fontsize
            )  # GridSpec标题字体大小
            self._hide_top_right_spines = kwargs.get("hide_top_right_spines")  # 隐藏上/右边框
            self._last_xticks_only = kwargs.get(
                "last_xticks_only"
            )  # 多个子图情况下只显示最下方图片的x轴ticks
            self._first_yticks_only = kwargs.get(
                "first_yticks_only"
            )  # 多个子图情况下只显示最左侧图片的y轴ticks

            """坐标轴相关的风格"""
            self._xlabel = kwargs.get("xlabel")  # x轴标题
            self._xlabel_fontsize = (
                kwargs.get("xlabel_fontsize") or figure.fontsize
            )  # x轴标题字体大小
            self._ylabel = kwargs.get("ylabel")  # y轴标题
            self._ylabel_fontsize = (
                kwargs.get("ylabel_fontsize") or figure.fontsize
            )  # x轴标题字体大小

            """刻度相关的风格"""
            self._xticklabel_fontsize = (
                kwargs.get("xticklabel_fontsize") or figure.fontsize
            )  # x轴刻度标签字体大小
            self._yticklabel_fontsize = (
                kwargs.get("yticklabel_fontsize") or figure.fontsize
            )  # y轴刻度标签字体大小
            self._xticklabel_rotation = kwargs.get("xticklabel_rotation")  # x抽刻度旋转角度
            self._yticklabel_rotation = kwargs.get("yticklabel_rotation")  # y抽刻度旋转角度
            self._remove_xticks = kwargs.get("remove_xticks")  # 移除x轴刻度
            self._remove_yticks = kwargs.get("remove_yticks")  # 移除y轴刻度

            """初始化自动执行一遍风格设置"""
            self.set_title(self._title, self._title_fontsize)
            self.set_ytitle(self._ytitle, self._ytitle_fontsize)
            self.set_gstitles(self._gs_titles, self._gs_titles_fontsize)
            self.xlabel(self._xlabel, self._xlabel_fontsize)
            self.ylabel(self._ylabel, self._ylabel_fontsize)
            self.set_tick_params(
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

        def set_title(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            self._figure.suptitle(title, fontsize=fontsize)

        def set_ytitle(
            self, title: Optional[str] = None, fontsize: Optional[float] = None
        ) -> None:
            self._figure.supylabel(title, fontsize=fontsize)

        def set_gstitles(
            self, titles: Optional[List[str]], fontsize: Optional[float] = None
        ) -> None:
            if titles is not None:
                for i, _ax in enumerate(self._figure.axes):
                    try:
                        _ax.set_title(titles[i], fontsize=fontsize)
                    except:
                        continue

        def set_tick_params(
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

    def set_default_style(self) -> None:
        pass
        # d_style = {
        #     "title": None,  # 总标题
        #     "title_fontsize": self.fontsize * 1.5,  # 总标题字体大小
        #     "ytitle": None,  # y轴总标题
        #     "ytitle_fontsize": self.fontsize * 1.5,  # y轴总标题字体大小
        #     "xticklabel_fontsize": self.fontsize,  # x轴刻度标签字体大小
        #     "yticklabel_fontsize": self.fontsize,  # y轴刻度标签字体大小
        # }

        # d_style.update(self.style)
        # print(d_style)
        # """整个Figure部分"""
        # # 总标题
        # if d_style.get("title") is not None:
        #     self.suptitle(self.style["title"], fontsize=d_style["title_fontsize"])

        # # y轴总标题
        # if d_style.get("ytitle") is not None:
        #     self.supylabel(self.style["ytitle"], fontsize=d_style["ytitle_fontsize"])

        # """每个ax部分"""
        # ylim_range = []
        # xlim_range = []
        # for i, ax in enumerate(self.axes):
        #     ax.tick_params(
        #         axis="x", labelsize=d_style["xticklabel_fontsize"]
        #     )  # 设置x轴刻度标签字体大小
        #     ax.tick_params(
        #         axis="y", labelsize=d_style["yticklabel_fontsize"]
        #     )  # 设置y轴刻度标签字体大小

        #     # y轴标签
        #     # yticklabels = [
        #     #     label.get_text().split("（")[0] for label in ax.get_yticklabels()
        #     # ]  # 去除y轴标签括号内内容
        #     # ax.set_yticklabels(yticklabels)

        #     # 添加grid标题
        #     if "gs_title" in self.style:
        #         # check_data_with_axes(self.style["gs_title"], self.axes)
        #         try:
        #             ax.set_title(self.style["gs_title"][i], fontsize=self.fontsize)
        #         except:
        #             continue
        #         # box = ax.get_position()
        #         # ax.set_position([box.x0, box.y0, box.width, box.height * 0.95])

        #     # 旋转x轴标签
        #     if "xlabel_rotation" in self.style:
        #         ax.tick_params(axis="x", labelrotation=self.style["xlabel_rotation"])

        #     # 旋转y轴标签
        #     if "ylabel_rotation" in self.style:
        #         ax.tick_params(axis="y", labelrotation=self.style["ylabel_rotation"])

        #         # 去除x轴ticks
        #     if "remove_xticks" in self.style and self.style["remove_xticks"]:
        #         ax.get_xaxis().set_ticks([])

        #         # 去除y轴ticks
        #     if "remove_yticks" in self.style and self.style["remove_yticks"]:
        #         ax.get_yaxis().set_ticks([])

        #     # 添加x轴标签
        #     if "xlabel" in self.style:
        #         ax.set_xlabel(self.style["xlabel"], fontsize=self.fontsize)

        #     # 添加y轴标签
        #     if "ylabel" in self.style:
        #         ax.set_ylabel(self.style["ylabel"], fontsize=self.fontsize)

        #         # 多个子图情况下只显示最下方图片的x轴label
        #     if "last_xticks_only" in self.style:
        #         if (
        #             self.style["last_xticks_only"]
        #             and (i % self.gs.nrows) != self.gs.nrows - 1
        #         ):
        #             ax.get_xaxis().set_visible(False)

        #         # 多个子图情况下只显示最左边图片的x轴label
        #     if "first_yticks_only" in self.style:
        #         if self.style["first_yticks_only"] and (i % self.gs.ncols) != 0:
        #             ax.get_xaxis().set_visible(False)

        #         # 隐藏上/右边框
        #     if (
        #         "hide_top_right_spines" in self.style
        #         and self.style["hide_top_right_spines"]
        #     ):
        #         ax.spines["right"].set_visible(False)
        #         ax.spines["top"].set_visible(False)
        #         ax.yaxis.set_ticks_position("left")
        #         ax.xaxis.set_ticks_position("bottom")

        #     # x轴显示lim
        #     if "xlim" in self.style:
        #         ax.set_xlim(self.style["xlim"][i][0], self.style["xlim"][i][1])

        #     # y轴显示lim，如果有多个y轴需要注意传参的个数
        #     if "ylim" in self.style:
        #         ax.set_ylim(self.style["ylim"][i][0], self.style["ylim"][i][1])
        #         try:
        #             ax2 = ax.get_shared_x_axes().get_siblings(ax)[0]
        #         except:
        #             pass
        #         if ax2 is not None:
        #             ax2.set_ylim(self.style["ylim"][i][0], self.style["ylim"][i][1])

        #     if "same_ylim" in self.style and self.style["same_ylim"]:
        #         ylim_min, ylim_max = ax.get_ylim()
        #         if i == 0:
        #             ylim_range = [ylim_min, ylim_max]
        #         else:
        #             if ylim_min > ylim_range[0]:
        #                 ax.set_ylim(bottom=ylim_range[0])
        #             else:
        #                 ylim_range = [ylim_min, ylim_range[1]]
        #             if ylim_max < ylim_range[1]:
        #                 ax.set_ylim(top=ylim_range[1])
        #             else:
        #                 ylim_range = [ylim_range[0], ylim_max]

        #     if "same_xlim" in self.style and self.style["same_xlim"]:
        #         xlim_min, xlim_max = ax.get_xlim()
        #         if i == 0:
        #             xlim_range = [xlim_min, xlim_max]
        #         else:
        #             if xlim_min < xlim_range[0]:
        #                 xlim_range = [xlim_min, xlim_range[1]]
        #             if xlim_max > xlim_range[1]:
        #                 xlim_range = [xlim_range[0], xlim_max]

        #     # # 次坐标y轴显示lim
        #     # if "y2lim" in self.style:
        #     #     ax2 = ax.get_shared_x_axes().get_siblings(ax)[0]
        #     #     ax2.set_ylim(self.style["y2lim"][i][0], self.style["y2lim"][i][1])

        #     # 主网格线
        #     if "major_grid" in self.style:
        #         ax.grid(
        #             which="major",
        #             color=self.style["major_grid"],
        #             axis="both",
        #             linestyle=":",
        #             linewidth=0.3,
        #         )

        #     # 次网格线
        #     if "minor_grid" in self.style:
        #         plt.minorticks_on()
        #         ax.grid(
        #             which="minor",
        #             color=self.style["minor_grid"],
        #             axis="both",
        #             linestyle=":",
        #             linewidth=0.2,
        #         )
        # if "same_xlim" in self.style and self.style["same_xlim"]:
        #     for ax in self.axes:
        #         ax.set_xlim(xlim_range[0], xlim_range[1])
        # if "same_ylim" in self.style and self.style["same_ylim"]:
        #     for ax in self.axes:
        #         ax.set_xlim(ylim_range[0], ylim_range[1])

    def save(self):
        # 设置一些基本格式
        self.set_default_style()

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
