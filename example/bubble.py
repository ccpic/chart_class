from data import test_data
import matplotlib.pyplot as plt
from figure import GridFigure

if __name__ == "__main__":
    df = test_data()

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
        data=df,
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
