"""
Plot classes for chart types.
"""

from __future__ import annotations
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from adjustText import adjust_text

from chart.plots.base import Plot


class PlotHist(Plot):
    """直方图绘制类

    支持核密度估计曲线、统计指标、等分线等功能。
    """

    def plot(
        self,
        bins: int = 10,
        tiles: int = 10,
        show_kde: bool = True,
        show_metrics: bool = True,
        show_tiles: bool = False,
        show_label: bool = False,
        ind: Optional[list] = None,
        **kwargs: Any,
    ) -> PlotHist:
        """继承基本类，绘制histogram直方图

        Args:
            bins (int, optional): 直方图柱的个数. Defaults to 10.
            tiles (int, optional): 等分线的个数. Defaults to 10.
            show_kde (bool, optional): 是否显示核密度估计曲线. Defaults to True.
            show_metrics (bool, optional): 是否显示均值和中位数. Defaults to True.
            show_tiles (bool, optional): 是否显示等分线_. Defaults to False.
            ind (Optional[list], optional): 评估点，如为None则为1000个等距点. Defaults to None.

        Returns:
            PlotHist: 返回一个自身的实例
        """

        df = self.data

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "color_hist": "grey",
                "color_kde": "darkorange",
                "color_mean": "purple",
                "color_median": "crimson",
            },
            **kwargs,
        )

        df.plot(
            kind="hist",
            density=True,
            bins=bins,
            ax=self.ax,
            color=d_style.get("color_hist"),
            legend=None,
            alpha=0.5,
        )
        if show_kde:
            ax_kde = self.ax.twinx()
            df.plot(
                kind="kde",
                ax=ax_kde,
                color=d_style.get("color_kde"),
                legend=None,
                ind=ind,
            )
            # ax_kde.get_legend().remove()
            ax_kde.set_yticks([])  # 删除y轴刻度
            ax_kde.set_ylabel(None)

        # 添加百分位信息
        if show_tiles:
            # 计算每个子区间的长度
            interval_length = 1.0 / tiles

            # 初始化结果列表，包含第一个边界值
            boundaries = [0.0]

            # 计算并添加每个子区间的边界值
            for i in range(1, tiles):
                boundary_value = i * interval_length
                boundaries.append(boundary_value)

            print(boundaries)
            # 计算百分位数据
            percentiles = df.quantile(boundaries).reset_index()
            print(percentiles, type(percentiles))

            # 在hist图基础上绘制百分位
            self.ax.set_xlim(self.style._xlim[0], self.style._xlim[1])
            for i, (index, row) in enumerate(percentiles.iterrows()):
                self.ax.axvline(row[1], color="crimson", linestyle=":")  # 竖分隔线
                self.ax.text(
                    row[1],
                    self.ax.get_ylim()[1] * 0.97,
                    int(row[1]),
                    ha="center",
                    color="crimson",
                    fontsize=self.fontsize,
                )
                if i < tiles - 1:
                    self.ax.text(
                        percentiles.iloc[i, 1]
                        + (percentiles.iloc[i + 1, 1] - percentiles.iloc[i, 1]) / 2,
                        self.ax.get_ylim()[1],
                        "D" + str(i + 1),
                        ha="center",
                        va="bottom",
                    )
                else:
                    self.ax.text(
                        percentiles.iloc[tiles - 1, 1]
                        + (self.ax.get_xlim()[1] - percentiles.iloc[tiles - 1, 1]) / 2,
                        self.ax.get_ylim()[1],
                        "D" + str(i + 1),
                        ha="center",
                        va="bottom",
                    )

        # 添加均值、中位数等信息
        if show_metrics:
            median = np.nanmedian(df.values)  # 计算中位数
            mean = np.nanmean(df.values)  # 计算平均数
            # if self.text_diff is not None:
            #     median_diff = self.text_diff[j]["中位数"]  # 计算对比中位数
            #     mean_diff = self.text_diff[j]["平均数"]  # 计算对比平均数

            if median > mean:
                yindex_median = 0.95
                yindex_mean = 0.9
                pos_median = "left"
                pos_mean = "right"
            else:
                yindex_mean = 0.95
                yindex_median = 0.9
                pos_median = "right"
                pos_mean = "left"

            self.ax.axvline(median, color=d_style.get("color_median"), linestyle=":")
            self.ax.text(
                median,
                self.ax.get_ylim()[1] * yindex_median,
                f"中位数：{self.fmt.format(median)}",
                ha=pos_median,
                color="white",
                fontsize=self.fontsize,
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor=d_style.get("color_median"),
                    edgecolor=d_style.get("color_median"),
                    linewidth=1,
                    alpha=0.7,
                ),
                zorder=100,
            )

            self.ax.axvline(mean, color=d_style.get("color_mean"), linestyle=":")
            self.ax.text(
                mean,
                self.ax.get_ylim()[1] * yindex_mean,
                f"平均数：{self.fmt.format(mean)}",
                ha=pos_mean,
                color="white",
                fontsize=self.fontsize,
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor=d_style.get("color_mean"),
                    edgecolor=d_style.get("color_mean"),
                    linewidth=1,
                    alpha=0.7,
                ),
                zorder=100,
            )

        # 去除ticks
        self.ax.get_yaxis().set_ticks([])
        # self.ax.xaxis.set_major_formatter(ticker.StrMethodFormatter(self.fmt))

        # 轴标题
        self.ax.set_ylabel("频次", fontsize=self.fontsize)

        # x轴显示范围
        if isinstance(df, pd.DataFrame):
            self.ax.set_xlim(df.min().min(), df.max().max())
        else:
            self.ax.set_xlim(df.min(), df.max())

        ax_kde.spines["right"].set_visible(False)
        ax_kde.spines["top"].set_visible(False)
        ax_kde.yaxis.set_ticks_position("left")
        ax_kde.xaxis.set_ticks_position("bottom")

        return self


