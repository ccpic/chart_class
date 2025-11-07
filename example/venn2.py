from data import test_data
import matplotlib.pyplot as plt
from chart import GridFigure

if __name__ == "__main__":
    df = test_data()

    f = plt.figure(
        FigureClass=GridFigure,
        nrows=2,
        ncols=5,
        width=16,
        height=5,
        fontsize=11,
        style={
            "title": "Venn2图",
        },
    )
    for i, col in enumerate(df.columns[-10:]):
        f.plot(
            kind="venn2",
            data=(100, 50, 30),
            ax_index=i,
            style={
                "title": col,
            },
            set_labels=("A", "B"),
        )

    f.save()
