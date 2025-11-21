"""
Plot class for word cloud chart type.
"""

from __future__ import annotations
from typing import Any, Optional, Literal
import numpy as np
import os
import platform
from chart.plots.base import Plot
from wordcloud import WordCloud


class PlotWordcloud(Plot):
    """词云图绘制类

    使用 wordcloud 库绘制文字云，支持矩形和圆形两种形状。
    """

    def plot(
        self,
        col_freq: Optional[str] = None,
        mask_shape: Literal["rectangle", "circle"] = "rectangle",
        mask_width: int = 800,
        mask_height: int = 600,
        **kwargs: Any,
    ) -> PlotWordcloud:
        """继承基本类，绘制文字云图

        Args:
            col_freq (Optional[str]): 指定频次列，如不指定则默认为df的第一列.
            mask_shape (Literal["rectangle", "circle"], optional): 词云形状类别，默认为矩形. Defaults to "rectangle".
            mask_width (int, optional): 形状为矩形时的矩形宽度. Defaults to 800.
            mask_height (int, optional): 形状为矩形时的矩形高度. Defaults to 600.

        Returns:
            PlotWordcloud: 返回自身实例
        """

        # 使用基类方法获取列数据
        df = self._get_column(col_freq, 0)

        df.dropna(inplace=True)
        d_words = df.to_dict()

        # 自动检测中文字体路径（支持 Windows 和 Linux）
        font_path = self._get_chinese_font_path()

        if mask_shape == "circle":
            # 产生一个以(150,150)为圆心,半径为130的圆形mask
            x, y = np.ogrid[:600, :600]
            mask = (x - 300) ** 2 + (y - 300) ** 2 > 260**2
            mask = 255 * mask.astype(int)
            wordcloud = WordCloud(
                width=800,
                height=800,
                font_path=font_path,
                background_color="white",
                mask=mask,
            )
        elif mask_shape == "rectangle":
            wordcloud = WordCloud(
                width=mask_width,
                height=mask_height,
                font_path=font_path,
                background_color="white",
            )

        wordcloud.generate_from_frequencies(frequencies=d_words)

        self.ax.imshow(wordcloud, interpolation="bilinear")
        self.ax.axis("off")

        return self

    def _get_chinese_font_path(self) -> Optional[str]:
        """获取微软雅黑字体路径
        
        Returns:
            Optional[str]: 字体文件路径，如果找不到则返回 None
        """
        system = platform.system()
        
        # 微软雅黑字体路径（按优先级）
        font_paths = []
        
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",     # 微软雅黑 Bold
            ]
        elif system == "Linux":
            # Linux 中微软雅黑字体可能的位置（需要用户提供字体文件）
            font_paths = [
                "/usr/share/fonts/truetype/msyh/msyh.ttc",      # 自定义安装位置
                "/usr/share/fonts/msyh.ttc",                     # 直接放在 fonts 目录
                "/app/fonts/msyh.ttc",                           # 应用目录下的字体
                "/usr/local/share/fonts/msyh.ttc",               # 本地字体目录
            ]
        elif system == "Darwin":
            font_paths = [
                "/Library/Fonts/Microsoft/Microsoft YaHei.ttf",
                "/System/Library/Fonts/Supplemental/Microsoft YaHei.ttf",
            ]
        
        # 尝试查找微软雅黑字体
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        # Linux 下尝试通过 fontconfig 查找微软雅黑
        if system == "Linux":
            try:
                import subprocess
                # 查找 Microsoft YaHei 或 微软雅黑
                result = subprocess.run(
                    ["fc-match", "-f", "%{file}", "Microsoft YaHei"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip()
                    if os.path.exists(path) and "msyh" in path.lower():
                        return path
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass
        
        # 如果都找不到，返回 None（wordcloud 会使用默认字体）
        return None
