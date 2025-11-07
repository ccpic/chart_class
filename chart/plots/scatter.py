"""
Plot classes for scatter chart types.
"""

from __future__ import annotations
from typing import Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from chart.plots.base import Plot
from adjustText import adjust_text
from chart.plots.utils import scatter_hist, regression_band
import math


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
        # label_mustshow: List[str] = [],
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
            # label_mustshow (List[str], optional): 强制显示该列表中的标签. Defaults to [].
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

        # 使用基类方法获取列数据
        x = self._get_column(x, 0)
        y = self._get_column(y, 1)
        z = self._get_column(z, 2)

        # z列标准化并乘以系数以得到一般情况下都合适的气泡大小
        z = (z / z.max() * 100) ** 1.8 * bubble_scale

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "x_fmt": "{:,.0f}",
                "y_fmt": "{:,.0f}",
                "alpha": 0.6,
                "random_color": True,
                "edgecolor": "black",
                "avg_linestyle": ":",
                "avg_linewidth": 1,
                "avg_color": "black",
            },
            **kwargs,
        )

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
                bbox_to_anchor = {
                    "center left": (1, 0.5),
                    "lower center": (0.5, -0.1),
                    "upper center": (0.5, -0.1),
                }

                ax_legend.legend(
                    handles=handles,
                    title=self.hue.name,
                    loc=self.style._legend_loc,
                    frameon=False,
                    ncol=self.style._legend_ncol,
                    bbox_to_anchor=bbox_to_anchor.get(self.style._legend_loc, (0.5, 1)),
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

        # 使用基类方法添加colorbar
        self._add_colorbar(
            scatter, self.hue.name if self.hue is not None else "", show_hist=show_hist
        )

        # 添加系列标签
        texts = []
        x_shown = x if xlim is None else x[x.between(xlim[0], xlim[1])]
        y_shown = y if ylim is None else y[y.between(ylim[0], ylim[1])]
        index_shown = x_shown.index.intersection(y_shown.index)

        for i in range(len(index_shown)):
            # print(index_shown[i])
            if (
                i < label_limit
                or (
                    not pd.api.types.is_categorical_dtype(y)  # 判断y轴不为category
                    and index_shown[i] in y.loc[index_shown].nlargest(label_topy).index
                )
                # or (index_shown[i] in label_mustshow)
                or (self.focus and index_shown[i] in self.focus)
            ):  # 在label_limit内或者强制要求展示y值最大item的标签或者在特别关注列表时
                d_label = {
                    "x": (
                        d_style.get("x_fmt").format(x.loc[index_shown].iloc[i])
                        if isinstance(x.loc[index_shown].iloc[i], str) is False
                        else x.loc[index_shown].iloc[i]
                    ),
                    "y": (
                        d_style.get("y_fmt").format(y.loc[index_shown].iloc[i])
                        if isinstance(y.loc[index_shown].iloc[i], str) is False
                        else y.loc[index_shown].iloc[i]
                    ),
                    "z": z.loc[index_shown].iloc[i],
                    "hue": (
                        self.hue.loc[index_shown].iloc[i]
                        if self.hue is not None
                        else None
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
                        fontsize=kwargs.get("label_fontsize", self.fontsize),
                        color=(
                            "red"
                            if (self.focus and (index_shown[i] in self.focus))
                            else "black"
                        ),
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
                # only_move="x"
            )

        # 添加轴label
        if self.style._xlabel is None:
            self.style._xlabel = x.name
        if self.style._ylabel is None:
            self.style._ylabel = y.name

        # 使用基类方法格式化坐标轴
        self._format_axis("x", d_style.get("x_fmt"))
        self._format_axis("y", d_style.get("y_fmt"))

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

        # 使用基类方法获取列数据
        if df.shape[1] == 1:  # 如果df只有1列，默认没有start，唯一列是end数据
            start = None
            end = self._get_column(None, 0)
        else:  # 如果df多于1列不指定，则分别读取df第1-2列为start, end
            start = self._get_column(start, 0)
            end = self._get_column(end, 1)
            diff = end.subtract(start)
            fmt_diff = self.fmt[:2] + "+" + self.fmt[2:]

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "color_line": "grey",
                "color_start": "grey",
                "color_end": self._colors.cmap_qual.colors[0],
                "random_color": True,
                "alpha": 0.3,
            },
            **kwargs,
        )
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

        # 使用基类方法添加colorbar
        self._add_colorbar(scatter_end, self.hue.name if self.hue is not None else "")

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
