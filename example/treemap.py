from data import test_data
import matplotlib.pyplot as plt
from chart import GridFigure

if __name__ == "__main__":
    df = test_data()

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
        data=df.reset_index().loc[:, ["药品名称", "谈判年份", "2022-12"]],
        ax_index=0,
        style={},
        level1="谈判年份",
        level2="药品名称",
        size="2022-12",
        # hue="谈判年份",
    )

    f.save()
