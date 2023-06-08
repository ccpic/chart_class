import os
from pptx import presentation, Presentation
from pptx.util import Inches, Pt, Cm
from pptx.shapes.base import BaseShape
from pptx.shapes.autoshape import Shape
from pptx.shapes.picture import Picture
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_VERTICAL_ANCHOR
from pptx.slide import SlideLayout, Slide
from typing import Any, Callable, Dict, List, Tuple, Union, Optional
from collections import namedtuple
import math

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


Loc = namedtuple("Loc", ["left", "top"])


class Section:
    def __init__(
        self,
        left: Union[Inches, Cm, int],
        top: Union[Inches, Cm, int],
        width: Union[Inches, Cm, int],
        height: Union[Inches, Cm, int],
    ) -> None:
        """初始化Section类，定义一个矩形范围

        Parameters
        ----------
        left: Union[Inches, Cm, int]
            左边距
        right: Union[Inches, Cm, int]
            右边距
        width: Union[Inches, Cm, int]
            宽度
        height: Union[Inches, Cm, int]
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


def is_light_color(color: Optional[Union[RGBColor, str]]) -> bool:
    """判断一个颜色是否是浅色

    Args:
        color (Optional[Union[RGBColor, str]]): 一个颜色，可以是pptx包的RGBColor类型，也可以是十六进制颜色字符串

    Returns:
        bool: 返回一个布尔值
    """
    if color is None:
        return True
    else:
        rgb_color = (
            color if isinstance(color, RGBColor) else RGBColor.from_string(color)
        )
        r, g, b = rgb_color
        hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))

        if hsp > 127.5:
            return True
        else:
            return False


def anchor_loc(
    shape_width: float,
    shape_height: float,
    loc: Loc,
    anchor: Literal[
        "center", "top_left", "left_top", "top_right", "right_top"
    ] = "center",
) -> Loc:
    """根据形状大小和不同锚点返回调整过的位置

    Args:
        shape_width (float): 形状宽度
        shape_height (float): 形状高度
        loc (Loc): 目标位置
        anchor (Literal["center", "top_left", "left_top", "top_right", "right_top"]): 锚点. Defaults to "center".

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
    return Loc(int(left), int(top))  # pptx很多参数如shape的top和left只接受整数


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

    def add_text(
        self,
        text: str,
        width: Union[Inches, Cm, int],
        height: Union[Inches, Cm, int],
        loc: Loc,
        anchor: Literal["center", "top_left", "top_right", "right_top"] = "center",
        fill_color: Optional[Union[RGBColor, str]] = None,
        line_color: Optional[Union[RGBColor, str]] = None,
        font_color: Optional[Union[RGBColor, str]] = None,
        font_size: Optional[Union[Pt, int]] = Pt(14),
        text_wrap: bool = False,
    ) -> Shape:
        left, top = anchor_loc(width, height, loc, anchor=anchor)
        shape = self.slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left=left,
            top=top,
            width=width,
            height=height,
        )

        # 形状填充
        fill = shape.fill
        if fill_color is None:
            fill.background()
        else:
            fill.solid()
            fill.fore_color.rgb = (
                fill_color
                if isinstance(fill_color, RGBColor)
                else RGBColor.from_string(fill_color)
            )

        # 边框
        line = shape.line
        if line_color is None:
            line.fill.background()
        else:
            line.color.rgb = (
                line_color
                if isinstance(line_color, RGBColor)
                else RGBColor.from_string(line_color)
            )

        # 形状文字
        text_frame = shape.text_frame
        text_frame.word_wrap = text_wrap
        p = text_frame.paragraphs[0]
        run = p.add_run()
        run.text = text

        # 设置字体
        font = run.font
        font.name = "Calibri"
        font.size = font_size
        font.bold = True
        font.italic = None  # cause value to be inherited from theme
        if font_color is None:
            if is_light_color(fill_color):
                font.color.rgb = RGBColor(0, 0, 0)
            else:
                font.color.rgb = RGBColor(255, 255, 255)
        else:
            font.color.rgb = (
                font_color
                if isinstance(font_color, RGBColor)
                else RGBColor.from_string(font_color)
            )

        return shape

    def add_image(
        self,
        image_file: str,
        width: Union[Inches, Cm, int],
        height: Union[Inches, Cm, int],
        loc: Loc,
        anchor: Literal["center", "top_left", "top_right", "right_top"] = "center",
    ) -> Picture:
        # 先插入图片，方便获取图片长宽（插入图片时如不同时指定宽和高，pptx高会自动缩放尺寸），再调整位置
        image = self.slide.shapes.add_picture(
            image_file=image_file,
            left=0,
            top=0,
            width=width,
            height=height,
        )

        left, top = anchor_loc(image.width, image.height, loc, anchor=anchor)
        image.left = left
        image.top = top

        return pic


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
    ) -> SlideContent:
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[layout_style])
        content = SlideContent(self.prs, slide)
        return content

    def save(self):
        self.prs.save(self.save_path)
        print("PPT has been saved")


if __name__ == "__main__":
    p = PPT("template.pptx")
    c = p.add_content_slide()
    c.add_text(
        "测试",
        width=Cm(4),
        height=Cm(0.5),
        loc=c.body.top_right,
        anchor="top_right",
        fill_color="F0CB46",
    )
    c.add_image(
        "D:\PyProjects\chart_class\plots\肾性贫血市场分治疗大类PTD滚动年趋势.png",
        width=c.body.width * 0.8,
        height=None,
        loc=c.body.center,
    )
    p.save()
