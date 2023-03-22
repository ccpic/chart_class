from base import *
from wordcloud import WordCloud


class PlotBoxWithDots(GridFigure):
    def plot(self) -> str:
        pass


class PlotWordCloud(GridFigure):
    def plot(
        self,
        mask_shape: str = "rectangle",
        mask_width: int = 800,
        mask_height: int = 600,
    ) -> str:
        """继承基本类，绘制文字云图

        Parameters
        ----------
        mask_shape : str, optional
            词云形状类别:circle|rectangle, by default "rectangle"
        mask_width : int, optional
            形状为矩形时的矩形宽度, by default 800
        mask_height : int, optional
            形状为矩形时的矩形高度, by default 600

        Returns
        -------
        str
            返回绘图保存的路径
        """
        for j, ax in enumerate(self.axes):
            try:
                df = self.data[j]
            except IndexError:
                ax.axis("off")
                continue
            df.dropna(inplace=True)

            d_words = {}
            for index, row in df.iterrows():
                d_words[index] = row[0]
            print(d_words)

            if mask_shape == "circle":
                # 产生一个以(150,150)为圆心,半径为130的圆形mask
                x, y = np.ogrid[:600, :600]
                mask = (x - 300) ** 2 + (y - 300) ** 2 > 260 ** 2
                mask = 255 * mask.astype(int)
                wordcloud = WordCloud(
                    width=800,
                    height=800,
                    font_path="C:/Windows/Fonts/SimHei.ttf",
                    background_color="white",
                    mask=mask,
                )
            elif mask_shape == "rectangle":
                wordcloud = WordCloud(
                    width=mask_width,
                    height=mask_height,
                    font_path="C:/Windows/Fonts/SimHei.ttf",
                    background_color="white",
                )

            wordcloud.generate_from_frequencies(frequencies=d_words)

            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")

        return self.save()


class PlotLine(GridFigure):
    def plot(
        self,
        series_showlabel: List[str] = [],
        endpoint_label_only: bool = False,
    ) -> str:
        """继承基本类，绘制线形图

        Parameters
        ----------
        series_showlabel : List[str], optional
            指定要显示标签的系列, by default []
        endpoint_label_only : bool, optional
            标签是全部显示还是只显示首尾节点, by default False

        Returns
        -------
        str
            返回绘图保存的路径
        """
        for j, ax in enumerate(self.axes):
            df = self.data[j]
            ITER_COLORS = cycle(COLOR_LIST)
            # Generate the lines
            for i, column in enumerate(df.columns):
                markerstyle = "o"

                # 如果有指定颜色就颜色，否则按预设列表选取
                color = COLOR_DICT.get(column, next(ITER_COLORS))

                ax.plot(
                    df.index,
                    df[column],
                    color=color,
                    linewidth=2,
                    label=column,
                    marker=markerstyle,
                    markersize=5,
                    markerfacecolor="white",
                    markeredgecolor=color,
                )

                # 标签
                if column in series_showlabel:
                    for k, idx in enumerate(df.index):
                        if endpoint_label_only:
                            if k == 0 or k == len(df.index) - 1:
                                t = plt.text(
                                    idx,
                                    df.iloc[k, i],
                                    self.fmt[j].format(df.iloc[k, i]),
                                    ha="right" if k == 0 else "left",
                                    va="center",
                                    size="small",
                                    color="white",
                                )

                                t.set_bbox(
                                    dict(facecolor=color, alpha=0.7, edgecolor=color)
                                )
                        else:
                            t = plt.text(
                                idx,
                                df.iloc[k, i],
                                self.fmt[j].format(df.iloc[k, i]),
                                ha="center",
                                va="center",
                                size="small",
                                color="white",
                            )
                            t.set_bbox(
                                dict(facecolor=color, alpha=0.7, edgecolor=color)
                            )

                # Customize the major grid
                ax.grid(which="major", linestyle=":", linewidth="0.5", color="grey")

                # y轴标签格式
                ax.yaxis.set_major_formatter(
                    FuncFormatter(lambda y, _: self.fmt[j].format(y))
                )

                # Shrink current axis by 20% and put a legend to the right of the current axis
                box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                ax.legend(
                    loc="center left",
                    bbox_to_anchor=(1, 0.5),
                    labelspacing=1.5,
                    frameon=False,
                    prop={"family": "SimHei", "size": self.fontsize},
                )

        return self.save()


