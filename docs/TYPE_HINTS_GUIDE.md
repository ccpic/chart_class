# Chart Class Library - 类型注解指南

## 概述

本项目采用 Python 类型注解（Type Hints）来提高代码质量、可维护性和开发体验。本指南说明项目中类型注解的使用规范和最佳实践。

## 基本原则

### 1. 导入规范

```python
# ✅ 推荐：使用 typing 模块的标准类型
from typing import Any, Dict, List, Tuple, Optional, Literal, Union

# ✅ 推荐：使用 from __future__ import annotations 支持前向引用
from __future__ import annotations

# ✅ 推荐：第三方库类型
import pandas as pd
import matplotlib.axes as mpl_axes
```

### 2. 常用类型注解

#### 基础类型
```python
def plot(
    self,
    stacked: bool = True,              # 布尔值
    show_label: bool = True,           # 布尔值
    label_threshold: float = 0.02,     # 浮点数
    period_change: int = 1,            # 整数
) -> PlotBar:                          # 返回值类型
    pass
```

#### Optional 类型
```python
# ✅ 推荐：可选参数使用 Optional
def plot(
    self,
    x: Optional[str] = None,           # 可以是 str 或 None
    savepath: Optional[str] = None,    # 可以是 str 或 None
) -> PlotBubble:
    pass

# ❌ 避免：不要使用 str = None 而不标注 Optional
def plot(self, x: str = None):  # 错误！
    pass
```

#### Union 类型
```python
# ✅ 多种可能类型使用 Union
def add_table(
    self,
    col_format: Union[List[str], Dict[str, str], str] = "abs",
) -> GridFigure:
    pass

# Pandas 数据类型
def __init__(
    self,
    data: Union[pd.DataFrame, pd.Series],
    ax: Optional[mpl.axes.Axes] = None,
) -> None:
    pass
```

#### Literal 类型
```python
# ✅ 推荐：限定字符串参数为特定值
def plot(
    self,
    kind: Literal[
        "bar", "barh", "line", "area", "bubble", 
        "stripdot", "hist", "boxdot", "treemap",
        "heatmap", "waffle", "funnel", "pie",
        "wordcloud", "table", "venn2", "venn3"
    ],
    axis: Literal["x", "y", "both"] = "both",
) -> mpl.axes.Axes:
    pass

# 数字 Literal
def transform(
    self,
    perc: Optional[Literal[1, 0, "index", "columns"]] = None,
) -> pd.DataFrame:
    pass
```

#### 容器类型
```python
# List
show_label: List[str] = []           # 字符串列表
colors: Optional[List[str]] = None   # 可选的字符串列表

# Dict
style: Dict[str, Any] = {}           # 字典，值可以是任意类型
d_label: Dict[str, str] = {}         # 字典，值必须是字符串

# Tuple
xlim: Optional[Tuple[float, float]] = None  # 二元组
set_labels: Optional[tuple] = None          # 任意长度元组
```

#### **kwargs 类型
```python
# ✅ 推荐：为 **kwargs 添加类型注解
def plot(
    self,
    stacked: bool = True,
    **kwargs: Any,  # 关键字参数可以是任意类型
) -> PlotBar:
    pass
```

## 模块规范

### chart/figure.py - GridFigure 类

**核心方法类型注解示例**：

```python
def plot(
    self,
    kind: Literal["bar", "barh", "line", ...],  # 18种图表类型
    data: pd.DataFrame,
    ax_index: int = 0,
    style: Dict[str, Any] = {},
    **kwargs: Any,
) -> mpl.axes.Axes:
    """动态选择 Plot 子类并绘图"""
    pass

def save(
    self, 
    savepath: Optional[str] = None,  # 使用 Optional
    dpi: int = 300
) -> None:
    """保存图表"""
    pass
```

### chart/plots/base.py - Plot 基类

**基类初始化**：
```python
class Plot:
    """所有绘图类的基类"""
    
    def __init__(
        self,
        data: Union[pd.DataFrame, pd.Series],  # 支持两种数据类型
        ax: Optional[mpl.axes.Axes] = None,
        figure: Optional[GridFigure] = None,
        hue: Optional[pd.Series] = None,
        focus: Optional[List[str]] = None,
        fmt: str = "{:,.0f}",
        fontsize: int = 11,
    ) -> None:
        pass
```

**工具方法**：
```python
def _merge_style_kwargs(
    self, 
    default_style: Dict[str, Any], 
    **kwargs: Any
) -> Dict[str, Any]:
    """合并默认样式和用户参数"""
    pass

def _get_color_for_item(
    self, 
    item: str, 
    stacked: bool = False
) -> str:
    """获取数据项的颜色"""
    pass

def _create_label_dict(
    self,
    value: Optional[float] = None,
    share: Optional[float] = None,
    gr: Optional[float] = None,
    index: Optional[str] = None,
    col: Optional[str] = None,
    **extra_fields: Any,
) -> Dict[str, str]:
    """创建标签格式化字典"""
    pass
```

### chart/plots/*.py - Plot 子类

