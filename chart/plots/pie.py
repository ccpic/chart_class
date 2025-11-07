"""
Plot class for Pie chart.
"""

from __future__ import annotations
from typing import Optional
import matplotlib.pyplot as plt
from chart.plots.base import Plot


class PlotPie(Plot):
    def plot(
        self,
        size: Optional[str] = None,
        label_formatter: str = "{abs}",
        donut: bool = False,
        donut_title: Optional[str] = None,
        **kwargs,
    ) -> PlotPie:
        """继承基本类，绘制饼图

        Args:
            size (Optional[str], optional): 指定size列，如不指定则默认为第1列. Defaults to None.
            donut (bool, optional): 甜甜圈图还是饼图. Defaults to False.
            donut_title (Optional[str], optional): 甜甜圈图中间的文字. Defaults to None.

        Returns:
            PlotPie: 返回一个自身实例
        """
        df = self.data

        # 使用基类方法获取列数据
        size = self._get_column(size, 0)
        share = size.transform(lambda x: x / x.sum())

        df_mask = []
        for index, value in share.items():
            df_mask.append(abs(value))  # 加abs是为了防止项目有负数

        # 使用基类方法合并样式参数
        d_style = self._merge_style_kwargs(
            {
                "pct_distance": 0.8,
                "start_angle": 90,
                "counter_clock": False,
                "line_width": 1,
                "edgecolor": "white",
                "label_fontsize": self.fontsize,
                "circle_distance": 0.7,
            },
            **kwargs,
        )

        # Draw the pie chart
        wedges, texts, autotexts = self.ax.pie(
            df_mask,
            labels=df.index,
            autopct="%1.1f%%",
            pctdistance=d_style.get("pct_distance"),
            startangle=d_style.get("start_angle"),
            counterclock=d_style.get("counter_clock"),
            wedgeprops={
                "linewidth": d_style.get("line_width"),
                "edgecolor": d_style.get("edgecolor"),
            },
            textprops={"fontsize": d_style.get("label_fontsize")},
        )

        for i, pie_wedge in enumerate(wedges):
            # 如果有指定颜色就颜色，否则按预设列表选取
            color = self._colors.get_color(pie_wedge.get_label())
            pie_wedge.set_facecolor(color)

            if size.iloc[i] < 0:
                pie_wedge.set_facecolor("white")

        for k, autotext in enumerate(autotexts):
            # 使用基类方法创建标签字典
            d_label = self._create_label_dict(
                value=size.iloc[k], share=share.iloc[k], index=index
            )
            # 支持自定义格式
            if fmt_abs := kwargs.get("fmt_abs"):
                d_label["abs"] = fmt_abs.format(size.iloc[k])
            if fmt_share := kwargs.get("fmt_share"):
                d_label["share"] = fmt_share.format(share.iloc[k])

            autotext.set_color("white")
            autotext.set_fontsize(self.fontsize)
            autotext.set_text(label_formatter.format(**d_label))
            if size.iloc[k] < 0:
                autotext.set_color("r")

        if donut:
            # Prepare the white center circle for Donat shape
            my_circle = plt.Circle(
                (0, 0), d_style.get("circle_distance"), color="white"
            )
            self.ax.text(
                0,
                0,
                donut_title,
                horizontalalignment="center",
                verticalalignment="center",
                size=self.fontsize,
            )
            self.ax.add_artist(my_circle)  # 用白色圆圈覆盖饼图，变成圈图

        self.style._show_legend = False  # Pie图默认不显示图例

        return self
