import pandas as pd

from dataframe import DfAnalyzer
import matplotlib.pyplot as plt
from figure import GridFigure

if __name__ == "__main__":
    df = pd.read_excel("data.xlsx", engine="openpyxl")
    a = DfAnalyzer(data=df, name="test", date_column="Date")
    a = a.transform(
        period="MAT",
        cols_grouper=["分子+年份+降幅", "CORPORATION", "PACKAGE", "数值类型"],
        cols_amount="数值",
    )
    pivoted = (
        a.get_pivot(
            index=a.date_column,
            columns="药品名称",
            query_str="数值类型=='金额'",
            values="数值",
        )
        .sort_index()
        .div(100000000)
    )
    print(pivoted)

    f = plt.figure(  # 必须使用plt.figure，如果直接初始化类会有些奇怪的错误，比如adjust_text包的一些问题
        FigureClass=GridFigure,
        ncols=2,
        fontsize=11,
        style={
            "title": "李四",
            "label_outer": False,
        },
    )
    f.plot_bubble(
        data=pivoted,
        ax_index=0,
        style={
            "title": "张三",
            "ylabel": "test",
            "xlabel": "test",
            "show_legend": False,
        },
        label_limit=205,
    )

    f.plot_bar(
        data=pivoted,
        ax_index=1,
        style={
            "title": "王五",
            "ylabel": "test",
            "xlabel": "test",
            "show_legend": False,
            "xticklabel_rotation": 90,
        },
    )
    f.save()