class PlotBoxdot(Plot):
    """带数据点的箱型图绘制类

    结合箱型图和散点图，展示数据分布和个体值。
    """

    def plot(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        label_limit: int = 0,
        label_threshold: float = 0,
        show_stats: bool = True,
        order: Optional[Union[None, list]] = None,
        **kwargs: Any,
    ) -> PlotBoxdot:
        """继承基本类，绘制带数据点的箱型图

        Args:
            x (Optional[str], optional): x轴类别数据的字段名，如不指定则为第1列. Defaults to None.
            y (Optional[str], optional): y轴数值数据的字段名，如不指定则为第2列. Defaults to None.
            label_limit (int, optional): 展示数据点标签的数量. Defaults to 0.
            label_threshold (float, optional): 对大于此值的数据点展示标签. Defaults to 0.
            show_stats (bool, optional): 是否显示统计值，包括最大值、最小值、中位数. Defaults to True.
            order (Optional[Union[None, list]], optional): 类别按什么排序，如果为None则按照数据自动排序. Defaults to None.

        Returns:
            PlotBoxWithDots: 返回一个自身实例
        """

        df = self.data

        x = df.columns[0] if x is None else x
        y = df.columns[1] if y is None else y

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs({"dot_size": 8, "jitter": 0.2}, **kwargs)

        ax = sns.stripplot(
            x=x,
            y=y,
            data=df,
            edgecolor="black",
            alpha=0.5,
            s=d_style.get("dot_size"),
            linewidth=1.0,
            jitter=d_style.get("jitter"),
            ax=self.ax,
            order=order,
            hue=self.hue,
        )
        ax = sns.boxplot(
            x=x,
            y=y,
            data=df,
            whis=np.inf,
            boxprops={"facecolor": "None"},
            order=order,
        )

        # 确保绘制完成后获取 x 轴标签
        self.figure.canvas.draw()
        ax_xticklabels = [t.get_text() for t in ax.get_xticklabels()]  # 获取x轴标签列表

        # 添加数据点标签

        labels = []
        for category in ax_xticklabels:
            df_temp = df[df[x] == category]
            for k, idx in enumerate(df_temp.index):
                if k == label_limit:
                    break

                point = ax.collections[ax_xticklabels.index(category)].get_offsets()[
                    k
                ]  # 获得散点图的坐标，因为有jitter，不能直接用原始数

                if point[1] > label_threshold:  # y值大于某阈值的才显示

                    labels.append(
                        plt.text(
                            point[0],
                            point[1],
                            idx,
                            size=self.fontsize * 0.8,
                            color="black",
                        )
                    )
        if len(labels) > 0:
            adjust_text(
                labels,
                arrowprops=dict(arrowstyle="->", color="black"),
            )

        # 添加最大值， 最小值，中位数标签
        if show_stats:
            df_groupby = df.groupby(x)[y]
            maxs = df_groupby.max().reindex(ax_xticklabels)  # 最高值
            mins = df_groupby.min().reindex(ax_xticklabels)  # 最低值
            medians = df_groupby.median().reindex(ax_xticklabels)  # 中位数

            for metric in [maxs, mins, medians]:
                for xtick in ax.get_xticks():
                    if metric is medians:
                        posx = xtick + 0.4
                    else:
                        posx = xtick + 0.25

                    ax.text(
                        posx,
                        metric[xtick],
                        self.fmt.format(metric[xtick]),
                        horizontalalignment="left",
                        verticalalignment="center",
                        size=self.fontsize,
                        color="black",
                        weight="semibold",
                    )

        return self
