"""
Plot classes for line and area chart types.
"""

from __future__ import annotations
from typing import Any, List
import numpy as np
from chart.plots.base import Plot
from adjustText import adjust_text


class PlotLine(Plot):
    """折线图绘制类

    支持多系列折线图、数据标签、标签智能调整功能。
    """

    def plot(
        self,
        show_label: List[str] = [],
        endpoint_label_only: bool = False,
        **kwargs: Any,
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

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "adjust_labels": True,
                "linewidth": 2,  # 线条粗细
                "linestyle": "-",  # 线条样式
                "marker": "o",  # 标记点样式
                "markersize": 5,  # 标记点大小
                "line_color": None,  # 线条颜色
            },
            **kwargs,
        )

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

        # 使用基类方法格式化y轴
        self._format_axis("y")

        return self


class PlotArea(Plot):
    """面积图绘制类

    支持堆积/并列面积图、数据标签功能。
    """

    def plot(
        self,
        stacked: bool = True,
        show_label: List[str] = [],
        endpoint_label_only: bool = False,
        **kwargs: Any,
    ) -> PlotArea:
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

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "linewidth": 2,
                "alpha": 1,
            },
            **kwargs,
        )

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

            # 使用基类方法格式化y轴
            self._format_axis("y")

        return self