**统一模式**：
```python
from __future__ import annotations
from typing import Any, Optional, List, Literal
from chart.plots.base import Plot

class PlotBar(Plot):
    """柱状图绘制类
    
    支持堆积/并列柱状图、数据标签、增长率线、平均线等功能。
    """
    
    def plot(
        self,
        stacked: bool = True,
        show_label: bool = True,
        label_formatter: str = "{abs}",
        label_threshold: float = 0.02,
        **kwargs: Any,
    ) -> PlotBar:  # 返回自身类型
        """绘制柱状图
        
        Args:
            stacked: 是否堆积
            show_label: 是否显示数据标签
            label_formatter: 标签格式
            label_threshold: 显示标签的阈值
            **kwargs: 其他样式参数
            
        Returns:
            返回自身实例以支持方法链
        """
        # 实现...
        return self  # 必须返回 self
```

### utils/dataframe.py - DfAnalyzer 类

```python
class DfAnalyzer:
    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        date_column: Optional[str] = None,
        period_interval: int = 1,
        strftime: str = "%Y-%m",
        sorter: Dict[str, list] = {},
        save_path: str = "/plots/",
    ) -> None:
        pass

    def get_pivot(
        self,
        index: Optional[str] = None,
        columns: Optional[str] = None,
        values: Optional[str] = None,
        aggfunc: Callable = sum,  # 可调用对象
        sort_values: Optional[
            Literal[
                "rows_by_last_col",
                "rows_by_first_col",
                "rows_by_cols_sum",
                "cols_by_rows_sum",
            ]
        ] = "rows_by_last_col",
        fillna: Optional[Union[int, float, str]] = 0,
    ) -> pd.DataFrame:
        pass
```

### utils/ppt.py - PPT 类

```python
from pptx.util import Inches, Cm

class Loc:
    def __init__(
        self, 
        left: Union[Inches, Cm, int], 
        top: Union[Inches, Cm, int]
    ) -> None:
        """位置类，定义PPT对象的坐标"""
        pass

    def __add__(
        self,
        other: Union[
            Tuple[Union[Inches, Cm, int], Union[Inches, Cm, int]],
            List[Union[Inches, Cm, int]],
        ],
    ) -> Loc:
        """支持位置运算"""
        pass
```

## 类型注解检查

### 使用 mypy 进行类型检查

安装 mypy：
```bash
pip install mypy
```

运行类型检查：
```bash
# 检查整个项目
mypy chart/ utils/

# 检查特定文件
mypy chart/figure.py

# 严格模式
mypy --strict chart/plots/
```

### VS Code 集成

在 `.vscode/settings.json` 中配置：
```json
{
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

## 常见问题

### 1. Any 的使用

```python
# ✅ 合理使用：当类型确实可以是任意值时
def _merge_style_kwargs(
    self, 
    default_style: Dict[str, Any],  # 样式值可以是多种类型
    **kwargs: Any,
) -> Dict[str, Any]:
    pass

# ❌ 避免：不要过度使用 Any
def process_data(data: Any) -> Any:  # 太宽泛
    pass
```

### 2. 前向引用

```python
# ✅ 推荐：使用 from __future__ import annotations
from __future__ import annotations

class PlotBar(Plot):
    def plot(self) -> PlotBar:  # 可以引用自身
        return self

# 或使用字符串
class PlotBar(Plot):
    def plot(self) -> "PlotBar":  # 字符串形式
        return self
```

### 3. 返回值类型

```python
# ✅ 明确返回值类型
def plot(self) -> PlotBar:
    return self

def save(self) -> None:  # 无返回值使用 None
    pass

def get_data(self) -> pd.DataFrame:
    return self.data
```

### 4. 可变默认参数

```python
# ❌ 避免：可变对象作为默认参数
def plot(self, show_label: List[str] = []):  # 危险！
    pass

# ✅ 推荐：使用 None 并在函数内初始化
def plot(self, show_label: Optional[List[str]] = None):
    if show_label is None:
        show_label = []
```

## 文档字符串与类型注解

### 结合 Google 风格 Docstring

```python
def plot(
    self,
    stacked: bool = True,
    show_label: bool = True,
    label_formatter: str = "{abs}",
    **kwargs: Any,
) -> PlotBar:
    """绘制柱状图
    
    Args:
        stacked: 是否堆积柱状图
        show_label: 是否显示数据标签
        label_formatter: 标签格式，支持占位符 {abs}, {share}, {gr}
        **kwargs: 其他样式参数
        
    Returns:
        返回自身实例以支持方法链
        
    Example:
        >>> f = plt.figure(FigureClass=GridFigure)
        >>> f.plot(kind='bar', data=df, stacked=True, show_label=True)
    """
    pass
```

## 类型注解的好处

1. **IDE 智能提示**：更好的代码补全和参数提示
2. **早期错误检测**：在运行前发现类型错误
3. **文档作用**：类型注解本身就是文档的一部分
4. **代码维护**：重构时更容易发现不兼容的修改
5. **团队协作**：明确的接口约定

## 参考资源

- [Python 官方文档 - typing 模块](https://docs.python.org/3/library/typing.html)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [mypy 文档](https://mypy.readthedocs.io/)
- [Pandas 类型注解](https://pandas.pydata.org/docs/development/contributing_codebase.html#type-hints)

## 更新日志

- **v2.0** (2024): 完成全项目类型注解优化
  - GridFigure 类所有公共方法
  - Plot 基类和17个子类
  - utils 模块主要类（DfAnalyzer, PPT, Loc, Section）
