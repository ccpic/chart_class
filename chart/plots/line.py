"""
Plot classes for line and area chart types.
"""

from __future__ import annotations
from typing import Any, List
import numpy as np
from chart.plots.base import Plot
from textalloc import allocate_text


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
                "adjust_labels_draw_lines": True,  # 是否绘制连接线
                "adjust_labels_linecolor": "black",  # 连接线颜色
                "adjust_labels_linewidth": 0.8,  # 连接线宽度
                "adjust_labels_max_distance": 0.1,  # 标签离数据点的最大距离
                "linewidth": 2,  # 线条粗细
                "linestyle": "-",  # 线条样式
                "marker": "o",  # 标记点样式
                "markersize": 5,  # 标记点大小
                "line_color": None,  # 线条颜色
                "label_fontsize": 11,  # 标签字体大小，默认11
                "label_color": "black",  # 标签颜色，默认黑色
                "label_weight": None,  # 标签字重：normal, bold, italic
                "label_bbox": None,  # 标签背景框配置
                "label_fmt": None,  # 标签数值格式，None则使用self.fmt
            },
            **kwargs,
        )

        lines = []
        texts = []
        # 保存每个文本对应的颜色信息，用于后续添加 bbox 样式
        text_colors = []
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
                    # 获取数值并转换为浮点数，处理可能的对象类型
                    try:
                        value = float(df.iloc[k, i])
                        if np.isnan(value) or np.isinf(value):
                            continue
                    except (ValueError, TypeError):
                        # 如果无法转换为数值，跳过这个标签
                        continue

                    # 确定 x 坐标：如果 idx 是数值类型则使用 idx，否则使用数值索引 k
                    # 这样可以避免 adjust_text 函数遇到对象类型时的类型转换错误
                    x_pos = (
                        idx
                        if isinstance(idx, (int, float, np.integer, np.floating))
                        else k
                    )

                    # 保存当前文本对应的颜色
                    text_colors.append(color)

                    # 使用指定的标签格式，如果没有则使用 self.fmt
                    label_fmt = d_style.get("label_fmt") or self.fmt
                    try:
                        formatted_value = label_fmt.format(value)
                    except (ValueError, KeyError):
                        # 如果格式化失败，使用默认格式
                        formatted_value = self.fmt.format(value)

                    # 构建标签文本参数
                    text_kwargs = {
                        "x": x_pos,
                        "y": value,
                        "s": formatted_value,
                        "va": "center",
                        "zorder": (
                            100
                            if self.focus is not None and column in self.focus
                            else 10
                        ),
                    }

                    # 字体大小
                    if d_style.get("label_fontsize"):
                        text_kwargs["size"] = d_style.get("label_fontsize")
                    else:
                        text_kwargs["size"] = 11

                    # 标签颜色：优先使用 label_color，否则使用白色
                    label_color = d_style.get("label_color")
                    if label_color:
                        text_kwargs["color"] = label_color
                    else:
                        text_kwargs["color"] = "white"

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
                    # 如果 label_weight 为 None 或 "normal"，不设置这些参数

                    # 对齐方式
                    if endpoint_label_only:
                        text_kwargs["ha"] = "right" if k == 0 else "left"
                    else:
                        text_kwargs["ha"] = "center"

                    # 创建文本时不添加 bbox，等 adjust_labels 处理后再添加
                    if endpoint_label_only:
                        if k == 0 or k == len(df.index) - 1:
                            texts.append(self.ax.text(**text_kwargs))
                    else:
                        texts.append(self.ax.text(**text_kwargs))

        # 优化标签位置
        if d_style.get("adjust_labels") is True and texts:
            try:
                # 提取文本位置和内容
                x_data = [t.get_position()[0] for t in texts]
                y_data = [t.get_position()[1] for t in texts]
                text_list = [t.get_text() for t in texts]

                # 记录调用前的文本对象集合
                texts_before = set(self.ax.texts)

                # 移除原始文本对象
                for t in texts:
                    t.remove()

                # 使用 textalloc 重新分配位置
                allocate_text(
                    self.ax.figure,
                    self.ax,
                    x_data,
                    y_data,
                    text_list,
                    x_scatter=x_data,
                    y_scatter=y_data,
                    textsize=self.fontsize,
                    linecolor=d_style.get("adjust_labels_linecolor", "black"),
                    draw_lines=d_style.get("adjust_labels_draw_lines", True),
                    linewidth=d_style.get("adjust_labels_linewidth", 0.8),
                    max_distance=d_style.get("adjust_labels_max_distance", 0.1),
                )

                # 找到新创建的文本对象
                texts_after = set(self.ax.texts)
                new_texts = list(texts_after - texts_before)

                # 按照 text_list 的顺序匹配新文本对象（textalloc 会按照输入顺序创建文本）
                # 为新文本对象添加 bbox 样式和文本颜色
                label_bbox = d_style.get("label_bbox")
                label_color = d_style.get("label_color")

                for idx, new_text in enumerate(new_texts):
                    if idx < len(text_colors):
                        color = text_colors[idx]

                        # 应用 label_bbox 配置（仅在启用时）
                        if label_bbox and label_bbox.get("enabled"):
                            bbox_style = {}
                            if label_bbox.get("boxstyle"):
                                bbox_style["boxstyle"] = label_bbox["boxstyle"]
                            if label_bbox.get("facecolor"):
                                bbox_style["facecolor"] = label_bbox["facecolor"]
                            else:
                                # 如果没有指定 facecolor，使用系列颜色
                                bbox_style["facecolor"] = color

                            # show_border 控制是否显示边框（默认为 True）
                            show_border = label_bbox.get("show_border", True)
                            if show_border:
                                # 只有在显示边框时才设置边框相关参数
                                if label_bbox.get("edgecolor"):
                                    bbox_style["edgecolor"] = label_bbox["edgecolor"]
                                else:
                                    # 如果没有指定 edgecolor，使用系列颜色
                                    bbox_style["edgecolor"] = color
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
                            else:
                                bbox_style["alpha"] = 0.7

                            new_text.set_bbox(bbox_style)

                        # 设置文本颜色：优先使用 label_color，否则使用黑色
                        if label_color:
                            new_text.set_color(label_color)
                        else:
                            new_text.set_color("black")

                        # 应用字体样式
                        label_weight = d_style.get("label_weight")
                        if label_weight:
                            if label_weight == "italic":
                                new_text.set_style("italic")
                                new_text.set_weight("normal")
                            elif label_weight == "bold":
                                new_text.set_weight("bold")
                                new_text.set_style("normal")
            except (IndexError, ValueError, TypeError, AttributeError) as e:
                # 如果标签位置调整失败，不影响图表显示，只记录错误
                import warnings

                warnings.warn(f"标签位置调整失败: {e}", UserWarning)
        else:
            # 如果未启用 adjust_labels，直接为文本添加 bbox 样式
            # 按照 text_colors 的顺序为文本添加 bbox
            label_bbox = d_style.get("label_bbox")
            label_color = d_style.get("label_color")

            for idx, text in enumerate(texts):
                if idx < len(text_colors):
                    color = text_colors[idx]

                    # 应用 label_bbox 配置（仅在启用时）
                    if label_bbox and label_bbox.get("enabled"):
                        bbox_style = {}
                        if label_bbox.get("boxstyle"):
                            bbox_style["boxstyle"] = label_bbox["boxstyle"]
                        if label_bbox.get("facecolor"):
                            bbox_style["facecolor"] = label_bbox["facecolor"]
                        else:
                            # 如果没有指定 facecolor，使用系列颜色
                            bbox_style["facecolor"] = color

                        # show_border 控制是否显示边框（默认为 True）
                        show_border = label_bbox.get("show_border", True)
                        if show_border:
                            # 只有在显示边框时才设置边框相关参数
                            if label_bbox.get("edgecolor"):
                                bbox_style["edgecolor"] = label_bbox["edgecolor"]
                            else:
                                # 如果没有指定 edgecolor，使用系列颜色
                                bbox_style["edgecolor"] = color
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
                        else:
                            bbox_style["alpha"] = 0.7

                        text.set_bbox(bbox_style)

                    # 设置文本颜色：优先使用 label_color，否则使用黑色
                    if label_color:
                        text.set_color(label_color)
                    else:
                        text.set_color("black")

                    # 应用字体样式
                    label_weight = d_style.get("label_weight")
                    if label_weight:
                        if label_weight == "italic":
                            text.set_style("italic")
                            text.set_weight("normal")
                        elif label_weight == "bold":
                            text.set_weight("bold")
                            text.set_style("normal")

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
                "adjust_labels": True,
                "adjust_labels_draw_lines": True,  # 是否绘制连接线
                "adjust_labels_linecolor": "black",  # 连接线颜色
                "adjust_labels_linewidth": 0.8,  # 连接线宽度
                "adjust_labels_max_distance": 0.1,  # 标签离数据点的最大距离
                "linewidth": 2,
                "alpha": 1,
                "label_fontsize": self.fontsize,  # 标签字体大小
                "label_color": None,  # 标签颜色
                "label_weight": None,  # 标签字重：normal, bold, italic
                "label_bbox": None,  # 标签背景框配置
            },
            **kwargs,
        )

        texts = []
        # 保存每个文本对应的颜色信息，用于后续添加 bbox 样式
        text_colors = []

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
                    # 获取数值并转换为浮点数，处理可能的对象类型
                    try:
                        value = float(df.iloc[k, i])
                        if np.isnan(value) or np.isinf(value):
                            continue
                    except (ValueError, TypeError):
                        # 如果无法转换为数值，跳过这个标签
                        continue

                    if stacked is True:
                        # 如果堆积，标签要挪到面积图中间
                        try:
                            # 确保求和操作返回数值类型
                            sum_before = float(df.iloc[k, :i].sum())
                            sum_after = float(df.iloc[k, : i + 1].sum())
                            position_y = (sum_before + sum_after) / 2
                        except (ValueError, TypeError):
                            position_y = value
                    else:
                        position_y = value

                    # 确定 x 坐标：如果 idx 是数值类型则使用 idx，否则使用数值索引 k
                    x_pos = (
                        idx
                        if isinstance(idx, (int, float, np.integer, np.floating))
                        else k
                    )

                    # 保存当前文本对应的颜色
                    text_colors.append(color)

                    # 构建标签文本参数
                    text_kwargs = {
                        "x": x_pos,
                        "y": position_y,
                        "s": self.fmt.format(value),
                        "va": "center",
                        "zorder": 10,
                    }

                    # 字体大小
                    if d_style.get("label_fontsize"):
                        text_kwargs["size"] = d_style.get("label_fontsize")
                    else:
                        text_kwargs["size"] = 11

                    # 标签颜色：优先使用 label_color，否则使用白色
                    label_color = d_style.get("label_color")
                    if label_color:
                        text_kwargs["color"] = label_color
                    else:
                        text_kwargs["color"] = "white"

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

                    # 对齐方式
                    text_kwargs["ha"] = "center"

                    # 创建文本时不添加 bbox，等 adjust_labels 处理后再添加
                    if endpoint_label_only:
                        if k == 0 or k == len(df.index) - 1:
                            texts.append(self.ax.text(**text_kwargs))
                    else:
                        texts.append(self.ax.text(**text_kwargs))

        # 优化标签位置
        if d_style.get("adjust_labels") is True and texts:
            try:
                # 提取文本位置和内容
                x_data = [t.get_position()[0] for t in texts]
                y_data = [t.get_position()[1] for t in texts]
                text_list = [t.get_text() for t in texts]

                # 记录调用前的文本对象集合
                texts_before = set(self.ax.texts)

                # 移除原始文本对象
                for t in texts:
                    t.remove()

                # 使用 textalloc 重新分配位置
                allocate_text(
                    self.ax.figure,
                    self.ax,
                    x_data,
                    y_data,
                    text_list,
                    x_scatter=x_data,
                    y_scatter=y_data,
                    textsize=self.fontsize,
                    linecolor=d_style.get("adjust_labels_linecolor", "black"),
                    draw_lines=d_style.get("adjust_labels_draw_lines", True),
                    linewidth=d_style.get("adjust_labels_linewidth", 0.8),
                    max_distance=d_style.get("adjust_labels_max_distance", 0.1),
                )

                # 找到新创建的文本对象
                texts_after = set(self.ax.texts)
                new_texts = list(texts_after - texts_before)

                # 按照 text_list 的顺序匹配新文本对象（textalloc 会按照输入顺序创建文本）
                # 为新文本对象添加 bbox 样式和文本颜色
                label_bbox = d_style.get("label_bbox")
                label_color = d_style.get("label_color")

                for idx, new_text in enumerate(new_texts):
                    if idx < len(text_colors):
                        color = text_colors[idx]

                        # 应用 label_bbox 配置（如果启用）
                        if label_bbox and label_bbox.get("enabled"):
                            bbox_style = {}
                            if label_bbox.get("boxstyle"):
                                bbox_style["boxstyle"] = label_bbox["boxstyle"]
                            if label_bbox.get("facecolor"):
                                bbox_style["facecolor"] = label_bbox["facecolor"]
                            else:
                                # 如果没有指定 facecolor，使用系列颜色
                                bbox_style["facecolor"] = color

                            # show_border 控制是否显示边框（默认为 True）
                            show_border = label_bbox.get("show_border", True)
                            if show_border:
                                # 只有在显示边框时才设置边框相关参数
                                if label_bbox.get("edgecolor"):
                                    bbox_style["edgecolor"] = label_bbox["edgecolor"]
                                else:
                                    # 如果没有指定 edgecolor，使用系列颜色
                                    bbox_style["edgecolor"] = color
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
                            else:
                                bbox_style["alpha"] = 0.7

                            new_text.set_bbox(bbox_style)
                        else:
                            # 如果没有启用 label_bbox，使用默认样式（向后兼容）
                            new_text.set_bbox(
                                dict(facecolor=color, alpha=0.7, edgecolor=color)
                            )

                        # 设置文本颜色：优先使用 label_color，否则使用黑色
                        if label_color:
                            new_text.set_color(label_color)
                        else:
                            new_text.set_color("black")

                        # 应用字体样式
                        label_weight = d_style.get("label_weight")
                        if label_weight:
                            if label_weight == "italic":
                                new_text.set_style("italic")
                                new_text.set_weight("normal")
                            elif label_weight == "bold":
                                new_text.set_weight("bold")
                                new_text.set_style("normal")
            except (IndexError, ValueError, TypeError, AttributeError) as e:
                # 如果标签位置调整失败，不影响图表显示，只记录错误
                import warnings

                warnings.warn(f"标签位置调整失败: {e}", UserWarning)
        else:
            # 如果未启用 adjust_labels，直接为文本添加 bbox 样式
            # 按照 text_colors 的顺序为文本添加 bbox
            label_bbox = d_style.get("label_bbox")
            label_color = d_style.get("label_color")

            for idx, text in enumerate(texts):
                if idx < len(text_colors):
                    color = text_colors[idx]

                    # 应用 label_bbox 配置（仅在启用时）
                    if label_bbox and label_bbox.get("enabled"):
                        bbox_style = {}
                        if label_bbox.get("boxstyle"):
                            bbox_style["boxstyle"] = label_bbox["boxstyle"]
                        if label_bbox.get("facecolor"):
                            bbox_style["facecolor"] = label_bbox["facecolor"]
                        else:
                            # 如果没有指定 facecolor，使用系列颜色
                            bbox_style["facecolor"] = color

                        # show_border 控制是否显示边框（默认为 True）
                        show_border = label_bbox.get("show_border", True)
                        if show_border:
                            # 只有在显示边框时才设置边框相关参数
                            if label_bbox.get("edgecolor"):
                                bbox_style["edgecolor"] = label_bbox["edgecolor"]
                            else:
                                # 如果没有指定 edgecolor，使用系列颜色
                                bbox_style["edgecolor"] = color
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
                        else:
                            bbox_style["alpha"] = 0.7

                        text.set_bbox(bbox_style)

                    # 设置文本颜色：优先使用 label_color，否则使用黑色
                    if label_color:
                        text.set_color(label_color)
                    else:
                        text.set_color("black")

                    # 应用字体样式
                    label_weight = d_style.get("label_weight")
                    if label_weight:
                        if label_weight == "italic":
                            text.set_style("italic")
                            text.set_weight("normal")
                        elif label_weight == "bold":
                            text.set_weight("bold")
                            text.set_style("normal")

        # 使用基类方法格式化y轴
        self._format_axis("y")

        return self
