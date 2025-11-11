"""
Chart 颜色管理模块
包含颜色字典、颜色管理器等工具
"""

from .color import COLOR_DICT, COLOR_LIST, CMAP_QUAL, CMAP_NORM, Colors
from .color_manager import ColorManager, ColorMapping

__all__ = [
    "COLOR_DICT",
    "COLOR_LIST",
    "CMAP_QUAL",
    "CMAP_NORM",
    "Colors",
    "ColorManager",
    "ColorMapping",
]
