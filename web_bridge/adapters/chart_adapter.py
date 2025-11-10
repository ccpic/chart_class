"""
Web 图表适配器
支持单图渲染和多子图画布渲染
"""

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, Any, List

# 导入现有库（只读引用）
from chart import GridFigure


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

            # 2. 创建 GridFigure
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
            )

            # 3. 按 ax_index 排序子图，确保顺序正确
            sorted_subplots = sorted(subplots, key=lambda x: x["ax_index"])

            # 4. 循环渲染每个子图
            for subplot in sorted_subplots:
                try:
                    # 转换数据为 DataFrame
                    data_dict = subplot["data"]
                    df = pd.DataFrame(
                        data=data_dict["data"], columns=data_dict["columns"]
                    )
                    if data_dict.get("index"):
                        df.index = data_dict["index"]

                    # 获取图表类型和参数
                    chart_type = subplot["chart_type"]
                    params = subplot["params"].copy()
                    ax_index = subplot["ax_index"]

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
        return ["bar", "line", "pie", "area", "scatter", "bubble"]

    def get_default_params(self, chart_type: str) -> Dict[str, Any]:
        """
        返回指定图表类型的默认参数

        用于前端表单初始化
        """
        defaults = {
            "bar": {"stacked": True, "show_label": True, "label_formatter": "{abs}"},
            "line": {"marker": "o", "show_label": False, "linewidth": 2},
            "pie": {"show_label": True, "autopct": "%1.1f%%"},
            "area": {"stacked": True, "alpha": 0.7},
            "scatter": {"marker": "o", "size": 50},
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
