"""
Chart Class Library
===================

一个用于数据可视化的Python库，提供：
- 图表绘制功能 (chart 模块)
- 数据分析工具 (utils 模块)

快速开始：
----------
>>> from chart import GridFigure
>>> from utils import DfAnalyzer, PPT
>>> import matplotlib.pyplot as plt
>>>
>>> # 创建图表
>>> f = plt.figure(FigureClass=GridFigure, width=10, height=6)
>>> f.plot(kind='bar', data=df, ax_index=0)
>>> f.save()

模块说明：
----------
- chart: 图表绘制核心模块，包含 GridFigure 和各种绘图类
- utils: 工具模块，包含 DfAnalyzer（数据分析）和 PPT（PPT生成）
- data: 数据文件和模板文件存储
- example: 使用示例
- docs: 文档
"""

__version__ = "2.0.0"
__author__ = "Your Name"

# 便捷导入
from chart import GridFigure, COLOR_DICT, CMAP_QUAL, CMAP_NORM, is_color_dark
from utils import DfAnalyzer, DateRange, PPT, SlideContent, Section, Loc, AnchorLoc

__all__ = [
    # Chart module
    "GridFigure",
    "COLOR_DICT",
    "CMAP_QUAL",
    "CMAP_NORM",
    "is_color_dark",
    # Utils module
    "DfAnalyzer",
    "DateRange",
    "PPT",
    "SlideContent",
    "Section",
    "Loc",
    "AnchorLoc",
]
