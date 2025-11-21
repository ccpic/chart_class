"""
Web 图表适配器
支持单图渲染和多子图画布渲染
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, Any, List

# 导入现有库（只读引用）
from chart import GridFigure

# 导入颜色管理器
try:
    from chart.color.color_manager import ColorManager
    _color_manager = ColorManager()
    _USE_COLOR_MANAGER = True
except ImportError:
    _color_manager = None
    _USE_COLOR_MANAGER = False


class WebChartAdapter:
    """Web 图表适配器 - 支持单图和多子图渲染"""

    def render_canvas(
        self, canvas_config: Dict[str, Any], subplots: List[Dict[str, Any]]
    ) -> bytes:
        """
        渲染多子图画布

        Args:
            canvas_config: 画布配置 {width, height, rows, cols, title, ytitle, show_legend, label_outer, ...}
            subplots: 子图列表 [{subplot_id, ax_index, chart_type, data, params}, ...]

        Returns:
            PNG 图片字节
        """
        try:
            # 1. 构建画布样式字典
            style = {
                "title": canvas_config.get("title"),
                "title_fontsize": canvas_config.get("title_fontsize"),
                "ytitle": canvas_config.get("ytitle"),
                "ytitle_fontsize": canvas_config.get("ytitle_fontsize"),
                "show_legend": canvas_config.get("show_legend", False),
                "legend_loc": canvas_config.get("legend_loc", "center left"),
                "legend_ncol": canvas_config.get("legend_ncol", 1),
                "bbox_to_anchor": canvas_config.get("bbox_to_anchor", (1, 0.5)),
                "label_outer": canvas_config.get("label_outer", False),
            }

            # 移除 None 值和空字符串，避免传递无效参数
            style = {k: v for k, v in style.items() if v is not None and v != ""}

            # 2. 从 ColorManager 加载最新的颜色字典
            if _USE_COLOR_MANAGER and _color_manager:
                # 获取所有颜色映射，优先使用 named_color（如果存在），否则使用 color（HEX）
                color_dict = {}
                for name, mapping in _color_manager._colors.items():
                    # 优先使用 named_color（matplotlib 命名颜色），否则使用 color（HEX）
                    color_dict[name] = mapping.named_color if mapping.named_color else mapping.color
            else:
                # 如果 ColorManager 不可用，使用默认颜色字典
                from chart.color.color import COLOR_DICT
                color_dict = COLOR_DICT

            # 3. 创建 GridFigure
            f = plt.figure(
                FigureClass=GridFigure,
                width=canvas_config.get("width", 15),
                height=canvas_config.get("height", 6),
                nrows=canvas_config.get("rows", 1),
                ncols=canvas_config.get("cols", 1),
                wspace=canvas_config.get("wspace", 0.1),
                hspace=canvas_config.get("hspace", 0.1),
                width_ratios=canvas_config.get("width_ratios"),
                height_ratios=canvas_config.get("height_ratios"),
                fontsize=canvas_config.get("fontsize", 14),
                style=style,
                color_dict=color_dict,  # 传递颜色字典
            )

            # 4. 按 ax_index 排序子图，确保顺序正确
            sorted_subplots = sorted(subplots, key=lambda x: x["ax_index"])

            # 5. 循环渲染每个子图
            for subplot in sorted_subplots:
                try:
                    # 转换数据为 DataFrame
                    data_dict = subplot["data"]
                    df = pd.DataFrame(
                        data=data_dict["data"], columns=data_dict["columns"]
                    )

                    # 将空字符串转换为 np.nan
                    df = df.replace("", np.nan)

                    if data_dict.get("index"):
                        df.index = data_dict["index"]
                        # 设置索引名称（如果提供）
                        if data_dict.get("index_name"):
                            df.index.name = data_dict["index_name"]
                        elif not df.index.name:
                            # 如果没有提供索引名称，设置默认值
                            df.index.name = "index"

                    # 获取图表类型和参数
                    chart_type = subplot["chart_type"]
                    params = subplot["params"].copy()

                    # 统一处理 whis 参数（用于箱型图等）
                    if "whis" in params:
                        whis_value = params["whis"]
                        if isinstance(whis_value, str):
                            if whis_value.lower() == "inf" or whis_value == "∞":
                                params["whis"] = np.inf
                            else:
                                try:
                                    params["whis"] = float(whis_value)
                                except ValueError:
                                    params.pop("whis", None)
                        elif whis_value is None:
                            params.pop("whis", None)
                    ax_index = subplot["ax_index"]

                    # 特殊处理：table 类型需要转换 col_defs
                    if chart_type == "table" and "col_defs" in params:
                        from plottable import ColumnDefinition
                        from plottable.plots import bar, percentile_bars, progress_donut
                        from chart.plots.utils import normed_cmap, format_value
                        from functools import partial
                        import matplotlib.cm as mpl_cm

                        # plot_fn 字符串到函数的映射
                        plot_fn_map = {
                            "bar": bar,
                            "percentile_bars": percentile_bars,
                            "progress_donut": progress_donut,
                        }

                        col_defs_data = params["col_defs"]
                        if col_defs_data and isinstance(col_defs_data, list):
                            # 转换前端的字典列表为 ColumnDefinition 对象列表
                            col_defs_objects = []
                            for col_def in col_defs_data:
                                # 过滤掉 undefined 或 None 的值
                                clean_def = {
                                    k: v
                                    for k, v in col_def.items()
                                    if v is not None and v != ""
                                }

                                # 处理 formatter_config：转换为 partial(format_value, ...)
                                col_formatter = None  # 保存列定义的 formatter，供 plot_kw 使用
                                if "formatter_config" in clean_def:
                                    fmt_cfg = clean_def.pop("formatter_config")
                                    fmt = fmt_cfg.get("fmt", "{:,.0f}")
                                    unit = fmt_cfg.get(
                                        "unit"
                                    )  # None 或 "亿"/"百万"/"万"/"千"
                                    empty_zero = fmt_cfg.get("empty_zero", True)
                                    empty_nan = fmt_cfg.get("empty_nan", True)

                                    col_formatter = partial(
                                        format_value,
                                        fmt=fmt,
                                        unit=unit,
                                        empty_zero=empty_zero,
                                        empty_nan=empty_nan,
                                    )
                                    clean_def["formatter"] = col_formatter
                                # 向后兼容：如果只有 formatter 字符串，也转换为 format_value
                                elif "formatter" in clean_def and isinstance(
                                    clean_def["formatter"], str
                                ):
                                    fmt_str = clean_def["formatter"]
                                    col_formatter = partial(
                                        format_value,
                                        fmt=fmt_str,
                                        empty_zero=True,
                                        empty_nan=True,
                                    )
                                    clean_def["formatter"] = col_formatter

                                # 转换 plot_fn 字符串为实际函数
                                if "plot_fn" in clean_def and isinstance(
                                    clean_def["plot_fn"], str
                                ):
                                    plot_fn_str = clean_def["plot_fn"]
                                    if plot_fn_str in plot_fn_map:
                                        clean_def["plot_fn"] = plot_fn_map[plot_fn_str]
                                    else:
                                        # 如果不支持的类型，移除该字段
                                        clean_def.pop("plot_fn", None)

                                # 处理 plot_kw.formatter：优先使用列定义的 formatter_config
                                if "plot_kw" in clean_def and isinstance(
                                    clean_def["plot_kw"], dict
                                ):
                                    plot_kw = clean_def["plot_kw"]
                                    if "formatter" in plot_kw:
                                        # 如果列定义有 formatter_config，使用它的配置（包括 unit）
                                        if col_formatter is not None:
                                            plot_kw["formatter"] = col_formatter
                                        # 否则，如果 plot_kw.formatter 是字符串，转换为 format_value
                                        elif isinstance(plot_kw["formatter"], str):
                                            fmt_str = plot_kw["formatter"]
                                            plot_kw["formatter"] = partial(
                                                format_value,
                                                fmt=fmt_str,
                                                empty_zero=True,
                                                empty_nan=True,
                                            )

                                # 处理 cmap_config：支持数值映射和分类映射
                                if "cmap_config" in clean_def:
                                    cmap_cfg = clean_def.pop("cmap_config")
                                    col_name = clean_def.get("name")

                                    # 检查映射模式
                                    mode = cmap_cfg.get("mode", "numeric")

                                    if mode == "numeric" and "numeric" in cmap_cfg:
                                        # 数值映射：调用 normed_cmap
                                        if col_name and col_name in df.columns:
                                            series = df[col_name]
                                            numeric_cfg = cmap_cfg["numeric"]
                                            cmap_name = numeric_cfg.get("cmap", "PiYG")
                                            num_stds = numeric_cfg.get("num_stds", 2.5)
                                            vmin = numeric_cfg.get("vmin")
                                            vmax = numeric_cfg.get("vmax")

                                            try:
                                                cmap = mpl_cm.get_cmap(cmap_name)
                                                clean_def["cmap"] = normed_cmap(
                                                    series,
                                                    cmap,
                                                    num_stds=num_stds,
                                                    vmin=vmin,
                                                    vmax=vmax,
                                                )
                                            except Exception as e:
                                                print(
                                                    f"警告: 生成 cmap (数值映射) 失败: {e}"
                                                )

                                    elif (
                                        mode == "categorical"
                                        and "categorical" in cmap_cfg
                                    ):
                                        # 分类映射：创建字典映射函数
                                        color_map = cmap_cfg["categorical"]
                                        default_color = "#808080"  # 灰色作为默认
                                        clean_def["cmap"] = lambda x: color_map.get(
                                            str(x), default_color
                                        )

                                    # 向后兼容旧格式（直接包含 cmap 字段）
                                    elif "cmap" in cmap_cfg:
                                        if col_name and col_name in df.columns:
                                            series = df[col_name]
                                            cmap_name = cmap_cfg.get("cmap", "PiYG")
                                            num_stds = cmap_cfg.get("num_stds", 2.5)
                                            vmin = cmap_cfg.get("vmin")
                                            vmax = cmap_cfg.get("vmax")

                                            try:
                                                cmap = mpl_cm.get_cmap(cmap_name)
                                                clean_def["cmap"] = normed_cmap(
                                                    series,
                                                    cmap,
                                                    num_stds=num_stds,
                                                    vmin=vmin,
                                                    vmax=vmax,
                                                )
                                            except Exception as e:
                                                print(
                                                    f"警告: 生成 cmap (向后兼容) 失败: {e}"
                                                )

                                # 处理 text_cmap_config：支持数值映射和分类映射
                                if "text_cmap_config" in clean_def:
                                    text_cmap_cfg = clean_def.pop("text_cmap_config")
                                    col_name = clean_def.get("name")

                                    # 检查映射模式
                                    mode = text_cmap_cfg.get("mode", "numeric")

                                    if mode == "numeric" and "numeric" in text_cmap_cfg:
                                        # 数值映射：调用 normed_cmap
                                        if col_name and col_name in df.columns:
                                            series = df[col_name]
                                            numeric_cfg = text_cmap_cfg["numeric"]
                                            cmap_name = numeric_cfg.get(
                                                "cmap", "RdYlGn"
                                            )
                                            num_stds = numeric_cfg.get("num_stds", 2.5)
                                            vmin = numeric_cfg.get("vmin")
                                            vmax = numeric_cfg.get("vmax")

                                            try:
                                                cmap = mpl_cm.get_cmap(cmap_name)
                                                clean_def["text_cmap"] = normed_cmap(
                                                    series,
                                                    cmap,
                                                    num_stds=num_stds,
                                                    vmin=vmin,
                                                    vmax=vmax,
                                                )
                                            except Exception as e:
                                                print(
                                                    f"警告: 生成 text_cmap (数值映射) 失败: {e}"
                                                )

                                    elif (
                                        mode == "categorical"
                                        and "categorical" in text_cmap_cfg
                                    ):
                                        # 分类映射：创建字典映射函数
                                        color_map = text_cmap_cfg["categorical"]
                                        default_color = "#000000"  # 黑色作为默认
                                        clean_def["text_cmap"] = (
                                            lambda x: color_map.get(
                                                str(x), default_color
                                            )
                                        )

                                    elif mode == "negative_red":
                                        # 负值标红：负数值显示红色，非负数值显示默认颜色
                                        # 注意：分类映射返回十六进制字符串，数值映射返回 rgba 元组
                                        # 为了与分类映射保持一致，我们也返回十六进制字符串
                                        def negative_red_mapper(x):
                                            try:
                                                # 处理各种可能的输入类型
                                                if isinstance(x, (int, float, np.number)):
                                                    val = float(x)
                                                elif isinstance(x, str):
                                                    # 如果是字符串，尝试解析（去除千位符、空格、百分号等）
                                                    cleaned = x.replace(',', '').replace(' ', '').replace('%', '').strip()
                                                    if not cleaned:
                                                        return "#000000"  # 黑色
                                                    val = float(cleaned)
                                                else:
                                                    # 其他类型，尝试直接转换
                                                    val = float(x)
                                                
                                                if val < 0:
                                                    return "#FF0000"  # 红色
                                                else:
                                                    return "#000000"  # 黑色（默认）
                                            except (ValueError, TypeError):
                                                # 如果无法转换为数值，返回默认颜色
                                                return "#000000"  # 黑色
                                        
                                        clean_def["text_cmap"] = negative_red_mapper

                                    # 向后兼容旧格式
                                    elif "cmap" in text_cmap_cfg:
                                        if col_name and col_name in df.columns:
                                            series = df[col_name]
                                            cmap_name = text_cmap_cfg.get(
                                                "cmap", "RdYlGn"
                                            )
                                            num_stds = text_cmap_cfg.get(
                                                "num_stds", 2.5
                                            )
                                            vmin = text_cmap_cfg.get("vmin")
                                            vmax = text_cmap_cfg.get("vmax")

                                            try:
                                                cmap = mpl_cm.get_cmap(cmap_name)
                                                clean_def["text_cmap"] = normed_cmap(
                                                    series,
                                                    cmap,
                                                    num_stds=num_stds,
                                                    vmin=vmin,
                                                    vmax=vmax,
                                                )
                                            except Exception as e:
                                                print(
                                                    f"警告: 生成 text_cmap (向后兼容) 失败: {e}"
                                                )

                                # 处理 textprops.bbox：将 boxstyle 和 pad 组合成 matplotlib 格式
                                if "textprops" in clean_def and isinstance(
                                    clean_def["textprops"], dict
                                ):
                                    textprops = clean_def["textprops"]
                                    if "bbox" in textprops and isinstance(
                                        textprops["bbox"], dict
                                    ):
                                        bbox = textprops["bbox"]

                                        # 过滤掉 None 值（facecolor 和 edgecolor 可选）
                                        bbox = {
                                            k: v
                                            for k, v in bbox.items()
                                            if v is not None
                                        }
                                        textprops["bbox"] = bbox

                                        # 如果同时存在 boxstyle 和 pad，组合成 "boxstyle,pad=value" 格式
                                        if "boxstyle" in bbox and "pad" in bbox:
                                            boxstyle = bbox["boxstyle"]
                                            pad = bbox["pad"]
                                            bbox["boxstyle"] = f"{boxstyle},pad={pad}"
                                            # 移除单独的 pad 字段（matplotlib 不接受）
                                            bbox.pop("pad", None)

                                # 确保必需的 name 字段存在
                                if "name" in clean_def:
                                    col_defs_objects.append(
                                        ColumnDefinition(**clean_def)
                                    )

                            params["col_defs"] = (
                                col_defs_objects if col_defs_objects else None
                            )

                    # 调用 f.plot() 绘制子图
                    f.plot(kind=chart_type, data=df, ax_index=ax_index, **params)

                except Exception as e:
                    # 错误处理：在对应位置显示错误信息
                    print(f"子图 {subplot['subplot_id']} 渲染失败: {str(e)}")
                    # 在图表上显示错误文本
                    if ax_index < len(f.axes):
                        ax = f.axes[ax_index]
                        ax.text(
                            0.5,
                            0.5,
                            f"渲染错误\n{str(e)}",
                            ha="center",
                            va="center",
                            color="red",
                            transform=ax.transAxes,
                        )

            # 5. 应用样式（必须在保存前调用）
            f.style.apply_style()

            # 6. 保存为 PNG（使用配置的 DPI 和透明度）
            dpi = canvas_config.get("dpi", 400)
            transparent = canvas_config.get("transparent", True)

            buf = BytesIO()
            f.savefig(
                buf, format="png", dpi=dpi, bbox_inches="tight", transparent=transparent
            )
            buf.seek(0)
            image_bytes = buf.read()
            buf.close()
            plt.close(f)

            return image_bytes

        except Exception as e:
            plt.close("all")
            raise ValueError(f"画布渲染失败: {str(e)}")

    def render_bar_chart(
        self, data_json: Dict[str, Any], params: Dict[str, Any]
    ) -> bytes:
        """
        渲染柱状图

        Args:
            data_json: {
                "columns": ["品牌A", "品牌B"],
                "index": ["2024-01", "2024-02"],
                "data": [[1000, 800], [1200, 900]]
            }
            params: {
                "stacked": True,
                "show_label": True,
                "label_formatter": "{abs}"  # MVP 固定值
            }

        Returns:
            PNG 图片的字节流
        """
        try:
            # 1. 转换为 DataFrame
            df = self._json_to_dataframe(data_json)

            # 2. 创建画布（固定 1x1）
            f = plt.figure(FigureClass=GridFigure, width=10, height=6)

            # 3. 调用原生 plot 方法
            f.plot(
                kind="bar",
                data=df,
                ax_index=0,
                stacked=params.get("stacked", True),
                show_label=params.get("show_label", True),
                label_formatter=params.get("label_formatter", "{abs}"),
            )

            # 4. 保存为字节流
            buf = BytesIO()
            f.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            plt.close(f)

            return buf.getvalue()

        except Exception as e:
            # 简单错误处理
            plt.close("all")
            raise ValueError(f"图表渲染失败: {str(e)}")

    def _json_to_dataframe(self, data_json: Dict[str, Any]) -> pd.DataFrame:
        """JSON 转 DataFrame"""
        df = pd.DataFrame(data_json["data"], columns=data_json["columns"])

        if "index" in data_json:
            df.index = data_json["index"]

        return df

    def get_supported_chart_types(self) -> List[str]:
        """返回支持的图表类型列表"""
        return ["bar", "line", "pie", "area", "bubble", "table", "hist", "boxdot"]

    def get_default_params(self, chart_type: str) -> Dict[str, Any]:
        """
        返回指定图表类型的默认参数

        用于前端表单初始化
        """
        defaults = {
            "bar": {"stacked": True, "show_label": True, "label_formatter": "{abs}"},
            "line": {
                "marker": "o",
                "show_label": [],
                "linewidth": 2,
                "endpoint_label_only": False,
                "adjust_labels": True,
            },
            "pie": {
                "size": None,
                "label_formatter": "{abs}",
                "donut": False,
                "donut_title": None,
                "pct_distance": 0.8,
                "start_angle": 90,
                "counter_clock": False,
                "line_width": 1,
                "edgecolor": "white",
                "label_fontsize": None,  # 使用全局字体大小
                "circle_distance": 0.7,
                "fmt_abs": None,
                "fmt_share": None,
            },
            "area": {
                "stacked": True,
                "alpha": 1,
                "show_label": [],
                "endpoint_label_only": False,
                "linewidth": 2,
            },
            "bubble": {
                "alpha": 0.6,
                "bubble_scale": 1,
                "edgecolor": "black",
                "random_color": False,
                "show_reg": False,
                "show_hist": False,
                "corr": None,
                "label_limit": 0,
                "label_formatter": "{index}",
                "x_avg": None,
                "y_avg": None,
                "avg_linestyle": "--",
                "avg_linewidth": 1,
                "avg_color": "gray",
            },
            "table": {
                "col_defs": [],
                "row_dividers": True,
                "footer_divider": True,
                "fontsize": 10,
            },
            "hist": {
                "bins": 10,
                "tiles": 10,
                "show_kde": True,
                "show_metrics": True,
                "show_tiles": False,
                "color_hist": "grey",
                "color_kde": "darkorange",
                "color_mean": "purple",
                "color_median": "crimson",
            },
            "boxdot": {
                "x": None,
                "y": None,
                "label_limit": 0,
                "label_threshold": 0,
                "show_stats": True,
                "order": None,
            },
        }
        return defaults.get(chart_type, {})


# 单例模式（可选优化）
_adapter_instance = None


def get_adapter() -> WebChartAdapter:
    """获取适配器实例"""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = WebChartAdapter()
    return _adapter_instance
