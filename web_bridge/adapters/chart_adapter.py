"""
MVP 版本的图表适配器
仅支持柱状图渲染
"""

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, Any

# 导入现有库（只读引用）
from chart import GridFigure


class WebChartAdapter:
    """Web 图表适配器 - MVP 版本"""

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


# 单例模式（可选优化）
_adapter_instance = None


def get_adapter() -> WebChartAdapter:
    """获取适配器实例"""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = WebChartAdapter()
    return _adapter_instance
