"""
Script to split plots.py into modular files.
"""

import re
import os

# 读取原始文件
with open("plots.py", "r", encoding="utf-8") as f:
    content = f.read()

# 定义类到文件的映射
class_mapping = {
    "bar.py": ["PlotBar", "PlotBarh"],
    "line.py": ["PlotLine", "PlotArea"],
    "scatter.py": ["PlotBubble", "PlotStripdot"],
    "statistical.py": ["PlotHist", "PlotBoxdot"],
    "heatmap.py": ["PlotHeatmap"],
    "specialty.py": ["PlotTreemap", "PlotPie", "PlotWaffle", "PlotFunnel"],
    "text.py": ["PlotWordcloud", "PlotTable"],
    "venn.py": ["PlotVenn2", "PlotVenn3"],
}

# 提取imports部分(到第一个函数定义之前)
imports_end = content.find("def scatter_hist")
if imports_end == -1:
    imports_end = content.find("class Plot:")

imports = content[:imports_end].strip()


# 为每个模块创建必要的imports
def get_module_imports(class_names):
    """根据类名确定需要的imports"""
    base_imports = '''"""
Plot classes for chart types.
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union, Optional, Literal, Sequence
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from itertools import cycle
from plots.base import Plot
'''

    # 根据不同的类添加特定的imports
    special_imports = []

    for class_name in class_names:
        if class_name in ["PlotBar", "PlotBarh"]:
            if "cycle" not in base_imports:
                special_imports.append("from itertools import cycle")
        elif class_name in ["PlotLine", "PlotArea"]:
            special_imports.append("from adjustText import adjust_text")
        elif class_name == "PlotBubble":
            special_imports.extend(
                [
                    "from adjustText import adjust_text",
                    "from plots.utils import scatter_hist, regression_band",
                    "from mpl_toolkits.axes_grid1 import make_axes_locatable",
                    "import warnings",
                ]
            )
        elif class_name == "PlotStripdot":
            special_imports.extend(
                [
                    "from mpl_toolkits.axes_grid1 import make_axes_locatable",
                    "import warnings",
                    "import math",
                ]
            )
        elif class_name == "PlotBoxdot":
            special_imports.extend(
                ["import seaborn as sns", "from adjustText import adjust_text"]
            )
        elif class_name == "PlotWordcloud":
            special_imports.append("from wordcloud import WordCloud")
        elif class_name == "PlotHeatmap":
            special_imports.append("import seaborn as sns")
        elif class_name == "PlotHist":
            special_imports.append("import scipy.stats as stats")
        elif class_name in ["PlotTreemap"]:
            special_imports.extend(
                ["import squarify", "import matplotlib.patches as patches"]
            )
        elif class_name in ["PlotPie", "PlotWaffle", "PlotFunnel"]:
            if class_name == "PlotWaffle":
                special_imports.append("from pywaffle import Waffle")
            if class_name == "PlotFunnel":
                special_imports.extend(
                    [
                        "import matplotlib.patches as patches",
                        "from matplotlib.collections import PatchCollection",
                    ]
                )
        elif class_name in ["PlotVenn2", "PlotVenn3"]:
            special_imports.extend(
                [
                    "from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles"
                ]
            )
        elif class_name == "PlotTable":
            special_imports.append("from plottable import ColumnDefinition, Table")

    # 去重
    special_imports = list(dict.fromkeys(special_imports))

    if special_imports:
        return base_imports + "\n" + "\n".join(special_imports) + "\n\n"
    return base_imports + "\n\n"


# 提取每个类的代码
def extract_class_code(content, class_name):
    """提取指定类的代码"""
    pattern = rf"^class {class_name}\(Plot\):.*?(?=^class [A-Z]|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(0).rstrip()
    return None


print("Starting to split plots.py...")
print(f"Creating directory: plots/")

# 确保目录存在
os.makedirs("plots", exist_ok=True)

# 为每个文件创建内容
for filename, class_names in class_mapping.items():
    print(f"\nCreating {filename} with classes: {', '.join(class_names)}")

    # 生成imports
    file_content = get_module_imports(class_names)

    # 提取每个类的代码
    for class_name in class_names:
        class_code = extract_class_code(content, class_name)
        if class_code:
            file_content += class_code + "\n\n"
            print(f"  ✓ Extracted {class_name}")
        else:
            print(f"  ✗ Failed to extract {class_name}")

    # 写入文件
    filepath = os.path.join("plots", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"  → Written to {filepath}")

print("\n✓ All files created successfully!")
print("\nNext steps:")
print("1. Review the generated files in the plots/ directory")
print("2. Update figure.py to import from plots module")
print("3. Test that everything still works")
