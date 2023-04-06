import pandas as pd
from typing import Any, Callable, Dict, List, Tuple, Union

class DfAnalyzer(pd.DataFrame):
    @property
    def _constructor(self):
        return DfAnalyzer._internal_constructor(self.__class__)

    class _internal_constructor(object):
        def __init__(self, cls):
            self.cls = cls

        def __call__(self, *args, **kwargs):
            kwargs["name"] = None
            # kwargs["date_column"] = None
            return self.cls(*args, **kwargs)

        def _from_axes(self, *args, **kwargs):
            return self.cls._from_axes(*args, **kwargs)

    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        date_column: str = None,
        sorter: Dict[str, list] = {},
        savepath: str = "./plots/",
        index=None,
        columns=None,
        dtype=None,
        copy=True,
    ):
        super(DfAnalyzer, self).__init__(
            data=data, index=index, columns=columns, dtype=dtype, copy=copy
        )
        self.data = data
        self.name = name
        self.date_column = date_column
        self.sorter = sorter
        self.savepath = savepath

    # # 根据列名和列值做数据筛选
    # def filtered(self, filter: dict = None):
    #     if filter is not None:
    #         # https: // stackoverflow.com / questions / 38137821 / filter - dataframe - using - dictionary
    #         return self[self.isin(filter).sum(1) == len(filter.keys())]
    #     else:
    #         return self

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
            self.query(query_str),
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
    a = DfAnalyzer(df,"test")
    print(a.get_pivot(index="a",))