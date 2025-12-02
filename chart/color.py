from matplotlib.colors import ListedColormap
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from itertools import cycle
from typing import Dict, Optional
import pandas as pd
import numpy as np
import warnings

# ===== 新的颜色管理系统 =====
# 颜色字典已迁移到数据库，不再使用硬编码
# 所有颜色映射应通过 color_dict 参数传入（从数据库获取）

# 颜色字典已迁移到数据库，不再使用硬编码
# 所有颜色映射应通过 color_dict 参数传入（从数据库获取）
COLOR_DICT: Dict[str, str] = {}
#     "#44546A",
#     "#6F8DB9",
#     "#BD2843",
#     "#ED94B6",
#     "#FAA53A",
#     "#2B9B33",
#     "Deepskyblue",
#     "Saddlebrown",
#     "Purple",
#     "Olivedrab",
#     "Pink",
# ]

COLOR_LIST = [
    "teal",
    "crimson",
    "navy",
    "darkorange",
    "darkgreen",
    "olivedrab",
    "purple",
    "pink",
    "deepskyblue",
    "saddlebrown",
    "tomato",
    "cornflowerblue",
    "magenta",
]

CMAP_QUAL = ListedColormap(COLOR_LIST)
CMAP_NORM = plt.get_cmap("PiYG")
RANDOM_CMAP = mpl.colors.ListedColormap(np.random.rand(256, 3))


def is_color_dark(color: str) -> bool:
    """
    判断一个颜色是深色还是浅色。
    参数:
        color (str): 可以是英文色名、hex字符串、rgb字符串等matplotlib支持的颜色格式
    返回:
        bool: 深色返回True，浅色返回False
    """
    rgb = mcolors.to_rgb(color)  # 转为0-1区间的r,g,b
    # 亮度算法（加权平均，符合人眼感知）
    luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return luminance < 0.5


class Colors:
    def __init__(
        self,
        color_dict: Optional[Dict[str, str]] = None,
        cmap_qual: mpl.colors.Colormap = CMAP_QUAL,
        cmap_norm: mpl.colors.Colormap = CMAP_NORM,
    ):
        self.color_dict = color_dict if color_dict is not None else {}
        self.cmap_qual = cmap_qual
        self.cmap_norm = cmap_norm
        self.iter_colors = cycle(self.cmap_qual(i) for i in range(self.cmap_qual.N))

    def get_color(self, name: str) -> str:
        color = self.color_dict.get(name, next(self.iter_colors))
        return color

    def get_colors(
        self,
        labels: pd.Series,
        color: str = None,
        hue: pd.Series = None,
        random_color: bool = True,
    ) -> list:
        if color is None:
            color = self.cmap_qual.colors[0]

        if hue is None:
            if random_color:
                cmap = RANDOM_CMAP
            else:
                cmap = ListedColormap([color])
            colors = [
                self.color_dict.get(labels[i], cmap(i)) for i in range(len(labels))
            ]
        else:
            # 如果hue字段是numeric
            if pd.api.types.is_numeric_dtype(hue.dtype):
                cmap = self.cmap_norm
                norm = mpl.colors.Normalize(vmin=min(hue), vmax=max(hue))
                colors = [cmap(norm(value)) for value in hue]
            # 如果hue字段是categorical
            else:
                cmap = self.cmap_qual
                levels, categories = pd.factorize(hue)

                colors = [self.color_dict.get(categories[i], cmap(i)) for i in levels]

        return cmap, colors
