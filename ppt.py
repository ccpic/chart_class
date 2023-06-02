import os
from pptx import presentation, Presentation
from pptx.util import Inches, Pt, Cm
from pptx.shapes.base import BaseShape
from pptx.shapes.autoshape import Shape
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_VERTICAL_ANCHOR
from pptx.slide import SlideLayout, Slide
from typing import Any, Callable, Dict, List, Tuple, Union, Optional
from collections import namedtuple

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


Loc = namedtuple("Loc", ["left", "top"])


class Section:
    def __init__(
        self,
        left: Union[Inches, Cm],
        top: Union[Inches, Cm],
        width: Union[Inches, Cm],
        height: Union[Inches, Cm],
    ) -> None:
        """初始化Section类，定义一个矩形范围

        Parameters
        ----------
        left: Union[Inches, Cm]
            左边距
        right: Union[Inches, Cm]
            右边距
        width: Union[Inches, Cm]
            宽度
        height: Union[Inches, Cm]
            高度
        """
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.right = self.left + self.width
        self.bottom = self.top + self.height

    def __repr__(self):
        return f"Section({self.left}, {self.top}, {self.width}, {self.height})"

    @property
    def left_top(self) -> Loc:
        """Section左上角坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.left, self.top)

    @property
    def mid_top(self) -> Loc:
        """Section上边居中位置坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.left + (self.width / 2), self.top)

    @property
    def right_top(self) -> Loc:
        """Section右上角坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.right, self.top)

    @property
    def left_mid(self) -> Loc:
        """Section左边居中位置坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.left, self.top + (self.height / 2))

    @property
    def center(self) -> Loc:
        """Section整体居中位置坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.left + (self.width / 2), self.top + (self.height / 2))

    @property
    def right_mid(self) -> Loc:
        """Section右边居中位置坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.right, self.top + (self.height / 2))

    @property
    def left_bottom(self) -> Loc:
        """Section左下角坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.left, self.bottom)

    @property
    def mid_bottom(self) -> Loc:
        """Section下边居中位置坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.left + (self.width / 2), self.bottom)

    @property
    def right_bottom(self) -> Loc:
        """Section右下角坐标

        Returns:
            Loc: 返回一个(左边距, 上边距)的tuple
        """
        return Loc(self.right, self.bottom)

    """alias"""
    top_left = left_top
    top_mid = mid_top
    top_right = right_top
    mid_left = left_mid
    mid = center
    mid_right = right_mid
    bottom_left = left_bottom
    bottom_mid = mid_bottom
    bottom_right = right_bottom


def anchor_loc(
    shape_width: float,
    shape_height: float,
    loc: Loc,
    anchor: Literal["center", "top_left", "top_right", "right_top"] = "center",
) -> Loc:
    """根据形状大小和不同锚点返回调整过的位置

    Args:
        shape_width (float): 形状宽度
        shape_height (float): 形状高度
        loc (Loc): 目标位置
        anchor (Literal["center", "top_left", "top_right", "right_top"]): 锚点. Defaults to "center".

    Returns:
        Loc: 返回一个代表调整后位置的tuple(左边距，上边距)
    """
    if anchor == "center":
        left = loc.left - shape_width / 2
        top = loc.top - shape_height / 2
    elif anchor in ["top_right", "right_top"]:
        left = loc.left - shape_width
        top = loc.top
    else:
        left = loc.left
        top = loc.top
    return Loc(left, top)


class SlideContent:
    def __init__(self, prs: Presentation, slide: Slide) -> None:
        self.prs = prs
        self.slide = slide

    @property
    def header(self) -> Section:
        return Section(
            left=Cm(0), top=Cm(0), width=self.prs.slide_width, height=Cm(2.72)
        )

    @property
    def body(self) -> Section:
        return Section(
            left=Cm(0), top=Cm(2.91), width=self.prs.slide_width, height=Cm(13.81)
        )

    @property
    def footer(self) -> Section:
        return Section(
            left=Cm(5.6), top=Cm(17.36), width=self.prs.slide_width, height=Cm(1.71)
        )

    def add_text(self):
        width = Cm(5)
        height = Cm(1)
        left, top = anchor_loc(width, height, self.body.top_right, anchor="top_right")
        obj_text = self.slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left=left,
            top=top,
            width=width,
            height=height,
        )


class PPT:
    def __init__(self, template_path: str, save_path: str = None) -> None:
        self.template_path = template_path
        self.save_path = (
            save_path or f"{os.path.dirname(self.template_path)}presentation.pptx"
        )
        self.prs = Presentation(template_path)

    @property
    def parent_slide(self) -> SlideLayout:
        """内容页幻灯片母版

        Returns
        -------
        SlideLayout
            返回该ppt的内容页幻灯片母版对象
        """
        slide = self.prs.slide_layouts[0]
        return slide

    def add_content_slide(
        self,
        layout_style: int = 0,
    ):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[layout_style])
        slide = SlideContent(self.prs, slide)
        t = slide.add_text()

    def save(self):
        self.prs.save(self.save_path)
        print("PPT has been saved")


if __name__ == "__main__":
    p = PPT("template.pptx")
    p.add_content_slide()
    p.save()
