import sys

sys.path.insert(0, sys.path[0] + "/../")
from dataframe import DfAnalyzer
import pandas as pd


def test_data() -> pd.DataFrame:
    """准备绘图示例的测试数据

    Returns:
        pd.DataFrame: 示例数据的pandas df
    """
    df = pd.read_excel("data.xlsx", engine="openpyxl")
    a = DfAnalyzer(data=df, name="test", date_column="Date", period_interval=3)
    a = a.transform(
        period="MAT",
        cols_amount="数值",
    )
    pivoted = (
        a.get_pivot(
            index=["谈判年份", "药品名称"],
            columns=a.date_column,
            query_str="数值类型=='金额'",
            values="数值",
        )
        .div(100000000)
        .reset_index()
        .set_index("药品名称")
    )

    return pivoted


if __name__ == "__main__":
    print(test_data())
