"""
Plot classes for bar chart types.
"""

from __future__ import annotations
from typing import Any, Literal, Optional, Dict
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from chart.plots.base import Plot


def _apply_text_style(
    text_kwargs: Dict[str, Any],
    d_style: Dict[str, Any],
    style_prefix: str,
    default_fontsize: int,
    default_color: str = "black",
) -> None:
    """应用文本样式到 text_kwargs 字典

    Args:
        text_kwargs: 文本参数字典，会被修改
        d_style: 样式参数字典
        style_prefix: 样式参数前缀，如 "gr_text" 或 "label"
        default_fontsize: 默认字体大小
        default_color: 默认颜色
    """
    # 字体大小：优先使用指定前缀的 fontsize，否则使用 label_fontsize，最后使用默认值
    if d_style.get(f"{style_prefix}_fontsize"):
        text_kwargs["fontsize"] = d_style.get(f"{style_prefix}_fontsize")
    elif d_style.get("label_fontsize"):
        text_kwargs["fontsize"] = d_style.get("label_fontsize")
    else:
        text_kwargs["fontsize"] = default_fontsize

    # 标签颜色：优先使用指定前缀的 color，否则使用默认颜色
    text_color = d_style.get(f"{style_prefix}_color")
    if text_color:
        text_kwargs["color"] = text_color
    else:
        text_kwargs["color"] = default_color

    # 字体样式：weight 用于加粗，style 用于斜体
    text_weight = d_style.get(f"{style_prefix}_weight")
    if text_weight:
        if text_weight == "italic":
            text_kwargs["style"] = "italic"
            text_kwargs["weight"] = "normal"
        elif text_weight == "bold":
            text_kwargs["weight"] = "bold"
            text_kwargs["style"] = "normal"

    # 文本框（bbox）：使用指定前缀的 bbox
    text_bbox = d_style.get(f"{style_prefix}_bbox")
    if text_bbox:
        # 构建 bbox 样式字典
        bbox_style = {}
        if text_bbox.get("boxstyle"):
            bbox_style["boxstyle"] = text_bbox["boxstyle"]
        if text_bbox.get("facecolor"):
            bbox_style["facecolor"] = text_bbox["facecolor"]
        else:
            # 如果没有指定 facecolor，使用默认颜色
            bbox_style["facecolor"] = default_color
        # show_border 控制是否显示边框（默认为 True）
        show_border = text_bbox.get("show_border", True)
        if show_border:
            # 只有在显示边框时才设置边框相关参数
            if text_bbox.get("edgecolor"):
                bbox_style["edgecolor"] = text_bbox["edgecolor"]
            else:
                # 如果没有指定 edgecolor，使用默认颜色
                bbox_style["edgecolor"] = default_color
            linewidth = text_bbox.get("linewidth")
            if linewidth is not None:
                bbox_style["linewidth"] = float(linewidth)
        else:
            # 不显示边框时，明确设置 linewidth 为 0 以隐藏边框
            bbox_style["linewidth"] = 0
        # 确保 alpha 不是 None
        alpha = text_bbox.get("alpha")
        if alpha is not None:
            bbox_style["alpha"] = float(alpha)
        else:
            bbox_style["alpha"] = 0.7

        if bbox_style:
            text_kwargs["bbox"] = bbox_style


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
        secondary_line_column: Optional[str] = None,
        show_avg_line: bool = False,
        label_threshold: float = 0.02,
        total_bar_width: float = 0.6,
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
            secondary_line_column (Optional[str], optional): 次坐标轴折线图要绘制的列名.
                                                             如果指定，则在次坐标轴上绘制该列的原始值折线图；如果为None，则不显示折线图. Defaults to None.
            label_threshold (float, optional): 显示数字标签的阈值，系列占堆积之和的比例大于此值才显示. Defaults to 0.02.
            total_bar_width (float, optional): 总体表现外框的宽度. Defaults to 0.6.

        Returns:
            self: 返回自身plot实例
        """
        df = self.data

        # 如果指定了次坐标轴列，创建排除该列的 DataFrame 用于柱状图绘制
        df_bar = df.copy()
        if secondary_line_column is not None and secondary_line_column in df.columns:
            df_bar = df.drop(columns=[secondary_line_column])

        df_share = self._calculate_share(df_bar, axis=1)
        df_gr = self.data.pct_change(axis=0, periods=1)
        avg = None
        if df_bar.shape[1] == 1:
            mean_result = df_bar.mean()
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
                "label_color": None,  # 标签颜色
                "label_weight": None,  # 标签字重：normal, bold, italic
                "label_bbox": None,  # 标签背景框配置
                "bbox": None,  # 标签背景（向后兼容）
                "fmt_abs": self.fmt,  # 绝对值标签格式
                "fmt_share": "{:.1%}",  # 占比标签格式
                "fmt_gr": "{:+.1%}",  # 增长率标签格式
                "gr_text_fontsize": self.fontsize,  # 增长率文本字体大小
                "gr_text_color": None,  # 增长率文本颜色
                "gr_text_weight": None,  # 增长率文本字重：normal, bold, italic
                "gr_text_bbox": None,  # 增长率文本背景框配置
                "total_text_fontsize": self.fontsize,  # 堆积总计值文本字体大小
                "total_text_color": None,  # 堆积总计值文本颜色
                "total_text_weight": None,  # 堆积总计值文本字重：normal, bold, italic
                "total_text_bbox": None,  # 堆积总计值文本背景框配置
                "secondary_line_color": "darkorange",  # 次坐标轴折线颜色
                "secondary_line_linestyle": "dashed",  # 次坐标轴折线样式
                "secondary_line_linewidth": 1,  # 次坐标轴折线宽度
                "secondary_line_marker": "o",  # 次坐标轴折线标记
                "secondary_line_markersize": 3,  # 次坐标轴折线标记大小
                "secondary_line_label_fmt": None,  # 次坐标轴折线标签格式，None则使用fmt_abs
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

            max_v = np.nanmax(df_bar.values) if df_bar.shape[1] > 0 else 0
            min_v = np.nanmin(df_bar.values) if df_bar.shape[1] > 0 else 0
            range_v = max_v - min_v

            # 重置颜色迭代器
            self._reset_color_cycle()

            # 用于非堆叠模式下的列索引（排除次坐标轴列）
            bar_col_index = 0
            for i, col in enumerate(df):
                # 如果该列被选为次坐标轴折线图，跳过绘制
                if secondary_line_column is not None and col == secondary_line_column:
                    continue
                # 计算出的指标
                v = df_bar.loc[index, col]
                share = df_share.loc[index, col]
                gr = df_gr.loc[index, col] if col in df_gr.columns else 0
                # 计算总体增长率时，使用 df_bar（排除次坐标轴列）
                if k > 0 and df_bar.shape[1] > 0:
                    total_gr = df_bar.iloc[k, :].sum() / df_bar.iloc[k - 1, :].sum() - 1
                else:
                    total_gr = 0

                # 直接创建标签字典，和气泡图一样的实现方式
                # 使用 fmt_abs 格式化绝对值
                fmt_abs = d_style.get("fmt_abs") or self.fmt
                # 使用 fmt_share 格式化占比
                fmt_share = d_style.get("fmt_share") or "{:.1%}"
                # 使用 fmt_gr 格式化增长率
                fmt_gr = d_style.get("fmt_gr") or "{:+.1%}"

                d_label = {
                    "abs": fmt_abs.format(v),
                    "share": fmt_share.format(share),
                    "gr": fmt_gr.format(gr),
                    "index": str(index),
                    "col": str(col),
                    "total_gr": fmt_gr.format(total_gr),
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
                    # 非堆叠模式下，使用 bar_col_index 而不是 i，因为跳过了次坐标轴列
                    pos_x = k + (bar_width or 0.8) * bar_col_index
                    bar_col_index += 1

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
                # 绘制总体表现外框（只绘制一次，在第一个被绘制的列时）
                if show_total_bar and bar_col_index == 0:
                    self.ax.bar(
                        df_bar.index,
                        df_bar.sum(axis=1) * 1.03,
                        width=total_bar_width,
                        linewidth=1,
                        linestyle="--",
                        facecolor=(1, 0, 0, 0.0),
                        edgecolor=(0, 0, 0, 1),
                    )

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

                    # 确保 ylim 和 label_threshold 都不是 None
                    ylim = self.ax.get_ylim()
                    ymax = (
                        ylim[1]
                        if ylim and len(ylim) > 1 and ylim[1] is not None
                        else 1.0
                    )
                    threshold = label_threshold if label_threshold is not None else 0.02
                    if ymax != 0 and abs(v / ymax) >= threshold:
                        # 构建标签文本参数
                        text_kwargs = {
                            "x": pos_x,
                            "y": pos_y,
                            "s": label_formatter.format(**d_label),
                            "va": va,
                            "ha": "center",
                            "multialignment": "center",
                            "zorder": 5,
                        }

                        # 字体大小
                        if d_style.get("label_fontsize"):
                            text_kwargs["fontsize"] = d_style.get("label_fontsize")

                        # 标签颜色：优先使用 label_color，否则使用自动计算的 fontcolor
                        label_color = d_style.get("label_color")
                        if label_color:
                            text_kwargs["color"] = label_color
                        else:
                            text_kwargs["color"] = fontcolor

                        # 字体样式：weight 用于加粗，style 用于斜体
                        label_weight = d_style.get("label_weight")
                        if label_weight:
                            if label_weight == "italic":
                                # 斜体使用 style 参数，同时确保 weight 为 normal
                                text_kwargs["style"] = "italic"
                                text_kwargs["weight"] = "normal"
                            elif label_weight == "bold":
                                # 加粗使用 weight 参数，同时确保 style 为 normal
                                text_kwargs["weight"] = "bold"
                                text_kwargs["style"] = "normal"
                            # normal 不需要设置任何参数

                        # 文本框（bbox）：优先使用 label_bbox，否则使用 bbox（向后兼容）
                        label_bbox = d_style.get("label_bbox")
                        if label_bbox:
                            # 构建 bbox 样式字典
                            bbox_style = {}
                            if label_bbox.get("boxstyle"):
                                bbox_style["boxstyle"] = label_bbox["boxstyle"]
                            if label_bbox.get("facecolor"):
                                bbox_style["facecolor"] = label_bbox["facecolor"]
                            # show_border 控制是否显示边框（默认为 True）
                            show_border = label_bbox.get("show_border", True)
                            if show_border:
                                # 只有在显示边框时才设置边框相关参数
                                if label_bbox.get("edgecolor"):
                                    bbox_style["edgecolor"] = label_bbox["edgecolor"]
                                linewidth = label_bbox.get("linewidth")
                                if linewidth is not None:
                                    bbox_style["linewidth"] = float(linewidth)
                            else:
                                # 不显示边框时，明确设置 linewidth 为 0 以隐藏边框
                                bbox_style["linewidth"] = 0
                            # 确保 alpha 不是 None
                            alpha = label_bbox.get("alpha")
                            if alpha is not None:
                                bbox_style["alpha"] = float(alpha)
                            if bbox_style:
                                text_kwargs["bbox"] = bbox_style
                        elif d_style.get("bbox"):
                            text_kwargs["bbox"] = d_style.get("bbox")

                        self.ax.text(**text_kwargs)
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
                            # 使用 df_bar 中的值计算位置
                            prev_val = (
                                df_bar.iloc[k - 1, df_bar.columns.get_loc(col)]
                                if col in df_bar.columns
                                else 0
                            )
                            curr_val = (
                                df_bar.iloc[k, df_bar.columns.get_loc(col)]
                                if col in df_bar.columns
                                else 0
                            )

                            # 构建增长率文本参数
                            gr_text_kwargs = {
                                "x": k - 0.5,
                                "y": (bottom_gr + prev_val / 2 + curr_val / 2) / 2,
                                "s": d_label["gr"],
                                "ha": "center",
                                "va": "center",
                                "zorder": 5,
                            }

                            # 使用公共函数应用文本样式
                            _apply_text_style(
                                gr_text_kwargs,
                                d_style,
                                "gr_text",
                                self.fontsize,
                                color if color else "black",
                            )

                            self.ax.text(**gr_text_kwargs)
                        # 累积 bottom_gr，使用 df_bar 中的值
                        if col in df_bar.columns:
                            prev_val = df_bar.iloc[k - 1, df_bar.columns.get_loc(col)]
                            curr_val = df_bar.iloc[k, df_bar.columns.get_loc(col)]
                            bottom_gr += prev_val + curr_val

                        # 绘制总体增长率
                        if show_total_label:
                            total_gr_val = total_gr
                            if not np.isinf(total_gr_val) and not np.isnan(
                                total_gr_val
                            ):
                                # 构建总体增长率文本参数
                                total_gr_text_kwargs = {
                                    "x": k - 0.5,
                                    "y": (
                                        df_bar.iloc[k, :].sum()
                                        + df_bar.iloc[k - 1, :].sum()
                                    )
                                    / 2
                                    * 1.05,
                                    "s": d_label["total_gr"],
                                    "ha": "center",
                                    "va": "bottom",
                                    "zorder": 5,
                                }

                                # 使用公共函数应用文本样式（总体增长率也使用 gr_text 样式）
                                _apply_text_style(
                                    total_gr_text_kwargs,
                                    d_style,
                                    "gr_text",
                                    self.fontsize,
                                    "black",
                                )

                                self.ax.text(**total_gr_text_kwargs)

            # 在柱状图顶端添加total值
            if show_total_label:
                total = df_bar.sum(axis=1)
                # 使用 fmt_abs 格式化总计值（如果没有指定则使用默认格式）
                fmt_total = d_style.get("fmt_abs") or self.fmt
                for p, v in enumerate(total.values):
                    # 构建总计值文本参数
                    total_text_kwargs = {
                        "x": p,
                        "y": (
                            v * 1.05 if show_total_bar else v
                        ),  # 如果绘制整体外框则优化total值文本的位置
                        "s": fmt_total.format(float(v)),
                        "ha": "center",
                        "va": "bottom",
                        "zorder": 5,
                    }

                    # 使用公共函数应用文本样式（总计值使用 total_text 样式）
                    _apply_text_style(
                        total_text_kwargs, d_style, "total_text", self.fontsize, "black"
                    )

                    self.ax.text(**total_text_kwargs)

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
        self.ax.get_xaxis().set_ticks(range(0, len(df_bar.index)), labels=df_bar.index)

        # 使用基类方法格式化y轴
        self._format_axis("y")

        # 只有在未隐藏 x 轴时才绘制 y=0 的参考线
        # 检查样式参数中是否隐藏了 x 轴
        hide_xaxis = d_style.get("hide_xaxis", False) or getattr(
            self.style, "_hide_xaxis", False
        )
        if not hide_xaxis:
            self.ax.axhline(0, color="black", linewidth=0.5)  # y轴为0的横线

        if secondary_line_column is not None:
            # 增加次坐标轴
            ax2 = self.ax.twinx()

            # 根据样式设置控制次坐标轴的边框
            # 次坐标轴应该遵循主坐标轴的边框设置
            if (
                hasattr(self.style, "_show_top_spine")
                or hasattr(self.style, "_show_right_spine")
                or hasattr(self.style, "_show_bottom_spine")
                or hasattr(self.style, "_show_left_spine")
            ):
                # 使用新的四个独立字段控制边框
                show_top = getattr(self.style, "_show_top_spine", True)
                show_right = getattr(self.style, "_show_right_spine", True)
                show_bottom = getattr(self.style, "_show_bottom_spine", True)
                show_left = getattr(self.style, "_show_left_spine", True)

                # 次坐标轴的边框控制：
                # - 上边框：遵循主坐标轴设置
                # - 右边框：遵循主坐标轴设置
                # - 下边框：隐藏（与主坐标轴共享）
                # - 左边框：隐藏（与主坐标轴共享）
                ax2.spines["top"].set_visible(show_top)
                ax2.spines["right"].set_visible(show_right)
                ax2.spines["bottom"].set_visible(False)
                ax2.spines["left"].set_visible(False)
            elif getattr(self.style, "_hide_top_right_spines", False):
                # 向后兼容：如果设置了 hide_top_right_spines，则隐藏上/右边框
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                ax2.spines["bottom"].set_visible(False)
                ax2.spines["left"].set_visible(False)

            # 如果指定了列，绘制该列的原始值
            if secondary_line_column not in df.columns:
                raise ValueError(
                    f"指定的列 '{secondary_line_column}' 不存在于数据中。可用列: {list(df.columns)}"
                )
            line_data = df[secondary_line_column]
            line_label = secondary_line_column
            # 使用指定的标签格式，如果没有则使用 fmt_abs
            label_fmt = (
                d_style.get("secondary_line_label_fmt")
                or d_style.get("fmt_abs")
                or self.fmt
            )

            color_line = d_style.get("secondary_line_color") or "darkorange"
            linestyle = d_style.get("secondary_line_linestyle") or "dashed"
            linewidth = d_style.get("secondary_line_linewidth") or 1
            marker = d_style.get("secondary_line_marker") or "o"
            markersize = d_style.get("secondary_line_markersize") or 3

            ax2.plot(
                line_data.index,
                line_data.values,
                label=line_label,
                color=color_line,
                linewidth=linewidth,
                linestyle=linestyle,
                marker=marker,
                markersize=markersize,
                markerfacecolor="white",
            )

            # 绘制标签
            for i in range(len(line_data)):
                value = float(line_data.values[i])
                if not np.isnan(value) and not np.isinf(value):
                    if value <= ax2.get_ylim()[1]:
                        try:
                            formatted_value = label_fmt.format(value)
                        except (ValueError, KeyError):
                            # 如果格式化失败，使用默认格式
                            formatted_value = self.fmt.format(value)

                        t = ax2.text(
                            x=line_data.index[i],
                            y=value,
                            s=formatted_value,
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
        show_total_label: bool = False,
        **kwargs: Any,
    ) -> PlotBarh:
        """继承基本Plot类，绘制柱状图

        Args:
            stacked (bool, optional): 是否堆积. Defaults to True.
            show_label (bool, optional): 是否显示数字标签. Defaults to True.
            label_formatter (str, optional): 主标签的格式，支持通配符{abs},{share},{gr},{index},{col}. Defaults to "{abs}".
            show_total_bar (bool, optional): 是否显示一个总体表现外框. Defaults to False.
            show_total_label (bool, optional): 是否在条形图整体外侧右边显示堆积之和数字标签. Defaults to False.
            show_gr_text (bool, optional): 是否显示增长率数字. Defaults to False.
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
                "label_color": None,  # 标签颜色，如果指定则使用，否则自动计算
                "label_weight": None,  # 标签字重：normal, bold, italic
                "label_bbox": None,  # 标签背景框配置
                "bbox": None,  # 标签背景（向后兼容）
                "fmt_abs": self.fmt,  # 绝对值标签格式
                "fmt_share": "{:.1%}",  # 占比标签格式
                "fmt_gr": "{:+.1%}",  # 增长率标签格式
                "total_text_fontsize": self.fontsize,  # 堆积总计值文本字体大小
                "total_text_color": None,  # 堆积总计值文本颜色
                "total_text_weight": None,  # 堆积总计值文本字重：normal, bold, italic
                "total_text_bbox": None,  # 堆积总计值文本背景框配置
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

                # 直接创建标签字典，使用 d_style 中的格式参数
                fmt_abs = d_style.get("fmt_abs") or self.fmt
                fmt_share = d_style.get("fmt_share") or "{:.1%}"
                d_label = {
                    "abs": fmt_abs.format(v),
                    "share": fmt_share.format(share),
                    "index": str(index),
                    "col": str(col),
                    "share_total": fmt_share.format(share_total),
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

                    threshold = label_threshold if label_threshold is not None else 0.02
                    # 对于堆积图，使用 share_total（系列占堆积之和的比例）
                    # 对于非堆积图，使用 x 轴最大值计算比例
                    if stacked and df.shape[1] > 1:
                        # 堆积图：使用占比判断
                        should_show = abs(share_total) >= threshold
                    else:
                        # 非堆积图：使用 x 轴最大值计算比例
                        xlim = self.ax.get_xlim()
                        xmax = (
                            xlim[1]
                            if xlim and len(xlim) > 1 and xlim[1] is not None
                            else 1.0
                        )
                        should_show = xmax != 0 and abs(v / xmax) >= threshold

                    if should_show:
                        # 构建标签文本参数
                        text_kwargs = {
                            "x": pos_x,
                            "y": pos_y,
                            "s": label_formatter.format(**d_label),
                            "va": "center",
                            "ha": ha,
                            "multialignment": "center",
                            "zorder": 5,
                        }

                        # 字体大小
                        if d_style.get("label_fontsize"):
                            text_kwargs["fontsize"] = d_style.get("label_fontsize")

                        # 标签颜色：优先使用 label_color，否则使用自动计算的 fontcolor
                        label_color = d_style.get("label_color")
                        if label_color:
                            text_kwargs["color"] = label_color
                        else:
                            text_kwargs["color"] = fontcolor

                        # 字体样式：weight 用于加粗，style 用于斜体
                        label_weight = d_style.get("label_weight")
                        if label_weight:
                            if label_weight == "italic":
                                # 斜体使用 style 参数，同时确保 weight 为 normal
                                text_kwargs["style"] = "italic"
                                text_kwargs["weight"] = "normal"
                            elif label_weight == "bold":
                                # 加粗使用 weight 参数，同时确保 style 为 normal
                                text_kwargs["weight"] = "bold"
                                text_kwargs["style"] = "normal"
                            # normal 不需要设置任何参数

                        # 文本框（bbox）：优先使用 label_bbox，否则使用 bbox（向后兼容）
                        label_bbox = d_style.get("label_bbox")
                        if label_bbox:
                            # 构建 bbox 样式字典
                            bbox_style = {}
                            if label_bbox.get("boxstyle"):
                                bbox_style["boxstyle"] = label_bbox["boxstyle"]
                            if label_bbox.get("facecolor"):
                                bbox_style["facecolor"] = label_bbox["facecolor"]
                            # show_border 控制是否显示边框（默认为 True）
                            show_border = label_bbox.get("show_border", True)
                            if show_border:
                                # 只有在显示边框时才设置边框相关参数
                                if label_bbox.get("edgecolor"):
                                    bbox_style["edgecolor"] = label_bbox["edgecolor"]
                                linewidth = label_bbox.get("linewidth")
                                if linewidth is not None:
                                    bbox_style["linewidth"] = float(linewidth)
                            else:
                                # 不显示边框时，明确设置 linewidth 为 0 以隐藏边框
                                bbox_style["linewidth"] = 0
                            # 确保 alpha 不是 None
                            alpha = label_bbox.get("alpha")
                            if alpha is not None:
                                bbox_style["alpha"] = float(alpha)
                            if bbox_style:
                                text_kwargs["bbox"] = bbox_style
                        elif d_style.get("bbox"):
                            text_kwargs["bbox"] = d_style.get("bbox")

                        self.ax.text(**text_kwargs)
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

        # 只有在未隐藏 y 轴时才绘制 x=0 的参考线
        # 检查样式参数中是否隐藏了 y 轴
        hide_yaxis = d_style.get("hide_yaxis", False) or getattr(
            self.style, "_hide_yaxis", False
        )
        if not hide_yaxis:
            self.ax.axvline(0, color="black", linewidth=0.5)  # x轴为0的竖线

        self.ax.invert_yaxis()  # 翻转y轴，最上方显示排名靠前的序列

        # 在条形图整体外侧右边添加total值
        if show_total_label:
            total = df.sum(axis=1)
            # 使用 fmt_abs 格式化总计值（如果没有指定则使用默认格式）
            fmt_total = d_style.get("fmt_abs") or self.fmt
            # 获取 x 轴范围，用于计算标签位置
            xlim = self.ax.get_xlim()
            # 计算标签的 x 位置（在条形图外侧右边）
            # 使用 x 轴范围的 2% 作为边距
            margin = (
                abs(xlim[1] - xlim[0]) * 0.02
                if xlim and len(xlim) > 1
                else abs(max_v - min_v) * 0.02
            )

            for p, v in enumerate(total.values):
                # 构建总计值文本参数
                total_text_kwargs = {
                    "x": v + margin,  # x 坐标：总计值 + 边距（显示在右侧）
                    "y": p,  # y 坐标：对应条形的位置
                    "s": fmt_total.format(float(v)),
                    "ha": "left",  # 水平对齐：左对齐（因为标签在右侧）
                    "va": "center",  # 垂直对齐：居中
                    "zorder": 5,
                }

                # 使用公共函数应用文本样式（总计值使用 total_text 样式）
                _apply_text_style(
                    total_text_kwargs, d_style, "total_text", self.fontsize, "black"
                )

                self.ax.text(**total_text_kwargs)

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
