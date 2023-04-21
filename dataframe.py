from __future__ import annotations
import pandas as pd
from typing import Any, Callable, Dict, List, Tuple, Union, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from figure import GridFigure
import copy

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class DateError(Exception):
    def __init__(self, message: str):
        """构造日期格式错误类，接收一个message参数，用于设置错误信息

        Parameters
        ----------
        message : str
            异常错误信息
        """
        self.message = message

    def __str__(self) -> str:
        """重写__str__方法，返回错误信息

        Returns
        -------
        str
            返回错误信息字符串
        """
        return repr(self.message)


class DateRange:
    def __init__(self, date: datetime):
        self.date = date
        """通过一个目标日期，生成对应该日期的MAT, MQT, YTD时间戳

        Parameters
        ----------
        date: datetime
            目标时间, 所有后续计算都围绕这个时间
        """

    def mat(
        self,
        freq: Literal["MS", "3MS", "Q", "D"] = "MS",  # 这里要用M而不是MS因为是month start
        strftime: str = "%Y-%m",
        yoy_period: bool = False,
    ) -> List[str]:
        """返回一个滚动年的时间戳字符串列表

        Parameters
        ----------
        freq : Literal["MS", "3MS", "Q", "D"], optional
            时间间距, by default "MS"
            "MS": by月
            "3MS": by3个月
            "Q": by自然季，月份只会出现3,6,9,12
            "D": by天
        strftime: str, optional
            时间戳字符串的格式, by default "%Y-%m"
        yoy_period: bool, optional
            是否同比, by default False
        Returns
        -------
        List[str]
            返回滚动年的时间戳字符串列表
        """

        mat_begin = self.date + relativedelta(months=-11)

        offset = relativedelta(years=-1) if yoy_period else relativedelta(years=0)

        mat = pd.date_range(
            start=mat_begin + offset,
            end=self.date + offset,
            freq=freq,
        )

        return mat.strftime(strftime).to_list()

    def ytd(
        self,
        freq: Literal["MS", "3MS", "Q", "D"] = "MS",  # 这里要用M而不是MS因为是month start
        strftime: str = "%Y-%m",
        yoy_period: bool = False,
    ) -> List[str]:
        """返回一个YTD(年至今)的时间戳字符串列表

        Parameters
        ----------
        freq : Literal["MS", "3MS", "Q", "D"], optional
            时间间距, by default "MS"
            "MS": by月
            "3MS": by3个月
            "Q": by自然季，月份只会出现3,6,9,12
            "D": by天
        strftime: str, optional
            时间戳字符串的格式, by default "%Y-%m"
        yoy_period: bool, optional
            是否同比, by default False
        Returns
        -------
        List[str]
            返回YTD(年至今)的时间戳字符串列表
        """

        ytd_begin = self.date.replace(month=1, day=1)

        offset = relativedelta(years=-1) if yoy_period else relativedelta(years=0)

        ytd = pd.date_range(
            start=ytd_begin + offset,
            end=self.date + offset,
            freq=freq,
        )

        return ytd.strftime(strftime).to_list()

    def mqt(
        self,
        freq: Literal["MS", "D"] = "MS",  # 这里要用M而不是MS因为是month start
        strftime: str = "%Y-%m",
        yoy_period: bool = False,
        last_period: bool = False,
    ) -> List[str]:
        """返回一个滚动季的时间戳字符串列表

        Parameters
        ----------
        freq : Literal["MS", "D"], optional
            时间间距, by default "MS"
            "MS": by月
            "D": by天
        strftime: str, optional
            时间戳字符串的格式, by default "%Y-%m"
        yoy_period: bool, optional
            是否同比, by default False
        last_period: bool, optional
            是否环比, by default False
        Returns
        -------
        List[str]
            返回滚动季的时间戳字符串列表
        """

        mqt_begin = self.date + relativedelta(months=-2)

        offset1 = relativedelta(years=-1) if yoy_period else relativedelta(years=0)
        offset2 = relativedelta(months=-3) if last_period else relativedelta(months=0)

        mqt = pd.date_range(
            start=mqt_begin + offset1 + offset2,
            end=self.date + offset1 + offset2,
            freq=freq,
        )

        return mqt.strftime(strftime).to_list()

    def mon(
        self,
        freq: Literal["MS", "D"] = "MS",
        strftime: str = "%Y-%m",
        yoy_period: bool = False,
        last_period: bool = False,
    ) -> List[str]:
        """返回一个单月的时间戳字符串列表

        Parameters
        ----------
        freq : Literal["MS", "3MS", "Q", "D"], optional
            时间间距, by default "MS"
            "MS": by月
            "3MS": by3个月
            "Q": by自然季，月份只会出现3,6,9,12
            "D": by天
        strftime: str, optional
            时间戳字符串的格式, by default "%Y-%m"
        yoy_period: bool, optional
            是否同比, by default False
        Returns
        -------
        List[str]
            返回YTD(年至今)的时间戳字符串列表
        """

        offset1 = relativedelta(years=-1) if yoy_period else relativedelta(years=0)
        offset2 = relativedelta(months=-1) if last_period else relativedelta(months=0)

        mon = pd.date_range(
            start=self.date.replace(day=1) + offset1 + offset2,
            end=self.date + offset1 + offset2,
            freq=freq,
        )

        return mon.strftime(strftime).to_list()


