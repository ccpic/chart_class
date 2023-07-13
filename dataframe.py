from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Union, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from figure import GridFigure
import copy
import matplotlib.pyplot as plt

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

    def __repr__(self) -> str:
        return f"DateRange({self.date})"

    def mat(
        self,
        freq: Literal["MS", "3MS", "Q", "D"] = "MS",
        # 这里要用M而不是MS因为是month start
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
        period_interval: Optional[int] = None,
        strftime: str = "%Y-%m",
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
        strftime: str, optional
            指定时间戳的字符串格式, by default "%Y-%m"
        sorter : Dict[str, list], optional
            排序字典，key为要排序的字段名，value为排序顺序, by default {}
        save_path : str, optional
            导出数据或生成图片的文件路径, by default "/plots/"
        """
        self.data = data
        self.name = name
        self.date_column = date_column
        self._strftime = strftime

        if self.date_column is not None:
            try:
                self.data[self.date_column] = pd.to_datetime(
                    self.data[self.date_column]
                )  # 尝试将时间戳字段转换为datetime格式
                self.date = self.data[self.date_column].max()  # 如有时间戳字段，尝试寻找最后一期时间
                self._period_interval = period_interval
                # self._freq = pd.infer_freq(
                #     self.data[self.date_column].unique()
                # )  # 自动判断时间戳字段的频率间隔是多少
                # if self._freq[:2] == "QS":
                #     self._period_interval = 3
                # elif self._freq[:2] == "MS":
                #     self._period_interval = 1
                self.date_range = DateRange(self.date)

            except:
                raise DateError("时间戳字段解析失败")

        self.sorter = sorter
        self.save_path = save_path

    def __repr__(self) -> str:
        """函数描述

        Returns:
            str: 返回一个函数描述字符串
        """
        df = a.data
        columns = ", ".join(df.columns.to_list())
        return (
            f"DfAnalyzer({df.shape[0]} rows, {df.shape[1]} columns)\nColumns: {columns}"
        )

    def unit_change(
        self, unit_str: Optional[Literal["十亿", "亿", "百万", "万", "千"]]
    ) -> int:
        """根据中文单位字符串返回数值换算要除以的整数，如输入"万"，返回10000

        Args:
            unit_str (str, optional): 中文单位字符串.，可输入值["十亿", "亿", "百万", "万", "千"].

        Returns:
            int: 数值换算要除以的整数
        """
        D_UNIT_CHANGE = {
            None: 1,
            "十亿": 1000000000,
            "亿": 100000000,
            "百万": 1000000,
            "万": 10000,
            "千": 1000,
        }
        return D_UNIT_CHANGE.get(unit_str)

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

        Returns
        -------
        pd.DataFrame
            返回一个数据透视后的pandas df
        """
        # 将日期列转换为Pandas日期时间类型，并设置为索引

        df = pd.pivot_table(
            self.data.query(query_str),
            values=values,
            index=index,
            columns=columns,
            aggfunc=aggfunc,
        )
        # pivot table对象转为默认df
        df = pd.DataFrame(df.to_records())

        try:
            df.set_index(index, inplace=True)
        except KeyError:  # 当index=None时，捕捉错误并set_index("index"字符串)
            df.set_index("index", inplace=True)

        # 如果index是日期格式，则根据格式转换为字符串
        if index == self.date_column:
            df.index = df.index.strftime(self._strftime)

        if columns == self.date_column:
            df.columns = pd.to_datetime(df.columns)
            df.columns = df.columns.strftime(self._strftime)

        if sort_values == "rows_by_last_col":
            df = df.sort_values(by=df.columns[-1], ascending=sort_asc)
        elif sort_values == "rows_by_first_col":
            df = df.sort_values(by=df.columns[0], ascending=sort_asc)
        elif sort_values == "rows_by_cols_sum":
            s = df.sum(axis=1).sort_values(ascending=sort_asc)
            df = df.loc[s.index, :]  # 行按照汇总总和大小排序
        elif sort_values == "cols_by_rows_sum":
            s = df.sum(axis=0).sort_values(ascending=sort_asc)
            df = df.loc[:, s.index]  # 列按照汇总总和大小排序

        if type(columns) is not list:
            if columns in self.sorter:
                df = df.reindex(columns=self.sorter[columns])

        if type(index) is not list:
            if index in self.sorter:
                df = df.reindex(self.sorter[index])  # 对于部分变量有固定排序

        # 删除所有都是缺失值的整行或整列
        if dropna:
            df = df.dropna(how="all")
            df = df.dropna(axis=1, how="all")

        # 缺失值替换
        if fillna is not None:
            df.fillna(fillna, inplace=True)
            df.replace([np.inf, -np.inf], fillna, inplace=True)

        if perc in [0, "index"]:
            df = df.div(df.sum(axis=1), axis=0)  # 计算行汇总的百分比
        elif perc in [1, "columns"]:
            df = df.div(df.sum(axis=0), axis=1)  # 计算列汇总的百分比

        return df

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
        df = self.data.copy()

        df.set_index(self.date_column, inplace=True)

        if period in ["MAT", "MQT"]:
            # 根据时间戳间隔和转换目标，确定滚动周期
            if period == "MAT":
                rolling_window = int(12 / self._period_interval)
            elif period == "MQT":
                rolling_window = int(3 / self._period_interval)

            if cols_grouper is None:
                df = df.rolling(window=rolling_window, min_periods=1).sum()
            else:
                # 按影响rolling计算的字段分组，并计算每个日期的滚动总计
                grouped = df.groupby(cols_grouper)
                rolling = (
                    grouped[cols_amount]
                    .rolling(window=rolling_window, min_periods=1)
                    .sum()
                )
                rolling = rolling.reset_index()

                # 将rolling统计还原到原df
                df = df.reset_index().rename(columns={"index": self.date_column})
                df = df.merge(
                    right=rolling, how="left", on=cols_grouper + [self.date_column]
                )

        elif period in ["YEAR", "QTR"]:
            if period == "YEAR":
                resample_window = "Y"
            elif period == "QTR":
                resample_window = "Q"

            if cols_grouper is None:
                df = df.resample(resample_window).agg("sum")
            else:
                grouped = (
                    df.groupby(cols_grouper)
                    .resample(resample_window)[cols_amount]
                    .agg("sum")
                )
                grouped = grouped.reset_index()
                # resample("Y")方法返回的时间戳为年尾12.31，将其改为和原始数一致
                grouped["Date"] = grouped["Date"].apply(
                    lambda x: x.replace(day=self.date.day)
                )

                # 将resample统计还原到原df
                df = df.reset_index().rename(columns={"index": self.date_column})
                df = df.merge(
                    right=grouped, how="right", on=cols_grouper + [self.date_column]
                )

        if cols_grouper is not None:
            # 解决merge后重复列都保留并自动重命名的问题
            if isinstance(cols_amount, str):
                cols_amount = [cols_amount]
            df = df.drop([s + "_x" for s in cols_amount], axis=1)
            df = df.rename(
                columns=lambda x: x.replace("_y", "")
                if x in [s + "_y" for s in cols_amount]
                else x
            )

        new_obj.data = df

        return new_obj

    def ptable(
        self,
        index: str,
        values: str,
        hue: Optional[str] = None,
        date: Optional[str] = None,
        query_str: str = "ilevel_0 in ilevel_0",  # 默认query语句能返回df总体
        fillna: bool = False,
        show_total: bool = False,
    ) -> pd.DataFrame:
        """计算一个针对有时间戳df的kpi汇总表，kpis 包括(排名, 当期表现, 同比净增长, 份额, 份额变化, 同比增长率, Evolution Index)


        Args:
            index (str): 透视表的行标签字段
            values (str): 透视表的值字段
            hue (Optional[str], optional): 分类标签字段. Defaults to None.
            date (Optional[str], optional): 指定日期，如不指定则以最新日期计算. Defaults to None.
            query_str (str, optional): 数据筛选字符串,如"Date=='2022-12'"_. Defaults to "ilevel_0 in ilevel_0".
            show_total (bool, optional): 是否显示汇总. Defaults to False.

        Returns:
            pd.DataFrame: _description_
        """
        df_ts = self.get_pivot(
            index=index,
            columns=self.date_column,
            values=values,
            query_str=query_str,
        )

        if date is None:
            df = df_ts.iloc[:, -1]  # 如果不指定date，则默认为最latest
            date_ya = int(((12 / self._period_interval) + 1) * -1)  # 根据期数计算year ago
            df_ya = df_ts.iloc[:, date_ya]
        else:
            df = df_ts.loc[:, date]
            date_ya = (pd.Timestamp(date) - pd.DateOffset(years=1)).strftime(
                self._strftime
            )  # 根据时间戳计算year ago
            df_ya = df_ts.loc[:, date_ya]

        df_rank = df.rank(ascending=False)  # 排名
        df_share = df.div(df.sum())  # 本期份额
        df_ya_share = df_ya.div(df_ya.sum())  # 上期份额
        df_share_diff = df_share.subtract(df_ya_share)  # 份额变化
        df_diff = df.subtract(df_ya)  # 净增长
        df_gr = df.div(df_ya).subtract(1)  # 增长率
        df_ei = df.div(df_ya).div(df.sum() / df_ya.sum()).mul(100)  # Evolution Index

        df_combined = pd.concat(
            [df_rank, df, df_diff, df_share, df_share_diff, df_gr, df_ei], axis=1
        )
        df_combined.columns = ["排名", "表现", "同比净增长", "份额", "份额变化", "同比增长率", "EI"]
        df_combined = df_combined.sort_values(by="表现", ascending=False)

        if hue:
            df_combined = df_combined.merge(
                self.data[[index, hue]], how="left", left_index=True, right_on=index
            )
            df_combined = df_combined.drop_duplicates()
            df_combined.set_index(index, inplace=True)
            df_combined.insert(1, hue, df_combined.pop(hue))

        if show_total:
            d_total = {}
            df_total = self.get_pivot(
                index=None,
                columns=self.date_column,
                values=values,
                query_str=query_str,
            )

            if date is None:
                d_total["表现"] = df_total.iloc[:, -1].values[0]
                date_ya = int(((12 / self._period_interval) + 1) * -1)  # 根据期数计算year ago
                total_ya = df_total.iloc[:, date_ya].values[0]
            else:
                d_total["表现"] = df_total.loc[:, date].values[0]
                date_ya = (pd.Timestamp(date) - pd.DateOffset(years=1)).strftime(
                    self._strftime
                )  # 根据时间戳计算year ago
                total_ya = df_total.loc[:, date_ya].values[0]

            d_total["同比净增长"] = d_total["表现"] - total_ya
            d_total["份额"] = 1
            d_total["份额变化"] = 0
            if total_ya != 0:
                d_total["同比增长率"] = d_total["表现"] / total_ya - 1
            else:
                d_total["同比增长率"] = np.inf
            d_total["EI"] = 100

            df_combined = df_combined.append(pd.Series(d_total, name="汇总"))

        if fillna:
            df_combined = df_combined.fillna(0)
            df_combined.replace([np.inf, -np.inf], 0, inplace=True)

        return df_combined


if __name__ == "__main__":
    df = pd.read_excel("data.xlsx", engine="openpyxl")
    a = DfAnalyzer(data=df, name="test", date_column="Date", period_interval=3)
    a = a.transform(
        period="MAT",
        cols_grouper=["分子+年份+降幅", "CORPORATION", "PACKAGE", "数值类型"],
        cols_amount="数值",
    )
    print(
        a.ptable(
            index="MOLECULE_CN",
            values="数值",
            hue="TC I",
            query_str="数值类型=='金额'",
            show_total=True,
        )
    )
    # pivoted = (
    #     a.get_pivot(
    #         index=["谈判年份", "药品名称"],
    #         columns=a.date_column,
    #         query_str="数值类型=='金额'",
    #         values="数值",
    #     )
    #     .div(100000000)
    #     .reset_index()
    #     .set_index("药品名称")
    # )
    # print(pivoted)

    # f = plt.figure(
    #     FigureClass=GridFigure,
    #     width=11,
    #     height=10,
    #     ncols=1,
    #     fontsize=11,
    #     style={
    #         "title": "Test",
    #         "label_outer": False,
    #     },
    # )

    # f.plot_bubble(
    #     data=pivoted,
    #     ax_index=0,
    #     style={},
    #     x="2022-12",
    #     y="2021-12",
    #     z="2022-12",
    #     hue="谈判年份",
    #     label_limit=100,
    #     label_formatter="{index}\n({x}, {y})",
    #     x_fmt="{:,.1f}",
    #     y_fmt="{:,.1f}",
    #     show_hist=True,
    #     show_legend=False,
    # )

    # f.save()
