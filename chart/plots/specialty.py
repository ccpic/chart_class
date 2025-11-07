"""
Plot classes for specialty chart types.
包含: Treemap, Heatmap, Waffle, Funnel
"""

from __future__ import annotations
from typing import List, Optional, Union, Literal

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np
import pandas as pd
import seaborn as sns
import squarify
from pywaffle import Waffle

from chart.plots.base import Plot


class PlotTreemap(Plot):
    """矩形树图类"""

    def plot(
        self,
        level1: str,
        size: str,
        level2: Optional[str] = None,
        **kwargs,
    ) -> PlotTreemap:
        """使用squarify包生成矩形Treemap

        Args:
            level1 (str): 第一层级字段名
            size (str): 大小字段名
            level2 (Optional[str], optional): 第二层级字段名. Defaults to None.

        Returns:
            PlotTreemap: 返回自身实例
        """

        df = self.data

        colors = self._colors.get_colors(labels=df.index, hue=self.hue)[1]

        df_size1 = pd.pivot_table(
            data=df, index=level1, columns=None, values=size, aggfunc=sum
        ).sort_values(by=size, ascending=False)

        # 使用Squarify导出矩形数据，以数据手动画图，可以控制更多元素
        list_size = df_size1[size].tolist()
        list_size = squarify.normalize_sizes(
            list_size, self.figure.width, self.figure.height
        )  # 根据设置的总体宽高正态化数据
        rects_data = squarify.squarify(
            list_size, 0, 0, self.figure.width, self.figure.height
        )  # Squarify算法计算出所有矩形的数据

        # 根据数据循环创建矩形并添加标签
        for i, r in enumerate(rects_data):
            color = self._colors.get_color(df.index[i])

            rect = patches.Rectangle(
                (r["x"], r["y"]),
                r["dx"],
                r["dy"],
                linewidth=10,
                edgecolor="#222222",
                facecolor=color,
            )  # 创建四边形
            self.ax.add_patch(rect)  # Add patch到轴
            # 动态添加标签并设置标签字体大小
            if r["dx"] > 0.02 * (self.figure.width * self.figure.height) or r["dx"] * r[
                "dy"
            ] > 0.01 * (self.figure.width * self.figure.height):
                plt.text(
                    (
                        r["x"] + r["dx"] / 2
                        if level2 is None
                        else r["x"] + r["dx"] * 0.05
                    ),  # 如无level2，则rect的水平中心，否则rect的left稍往右偏移
                    (
                        r["y"] + r["dy"] / 2
                        if level2 is None
                        else r["y"] + r["dy"] - r["dx"] * 0.05
                    ),  # 如无level2，则rect的垂直中心，否则rect的Top稍往下偏移
                    df_size1.index[i],
                    ha="center" if level2 is None else "left",
                    va="center",
                    multialignment="center",
                    fontsize=(self.fontsize * r["dx"])
                    ** 0.5,  # / (self.width * self.height),
                    color="black" if level2 is None else "grey",
                )

            # 绘制Level2
            if level2 is not None:
                df_size2 = pd.pivot_table(
                    data=df[df[level1] == df_size1.index[i]],
                    index=level2,
                    columns=None,
                    values=size,
                    aggfunc=sum,
                ).sort_values(by=size, ascending=False)
                list_size2 = df_size2[size].tolist()
                list_size2 = squarify.normalize_sizes(
                    list_size2, r["dx"], r["dy"]
                )  # 根据设置的总体宽高正态化数据
                rects_data = squarify.squarify(
                    list_size2, r["x"], r["y"], r["dx"], r["dy"]
                )  # Squarify算法计算出所有矩形的数据

                for j, r2 in enumerate(rects_data):
                    rect2 = patches.Rectangle(
                        (r2["x"], r2["y"]),
                        r2["dx"],
                        r2["dy"],
                        linewidth=2,
                        edgecolor="#222222",
                        facecolor=color if self.hue is None else colors[i],
                    )  # 创建四边形
                    self.ax.add_patch(rect2)  # Add patch到轴
                    # 动态添加标签并设置标签字体大小
                    if r2["dx"] > 0.02 * (self.figure.width * self.figure.height) or r2[
                        "dx"
                    ] * r["dy"] > 0.01 * (self.figure.width * self.figure.height):
                        plt.text(
                            r2["x"] + r2["dx"] / 2,  # rect的水平中心
                            r2["y"] + r2["dy"] / 2,  # rect的垂直中心
                            df_size2.index[j],
                            ha="center",
                            va="center",
                            multialignment="center",
                            fontsize=(self.fontsize * r2["dx"])
                            ** 0.5,  # / (self.width * self.height),
                        )

        # 去除边框的刻度
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Squarify包要求width和height的乘积等于上方主数据的和，所以要如此设置
        self.ax.set_xlim(0, self.figure.width)
        self.ax.set_ylim(0, self.figure.height)

        return self