class DfAnalyzer:
    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        date_column: Optional[str] = None,
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
        date_column : Optional[str], optional
            指定时间戳字段名称（如有）, by default None
        sorter : Dict[str, list], optional
            排序字典，key为要排序的字段名，value为排序顺序, by default {}
        save_path : str, optional
            导出数据或生成图片的文件路径, by default "/plots/"
        """
        self.data = data
        self.name = name
        self.date_column = date_column

        if self.date_column is not None:
            try:
                self.data[self.date_column] = pd.to_datetime(
                    self.data[self.date_column]
                )  # 尝试将时间戳字段转换为datetime格式
                self.date = self.data[self.date_column].max()  # 如有时间戳字段，尝试寻找最后一期时间
                self._freq = pd.infer_freq(self.data[self.date_column].unique())
                # 自动判断时间戳字段的频率间隔是多少
                self.date_range = DateRange(self.date)

            except:
                raise DateError("时间戳字段解析失败")

        self.sorter = sorter
        self.save_path = save_path

    # 透视
    def get_pivot(
        self,
        index: Optional[str] = None,
        columns: Optional[str] = None,
        values: Optional[str] = None,
        aggfunc: Callable = sum,
        query_str: str = "ilevel_0 in ilevel_0",  # 默认query语句能返回df总体
        perc: Optional[Literal[1, 0, "index", "columns"]] = None,
        sort_values: Optional[
            Literal[
                "rows_by_last_col",
                "rows_by_first_col",
                "rows_by_cols_sum",
                "cols_by_rows_sum",
            ]
        ] = "rows_by_last_col",
        sort_asc: bool = False,
        dropna: bool = True,
        fillna: Optional[Union[int, float, str]] = 0,
        strftime: str = "%Y-%m",
    ) -> pd.DataFrame:
        """生成一个数据透视表，比直接用pd.pivot_table更适合日常场景

        Parameters
        ----------
        index : Optional[str], optional
            透视表的行标签字段, by default None
        columns : Optional[str], optional
            透视表的列标签字段, by default None
        values : Optional[str], optional
            透视表的值字段, by default None
        aggfunc : Callable, optional
            透视表的值字段汇总方式, by default sum
        query_str : str, optional
            数据筛选字符串,如"Date=='2022-12'", by default "ilevel_0 in ilevel_0"
        sort_values : Optional[ Literal[ "rows_by_last_col", "rows_by_first_col", "rows_by_cols_sum", "cols_by_rows_sum", ] ], optional
            根据值排序, by default "rows_by_last_col"
            "rows_by_last_col": 根据最后一列值排序行
            "rows_by_first_col": 根据第一列值排序行
            "rows_by_cols_sum": 根据列汇总排序行
            "cols_by_rows_sum": 按照行汇总排序列
        sort_asc : bool, optional
            排序时是否升序，否则降序, by default False
        dropna : bool, optional
            是否删除所有都是缺失值的整行或整列, by default True
        fillna : Optional[Union[int, float, str]] , optional
            缺失值替换, by default 0
        strftime: str, optional
            如果index是日期格式，则转换为字符串的格式, by default "%Y-%m"

        Returns
        -------
        pd.DataFrame
            返回一个数据透视后的pandas df
        """
        # 将日期列转换为Pandas日期时间类型，并设置为索引

        _df = pd.pivot_table(
            self.data.query(query_str),
            values=values,
            index=index,
            columns=columns,
            aggfunc=aggfunc,
        )
        # pivot table对象转为默认df
        _df = pd.DataFrame(_df.to_records())

        try:
            _df.set_index(index, inplace=True)
        except KeyError:  # 当index=None时，捕捉错误并set_index("index"字符串)
            _df.set_index("index", inplace=True)

        # 如果index是日期格式，则根据格式转换为字符串
        if index == self.date_column:
            _df.index = _df.index.strftime(strftime)

        if sort_values == "rows_by_last_col":
            _df = _df.sort_values(by=_df.columns[-1], ascending=sort_asc)
        elif sort_values == "rows_by_first_col":
            _df = _df.sort_values(by=_df.columns[0], ascending=sort_asc)
        elif sort_values == "rows_by_cols_sum":
            s = _df.sum(axis=1).sort_values(ascending=sort_asc)
            _df = _df.loc[s.index, :]  # 行按照汇总总和大小排序
        elif sort_values == "cols_by_rows_sum":
            s = _df.sum(axis=0).sort_values(ascending=sort_asc)
            _df = _df.loc[:, s.index]  # 列按照汇总总和大小排序

        if type(columns) is not list:
            if columns in self.sorter:
                _df = _df.reindex(columns=self.sorter[columns])

        if type(index) is not list:
            if index in self.sorter:
                _df = _df.reindex(self.sorter[index])  # 对于部分变量有固定排序

        # 删除所有都是缺失值的整行或整列
        if dropna:
            _df = _df.dropna(how="all")
            _df = _df.dropna(axis=1, how="all")

        # 缺失值替换
        if fillna is not None:
            _df = _df.fillna(fillna)

        if perc in [0, "index"]:
            _df = _df.div(_df.sum(axis=1), axis=0)  # 计算行汇总的百分比
        elif perc in [1, "columns"]:
            _df = _df.div(_df.sum(axis=0), axis=1)  # 计算列汇总的百分比

        return _df

    def transform(
        self,
        period: Literal[
            "MAT",
            "MQT",
            "YEAR",
            "QTR",
        ],
        cols_grouper: Union[List[str], str],
        cols_amount: Union[List[str], str],
    ) -> DfAnalyzer:
        """如有时间戳字段，将self.data转换为别的时间模式，原始数据可以为季度或月度数据

        Parameters
        ----------
        period : Literal[ "MAT", "MQT", "YEAR", "QTR", ]
            转换为什么时间模式
            MAT - 滚动年
            MQT - 滚动季
            YEAR - 自然年
            QTR - 自然季
        cols_grouper : Union[List[str], str]
            指出分组汇总数据时，哪些是分组字段
        cols_amount : Union[List[str], str]
            指出分组汇总数据时，哪些是数据字段

        Returns
        -------
        pd.DataFrame
            返回一个转换后的pandas df

        Raises
        ------
        DateError
            没有设定时间戳字段则会报错
        """
        if self.date_column is None:
            raise DateError("没有设定时间戳字段")

        new_obj = copy.copy(self)
        _df = self.data.copy()

        _df.set_index(self.date_column, inplace=True)

        if period in ["MAT", "MQT"]:
            # 根据时间戳间隔和转换目标，确定滚动周期，如本身数据如为QS(Quarter Start)，想转换为MAT数据，则滚动周期为4
            if self._freq[:2] == "QS":
                if period == "MAT":
                    rolling_window = 4
                elif period == "MQT":
                    rolling_window = 1
            elif self._freq[:2] == "MS":
                if period == "MAT":
                    rolling_window = 12
                elif period == "MQT":
                    rolling_window = 3

            # 按影响rolling计算的字段分组，并计算每个日期的滚动总计
            grouped = _df.groupby(cols_grouper)
            rolling = (
                grouped[cols_amount].rolling(window=rolling_window, min_periods=1).sum()
            )
            rolling = rolling.reset_index()

            # 将rolling统计还原到原df
            _df = _df.reset_index().rename(columns={"index": self.date_column})
            _df = _df.merge(
                right=rolling, how="left", on=cols_grouper + [self.date_column]
            )

        elif period in ["YEAR", "QTR"]:
            if period == "YEAR":
                resample_window = "Y"
            elif period == "QTR":
                resample_window = "Q"

            grouped = (
                _df.groupby(cols_grouper)
                .resample(resample_window)[cols_amount]
                .agg("sum")
            )
            grouped = grouped.reset_index()
            # resample("Y")方法返回的时间戳为年尾12.31，将其改为和原始数一致
            grouped["Date"] = grouped["Date"].apply(
                lambda x: x.replace(day=self.date.day)
            )

            # 将resample统计还原到原df
            _df = _df.reset_index().rename(columns={"index": self.date_column})
            _df = _df.merge(
                right=grouped, how="right", on=cols_grouper + [self.date_column]
            )

        # 解决merge后重复列都保留并自动重命名的问题
        if isinstance(cols_amount, str):
            cols_amount = [cols_amount]
        _df = _df.drop([s + "_x" for s in cols_amount], axis=1)
        _df = _df.rename(
            columns=lambda x: x.replace("_y", "")
            if x in [s + "_y" for s in cols_amount]
            else x
        )

        new_obj.data = _df

        return new_obj


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
            columns="谈判年份",
            query_str="数值类型=='金额'",
            values="数值",
        )
        .sort_index()
        .div(100000000)
    ).iloc[-6:]
    print(pivoted)
    # f = PlotStackedBar(
    #     data=pivoted,
    #     width=17,
    #     height=6,
    #     style={
    #         "title": "Test",
    #         "xticklabel_rotation": 90,
    #         # "xlabel": "年份",
    #         "ylabel": "金额",
    #         # "hide_top_right_spines": True,
    #         "major_grid":{"linewidth":1}
    #     },
    # )
    # f.style.title(title="陈诚")
    # f.plot(show_total_label=True)
    f = GridFigure(
        fontsize=12,
        style={
            "title": "123",
            "label_outer": True,
        },
    )
    f.plot_bar(
        data=pivoted,
        ax_index=0,
        style={
            "xticklabel_rotation": 0,
            "ylabel": "test",
        },
        show_label=True,
        show_total_label=True,
        show_total_bar=True,
        add_gr_text=True,
    )
    f.save()
