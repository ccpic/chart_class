from data import test_data
import matplotlib.pyplot as plt
from figure import GridFigure

if __name__ == "__main__":
    df = test_data()
    df.drop(columns=["谈判年份"])
    df = df.sum(axis=1)

    print(df)
    
    f = plt.figure(
        FigureClass=GridFigure,
        width=12,
        height=10,
        ncols=1,
        fontsize=11,
        style={"title": "词云"},
    )

    f.plot(kind="wordcloud", data=df)
    f.save(transparent=False)
