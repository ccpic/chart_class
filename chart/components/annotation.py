import matplotlib as mpl
from typing import Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class Connection:
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
        """_summary_

        Args:
            ax (mpl.axes.Axes): _description_
            x1 (float): _description_
            x2 (float): _description_
            y1 (float): _description_
            y2 (float): _description_
            text (str): _description_
            offset (float, optional): _description_. Defaults to None.
        """
        self._ax = ax
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.y_max = max(self.y1, self.y2)
        self.text = text
        if offset is None:
            self.offset = (self._ax.get_ylim()[1] - self._ax.get_ylim()[0]) / 10
        else:
            self.offset = offset

    def draw(
        self,
        color: str = "black",
        linewidth: float = 1,
        linestyle: str = "--",
        arrow: Optional[Literal[1, 2]] = None,
    ) -> None:
        x_hline = [self.x1, self.x2]
        y_hline = [self.y_max + self.offset, self.y_max + self.offset]
        self._ax.plot(
            x_hline, y_hline, color=color, linewidth=linewidth, linestyle=linestyle
        )

        x_vline1 = [self.x1, self.x1]
        y_vline1 = [self.y1, self.y_max + self.offset]
        self._ax.plot(
            x_vline1, y_vline1, color=color, linewidth=linewidth, linestyle=linestyle
        )
        if arrow == 1:
            self._ax.annotate(
                "",
                xy=(self.x1, self.y1),
                xytext=(self.x1, self.y1 + 0.1),
                arrowprops=dict(color=color, arrowstyle="->"),
                color=color,
            )

        x_vline2 = [self.x2, self.x2]
        y_vline2 = [self.y2, self.y_max + self.offset]
        self._ax.plot(
            x_vline2, y_vline2, color=color, linewidth=linewidth, linestyle=linestyle
        )
        if arrow == 2:
            self._ax.annotate(
                "",
                xy=(self.x2, self.y2),
                xytext=(self.x2, self.y2 + 0.1),
                arrowprops=dict(color=color, arrowstyle="->"),
                color=color,
            )

        self._ax.text(
            (self.x1 + self.x2) / 2,
            self.y_max + self.offset,
            self.text,
            ha="center",
            va="bottom",
            color=color,
            bbox=dict(facecolor="white", alpha=0.5, ec="black"),
        )
