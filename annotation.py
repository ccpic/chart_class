import matplotlib as mpl


class Connection:
    def __init__(
        self,
        ax: mpl.axes.Axes,
        x1: float,
        x2: float,
        y1: float,
        y2: float,
        text: str,
        offset: float = None,
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
        if offset == None:
            self.offset = (self._ax.get_ylim()[1] - self._ax.get_ylim()[0]) / 10
        else:
            self.offset = offset

    def draw(self, color="black", linewidth=1, linestyle="--") -> None:
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

        x_vline2 = [self.x2, self.x2]
        y_vline2 = [self.y2, self.y_max + self.offset]
        self._ax.plot(
            x_vline2, y_vline2, color=color, linewidth=linewidth, linestyle=linestyle
        )

        self._ax.text(
            (self.x1 + self.x2) / 2,
            self.y_max + self.offset,
            self.text,
            ha="center",
            va="bottom",
        )
