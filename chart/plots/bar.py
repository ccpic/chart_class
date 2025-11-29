"""
Plot classes for bar chart types.
"""

from __future__ import annotations
from typing import Any, Literal, Optional, Dict
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from chart.plots.base import Plot


class PlotBar(Plot):
    """柱状图绘制类

    支持堆积/并列柱状图、数据标签、增长率线、平均线等功能。
    """

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
        **kwargs: Any,
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
        df_share = self._calculate_share(df, axis=1)
        df_gr = self.data.pct_change(axis=0, periods=period_change)
        avg = None
        if df.shape[1] == 1:
            mean_result = df.mean()
            if isinstance(mean_result, pd.Series):
                avg = float(mean_result.iloc[0])
            else:
                avg = float(mean_result)

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "bar_width": 0.8,  # 柱宽
                "bar_color": None,  # 柱指定颜色
                "label_fontsize": self.fontsize,  # 标签字体大小
                "bbox": None,  # 标签背景
                "fmt_abs": self.fmt,  # 绝对值标签格式
                "fmt_share": "{:.1%}",  # 占比标签格式
                "fmt_gr": "{:+.1%}",  # 增长率标签格式
            },
            **kwargs,
        )

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

            # 重置颜色迭代器
            self._reset_color_cycle()

            for i, col in enumerate(df):
                # 计算出的指标
                v = df.loc[index, col]
                share = df_share.loc[index, col]
                gr = df_gr.loc[index, col]
                total_gr = df.iloc[k, :].sum() / df.iloc[k - 1, :].sum() - 1

                # 直接创建标签字典，和气泡图一样的实现方式
                d_label = {
                    "abs": self.fmt.format(v),
                    "share": "{:.1%}".format(share),
                    "gr": "{:+.1%}".format(gr),
                    "index": str(index),
                    "col": str(col),
                    "total_gr": (d_style.get("fmt_gr") or "{:+.1%}").format(total_gr),
                }

                # 使用基类方法获取颜色
                if d_style.get("bar_color"):
                    color = d_style.get("bar_color")
                else:
                    color = self._get_color_for_item(
                        col if stacked else index, stacked=stacked
                    )

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
                    pos_x = k + (bar_width or 0.8) * i

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
                            multialignment="center",
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
                        if not np.isinf(gr) and not np.isnan(gr):
                            self.ax.text(
                                x=k - 0.5,
                                y=(
                                    bottom_gr
                                    + df.iloc[k - 1, i] / 2
                                    + df.iloc[k, i] / 2
                                )
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
                            total_gr_val = total_gr
                            if not np.isinf(total_gr_val) and not np.isnan(
                                total_gr_val
                            ):
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
            bar_width_val = bar_width or 0.8
            self.ax.set_xticks(
                np.arange(df.shape[0]) + bar_width_val / df.shape[1], df.index
            )
        else:
            self.ax.set_xticks(np.arange(df.shape[0]), df.index)

        # x轴标签
        self.ax.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

        # 使用基类方法格式化y轴
        self._format_axis("y")

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
                FuncFormatter(lambda y, _: self.fmt.format(y))
            )
            ax2.get_yaxis().set_ticks([])

            # # x轴标签
            # ax2.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

        if show_avg_line and df.shape[1] == 1 and avg is not None:
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
    """横向柱状图绘制类

    支持堆积/并列横向柱状图，标签智能定位功能。
    """

    def plot(
        self,
        stacked: bool = True,
        show_label: bool = True,
        label_formatter: str = "{abs}",
        label_threshold: float = 0.02,
        label_pos: Literal["smart", "center", "outer"] = "smart",
        **kwargs: Any,
    ) -> PlotBarh:
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
        df_share = self._calculate_share(df, axis=1)
        df_share_total = df.div(df.sum())

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "bar_height": 0.8,  # bar高度
                "bar_color": None,  # 柱指定颜色
                "label_fontsize": self.fontsize,  # 标签字体大小
                "bbox": None,  # 标签背景
                "fmt_abs": self.fmt,  # 绝对值标签格式
                "fmt_share": "{:.1%}",  # 占比标签格式
                "fmt_gr": "{:+.1%}",  # 增长率标签格式
            },
            **kwargs,
        )

        # 绝对值bar图和增长率标注
        max_v = np.nanmax(df.values)
        min_v = np.nanmin(df.values)
        for k, index in enumerate(df.index):
            left_pos = 0
            left_neg = 0

            # 重置颜色迭代器
            self._reset_color_cycle()

            for i, col in enumerate(df):
                # 计算出的指标
                v = df.loc[index, col]
                share = df_share.loc[index, col]
                share_total = df_share_total.loc[index, col]

                # 直接创建标签字典，和气泡图一样的实现方式
                d_label = {
                    "abs": self.fmt.format(v),
                    "share": "{:.1%}".format(share),
                    "index": str(index),
                    "col": str(col),
                    "share_total": (d_style.get("fmt_share") or "{:.1%}").format(
                        share_total
                    ),
                }

                # 使用基类方法获取颜色
                if d_style.get("bar_color"):
                    color = d_style.get("bar_color")
                else:
                    color = self._get_color_for_item(
                        col if stacked else index, stacked=stacked
                    )

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
                    bar_height_val = bar_height or 0.8
                    pos_y = k + bar_height_val * i

                # 绘制bar图
                bar_height_val = bar_height or 0.8
                self.ax.barh(
                    pos_y,
                    v,
                    height=bar_height_val,
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
                            multialignment="center",
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
            bar_height_val = d_style.get("bar_height") or 0.8
            self.ax.set_yticks(
                np.arange(df.shape[0]) + bar_height_val / df.shape[1], df.index
            )
        else:
            self.ax.set_yticks(np.arange(df.shape[0]), df.index)

        # y轴标签
        self.ax.get_yaxis().set_ticks(range(0, len(df.index)), labels=df.index)

        # 使用基类方法格式化x轴
        self._format_axis("x")

        self.ax.axvline(0, color="black", linewidth=0.5)  # x轴为0的竖线

        self.ax.invert_yaxis()  # 翻转y轴，最上方显示排名靠前的序列

        return self


class PlotWaterfall(Plot):
    """瀑布图绘制类

    瀑布图用于展示累积变化，显示从起始值到结束值的过程。
    第一个和最后一个柱子显示绝对值，中间柱子显示差值。
    """

    def plot(
        self,
        size: Optional[str] = None,
        show_connector: bool = True,
        connector_style: Optional[Dict[str, Any]] = None,
        show_label: bool = True,
        label_formatter: str = "{abs}",
        label_pos: Literal["top", "center", "bottom"] = "top",
        positive_color: str = "green",
        negative_color: str = "red",
        start_color: Optional[str] = None,
        end_color: Optional[str] = None,
        bar_width: float = 0.8,
        **kwargs: Any,
    ) -> PlotWaterfall:
        """继承基本Plot类，绘制瀑布图

        Args:
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
            show_connector (bool, optional): 是否显示连接线. Defaults to True.
            connector_style (Optional[Dict[str, Any]], optional): 连接线样式字典. Defaults to None.
            show_label (bool, optional): 是否显示数字标签. Defaults to True.
            label_formatter (str, optional): 标签格式，支持{abs},{index}. Defaults to "{abs}".
            label_pos (Literal["top", "center", "bottom"], optional): 标签位置. Defaults to "top".
            positive_color (str, optional): 正值颜色. Defaults to "green".
            negative_color (str, optional): 负值颜色. Defaults to "red".
            start_color (Optional[str], optional): 起始柱子颜色，如不指定则使用调色板第一个颜色. Defaults to None.
            end_color (Optional[str], optional): 结束柱子颜色，如不指定则使用调色板第一个颜色. Defaults to None.
            bar_width (float, optional): 柱宽. Defaults to 0.8.

        Returns:
            PlotWaterfall: 返回自身实例
        """
        df = self.data

        # 使用基类方法获取列数据
        size_col = self._get_column(size, 0)
        values = size_col.values
        labels = df.index.tolist()

        # 计算瀑布图数据
        # 第一个值：从0到第一个值（起始值）
        # 中间值：使用原始数值，从前面所有值的累积和开始，高度为原始值
        # 最后一个值：从0起始，高度为最后一个值本身
        waterfall_values = []
        waterfall_bottom = []

        for i in range(len(values)):
            if i == 0:
                # 第一个值：从0到第一个值（起始值）
                waterfall_values.append(values[i])
                waterfall_bottom.append(0.0)
            elif i == len(values) - 1:
                # 最后一个值：从0起始，高度为最后一个值本身
                waterfall_values.append(values[i])  # 使用最后一个值本身作为高度
                waterfall_bottom.append(0.0)  # 从0起始
            else:
                # 中间值：使用原始数值，从前面所有值的累积和开始，高度为原始值
                # 第N个柱子的起点是前N个值的累积和
                cumulative_sum = sum(values[:i])  # 前i个值的累积和
                waterfall_values.append(values[i])
                waterfall_bottom.append(cumulative_sum)

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "bar_width": bar_width,
                "label_fontsize": self.fontsize,
                "fmt_abs": self.fmt,
                "label_color": None,  # 标签颜色，如果指定则使用，否则自动计算
            },
            **kwargs,
        )

        # 从 kwargs 或默认值获取颜色参数（避免被覆盖）
        final_positive_color = kwargs.get("positive_color", positive_color)
        final_negative_color = kwargs.get("negative_color", negative_color)
        final_start_color = kwargs.get("start_color", start_color)
        final_end_color = kwargs.get("end_color", end_color)

        # 获取调色板第一个颜色（用于第一个和最后一个柱子，如果未指定颜色）
        # 重置颜色迭代器并获取第一个颜色
        self._reset_color_cycle()
        default_color = next(self._colors.iter_colors)

        # 确定起始和结束柱子的颜色
        start_bar_color = (
            final_start_color if final_start_color is not None else default_color
        )
        end_bar_color = (
            final_end_color if final_end_color is not None else default_color
        )

        # 绘制柱子
        for i in range(len(waterfall_values)):
            value = waterfall_values[i]
            bottom = waterfall_bottom[i]

            # 确定颜色
            if i == 0:
                # 第一个柱子使用起始颜色
                color = start_bar_color
            elif i == len(waterfall_values) - 1:
                # 最后一个柱子使用结束颜色
                color = end_bar_color
            else:
                # 中间柱子：根据数值正负使用不同颜色
                # 直接根据 values[i] 的正负来判断颜色
                if values[i] >= 0:
                    color = final_positive_color
                else:
                    color = final_negative_color

            # 绘制柱子
            self.ax.bar(
                i,
                value,
                width=d_style.get("bar_width"),
                bottom=bottom,
                color=color,
                zorder=3,
            )

            # 绘制标签（包括第一个和最后一个柱子）
            if show_label:
                # 创建标签字典
                # 所有柱子都显示对应的原始值
                abs_value = values[i]

                d_label = {
                    "abs": d_style.get("fmt_abs").format(abs_value),
                    "index": str(labels[i]),
                }

                # 确定标签位置
                if label_pos == "top":
                    label_y = (
                        bottom
                        + value
                        + (abs(value) * 0.05 if value >= 0 else -abs(value) * 0.05)
                    )
                    va = "bottom" if value >= 0 else "top"
                elif label_pos == "bottom":
                    label_y = bottom + (
                        abs(value) * 0.05 if value >= 0 else -abs(value) * 0.05
                    )
                    va = "bottom" if value >= 0 else "top"
                else:  # center
                    label_y = bottom + value / 2
                    va = "center"

                # 确定标签颜色
                # 如果标签位置是"top"，强制使用黑色（除非用户明确指定了其他颜色）
                user_label_color = d_style.get("label_color")
                if label_pos == "top":
                    # 标签在顶部时，使用黑色以确保可见性（除非用户明确指定了其他颜色）
                    label_color = (
                        user_label_color if user_label_color is not None else "black"
                    )
                elif user_label_color is not None:
                    # 如果用户指定了标签颜色，使用用户指定的颜色
                    label_color = user_label_color
                else:
                    # 否则自动计算标签颜色
                    # 对于第一个和最后一个柱子（bottom == 0），根据柱子高度判断
                    # 对于中间柱子，根据柱子高度和底部位置的关系判断
                    if i == 0 or i == len(waterfall_values) - 1:
                        # 第一个和最后一个柱子：如果柱子高度足够大，使用白色；否则使用黑色以确保可见性
                        if abs(value) > 0.1:
                            label_color = "white"
                        else:
                            label_color = "black"
                    else:
                        # 中间柱子：根据柱子高度和底部位置的关系决定颜色
                        label_color = (
                            "white" if abs(value) > abs(bottom) * 0.3 else "black"
                        )

                # 确保标签一定显示，使用更高的zorder
                self.ax.text(
                    i,
                    label_y,
                    label_formatter.format(**d_label),
                    ha="center",
                    va=va,
                    fontsize=d_style.get("label_fontsize"),
                    color=label_color,
                    zorder=10,  # 提高zorder确保标签在最上层
                )

            # 绘制连接线
            if show_connector and i < len(waterfall_values) - 1:
                # 连接当前柱子顶部到下一个柱子
                current_top = bottom + waterfall_values[i]

                # 连接到下一个柱子的位置
                if i + 1 == len(waterfall_values) - 1:
                    # 如果下一个柱子是最后一个柱子，连接到最后一个柱子的顶部
                    next_y = waterfall_bottom[i + 1] + waterfall_values[i + 1]
                else:
                    # 否则连接到下一个柱子的底部
                    next_y = waterfall_bottom[i + 1]

                # 默认连接线样式
                default_connector_style = {
                    "color": "gray",
                    "linestyle": "--",
                    "linewidth": 1,
                    "alpha": 0.7,
                }
                connector_style_final = {
                    **default_connector_style,
                    **(connector_style or {}),
                }

                self.ax.plot(
                    [
                        i + d_style.get("bar_width") / 2,
                        i + 1 - d_style.get("bar_width") / 2,
                    ],
                    [current_top, next_y],
                    color=connector_style_final.get("color"),
                    linestyle=connector_style_final.get("linestyle"),
                    linewidth=connector_style_final.get("linewidth"),
                    alpha=connector_style_final.get("alpha"),
                    zorder=2,
                )

        # 设置x轴刻度
        self.ax.set_xticks(range(len(labels)), labels)

        # 计算y轴最大值，留出一些空白
        # 计算所有柱子的顶部位置的最大值
        max_top = max(
            bottom + value for bottom, value in zip(waterfall_bottom, waterfall_values)
        )

        # 计算y轴最大值，留出10%的余量
        y_margin = max_top * 0.1  # 10%的余量
        y_max = max_top + y_margin

        # 只设置y轴最大值，让matplotlib自动处理最小值
        current_ylim = self.ax.get_ylim()
        self.ax.set_ylim(current_ylim[0], y_max)

        # 使用基类方法格式化y轴
        self._format_axis("y")

        # 添加y=0的参考线
        self.ax.axhline(0, color="black", linewidth=0.5, linestyle="-", zorder=1)

        return self
