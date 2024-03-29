import pandas as pd

from dataframe import DfAnalyzer
import matplotlib.pyplot as plt
from figure import GridFigure


if __name__ == "__main__":
    df = pd.read_excel("data.xlsx", engine="openpyxl")
    a = DfAnalyzer(data=df, name="test", date_column="Date", period_interval=3)
    a = a.transform(
        period="MAT",
        cols_amount="数值",
    )
    pivoted = (
        a.get_pivot(
            index=["谈判年份", "药品名称"],
            columns=a.date_column,
            query_str="数值类型=='金额'",
            values="数值",
        )
        .div(100000000)
        .reset_index()
        .set_index("药品名称")
    )
    print(pivoted)

    """绘制华夫图
    """
    f = plt.figure(
        FigureClass=GridFigure,
        nrows=2,
        ncols=5,
        width=16,
        height=5,
        fontsize=11,
        style={
            "title": "华夫图",
        },
    )
    for i, col in enumerate(pivoted.columns[-10:]):
        f.plot(
            kind="waffle",
            data=pivoted,
            ax_index=i,
            style={"title": col},
            size=col,
            icons="user",
        )

    f.save()

    """绘制Treemap
    """

    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=30,
        style={
            "title": "Treemap图",
        },
    )

    f.plot(
        kind="treemap",
        data=pivoted.reset_index().loc[:, ["药品名称", "谈判年份", "2022-12"]],
        ax_index=0,
        style={},
        level1="谈判年份",
        level2="药品名称",
        size="2022-12",
        # hue="谈判年份",
    )

    f.save()

    """绘制气泡图
    """
    f = plt.figure(
        FigureClass=GridFigure,
        width=11,
        height=10,
        ncols=1,
        fontsize=11,
        style={
            "title": "气泡图",
        },
    )

    f.plot(
        kind="bubble",
        data=pivoted,
        ax_index=0,
        style={},
        x="2022-12",
        y="2021-12",
        z="2022-12",
        hue="谈判年份",
        label_limit=10,
        label_formatter="{index}\n({x}, {y})",
        x_fmt="{:,.1f}",
        y_fmt="{:,.1f}",
        show_hist=True,
        show_legend=False,
    )

    f.save()

    """绘制算珠图"""
    f = plt.figure(
        FigureClass=GridFigure,
        width=11,
        height=10,
        ncols=1,
        fontsize=11,
        style={
            "title": "算珠图",
        },
    )

    f.plot(
        kind="stripdot",
        data=pivoted,
        fmt="{:,.1f}",
        ax_index=0,
        start="2021-12",
        end="2022-12",
        style={},
        hue="谈判年份",
    )
    f.save()

    """绘制箱型散点图"""
    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=11,
        style={
            "title": "箱型散点图",
        },
    )

    f.plot(
        kind="boxdot",
        data=pivoted,
        ax_index=0,
        style={},
        x="谈判年份",
        y="2022-12",
    )
    f.save()

    """绘制直方图"""
    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=11,
        style={
            "title": "直方图",
        },
    )

    f.plot(
        kind="hist",
        data=pivoted.loc[:, "2022-12"],
        ax_index=0,
        style={},
    )
    f.save()

    """绘制折线图"""
    pivoted = (
        a.get_pivot(
            index="药品名称",
            columns=a.date_column,
            query_str="数值类型=='金额'",
            values="数值",
        )
        .div(1000000)
        .head(10)
        .transpose()
    )
    print(pivoted)

    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=11,
        style={
            "title": "折线图",
        },
    )

    f.plot(
        kind="line",
        data=pivoted.iloc[:, 1],
        ax_index=0,
        style={"minor_grid": {}, "xticklabel_rotation": 90},
        show_label=pivoted.columns[1],
    )

    f.annotate(x1=2, x2=19, text="啦啦啦啦")
    f.annotate(x1=20, x2=22, text="啦啦啦啦")
    f.save()

    """绘制柱状图
    """
    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=11,
        style={
            "title": "柱状图",
        },
    )

    f.plot(
        kind="bar",
        data=pivoted.iloc[:, 0],
        ax_index=0,
        style={"xticklabel_rotation": 90},
        color_dict={"奥拉帕利片": "darkorange"},
    )

    f.save()

    """绘制热力图
    """

    f = plt.figure(
        FigureClass=GridFigure,
        width=12,
        height=10,
        ncols=1,
        fontsize=11,
        style={"title": "热力图"},
    )

    f.plot(kind="heatmap", data=pivoted, ax_index=0, style={"xticklabel_rotation": 90})

    f.save(transparent=False)

    """绘制词云
    """

    f = plt.figure(
        FigureClass=GridFigure,
        width=12,
        height=10,
        ncols=1,
        fontsize=11,
        style={"title": "词云"},
    )

    f.plot(kind="wordcloud", data=pivoted.transpose().sum(axis=1))
    f.save(transparent=False)
