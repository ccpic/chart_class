"""
Utils Module - 工具模块

提供数据分析和PPT生成等辅助功能：
- DfAnalyzer: DataFrame分析工具
- PPT: PowerPoint生成工具
"""

from utils.dataframe import DfAnalyzer, DateRange

# PPT 功能可选导入（需要 python-pptx 包）
try:
    from utils.ppt import PPT, SlideContent, Section, Loc, AnchorLoc

    _has_ppt = True
except ImportError:
    _has_ppt = False
    PPT = SlideContent = Section = Loc = AnchorLoc = None

__all__ = [
    "DfAnalyzer",
    "DateRange",
]

if _has_ppt:
    __all__.extend(
        [
            "PPT",
            "SlideContent",
            "Section",
            "Loc",
            "AnchorLoc",
        ]
    )
