# Chart Class Library - AI Coding Agent Instructions

## 项目概述
这是一个基于 Matplotlib 的中文数据可视化库，专注于简化专业图表创建。核心设计理念：通过 `GridFigure` 提供统一画布，通过 Plot 子类实现各类图表的绘制。

## 架构模式

### 核心设计：Figure + Plot 组合模式
```python
# GridFigure 是主入口（继承自 matplotlib.figure.Figure）
f = plt.figure(FigureClass=GridFigure, width=15, height=6)

# 通过 f.plot() 方法动态实例化对应的 Plot 子类
f.plot(kind='bar', data=df, ax_index=0)  # 实际调用 PlotBar
```

**关键实现**：`chart/figure.py` 的 `plot()` 方法使用反射机制根据 `kind` 参数动态选择 Plot 类：
- `kind='bar'` → 实例化 `PlotBar(data, ax, ...).plot(**kwargs)`
- 所有 Plot 类必须在 `figure.py` 顶部导入（见 line 9-21）

### Plot 基类继承层次
所有绘图类继承自 `chart/plots/base.py::Plot`，必须实现 `plot()` 方法：

```python
class PlotBar(Plot):
    def plot(self, stacked=True, show_label=True, **kwargs) -> PlotBar:
        # 1. 使用 self._merge_style_kwargs() 合并样式参数
        # 2. 使用 self._get_color_for_item() 获取颜色
        # 3. 使用 self._create_label_dict() 创建标签数据
        return self
```

**基类提供的9个工具方法**（Phase 2 重构成果）：
- `_merge_style_kwargs()` - 合并默认样式和用户参数
- `_get_color_for_item()` / `_reset_color_cycle()` - 颜色管理
- `_calculate_share()` - 计算占比
- `_create_label_dict()` - 生成标签字典（支持 `{abs}`, `{share}`, `{gr}` 等占位符）
- `_format_axis()` - 格式化坐标轴
- `_add_colorbar()` / `_add_text_with_bbox()` - UI 组件

## 模块组织（v2.0 重构后）

### 导入规则
```python
# ✅ 正确：从模块导入
from chart import GridFigure, COLOR_DICT
from utils import DfAnalyzer, PPT

# ❌ 错误：不要从根导入文件
from figure import GridFigure  # 旧版本，已废弃
```

### 文件职责划分
- **chart/figure.py** - `GridFigure` 主类，处理网格布局、样式应用、图表路由
- **chart/plots/** - 17种图表类型，每个文件 1-4 个 Plot 子类
  - `specialty.py` 包含 4 个专业图表（Treemap/Heatmap/Waffle/Funnel）
- **chart/color.py** - 颜色配置（`COLOR_DICT`, `CMAP_QUAL`），中文品牌颜色映射
- **utils/dataframe.py** - 数据处理（`DfAnalyzer` 支持 MAT/YTD/MQT 时间转换）
- **utils/ppt.py** - PPT 生成（可选依赖 `python-pptx`）

## 开发工作流

### 添加新图表类型
1. 在 `chart/plots/` 下创建新文件或编辑 `specialty.py`
2. 继承 `Plot` 基类，实现 `plot()` 方法
3. 在 `chart/figure.py` 添加导入：`from chart.plots.xxx import PlotXxx`
4. 在 `chart/plots/__init__.py` 添加到 `__all__`
5. 创建 `example/xxx.py` 示例文件

### 测试模式
```bash
# 运行示例验证功能
python example/bar.py  # 生成图表到 example/plots/柱状图.png

# 示例数据准备模式（example/data.py）
from utils import DfAnalyzer
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "data.xlsx")
df = pd.read_excel(data_path)
```

### 关键约定

**中文优先**：
- 所有文档字符串使用中文
- 参数名使用英文，注释用中文
- 输出文件名、图表标题支持中文（依赖 `mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei"]`）

**数据格式**：
- 输入：`pandas.DataFrame`，索引为分类，列为数值或时间序列
- `DfAnalyzer` 假设存在 `date_column` 用于时间序列分析
- 数字格式化使用 `fmt` 参数（默认 `"{:,.0f}"`）

**样式系统**：
- 全局样式：通过 `GridFigure(style={...})` 设置
- 图表样式：通过 `f.plot(style={...})` 设置
- 样式键参考 `chart/plots/base.py::Plot.Style` 的 `d_style` 字典

**颜色管理**：
- 使用 `color_dict` 映射中文品牌名到十六进制颜色
- `focus` 参数高亮特定数据项
- `hue` 参数按列自动着色

## 常见陷阱

1. **导入错误**：Phase 2 后所有导入必须使用 `chart.` 或 `utils.` 前缀
2. **Plot 返回值**：`plot()` 方法必须 `return self` 以支持方法链
3. **ax_index**：多子图时，`ax_index` 从 0 开始计数（对应 GridSpec 位置）
4. **可选依赖**：`utils.ppt` 需要 `python-pptx`，捕获 ImportError 优雅降级
5. **路径处理**：数据文件使用相对于项目根的路径（见 `example/data.py::test_data()`）

## 参考文档
- 架构决策：`docs/PROJECT_RESTRUCTURE_SUMMARY.md`
- Phase 2 重构：`docs/PHASE2_SUMMARY.md`
- API 示例：`example/` 文件夹（11个图表类型）
