# Chart Class Library

一个用于数据可视化的 Python 库，提供简洁的 API 来创建各种专业图表。

## 📦 安装

```bash
git clone https://github.com/ccpic/chart_class.git
cd chart_class
pip install -r requirements.txt
```

## 🚀 快速开始

```python
import matplotlib.pyplot as plt
from chart import GridFigure
import pandas as pd

# 准备数据
df = pd.DataFrame({
    '类别': ['A', 'B', 'C', 'D'],
    '数值': [10, 25, 15, 30]
})

# 创建图表
f = plt.figure(
    FigureClass=GridFigure,
    width=10,
    height=6,
    fontsize=12
)

# 绘制柱状图
f.plot(
    kind='bar',
    data=df,
    ax_index=0,
    x='类别',
    y='数值'
)

# 保存图表
f.save()
```

## 📊 支持的图表类型

### 基础图表
- **柱状图** (`bar`, `barh`) - 横向/纵向柱状图
- **折线图** (`line`) - 折线图和面积图
- **饼图** (`pie`) - 饼图和环形图

### 散点图表
- **气泡图** (`bubble`) - 带大小维度的散点图
- **算珠图** (`stripdot`) - 带起止点的散点图

### 统计图表
- **直方图** (`hist`) - 数据分布直方图
- **箱型图** (`boxdot`) - 箱型图和散点组合

### 专业图表
- **热力图** (`heatmap`) - 数据热力图
- **树图** (`treemap`) - 矩形树图
- **华夫饼图** (`waffle`) - 华夫饼图
- **漏斗图** (`funnel`) - 漏斗图

### 其他
- **词云** (`wordcloud`) - 文字云图
- **维恩图** (`venn2`, `venn3`) - 2/3圆维恩图
- **表格** (`table`) - 数据表格

## 📁 项目结构

```
chart_class/
├── chart/              # 图表绘制核心模块
│   ├── figure.py       # GridFigure 主类
│   ├── color.py        # 颜色配置
│   └── plots/          # 各种绘图类
├── utils/              # 工具模块
│   ├── dataframe.py    # 数据分析工具
│   └── ppt.py          # PPT生成工具
├── data/               # 数据文件
├── example/            # 使用示例
└── docs/               # 文档
```

## 🔧 核心功能

### 1. 灵活的网格布局

```python
# 创建 2x2 的子图布局
f = plt.figure(
    FigureClass=GridFigure,
    nrows=2,
    ncols=2,
    width=15,
    height=12
)

# 在不同位置绘制图表
f.plot(kind='bar', data=df1, ax_index=0)
f.plot(kind='line', data=df2, ax_index=1)
f.plot(kind='pie', data=df3, ax_index=2)
f.plot(kind='heatmap', data=df4, ax_index=3)
```

### 2. 数据分析工具

```python
from utils import DfAnalyzer

# 创建分析器
analyzer = DfAnalyzer(
    data=df,
    name="销售数据",
    date_column="日期"
)

# 转换为滚动年数据
analyzer_mat = analyzer.transform(
    period="MAT",
    cols_amount="销售额"
)

# 生成数据透视表
pivot = analyzer.get_pivot(
    index="产品",
    columns="日期",
    values="销售额"
)
```

### 3. PPT 生成（可选）

```python
from utils import PPT

# 创建 PPT
ppt = PPT("template.pptx")
slide = ppt.add_content_slide()

# 添加标题和图片
slide.set_title("销售分析报告")
slide.add_image("chart.png", loc=slide.body.center)

# 保存
ppt.save("output.pptx")
```

## 🎨 自定义样式

```python
# 自定义颜色
from chart import COLOR_DICT, CMAP_QUAL

f = plt.figure(
    FigureClass=GridFigure,
    color_dict=COLOR_DICT,      # 自定义颜色字典
    cmap_qual=CMAP_QUAL,        # 自定义colormap
)

# 自定义样式
f.plot(
    kind='bar',
    data=df,
    style={
        'title': '销售数据',
        'xlabel': '产品',
        'ylabel': '销售额（万元）'
    },
    fmt='{:,.1f}',              # 数字格式
    show_label=True             # 显示数值标签
)
```

## 📖 示例

查看 `example/` 文件夹获取更多示例：

- `bar.py` - 柱状图示例
- `line.py` - 折线图示例
- `bubble.py` - 气泡图示例
- `heatmap.py` - 热力图示例
- `treemap.py` - 树图示例
- 更多...

运行示例：

```bash
python example/bar.py
python example/bubble.py
```

## 📚 文档

详细文档请查看 `docs/` 文件夹：

- [项目重构总结](docs/PROJECT_RESTRUCTURE_SUMMARY.md)
- [文件整合总结](docs/FILE_CONSOLIDATION_SUMMARY.md)
- [清理总结](docs/CLEANUP_SUMMARY.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 📮 联系

如有问题，请通过 GitHub Issues 联系。

---

**版本**: 2.0.0  
**更新日期**: 2025-11-07
