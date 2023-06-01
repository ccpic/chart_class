import os
from pptx import presentation, Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_VERTICAL_ANCHOR
from pptx.slide import SlideLayout, Slide


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


if __name__ == "__main__":
    p = PPT("template.pptx")
    print(p.parent_slide)
