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
            "title": "算珠图",
        },
    )

    f.plot(
        kind="stripdot",
        data=df,
        fmt="{:,.1f}",
        ax_index=0,
        start="2021-12",
        end="2022-12",
        style={},
        hue="谈判年份",
    )
    f.save()
