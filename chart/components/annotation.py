import matplotlib as mpl
from typing import Optional, Any, Dict

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class Connection:
    """在图表中绘制连接两个数据点的注释线

    该类用于在柱状图等图表中，连接两个数据点并显示注释文本。
    绘制效果：
    - 在两点上方绘制一条水平连接线
    - 从两个点分别向上绘制垂直线连接到水平线
    - 在水平线上方居中显示文本标签
    - 可选择在某个端点添加箭头

    典型应用场景：
    - 柱状图中标注两个柱子之间的对比关系
    - 显示数据点之间的差值或变化
    """

    def __init__(
        self,
        ax: mpl.axes.Axes,
        x1: float,
        x2: float,
        y1: float,
        y2: float,
        text: str,
        offset: Optional[float] = None,
    ) -> None:
        """初始化连接对象

        Args:
            ax (mpl.axes.Axes): matplotlib 坐标轴对象，用于绘制
            x1 (float): 第一个点的 x 坐标
            x2 (float): 第二个点的 x 坐标
            y1 (float): 第一个点的 y 坐标（数据值）
            y2 (float): 第二个点的 y 坐标（数据值）
            text (str): 显示在水平连接线上方的文本标签
            offset (Optional[float], optional): 水平连接线距离最高点的垂直偏移量。
                如果为 None，则自动计算为 y 轴范围的 1/10。Defaults to None.
        """
        self._ax = ax
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        # 计算两个点中 y 值较大的那个，用于确定水平连接线的位置
        self.y_max = max(self.y1, self.y2)
        self.text = text
        # 如果未指定偏移量，则使用 y 轴范围的 1/10 作为默认偏移
        if offset is None:
            ylim = self._ax.get_ylim()
            self.offset = (ylim[1] - ylim[0]) / 10
        else:
            self.offset = offset

    def draw(
        self,
        color: str = "black",
        linewidth: float = 1,
        linestyle: str = "--",
        arrow: Optional[Literal[1, 2]] = None,
        text_color: Optional[str] = None,
        text_weight: Optional[str] = None,
        text_size: Optional[float] = None,
        text_offset: Optional[float] = None,
        bbox_facecolor: Optional[str] = None,
        bbox_edgecolor: Optional[str] = None,
        bbox_alpha: Optional[float] = None,
        bbox_boxstyle: Optional[str] = None,
        bbox_linewidth: Optional[float] = None,
    ) -> None:
        """绘制连接线和文本标签

        Args:
            color (str, optional): 线条和文本的颜色。Defaults to "black".
            linewidth (float, optional): 线条宽度。Defaults to 1.
            linestyle (str, optional): 线条样式，如 "--"（虚线）、"-"（实线）等。Defaults to "--".
            arrow (Optional[Literal[1, 2]], optional): 是否在端点添加箭头。
                1 表示在第一个点 (x1, y1) 添加箭头，
                2 表示在第二个点 (x2, y2) 添加箭头，
                None 表示不添加箭头。Defaults to None.
            text_color (Optional[str], optional): 文本颜色。如果为 None，则使用 color。Defaults to None.
            text_weight (Optional[str], optional): 文本字重，如 "normal", "bold", "semibold" 等。Defaults to None.
            text_size (Optional[float], optional): 文本字体大小。Defaults to None.
            text_offset (Optional[float], optional): 文本相对于水平连接线的垂直偏移量。
                如果为 None，则使用默认偏移（基于字体大小）。Defaults to None.
            bbox_facecolor (Optional[str], optional): 文本框背景颜色。Defaults to None.
            bbox_edgecolor (Optional[str], optional): 文本框边框颜色。Defaults to None.
            bbox_alpha (Optional[float], optional): 文本框背景透明度（0-1）。Defaults to None.
            bbox_boxstyle (Optional[str], optional): 文本框样式，如 "round", "round,pad=0.5", "circle" 等。Defaults to None.
            bbox_linewidth (Optional[float], optional): 文本框边框宽度。Defaults to None.
        """
        # 绘制水平连接线（在两点上方）
        x_hline = [self.x1, self.x2]
        y_hline = [self.y_max + self.offset, self.y_max + self.offset]
        self._ax.plot(
            x_hline, y_hline, color=color, linewidth=linewidth, linestyle=linestyle
        )

        # 绘制从第一个点向上的垂直线
        x_vline1 = [self.x1, self.x1]
        y_vline1 = [self.y1, self.y_max + self.offset]
        self._ax.plot(
            x_vline1, y_vline1, color=color, linewidth=linewidth, linestyle=linestyle
        )
        # 如果指定在第一个点添加箭头
        if arrow == 1:
            self._ax.annotate(
                "",
                xy=(self.x1, self.y1),  # 箭头指向的点
                xytext=(self.x1, self.y1 + 0.1),  # 箭头起始点（向上偏移 0.1）
                arrowprops=dict(color=color, arrowstyle="->"),
                color=color,
            )

        # 绘制从第二个点向上的垂直线
        x_vline2 = [self.x2, self.x2]
        y_vline2 = [self.y2, self.y_max + self.offset]
        self._ax.plot(
            x_vline2, y_vline2, color=color, linewidth=linewidth, linestyle=linestyle
        )
        # 如果指定在第二个点添加箭头
        if arrow == 2:
            self._ax.annotate(
                "",
                xy=(self.x2, self.y2),  # 箭头指向的点
                xytext=(self.x2, self.y2 + 0.1),  # 箭头起始点（向上偏移 0.1）
                arrowprops=dict(color=color, arrowstyle="->"),
                color=color,
            )

        # 在水平连接线上方居中显示文本标签
        # 计算文本的垂直位置（考虑文本偏移量）
        text_y_offset = text_offset if text_offset is not None else 0.0
        text_y = self.y_max + self.offset + text_y_offset

        # 构建文本样式参数
        text_kwargs: Dict[str, Any] = {
            "ha": "center",  # 水平对齐：居中
            "va": "bottom",  # 垂直对齐：底部对齐（文本在线上方）
        }

        # 文本颜色：优先使用 text_color，否则使用 color
        text_kwargs["color"] = text_color if text_color is not None else color

        # 文本字重
        if text_weight is not None:
            text_kwargs["weight"] = text_weight

        # 文本字体大小
        if text_size is not None:
            text_kwargs["fontsize"] = text_size

        # 构建文本框样式
        bbox_dict: Dict[str, Any] = {}
        if bbox_facecolor is not None:
            bbox_dict["facecolor"] = bbox_facecolor
        else:
            bbox_dict["facecolor"] = "white"  # 默认白色背景

        if bbox_alpha is not None:
            bbox_dict["alpha"] = bbox_alpha
        else:
            bbox_dict["alpha"] = 0.5  # 默认半透明

        if bbox_edgecolor is not None:
            bbox_dict["edgecolor"] = bbox_edgecolor
        else:
            bbox_dict["edgecolor"] = "black"  # 默认黑色边框

        # 文本框样式（boxstyle）
        if bbox_boxstyle is not None:
            bbox_dict["boxstyle"] = bbox_boxstyle

        # 文本框边框宽度
        if bbox_linewidth is not None:
            bbox_dict["linewidth"] = bbox_linewidth

        text_kwargs["bbox"] = bbox_dict

        self._ax.text(
            (self.x1 + self.x2) / 2,  # x 坐标：两点中点
            text_y,  # y 坐标：水平连接线位置 + 文本偏移量
            self.text,
            **text_kwargs,
        )
