from data import test_data
import matplotlib.pyplot as plt
from figure import GridFigure

if __name__ == "__main__":
    df = test_data()

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
        data=df,
        ax_index=0,
        style={},
        x="谈判年份",
        y="2022-12",
    )
    f.save()
