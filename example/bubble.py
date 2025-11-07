from data import test_data
import matplotlib.pyplot as plt
from chart import GridFigure
import pandas as pd

if __name__ == "__main__":
    # df = test_data()

    # f = plt.figure(
    #     FigureClass=GridFigure,
    #     width=11,
    #     height=10,
    #     ncols=1,
    #     fontsize=11,
    #     style={
    #         "title": "气泡图",
    #     },
    # )

    # f.plot(
    #     kind="bubble",
    #     data=df,
    #     ax_index=0,
    #     style={},
    #     x="2022-12",
    #     y="2021-12",
    #     z="2022-12",
    #     hue="初次谈判年份",
    #     label_limit=10,
    #     label_formatter="{index}\n({x}, {y})",
    #     x_fmt="{:,.1f}",
    #     y_fmt="{:,.1f}",
    #     show_hist=True,
    #     show_legend=False,
    # )

    # f.save()

    df = pd.read_excel(
        "法伯样本医院恩那罗份额2024Q1.xlsx", sheet_name="by医院-HIF+ESA0.6市场"
    )
    print(df)

    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=11,
        style={
            "title": "CPA数据2024Q1恩那罗有量终端PTD表现",
        },
    )

    f.plot(
        kind="bubble",
        data=df,
        ax_index=0,
        style={},
        x="恩那度司他(PTD)",
        y="恩那度司他 PTD-Share%",
        z="HIF+ESA*0.6(PTD)",
        hue="省份",
        label_limit=10,
        label_formatter="{index}\n({x}, {y})",
        x_fmt="{:,.1f}",
        y_fmt="{:,.1f}",
        show_hist=False,
        show_legend=False,
    )

    f.save()