# 继承基本类，堆积柱状对比图类
class PlotStackedBar(GridFigure):
    def __init__(
        self,
        data,  # 原始数
        savepath: str = "./plots/",  # 保存位置
        width: int = 15,  # 宽
        height: int = 6,  # 高
        fontsize: int = 14,  # 字体大小
        gs: GridSpec = None,  # GridSpec
        fmt: list = [",.0f"],  # 每个grid的数字格式
        style: dict = {"title": "test"},  # 风格字典
        data_line=None,  # 折线图数据
        fmt_line=None,  # 折线图格式
        *args,
        **kwargs,
    ):
        super().__init__(
            data,
            savepath,
            width,
            height,
            fontsize,
            gs,
            fmt,
            style,
            *args,
            **kwargs,
        )
        self.data_line = data_to_list(data_line)
        if fmt_line is not None:
            self.fmt_line = ["{:%s}" % f for f in fmt_line]
        else:
            self.fmt_line = None

        if self.data_line is not None:
            check_data_with_axes(self.data_line, self.axes)
        if self.fmt_line is not None:
            check_data_with_axes(self.fmt_line, self.axes)

    def plot(
        self,
        stacked: bool = True,
        show_label: bool = True,
        show_total_label: bool = False,
        add_gr_text: bool = False,
        threshold: float = 0.02,
        show_legend: bool = True,
        *args,
        **kwargs,
    ) -> str:
        """继承基本类，绘制堆积柱状图

        Parameters
        ----------
        stacked : bool, optional
            是否堆积, by default True
        show_label : bool, optional
            是否显示数字标签, by default True
        show_total_label : bool, optional
            是否在最上方显示堆积之和数字标签, by default False
        add_gr_text : bool, optional
            是否显示增长率数字, by default False
        threshold : float, optional
            显示数字标签的阈值，系列占堆积之和的比例大于此值才显示, by default 0.02
        show_legend : bool, optional
            是否显示图例, by default True

        Returns
        -------
        str
            返回绘图保存的路径
        """
        for j, ax in enumerate(self.axes):
            # 处理绘图数据
            df = self.data[j]
            print(df)
            df_gr = self.data[j].pct_change(axis=1)
            if self.data_line is not None:
                df_line = self.data_line[j]

            # 绝对值bar图和增长率标注
            for k, index in enumerate(df.index):
                bottom_pos = 0
                bottom_neg = 0
                bottom_gr = 0
                bbox_props = None
                max_v = df.values.max()
                min_v = df.values.min()
                ITER_COLORS = cycle(COLOR_LIST)
                for i, col in enumerate(df):
                    v = df.loc[index, col]

                    if stacked:
                        if v >= 0:
                            bottom = bottom_pos
                        else:
                            bottom = bottom_neg
                    else:
                        bottom = 0

                    # 如果有指定颜色就颜色，否则按预设列表选取
                    if stacked:
                        if col in COLOR_DICT.keys():
                            color = COLOR_DICT[col]
                        elif index in COLOR_DICT.keys():
                            color = COLOR_DICT[index]
                        else:
                            color = next(ITER_COLORS)
                    else:
                        color = next(ITER_COLORS)

                    # bar宽度
                    bar_width = 0
                    if stacked:
                        if isinstance(
                            df.index, pd.DatetimeIndex
                        ):  # 如果x轴是日期，宽度是以“天”为单位的
                            bar_width = 20
                        else:
                            bar_width = 0.5
                    else:
                        bar_width = 0.8 / df.shape[1]

                    # bar x轴位置
                    if stacked:
                        pos_x = k
                    else:
                        pos_x = k + bar_width * i

                    # 绘制bar图
                    bar = ax.bar(
                        pos_x,
                        v,
                        width=bar_width,
                        color=color,
                        bottom=bottom,
                        label=col,
                    )
                    if show_label is True:
                        if stacked is False or df.shape[1] == 1:  # 非堆叠图或只有一列数的情况（非堆叠）
                            # 根据数据判断标签是否需要微调
                            if 0 <= v < max_v * 0.05:
                                pos_y = v * 1.1
                                va = "bottom"
                                fontcolor = color
                            elif min_v * 0.05 < v < 0:
                                pos_y = v * 0.9
                                va = "top"
                                fontcolor = color
                            else:
                                pos_y = v / 2
                                va = "center"
                                fontcolor = "white"

                        else:  # 堆叠的情况
                            pos_y = bottom + v / 2
                            va = "center"
                            fontcolor = "white"

                        if abs(v) >= threshold:
                            ax.text(
                                pos_x,
                                pos_y,
                                self.fmt[j].format(v),
                                color=fontcolor,
                                va=va,
                                ha="center",
                                fontsize=self.fontsize,
                                **NUM_FONT,
                            )
                    if v >= 0:
                        bottom_pos += v
                    else:
                        bottom_neg += v

                    patches = ax.patches
                    for rect in patches:
                        height = rect.get_height()
                        # 负数则添加纹理
                        if height < 0:
                            rect.set_hatch("//")

                    if add_gr_text:
                        if k > 0:
                            # 各系列增长率标注
                            ax.annotate(
                                "{:+.1%}".format(df_gr.iloc[k, i]),
                                xy=(
                                    0.5,
                                    (
                                        bottom_gr
                                        + df.iloc[k - 1, i] / 2
                                        + df.iloc[k, i] / 2
                                    )
                                    / 2,
                                ),
                                ha="center",
                                va="center",
                                color=color,
                                fontsize=self.fontsize,
                                bbox=bbox_props,
                            )
                            bottom_gr += df.iloc[k - 1, i] + df.iloc[k, i]

                # 在柱状图顶端添加total值
                if show_total_label:
                    total = df.sum(axis=1)
                    for p, v in enumerate(total.values):
                        ax.text(
                            x=p,
                            y=v,
                            s=self.fmt[j].format(float(v)),
                            fontsize=self.fontsize,
                            ha="center",
                            va="bottom",
                        )

                # box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width, box.height * 1.1])

            # 如果是非堆叠图要手动指定x轴ticks
            if stacked is False:
                plt.xticks(np.arange(df.shape[0]) + bar_width / df.shape[1], df.index)
            else:
                plt.xticks(np.arange(df.shape[0]), df.index)

            # # x轴标签
            # ax.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

            # y轴标签格式
            ax.yaxis.set_major_formatter(
                FuncFormatter(lambda y, _: self.fmt[j].format(y))
            )

            ax.axhline(0, color="black", linewidth=0.5)  # y轴为0的横线

            if self.data_line is not None:

                # 增加次坐标轴
                ax2 = ax.twinx()

                if isinstance(df_line, pd.DataFrame):
                    label = df_line.columns[0]
                else:
                    label = df_line.name

                color_line = "darkorange"
                line = ax2.plot(
                    df_line.index,
                    df_line.values,
                    label=label,
                    color=color_line,
                    linewidth=1,
                    linestyle="dashed",
                    marker="o",
                    markersize=3,
                    markerfacecolor="white",
                )
                if "y2lim" in kwargs:
                    ax2.set_ylim(kwargs["y2lim"][0], kwargs["y2lim"][1])

                for i in range(len(df_line)):
                    if float(df_line.values[i]) <= ax2.get_ylim()[1]:
                        t = ax2.text(
                            x=df_line.index[i],
                            y=df_line.values[i],
                            s=self.fmt_line[j].format(float(df_line.values[i])),
                            ha="center",
                            va="bottom",
                            fontsize=self.fontsize,
                            color="white",
                        )
                        t.set_bbox(
                            dict(facecolor=color_line, alpha=0.7, edgecolor=color_line)
                        )

                # 次坐标轴标签格式
                ax2.yaxis.set_major_formatter(
                    FuncFormatter(lambda y, _: self.fmt_line[j].format(y))
                )
                ax2.get_yaxis().set_ticks([])

                # # x轴标签
                # ax2.get_xaxis().set_ticks(range(0, len(df.index)), labels=df.index)

            # 图例
            if show_legend:
                box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

                handles, labels = ax.get_legend_handles_labels()
                if self.data_line is not None:
                    handles2, labels2 = ax2.get_legend_handles_labels()
                    by_label = dict(
                        zip(
                            labels[::-1] + labels2[::-1],
                            handles[::-1] + handles2[::-1],
                        )
                    )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
                else:
                    by_label = dict(
                        zip(
                            labels[::-1],
                            handles[::-1],
                        )
                    )  # 和下放调用.values()/.keys()配合去除重复的图例，顺便倒序让图例与图表保持一致
                ax.legend(
                    by_label.values(),
                    by_label.keys(),
                    loc="center left",
                    ncol=1,
                    bbox_to_anchor=(1, 0.5),
                    labelspacing=1,
                    frameon=False,
                    prop={"family": "SimHei", "size": self.fontsize},
                )

        return self.save()
