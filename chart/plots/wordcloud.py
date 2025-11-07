"""
Plot class for word cloud chart type.
"""

from __future__ import annotations
from typing import Optional, Literal
import numpy as np
from chart.plots.base import Plot
from wordcloud import WordCloud


class PlotWordcloud(Plot):
    def plot(
        self,
        col_freq: Optional[str] = None,
        mask_shape: Literal["rectangle", "circle"] = "rectangle",
        mask_width: int = 800,
        mask_height: int = 600,
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

        font_path = "C:/Windows/Fonts/msyh.ttc"  # 字体路径

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
