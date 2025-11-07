"""
Chart Module - 图表绘制核心模块

提供完整的图表绘制功能，包括：
- GridFigure: 主画布类
- 颜色管理和配置
- 各种类型的绘图类
"""

from chart.figure import GridFigure
from chart.color import COLOR_DICT, CMAP_QUAL, CMAP_NORM, is_color_dark

__all__ = [
    "GridFigure",
    "COLOR_DICT",
    "CMAP_QUAL",
    "CMAP_NORM",
    "is_color_dark",
]
