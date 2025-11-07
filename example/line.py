from data import test_data
import matplotlib.pyplot as plt
from chart import GridFigure

if __name__ == "__main__":
    df = test_data()
    df.drop(columns=["谈判年份"], inplace=True)
    df = df.head(10).transpose()

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
        data=df,
        ax_index=0,
        style={"minor_grid": {}, "xticklabel_rotation": 90},
        show_label=df.columns,
        endpoint_label_only=True,
    )

    f.annotate(x1=2, x2=19, text="啦啦啦啦")
    f.annotate(x1=20, x2=22, text="啦啦啦啦")
    f.save()
