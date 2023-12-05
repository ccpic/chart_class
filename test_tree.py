from __future__ import annotations
import matplotlib.pyplot as plt
from figure import GridFigure
import pandas as pd

if __name__ == "__main__":
    data = [
        {
            "Occupation": "Engineer",
            "Name": "Alice",
            "Salary": 100000,
        },
        {
            "Occupation": "Engineer",
            "Name": "Bob",
            "Salary": 120000,
        },
        {
            "Occupation": "Data Scientist",
            "Name": "Charlie",
            "Salary": 90000,
        },
        {
            "Occupation": "Data Scientist",
            "Name": "David",
            "Salary": 110000,
        },
    ]

    df = pd.DataFrame(data)
    print(df)

    """绘制Treemap
    """
    f = plt.figure(
        FigureClass=GridFigure,
        width=12,
        height=12,
        ncols=1,
        fontsize=30,
        style={
            "title": "Treemap图",
        },
    )

    f.plot(
        kind="treemap",
        data=df,
        ax_index=0,
        style={},
        level1 = "Occupation",
        level2 = "Name",
        size="Salary",
    )

    f.save()
