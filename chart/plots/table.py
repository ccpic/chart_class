"""
Plot class for table chart type.
"""

from __future__ import annotations
from typing import Any, List, Optional
from chart.plots.base import Plot
from plottable import ColumnDefinition, Table


class PlotTable(Plot):
    """表格绘制类

    使用 plottable 库绘制美化表格，支持自定义列样式。
    """

    def plot(
        self,
        col_defs: Optional[List[ColumnDefinition]] = None,
        exclude_plot_rows: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PlotTable:
        """继承基本类，使用Plottable库绘制表格

        Args:
            col_defs (Optional[List[ColumnDefinition]]): 列样式定义, defaults to None.
            exclude_plot_rows (Optional[List[str]]): 跳过条形图的行索引列表，这些行仍会应用formatter, defaults to None.

        Returns:
            PlotTable: 返回一个自身实例
        """
        df = self.data

        # 如果指定了要跳过条形图的行，创建自定义Table类
        if exclude_plot_rows:
            from plottable.cell import create_cell, ColumnType, Row

            class CustomTable(Table):
                """自定义 Table 类，跳过指定行的 plot_fn"""

                def _get_row(self, idx: int, content: list) -> Row:
                    widths = self._get_column_widths()
                    x = 0
                    row = Row(cells=[], index=idx)

                    # 检查当前行是否应该跳过条形图
                    row_name = df.index[idx] if idx < len(df.index) else None
                    should_exclude_plot = row_name in exclude_plot_rows

                    for col_idx, (colname, width, _content) in enumerate(
                        zip(self.column_names, widths, content)
                    ):
                        col_def = self.column_definitions[colname]

                        # 如果当前行应该跳过条形图且有 plot_fn，则跳过 plot_fn，使用普通文本单元格
                        if "plot_fn" in col_def and not should_exclude_plot:
                            plot_fn = col_def.get("plot_fn")
                            plot_kw = col_def.get("plot_kw", {})

                            cell = create_cell(
                                column_type=ColumnType.SUBPLOT,
                                xy=(x, idx),
                                content=_content,
                                plot_fn=plot_fn,
                                plot_kw=plot_kw,
                                row_idx=idx,
                                col_idx=col_idx,
                                width=width,
                                rect_kw=self.cell_kw,
                                ax=self.ax,
                            )
                        else:
                            textprops = self._get_column_textprops(col_def)

                            # 如果当前行应该跳过条形图且有 plot_fn，需要从 plot_kw 中提取 formatter
                            if should_exclude_plot and "plot_fn" in col_def:
                                plot_kw = col_def.get("plot_kw", {})
                                if "formatter" in plot_kw:
                                    # 将 formatter 添加到 col_def 中，这样 _apply_column_formatters 就能处理它
                                    col_def["formatter"] = plot_kw["formatter"]

                            cell = create_cell(
                                column_type=ColumnType.STRING,
                                xy=(x, idx),
                                content=_content,
                                row_idx=idx,
                                col_idx=col_idx,
                                width=width,
                                rect_kw=self.cell_kw,
                                textprops=textprops,
                                ax=self.ax,
                            )

                        row.append(cell)
                        self.columns[colname].append(cell)
                        self.cells[(idx, col_idx)] = cell
                        cell.draw()

                        x += width

                    return row

            table_class = CustomTable
        else:
            table_class = Table

        self.table = table_class(
            df=df,
            ax=self.ax,
            column_definitions=col_defs,
            row_dividers=True,
            footer_divider=True,
            textprops={
                "fontsize": self.fontsize,
            },
            even_row_color="#eeeeee",
            row_divider_kw={"linewidth": 0.5, "linestyle": (0, (1, 5))},
            col_label_divider_kw={"linewidth": 1, "linestyle": "-"},
            col_label_cell_kw={"height": 2},
            column_border_kw={"linewidth": 1, "linestyle": "-"},
        ).autoset_fontcolors(colnames=[df.index.name] + list(df.columns))

        # 指定行背景色
        if kwargs.get("row_facecolors") is not None:
            row_facecolors = kwargs.get("row_facecolors")
            for i, row in enumerate(df.index):
                if row in row_facecolors.keys():
                    self.table.rows[i].set_facecolor(row_facecolors[row])

        # 指定行字体色
        if kwargs.get("row_fontcolors") is not None:
            row_fontcolors = kwargs.get("row_fontcolors")
            for i, row in enumerate(df.index):
                if row in row_fontcolors.keys():
                    self.table.rows[i].set_fontcolor(row_fontcolors[row])

        return self
