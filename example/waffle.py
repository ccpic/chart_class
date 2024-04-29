from data import test_data
import matplotlib.pyplot as plt
from figure import GridFigure

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
            "title": "华夫图",
        },
    )
    for i, col in enumerate(df.columns[-10:]):
        f.plot(
            kind="waffle",
            data=df,
            ax_index=i,
            style={
                "title": col,
            },
            size=col,
            # icons="user",
        )

    f.save()
