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
            "title": "柱状图",
        },
    )

    f.plot(
        kind="bar",
        data=df,
        ax_index=0,
        style={"xticklabel_rotation": 90},
        color_dict={"奥拉帕利片": "darkorange"},
        show_total_label=True,
    )

    f.save()
