import pandas as pd
from typing import Any, Callable, Dict, List, Tuple, Union


class DfAnalyzer:
    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        date_column: str = None,
        sorter: Dict[str, list] = {},
        save_path: str = "/plots/",
    ):
        """一个自定义类用来分析pandas dataframe

        Parameters
        ----------
        data : pd.DataFrame
            原始数
        name : str
            数据集名称，可用在后续绘图的标题等处
        date_column : str, optional
            时间戳字段名称（如有）, by default None
        sorter : Dict[str, list], optional
            排序字典，key为要排序的字段名，value为排序顺序, by default {}
        save_path : str, optional
            导出数据或生成图片的文件路径, by default "/plots/"
        """
        self.data = data
        self.name = name
        self.date_column = date_column
        self.sorter = sorter
        self.save_path = save_path

    # 透视
    def get_pivot(
        self,
        index: str = None,
        columns: str = None,
        values: str = None,
        aggfunc: Callable = sum,
        query_str: str = "ilevel_0 in ilevel_0",  # 默认query语句能返回df总体
        perc: bool = False,
        sort_values: bool = True,
        dropna: bool = True,
        fillna: bool = True,
        **kwargs,
    ) -> pd.DataFrame:
        pivoted = pd.pivot_table(
            self.data.query(query_str),
            values=values,
            index=index,
            columns=columns,
            aggfunc=aggfunc,
        )
        # pivot table对象转为默认df
        pivoted = pd.DataFrame(pivoted.to_records())
        try:
            pivoted.set_index(index, inplace=True)
        except KeyError:  # 当index=None时，捕捉错误并set_index("index"字符串)
            pivoted.set_index("index", inplace=True)

        if sort_values is True:
            s = pivoted.sum(axis=1).sort_values(ascending=False)
            pivoted = pivoted.loc[s.index, :]  # 行按照汇总总和大小排序
            s = pivoted.sum(axis=0).sort_values(ascending=False)
            pivoted = pivoted.loc[:, s.index]  # 列按照汇总总和大小排序

        if columns in self.sorter:
            pivoted = pivoted.reindex(columns=self.sorter[columns])

        if type(index) is not list:
            if index in self.sorter:
                pivoted = pivoted.reindex(self.sorter[index])  # 对于部分变量有固定排序

        # 删除NA或替换NA为0
        if dropna is True:
            pivoted = pivoted.dropna(how="all")
            pivoted = pivoted.dropna(axis=1, how="all")
        else:
            if fillna is True:
                pivoted = pivoted.fillna(0)

        if perc is True:
            pivoted = pivoted.div(pivoted.sum(axis=1), axis=0)  # 计算行汇总的百分比

        if "head" in kwargs:  # 只取top n items
            pivoted = pivoted.head(kwargs["head"])

        if "tail" in kwargs:  # 只取bottom n items
            pivoted = pivoted.tail(kwargs["tail"])

        # if index == self.date_column:
        #     pivoted.index = pd.to_datetime(pivoted.index, format='%Y-%m')

        # if columns == self.date_column:
        #     pivoted.columns = pd.to_datetime(pivoted.columns, format='%Y-%m')

        return pivoted


if __name__ == "__main__":
    df = pd.DataFrame({"a": [1, 1, 3], "b": [3, 5, 4], "z": [1, 1, 1]})
    a = DfAnalyzer(df, "test")
    print(
        a.get_pivot(
            index="a",
        )
    )