class PlotHeatmap(Plot):
    """热力图类"""

    def plot(
        self,
        cmap: Optional[Union[str, list]] = None,
        cbar: bool = True,
        show_label: bool = True,
        **kwargs,
    ) -> PlotHeatmap:
        """继承基本类，生成网格热力图类

        Args:
            cmap (Optional[Union[str, list]], optional): 自定义颜色方案，可以是cmap名或颜色列表. Defaults to None.
            cbar (bool, optional): 是否添加colorbar. Defaults to True.
            show_label (bool, optional): 是否往每个网格添加标签文本. Defaults to True.

        Returns:
            PlotHeatmap: 返回自身实例
        """
        sns.heatmap(
            data=self.data,
            ax=self.ax,
            annot=show_label,
            cbar=cbar,
            cmap=self._colors.cmap_norm if cmap is None else cmap,
            fmt=self.fmt[2:-1],  # seaborn格式会自己加{:}
            annot_kws={"fontsize": self.fontsize},
        )

        return self


class PlotWaffle(Plot):
    """华夫饼图类"""

    def plot(
        self,
        rows: int = 10,
        columns: int = 10,
        size: Optional[str] = None,
        colors: Optional[List[str]] = None,
        vertical: bool = True,
        block_arranging_style: Literal["snake", "new-line"] = "snake",
        icons: Optional[Union[List[str], str]] = None,
        **kwargs,
    ) -> PlotWaffle:
        """继承基本类，绘制华夫图

        Args:
            rows (int, optional): 行数. Defaults to 10.
            columns (int, optional): 列数. Defaults to 10.
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
            colors (Optional[List[str]], optional): 指定颜色列表，如不指定将使用默认颜色方案. Defaults to None.
            vertical (bool, optional): 分类按垂直发展. Defaults to True.
            block_arranging_style (Literal["snake", "new-line"], optional): 每个分类如何起始，"snake"为紧接上类末尾，"new-line"为每类新起一行. Defaults to "snake".
            icons (Optional[Union[List[str], str]], optional): 指定矢量图形，为Font Awesome字符串. Defaults to None.

        Returns:
            PlotWaffle: 返回一个自身实例
        """
        # 使用基类方法获取列数据
        size = self._get_column(size, 0)
        share = (
            size.transform(lambda x: x / x.sum()).mul(100).astype(int).values.tolist()
        )

        if colors is None:
            colors = []
            for idx in size.index:
                # 使用基类方法获取颜色
                colors.append(self._get_color_for_item(idx, stacked=True))

        self.ax.set_aspect(aspect="equal")

        Waffle.make_waffle(
            ax=self.ax,  # pass axis to make_waffle
            rows=rows,
            columns=columns,
            values=share,
            colors=colors,
            rounding_rule="ceil",
            vertical=vertical,
            block_arranging_style=block_arranging_style,
            icons=icons,
            **kwargs,
        )

        return self


class PlotFunnel(Plot):
    """漏斗图类"""

    def plot(
        self, size: Optional[str] = None, height: Optional[float] = 0.7, **kwargs
    ) -> PlotFunnel:
        """继承基本类，绘制漏斗图

        Args:
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
            height (Optional[float], optional): 漏斗高度. Defaults to 0.7.

        Returns:
            PlotFunnel: 返回一个自身实例
        """
        df = self.data

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "color": "navy",
                "bbox": dict(
                    boxstyle="round,pad=0.5",
                    facecolor="grey",
                    edgecolor="black",
                    linewidth=1,
                    alpha=0.5,
                ),
                "label_ha": "center",
                "show_label": True,
            },
            **kwargs,
        )

        labels = df.index
        # 使用基类方法获取列数据
        size = self._get_column(size, 0)
        max_size = size[0]
        dummy1 = [max_size / 2 - i / 2 for i in size]  # 为了形成漏斗两侧的留白
        dummy2 = [
            i + j for i, j in zip(size, dummy1)
        ]  # 原始值+留白，使漏斗bar出现在图片中间

        self.ax.barh(
            labels[::-1], dummy2[::-1], color=d_style.get("color"), height=height
        )
        self.ax.barh(labels[::-1], dummy1[::-1], color="white", height=height)
        self.ax.axis("off")

        polygons = []
        for i in range(len(size)):
            # 标签
            if d_style.get("show_label"):
                self.ax.text(
                    max_size * (-0.1),
                    i,
                    labels[::-1][i],
                    ha=d_style.get("label_ha"),
                    va="center",
                    multialignment="center",
                    fontsize=self.fontsize * 1.2,
                    bbox=d_style.get("bbox"),
                )

            # 数量
            self.ax.text(
                dummy2[0] / 2,
                i,
                self.fmt.format(size[::-1][i]),
                ha="center",
                va="center",
                multialignment="center",
                fontsize=self.fontsize,
                color="white",
            )

            # 转化率
            if i < (len(size) - 1):
                self.ax.text(
                    dummy2[0] / 2,
                    len(size) - 1.5 - i,
                    "{:.1%}".format(size[i + 1] / size[i]),
                    ha="center",
                    va="center",
                    multialignment="center",
                    fontsize=self.fontsize,
                )

                polygons.append(
                    patches.Polygon(
                        xy=np.array(
                            [
                                (dummy1[i + 1], len(size) - 2 + height / 2 - i),
                                (dummy2[i + 1], len(size) - 2 + height / 2 - i),
                                (dummy2[i], len(size) - 1 - height / 2 - i),
                                (dummy1[i], len(size) - 1 - height / 2 - i),
                            ]
                        )
                    )
                )
        self.ax.add_collection(
            PatchCollection(polygons, facecolor=d_style.get("color"), alpha=0.5)
        )
        return self
