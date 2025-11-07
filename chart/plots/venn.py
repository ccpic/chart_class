"""
Plot classes for chart types.
"""

from __future__ import annotations
from typing import Any, Optional

from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles

from chart.plots.base import Plot


class PlotVenn2(Plot):
    """二元韦恩图绘制类

    使用 matplotlib_venn 绘制2组数据的韦恩图。
    """

    def plot(
        self,
        set1: Optional[set] = None,
        set2: Optional[set] = None,
        set_labels: Optional[tuple] = None,
        **kwargs: Any,
    ) -> PlotVenn2:
        """继承基本类，绘制2组数据的Venn图

        Args:
            set1 (Optional[set], optional): 第1组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set2 (Optional[set], optional): 第2组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set_labels (tuple, optional): 组别标签. Defaults to None.

        Returns:
            PlotVenn2: 返回一个自身实例
        """
        if all((set1, set2)):
            v = venn2(subsets=(set1, set2), set_labels=set_labels, ax=self.ax)
            venn2_circles(subsets=(set1, set2), ax=self.ax)
        else:
            v = venn2(subsets=self.data, set_labels=set_labels, ax=self.ax)
            venn2_circles(subsets=self.data, ax=self.ax)

        # 获取并设置所有文本对象的字体大小
        for text in self.ax.texts:
            text.set_fontsize(self.fontsize)

        # 颜色
        if color := kwargs.get("color"):
            for i, id in enumerate(["10", "01", "11"]):
                v.get_patch_by_id(id).set_color(color[i])

        return self


class PlotVenn3(Plot):
    """三元韦恩图绘制类

    使用 matplotlib_venn 绘制3组数据的韦恩图。
    """

    def plot(
        self,
        set1: Optional[set] = None,
        set2: Optional[set] = None,
        set3: Optional[set] = None,
        set_labels: Optional[tuple] = None,
        **kwargs: Any,
    ) -> PlotVenn3:
        """继承基本类，绘制2组数据的Venn图

        Args:
            set1 (Optional[set], optional): 第1组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set2 (Optional[set], optional): 第2组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set3 (Optional[set], optional): 第3组原始数据，如果不提供则计算data参数传来的值. Defaults to None.
            set_labels (tuple, optional): 组别标签. Defaults to None.

        Returns:
            PlotVenn3: 返回一个自身实例
        """
        if all((set1, set2, set3)):
            v = venn3(subsets=(set1, set2, set3), set_labels=set_labels, ax=self.ax)
            venn3_circles(subsets=(set1, set2, set3), ax=self.ax)
        else:
            v = venn3(subsets=self.data, set_labels=set_labels, ax=self.ax)
            venn3_circles(subsets=self.data, ax=self.ax)

        # 获取并设置所有文本对象的字体大小
        for text in self.ax.texts:
            text.set_fontsize(self.fontsize)

        # 颜色
        if color := kwargs.get("color"):
            for i, id in enumerate(["100", "010", "110", "001", "101", "011", "111"]):
                try:
                    v.get_patch_by_id(id).set_color(color[i])
                except Exception:
                    pass

        return self
