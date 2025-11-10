# Chart Class Web 可视化工具开发计划

## 项目概述

基于现有的 `chart_class2` Python 绘图库，构建一个全栈 Web 可视化工具，实现在线数据准备、参数配置和图表生成功能。

### 技术栈

**后端**：
- FastAPI - 高性能 Python Web 框架
- chart_class - 现有的 Matplotlib 绘图库
- Pydantic - 数据验证
- python-multipart - 文件上传
- Pillow - 图片处理

**前端**：
- Next.js 14+ (App Router) - React 框架
- TypeScript - 类型安全
- Tailwind CSS - 样式框架
- shadcn/ui - UI 组件库
- React Hook Form - 表单管理
- Zustand/Redux - 状态管理
- AG Grid / Handsontable - 表格编辑器

**风格定位**：
- 商务风格
- 黑白主题（暗色模式可选）
- 简洁、专业的 UI 设计

---

## 功能模块分解

### 1. 画布模块 (Canvas Module)

#### 1.1 Grid 布局设计器
**功能描述**：
- 可视化配置 GridFigure 的网格布局
- 支持拖拽调整网格大小和位置
- 支持嵌套网格（GridSpec 嵌套）
- 实时预览布局结构

**核心功能**：
- [ ] 网格行列数设置（rows, cols）
- [ ] 子图位置选择（ax_index）
- [ ] 网格合并（跨行跨列）
- [ ] 画布尺寸设置（width, height）
- [ ] 全局样式配置
  - [ ] 字体族（font family）
  - [ ] 标题对齐（title_align）
  - [ ] 外边距（outer_space）
  - [ ] 内边距（inner_space）
  - [ ] 是否显示外边框（label_outer）

**数据结构示例**：
```typescript
interface CanvasConfig {
  id: string;
  width: number;        // 画布宽度（英寸）
  height: number;       // 画布高度（英寸）
  rows: number;         // 网格行数
  cols: number;         // 网格列数
  style: {
    title_align?: 'left' | 'center' | 'right';
    outer_space?: number;
    inner_space?: number;
    label_outer?: boolean;
    font_family?: string;
  };
  subplots: SubplotConfig[];  // 子图配置列表
}

interface SubplotConfig {
  id: string;
  ax_index: number;     // 子图在网格中的位置
  rowspan?: number;     // 跨行数
  colspan?: number;     // 跨列数
  chart_type: string;   // 图表类型（对应 kind 参数）
  data_id?: string;     // 关联的数据集 ID
  params: ChartParams;  // 图表参数
}
```

**UI 设计**：
```
┌─────────────────────────────────────────────────┐
│  Canvas Designer                         [Save] │
├─────────────────────────────────────────────────┤
│ ┌─────────┐  Layout: [3] rows × [2] cols       │
│ │  Grid   │  Size: [15] w × [6] h (inches)     │
│ │Preview  │                                     │
│ │         │  ┌─────────────────────────────┐   │
│ │ ┌─┬─┐   │  │ Subplot 1                   │   │
│ │ │1│2│   │  │ Type: Bar Chart             │   │
│ │ ├─┼─┤   │  │ Position: [0] (ax_index)    │   │
│ │ │3│4│   │  │ [Edit Data] [Configure]     │   │
│ │ ├─┴─┤   │  └─────────────────────────────┘   │
│ │ │ 5 │   │                                     │
│ │ └───┘   │  + Add Subplot                     │
│ └─────────┘                                     │
└─────────────────────────────────────────────────┘
```

---

### 2. 绘图模块 (Chart Module)

#### 2.1 数据准备子模块 (Data Preparation)

**功能描述**：
- 提供类 Excel 的数据编辑界面
- 支持多种数据导入方式
- 数据验证和预览

**核心功能**：

**2.1.1 数据导入**
- [ ] 文件上传（Excel, CSV, JSON）
  - [ ] 拖拽上传
  - [ ] 文件格式验证
  - [ ] 自动解析表头和数据类型
- [ ] 手动输入
  - [ ] Excel 式单元格编辑
  - [ ] 行列增删
  - [ ] 数据类型设置（文本/数字/日期）
- [ ] 剪贴板粘贴
  - [ ] 从 Excel/Google Sheets 复制
  - [ ] 智能格式识别

**2.1.2 数据管理**
- [ ] 数据集列表
  - [ ] 多个数据集管理
  - [ ] 数据集重命名
  - [ ] 数据集删除
- [ ] 数据预览
  - [ ] 前10行预览
  - [ ] 数据统计（行数、列数、数据类型）
  - [ ] 缺失值检测

**数据结构示例**：
```typescript
interface Dataset {
  id: string;
  name: string;
  created_at: string;
  columns: ColumnDef[];
  rows: any[][];
  metadata: {
    row_count: number;
    col_count: number;
    has_index: boolean;
    index_name?: string;
  };
}

interface ColumnDef {
  name: string;
  type: 'string' | 'number' | 'date';
  format?: string;  // 数字格式化
}
```

**UI 设计**：
```
┌─────────────────────────────────────────────────────────┐
│ Data Preparation                                        │
├─────────────────────────────────────────────────────────┤
│ Dataset: [Sales Data ▼]  [+ New] [Import ▲] [Export ▼] │
├─────────────────────────────────────────────────────────┤
│ ┌─────┬───────────┬────────┬────────┬────────┐         │
│ │     │ Month     │ Brand A│ Brand B│ Brand C│  <- 表头│
│ ├─────┼───────────┼────────┼────────┼────────┤         │
│ │  0  │ 2024-01   │  1000  │  800   │  600   │  <- 数据│
│ │  1  │ 2024-02   │  1200  │  900   │  700   │         │
│ │  2  │ 2024-03   │  1100  │  1000  │  800   │         │
│ │ ... │    ...    │  ...   │  ...   │  ...   │         │
│ └─────┴───────────┴────────┴────────┴────────┘         │
│                                                         │
│ Rows: 12  Cols: 4  Missing: 0                          │
│ [+ Add Row] [+ Add Column]                             │
└─────────────────────────────────────────────────────────┘
```

---

#### 2.2 参数配置与渲染子模块 (Chart Configuration & Preview)

**功能描述**：
- 为每个子图配置绘图参数
- 实时预览单个图表
- 参数与 chart_class API 一一对应

**核心功能**：

**2.2.1 图表类型选择**
- [ ] 17种图表类型选择器
  - Bar, Barh, Line, Area, Bubble, Stripdot
  - Hist, Boxdot, Treemap, Heatmap, Waffle, Funnel
  - Pie, Wordcloud, Table, Venn2, Venn3

**2.2.2 通用参数配置**
- [ ] 数据映射
  - [ ] 选择数据集
  - [ ] 列映射（x, y, z, hue 等）
- [ ] 格式化
  - [ ] 数字格式（fmt）
  - [ ] 字体大小（fontsize）
- [ ] 颜色配置
  - [ ] 颜色字典（color_dict）
  - [ ] 色彩映射（cmap_qual, cmap_norm）
  - [ ] 高亮项（focus）

**2.2.3 图表特定参数**
每种图表类型有专属的参数配置表单（动态加载）

**Bar Chart 示例参数**：
```typescript
interface BarChartParams {
  // 基础参数
  stacked: boolean;
  show_label: boolean;
  label_formatter: string;
  label_threshold: number;
  
  // 高级参数
  show_total_bar: boolean;
  show_total_label: boolean;
  show_gr_text: boolean;
  show_gr_line: boolean;
  show_avg_line: boolean;
  period_change: number;
  
  // 样式参数
  style?: {
    bar_width?: number;
    bar_color?: string;
    label_fontsize?: number;
    // ...
  };
}
```

**2.2.4 预览功能**
- [ ] 单图实时预览
  - [ ] 参数变更自动刷新
  - [ ] 防抖优化（避免频繁请求）
- [ ] 错误提示
  - [ ] 参数验证错误
  - [ ] 后端渲染错误
  - [ ] 数据格式错误

**UI 设计**（左中右三段布局）：
```
┌─────────────┬────────────────────────────┬──────────────────────┐
│ Core Setup  │ Preview                    │ Detail Settings      │
├─────────────┤                            ├──────────────────────┤
│ Subplot     │  ┌────────────────────┐   │ Basic Settings       │
│ └─ [0 ▼]    │  │                    │   │ └─ ☑ Stacked         │
│             │  │                    │   │ └─ ☑ Show Labels     │
│ Chart Type  │  │  [图表预览区域]    │   │ └─ Format:           │
│ └─ [Bar ▼]  │  │                    │   │    [{abs}        ▼]  │
│             │  │                    │   │                      │
│ Dataset     │  │                    │   │ Advanced Settings    │
│ └─ [Sales ▼]│  │                    │   │ └─ ☑ Show Total Bar  │
│             │  └────────────────────┘   │ └─ ☐ Show Avg Line   │
│ Actions     │                            │ └─ ☐ Show GR Text    │
│ ├─ [Apply]  │  Status: ✓ Rendered       │ └─ Period: [1    ▼] │
│ ├─ [Save]   │  [Refresh Preview]        │                      │
│ └─ [Reset]  │                            │ Style Customization  │
│             │                            │ └─ Bar Width: [0.8]  │
│             │                            │ └─ Label Size: [12]  │
│             │                            │ └─ Color Scheme:     │
│             │                            │    [Default      ▼]  │
│             │                            │                      │
│             │                            │ [▼ More Options...]  │
└─────────────┴────────────────────────────┴──────────────────────┘

布局说明：
- 左侧（Core Setup）：200-250px 固定宽度，核心控制区
- 中间（Preview）：弹性宽度，占据剩余空间的主要部分
- 右侧（Detail Settings）：300-350px 固定宽度，可滚动的详细配置
```

---

### 3. 最终渲染模块 (Final Rendering)

**功能描述**：
- 整合画布布局和所有子图配置
- 向后端发送完整参数
- 获取最终的 Matplotlib 图表

**核心功能**：
- [ ] 参数整合
  - [ ] 收集画布配置（GridFigure 参数）
  - [ ] 收集所有子图配置和数据
  - [ ] 生成完整的 API 请求负载
- [ ] 后端渲染
  - [ ] 发送渲染请求
  - [ ] 显示渲染进度
  - [ ] 错误处理和重试
- [ ] 结果展示
  - [ ] 图片预览（可缩放）
  - [ ] 下载为 PNG/JPG/PDF
  - [ ] 复制到剪贴板
  - [ ] 保存配置为项目文件

**数据流**：
```
Frontend                          Backend
────────                          ───────
CanvasConfig    ──────────────▶   FastAPI
  ├─ Layout                        ├─ 参数验证
  ├─ Style                         ├─ 数据处理
  └─ Subplots[]                    ├─ GridFigure 创建
      ├─ Dataset                   ├─ 循环绘制子图
      └─ Params                    │   └─ f.plot(kind=...)
                                   └─ 图片生成
                  ◀──────────────
                  PNG/Base64
```

---

## 架构设计：桥接层模式

### 设计原则

为了保护现有的 `chart_class2` 库不受 Web 应用的影响（该库被其他程序广泛引用），我们采用**桥接层（Bridge Layer）**架构：

- ✅ **现有库保持不变**：`chart/` 目录下的所有代码无需修改
- ✅ **Web 专用桥接层**：创建独立的适配器层处理 Web 请求
- ✅ **清晰的职责分离**：桥接层负责数据转换、验证、Web 特定逻辑
- ✅ **向后兼容**：其他程序继续直接使用 `chart_class2` 库

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Data Manager │  │Chart Editor  │  │Canvas Designer│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API Layer (FastAPI Routes)              │   │
│  │  /api/datasets  /api/charts/preview  /api/render    │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                            │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │           Bridge Layer（桥接层 - 新增）               │  │
│  │  ┌─────────────────────────────────────────────┐     │  │
│  │  │ WebChartAdapter                             │     │  │
│  │  │  - JSON → pandas.DataFrame 转换             │     │  │
│  │  │  - Web 参数 → chart_class 参数映射          │     │  │
│  │  │  - 图片序列化（Base64/文件流）               │     │  │
│  │  │  - 错误处理和日志                            │     │  │
│  │  │  - 缓存管理                                  │     │  │
│  │  └─────────────────────────────────────────────┘     │  │
│  │  ┌─────────────────────────────────────────────┐     │  │
│  │  │ DatasetManager                              │     │  │
│  │  │  - 文件上传处理（Excel/CSV）                 │     │  │
│  │  │  - 数据验证和清洗                            │     │  │
│  │  │  - 数据库 CRUD                               │     │  │
│  │  └─────────────────────────────────────────────┘     │  │
│  │  ┌─────────────────────────────────────────────┐     │  │
│  │  │ ProjectManager                              │     │  │
│  │  │  - 项目配置持久化                            │     │  │
│  │  │  - 配置校验                                  │     │  │
│  │  └─────────────────────────────────────────────┘     │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                            │                                  │
│                            │ 调用原生 API                      │
│                            ▼                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      chart_class2 Library（现有库 - 不修改）          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │GridFigure│  │ Plot 子类│  │  Utils   │           │   │
│  │  │  figure  │  │  plots/  │  │ dataframe│           │   │
│  │  │  color   │  │  base    │  │   ppt    │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
chart_class2/                    # 项目根目录
├── chart/                       # ✅ 现有绘图库（不修改）
│   ├── __init__.py
│   ├── figure.py
│   ├── color.py
│   ├── plots/
│   └── components/
├── utils/                       # ✅ 现有工具（不修改）
│   ├── dataframe.py
│   └── ppt.py
├── example/                     # ✅ 现有示例（不修改）
│
├── web_bridge/                  # 🆕 Web 桥接层（新增）
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── chart_adapter.py    # 图表适配器
│   │   ├── data_adapter.py     # 数据适配器
│   │   └── config_adapter.py   # 配置适配器
│   ├── models/
│   │   ├── __init__.py
│   │   ├── web_models.py       # Pydantic Web 数据模型
│   │   └── db_models.py        # 数据库模型（SQLAlchemy）
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dataset_service.py  # 数据集管理服务
│   │   ├── chart_service.py    # 图表渲染服务
│   │   └── project_service.py  # 项目管理服务
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py      # 图片处理工具
│       ├── cache.py            # 缓存工具
│       └── validators.py       # 数据验证工具
│
├── web_api/                     # 🆕 FastAPI 应用（新增）
│   ├── __init__.py
│   ├── main.py                 # FastAPI 主应用
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── datasets.py         # 数据集路由
│   │   ├── charts.py           # 图表路由
│   │   └── projects.py         # 项目路由
│   ├── middleware/
│   │   ├── error_handler.py    # 错误处理
│   │   └── cors.py             # CORS 配置
│   └── config.py               # 配置文件
│
├── frontend/                    # 🆕 Next.js 前端（新增）
│   ├── app/
│   ├── components/
│   └── ...
│
└── tests/                       # 🆕 测试（新增）
    ├── test_bridge/
    └── test_api/
```

### 桥接层核心组件设计

#### 1. WebChartAdapter（图表适配器）

```python
# web_bridge/adapters/chart_adapter.py

from typing import Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# 导入现有库（只读引用）
from chart import GridFigure
from chart.color import COLOR_DICT, CMAP_QUAL

class WebChartAdapter:
    """
    Web 图表适配器
    职责：将 Web 请求参数转换为 chart_class2 的原生 API 调用
    不修改任何 chart_class2 的代码
    """
    
    def __init__(self):
        self.color_dict = COLOR_DICT
        self.cmap_qual = CMAP_QUAL
    
    def render_single_chart(
        self, 
        chart_type: str, 
        data: pd.DataFrame, 
        params: Dict[str, Any]
    ) -> bytes:
        """
        渲染单个图表（用于预览）
        
        Args:
            chart_type: 图表类型（对应 kind 参数）
            data: pandas DataFrame
            params: 图表参数（已验证）
        
        Returns:
            PNG 图片的字节流
        """
        # 创建简单画布
        f = plt.figure(FigureClass=GridFigure, width=10, height=6)
        
        # 调用原生 plot 方法
        f.plot(kind=chart_type, data=data, **params)
        
        # 保存为字节流
        buf = BytesIO()
        f.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(f)
        
        return buf.getvalue()
    
    def render_canvas(
        self,
        width: float,
        height: float,
        rows: int,
        cols: int,
        style: Dict[str, Any],
        subplots: list
    ) -> bytes:
        """
        渲染完整画布
        
        Args:
            width, height: 画布尺寸
            rows, cols: 网格布局
            style: 全局样式
            subplots: 子图配置列表，每个元素包含：
                {
                    'ax_index': int,
                    'chart_type': str,
                    'data': pd.DataFrame,
                    'params': dict
                }
        
        Returns:
            PNG 图片的字节流
        """
        # 创建 GridFigure
        f = plt.figure(
            FigureClass=GridFigure,
            width=width,
            height=height,
            rows=rows,
            cols=cols,
            style=style or {}
        )
        
        # 循环绘制子图
        for subplot in subplots:
            f.plot(
                kind=subplot['chart_type'],
                data=subplot['data'],
                ax_index=subplot['ax_index'],
                **subplot['params']
            )
        
        # 保存为高分辨率图片
        buf = BytesIO()
        f.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(f)
        
        return buf.getvalue()
    
    def image_to_base64(self, image_bytes: bytes) -> str:
        """将图片字节流转换为 Base64 字符串"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def validate_chart_params(
        self, 
        chart_type: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        验证并清洗图表参数
        移除无效参数，设置默认值
        """
        # 这里可以根据图表类型进行特定验证
        # 但不修改 chart_class2 的验证逻辑
        validated = params.copy()
        
        # 示例：移除 None 值
        validated = {k: v for k, v in validated.items() if v is not None}
        
        return validated
```

#### 2. DataAdapter（数据适配器）

```python
# web_bridge/adapters/data_adapter.py

import pandas as pd
from typing import Dict, List, Any, Optional
import json

class DataAdapter:
    """
    数据适配器
    职责：Web 前端数据格式 ↔ pandas DataFrame 转换
    """
    
    @staticmethod
    def json_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
        """
        将前端 JSON 数据转换为 pandas DataFrame
        
        前端格式：
        {
            "columns": ["Month", "Brand A", "Brand B"],
            "index": ["2024-01", "2024-02", ...],
            "data": [[1000, 800], [1200, 900], ...],
            "dtypes": {"Month": "datetime64", "Brand A": "int64", ...}
        }
        """
        df = pd.DataFrame(
            data['data'], 
            columns=data['columns']
        )
        
        # 设置索引
        if 'index' in data and data['index']:
            df.index = data['index']
        
        # 恢复数据类型
        if 'dtypes' in data:
            for col, dtype in data['dtypes'].items():
                if col in df.columns:
                    if dtype.startswith('datetime'):
                        df[col] = pd.to_datetime(df[col])
                    elif dtype in ['int64', 'float64']:
                        df[col] = df[col].astype(dtype)
        
        return df
    
    @staticmethod
    def dataframe_to_json(df: pd.DataFrame) -> Dict[str, Any]:
        """
        将 pandas DataFrame 转换为前端 JSON 格式
        """
        return {
            "columns": df.columns.tolist(),
            "index": df.index.tolist() if not df.index.name else df.index.name,
            "data": df.values.tolist(),
            "dtypes": {col: str(df[col].dtype) for col in df.columns},
            "shape": df.shape
        }
    
    @staticmethod
    def excel_to_dataframe(file_path: str, **kwargs) -> pd.DataFrame:
        """从 Excel 文件加载数据"""
        return pd.read_excel(file_path, **kwargs)
    
    @staticmethod
    def csv_to_dataframe(file_path: str, **kwargs) -> pd.DataFrame:
        """从 CSV 文件加载数据"""
        return pd.read_csv(file_path, **kwargs)
```

#### 3. Pydantic 数据模型（Web 专用）

```python
# web_bridge/models/web_models.py

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum

class ChartType(str, Enum):
    """支持的图表类型"""
    BAR = "bar"
    BARH = "barh"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    BUBBLE = "bubble"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    WAFFLE = "waffle"
    FUNNEL = "funnel"
    WORDCLOUD = "wordcloud"
    TABLE = "table"
    VENN2 = "venn2"
    VENN3 = "venn3"
    HIST = "hist"
    BOXDOT = "boxdot"
    STRIPDOT = "stripdot"

class DatasetModel(BaseModel):
    """数据集模型"""
    id: Optional[str] = None
    name: str
    columns: List[str]
    index: Optional[List[str]] = None
    data: List[List[Any]]
    dtypes: Dict[str, str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sales Data",
                "columns": ["Month", "Brand A", "Brand B"],
                "data": [[1000, 800], [1200, 900]],
                "dtypes": {"Month": "object", "Brand A": "int64", "Brand B": "int64"}
            }
        }

class ChartParamsModel(BaseModel):
    """图表参数基类（可扩展为具体图表类型）"""
    stacked: Optional[bool] = True
    show_label: Optional[bool] = True
    label_formatter: Optional[str] = "{abs}"
    fontsize: Optional[int] = 12
    color_dict: Optional[Dict[str, str]] = None
    focus: Optional[List[str]] = None
    style: Optional[Dict[str, Any]] = None

class SubplotConfigModel(BaseModel):
    """子图配置"""
    id: str
    ax_index: int
    chart_type: ChartType
    data_id: str
    params: Dict[str, Any]
    rowspan: Optional[int] = 1
    colspan: Optional[int] = 1

class CanvasConfigModel(BaseModel):
    """画布配置"""
    width: float = Field(default=15, ge=1, le=50)
    height: float = Field(default=6, ge=1, le=50)
    rows: int = Field(default=1, ge=1, le=10)
    cols: int = Field(default=1, ge=1, le=10)
    style: Optional[Dict[str, Any]] = None

class RenderRequestModel(BaseModel):
    """渲染请求"""
    canvas: CanvasConfigModel
    datasets: Dict[str, DatasetModel]  # key 为 data_id
    subplots: List[SubplotConfigModel]
```

---

## 后端 API 设计

### 3.1 API 端点规划

```python
# FastAPI 路由结构

# 数据管理
POST   /api/datasets                 # 上传数据集
GET    /api/datasets                 # 获取数据集列表
GET    /api/datasets/{id}            # 获取数据集详情
PUT    /api/datasets/{id}            # 更新数据集
DELETE /api/datasets/{id}            # 删除数据集

# 图表预览（单图）
POST   /api/charts/preview           # 预览单个图表
  Request: {
    chart_type: "bar",
    data: {...},
    params: {...}
  }
  Response: {
    image: "base64_string",
    metadata: {...}
  }

# 最终渲染（完整画布）
POST   /api/render                   # 渲染完整画布
  Request: {
    canvas: CanvasConfig,
    datasets: Dataset[],
    subplots: SubplotConfig[]
  }
  Response: {
    image: "base64_string",
    format: "png",
    metadata: {...}
  }

# 配置管理
POST   /api/projects                 # 保存项目配置
GET    /api/projects                 # 获取项目列表
GET    /api/projects/{id}            # 获取项目配置
PUT    /api/projects/{id}            # 更新项目
DELETE /api/projects/{id}            # 删除项目

# 工具端点
GET    /api/chart-types              # 获取支持的图表类型
GET    /api/chart-types/{type}/schema # 获取图表参数 schema
```

### 3.2 核心实现逻辑（基于桥接层）

```python
# web_api/main.py - FastAPI 主应用

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn

# 导入桥接层（不直接导入 chart_class2）
from web_bridge.adapters.chart_adapter import WebChartAdapter
from web_bridge.adapters.data_adapter import DataAdapter
from web_bridge.models.web_models import (
    RenderRequestModel, 
    DatasetModel,
    ChartType
)
from web_bridge.services.dataset_service import DatasetService
from web_bridge.services.chart_service import ChartService

app = FastAPI(title="Chart Class Web API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
chart_service = ChartService()
dataset_service = DatasetService()

# ============ 图表预览端点 ============

@app.post("/api/charts/preview")
async def preview_chart(
    chart_type: ChartType,
    dataset: DatasetModel,
    params: dict
):
    """
    预览单个图表
    
    使用桥接层，不直接操作 chart_class2
    """
    try:
        # 通过适配器转换数据
        df = DataAdapter.json_to_dataframe(dataset.dict())
        
        # 通过适配器渲染图表
        adapter = WebChartAdapter()
        image_bytes = adapter.render_single_chart(
            chart_type=chart_type.value,
            data=df,
            params=params
        )
        
        # 返回 Base64 编码的图片
        image_base64 = adapter.image_to_base64(image_bytes)
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{image_base64}",
            "metadata": {
                "chart_type": chart_type,
                "rows": len(dataset.data),
                "cols": len(dataset.columns)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============ 完整画布渲染端点 ============

@app.post("/api/render")
async def render_canvas(request: RenderRequestModel):
    """
    渲染完整画布
    
    通过桥接层调用 chart_class2，保持原库不变
    """
    try:
        # 准备子图数据
        subplots_data = []
        for subplot in request.subplots:
            # 获取数据集
            dataset = request.datasets.get(subplot.data_id)
            if not dataset:
                raise ValueError(f"Dataset {subplot.data_id} not found")
            
            # 转换为 DataFrame
            df = DataAdapter.json_to_dataframe(dataset.dict())
            
            subplots_data.append({
                'ax_index': subplot.ax_index,
                'chart_type': subplot.chart_type.value,
                'data': df,
                'params': subplot.params
            })
        
        # 通过适配器渲染
        adapter = WebChartAdapter()
        image_bytes = adapter.render_canvas(
            width=request.canvas.width,
            height=request.canvas.height,
            rows=request.canvas.rows,
            cols=request.canvas.cols,
            style=request.canvas.style or {},
            subplots=subplots_data
        )
        
        # 返回图片
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=chart.png"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============ 数据集管理端点 ============

@app.post("/api/datasets")
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = None
):
    """上传并保存数据集"""
    try:
        result = await dataset_service.upload_file(file, name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/datasets")
async def list_datasets():
    """获取数据集列表"""
    return await dataset_service.list_all()

@app.get("/api/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """获取数据集详情"""
    dataset = await dataset_service.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

# ============ 工具端点 ============

@app.get("/api/chart-types")
async def get_chart_types():
    """获取支持的图表类型"""
    return {
        "chart_types": [
            {"value": ct.value, "label": ct.name.title()} 
            for ct in ChartType
        ]
    }

@app.get("/api/chart-types/{chart_type}/schema")
async def get_chart_schema(chart_type: ChartType):
    """获取图表参数 Schema"""
    # 可以根据图表类型返回不同的参数定义
    return chart_service.get_param_schema(chart_type)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```python
# web_bridge/services/chart_service.py

from typing import Dict, Any
from web_bridge.adapters.chart_adapter import WebChartAdapter

class ChartService:
    """
    图表服务
    封装图表相关的业务逻辑
    """
    
    def __init__(self):
        self.adapter = WebChartAdapter()
    
    def get_param_schema(self, chart_type: str) -> Dict[str, Any]:
        """
        获取图表参数的 JSON Schema
        用于前端动态生成表单
        """
        # 基础参数（所有图表通用）
        base_schema = {
            "type": "object",
            "properties": {
                "show_label": {
                    "type": "boolean",
                    "default": True,
                    "title": "显示标签"
                },
                "fontsize": {
                    "type": "integer",
                    "default": 12,
                    "minimum": 8,
                    "maximum": 24,
                    "title": "字体大小"
                }
            }
        }
        
        # 图表特定参数
        chart_schemas = {
            "bar": {
                "stacked": {
                    "type": "boolean",
                    "default": True,
                    "title": "堆叠显示"
                },
                "show_total_bar": {
                    "type": "boolean",
                    "default": False,
                    "title": "显示总计柱"
                },
                "label_formatter": {
                    "type": "string",
                    "default": "{abs}",
                    "enum": ["{abs}", "{share}", "{abs}\\n{share}"],
                    "title": "标签格式"
                }
            },
            "line": {
                "show_marker": {
                    "type": "boolean",
                    "default": True,
                    "title": "显示标记点"
                },
                "linewidth": {
                    "type": "number",
                    "default": 2,
                    "minimum": 0.5,
                    "maximum": 5,
                    "title": "线条宽度"
                }
            },
            # 其他图表类型...
        }
        
        # 合并基础参数和特定参数
        if chart_type in chart_schemas:
            base_schema["properties"].update(chart_schemas[chart_type])
        
        return base_schema
```

```python
# web_bridge/services/dataset_service.py

from typing import List, Dict, Any, Optional
from fastapi import UploadFile
import pandas as pd
import uuid
from pathlib import Path

from web_bridge.adapters.data_adapter import DataAdapter
from web_bridge.models.db_models import Dataset  # SQLAlchemy 模型

class DatasetService:
    """
    数据集管理服务
    处理数据上传、存储、检索
    """
    
    def __init__(self):
        self.upload_dir = Path("./uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_file(
        self, 
        file: UploadFile, 
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传并解析文件
        
        Returns:
            数据集的 JSON 表示
        """
        # 保存文件
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 解析文件
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = DataAdapter.excel_to_dataframe(str(file_path))
        elif file.filename.endswith('.csv'):
            df = DataAdapter.csv_to_dataframe(str(file_path))
        else:
            raise ValueError("Unsupported file format")
        
        # 转换为 Web 格式
        dataset_json = DataAdapter.dataframe_to_json(df)
        dataset_json['id'] = file_id
        dataset_json['name'] = name or file.filename
        
        # 保存到数据库（示例，实际使用 SQLAlchemy）
        # await db.save(Dataset(**dataset_json))
        
        return dataset_json
    
    async def list_all(self) -> List[Dict[str, Any]]:
        """获取所有数据集"""
        # 从数据库获取
        # datasets = await db.query(Dataset).all()
        # return [dataset.to_dict() for dataset in datasets]
        return []
    
    async def get_by_id(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取数据集"""
        # dataset = await db.query(Dataset).filter_by(id=dataset_id).first()
        # return dataset.to_dict() if dataset else None
        return None
```

### 3.3 桥接层的优势总结

✅ **保护现有代码**：
- `chart/` 和 `utils/` 目录完全不变
- 其他程序继续使用原有 API
- Web 应用通过桥接层间接调用

✅ **职责清晰**：
- 桥接层：数据转换、验证、Web 特定逻辑
- 原库：纯粹的绘图功能

✅ **易于维护**：
- Web 功能变更只需修改 `web_bridge/` 和 `web_api/`
- 不会影响其他依赖 `chart_class2` 的项目

✅ **可扩展性**：
- 未来可以添加其他接口（CLI、桌面应用）
- 只需创建新的适配器层

✅ **测试友好**：
- 桥接层和原库可以独立测试
- Mock 适配器方便前端开发

---

## 前端架构设计

### 4.1 项目结构

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # 根布局
│   ├── page.tsx                  # 首页（项目列表）
│   ├── canvas/                   # 画布设计器
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   ├── chart/                    # 图表配置
│   │   └── [id]/
│   │       ├── data/page.tsx     # 数据准备
│   │       └── config/page.tsx   # 参数配置
│   └── api/                      # API 路由（如需要）
│
├── components/                   # React 组件
│   ├── canvas/
│   │   ├── GridPreview.tsx       # 网格预览组件
│   │   ├── SubplotEditor.tsx     # 子图编辑器
│   │   └── CanvasToolbar.tsx     # 工具栏
│   ├── data/
│   │   ├── DataTable.tsx         # 数据表格（AG Grid）
│   │   ├── DataImporter.tsx      # 数据导入
│   │   └── DatasetManager.tsx    # 数据集管理
│   ├── chart/
│   │   ├── ChartEditor.tsx       # 三段式布局主容器
│   │   ├── CoreSetup/            # 左侧核心设置区
│   │   │   ├── SubplotSelector.tsx
│   │   │   ├── ChartTypeSelector.tsx
│   │   │   ├── DatasetSelector.tsx
│   │   │   └── ActionButtons.tsx
│   │   ├── Preview/              # 中间预览区
│   │   │   ├── ChartPreview.tsx
│   │   │   └── PreviewControls.tsx
│   │   └── DetailSettings/       # 右侧详细设置区
│   │       ├── BasicSettings.tsx
│   │       ├── AdvancedSettings.tsx
│   │       └── StyleCustomization.tsx
│   └── ui/                       # shadcn/ui 组件
│       ├── button.tsx
│       ├── input.tsx
│       ├── select.tsx
│       └── ...
│
├── lib/                          # 工具函数
│   ├── api.ts                    # API 客户端
│   ├── chart-schemas.ts          # 图表参数 Schema
│   └── utils.ts                  # 通用工具
│
├── store/                        # 状态管理（Zustand）
│   ├── canvasStore.ts            # 画布状态
│   ├── dataStore.ts              # 数据集状态
│   └── chartStore.ts             # 图表配置状态
│
├── types/                        # TypeScript 类型
│   ├── canvas.ts
│   ├── dataset.ts
│   └── chart.ts
│
└── styles/
    └── globals.css               # Tailwind 全局样式
```

### 4.2 状态管理设计

```typescript
// store/canvasStore.ts
import { create } from 'zustand';

interface CanvasState {
  canvases: Map<string, CanvasConfig>;
  currentCanvasId: string | null;
  
  // Actions
  createCanvas: (config: CanvasConfig) => void;
  updateCanvas: (id: string, config: Partial<CanvasConfig>) => void;
  deleteCanvas: (id: string) => void;
  setCurrentCanvas: (id: string) => void;
  
  // Subplots
  addSubplot: (canvasId: string, subplot: SubplotConfig) => void;
  updateSubplot: (canvasId: string, subplotId: string, params: Partial<SubplotConfig>) => void;
  deleteSubplot: (canvasId: string, subplotId: string) => void;
}

export const useCanvasStore = create<CanvasState>((set) => ({
  // 实现...
}));
```

---

## 技术难点与解决方案

### 5.1 数据处理

**难点**：
- 前后端数据格式转换（JSON ↔ pandas DataFrame）
- 大数据集的传输和处理
- 数据类型保留（日期、数字格式）

**解决方案**：
```python
# 后端：Pydantic 模型定义
from pydantic import BaseModel

class DatasetModel(BaseModel):
    columns: List[str]
    index: Optional[List[str]]
    data: List[List[Any]]
    dtypes: Dict[str, str]  # {'col1': 'int64', 'col2': 'datetime64'}
    
    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.data, columns=self.columns)
        if self.index:
            df.index = self.index
        
        # 恢复数据类型
        for col, dtype in self.dtypes.items():
            if dtype.startswith('datetime'):
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(dtype)
        
        return df
```

### 5.2 图表参数映射

**难点**：
- 17种图表类型，每种有不同参数
- 参数验证和默认值
- UI 表单动态生成

**解决方案**：
```typescript
// 使用 JSON Schema 定义参数
const CHART_SCHEMAS = {
  bar: {
    type: 'object',
    properties: {
      stacked: { type: 'boolean', default: true },
      show_label: { type: 'boolean', default: true },
      label_formatter: { type: 'string', default: '{abs}' },
      label_threshold: { type: 'number', default: 0.02, min: 0, max: 1 },
      // ...
    }
  },
  // 其他图表类型...
};

// 使用 react-hook-form + zod 验证
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const barSchema = z.object({
  stacked: z.boolean(),
  show_label: z.boolean(),
  // ...
});
```

### 5.3 实时预览性能

**难点**：
- 频繁的参数变更导致大量渲染请求
- 后端 Matplotlib 渲染较慢
- 网络传输延迟

**解决方案**：
```typescript
// 1. 防抖（Debounce）
import { useDebouncedCallback } from 'use-debounce';

const debouncedPreview = useDebouncedCallback(
  (params) => {
    fetchChartPreview(params);
  },
  500  // 500ms 延迟
);

// 2. 缓存策略
const previewCache = new Map<string, string>();

// 3. 乐观更新
const [previewImage, setPreviewImage] = useState(null);
const [isLoading, setIsLoading] = useState(false);

// 显示加载状态，但不阻塞 UI
```

### 5.4 网格布局可视化

**难点**：
- GridSpec 的复杂嵌套逻辑
- 拖拽调整网格位置
- 跨行跨列的表示

**解决方案**：
```typescript
// 使用 react-grid-layout
import GridLayout from 'react-grid-layout';

const GridPreview = ({ rows, cols, subplots }) => {
  const layout = subplots.map(subplot => ({
    i: subplot.id,
    x: subplot.ax_index % cols,
    y: Math.floor(subplot.ax_index / cols),
    w: subplot.colspan || 1,
    h: subplot.rowspan || 1,
  }));
  
  return (
    <GridLayout
      layout={layout}
      cols={cols}
      rowHeight={100}
      width={800}
      onLayoutChange={handleLayoutChange}
    >
      {subplots.map(subplot => (
        <div key={subplot.id} className="grid-item">
          {subplot.chart_type}
        </div>
      ))}
    </GridLayout>
  );
};
```

---

## UI/UX 设计规范

### 6.1 颜色主题（黑白商务风格）

```css
/* Tailwind 配置 */
module.exports = {
  theme: {
    extend: {
      colors: {
        // 主色调：黑白灰
        background: {
          DEFAULT: '#FFFFFF',
          secondary: '#F5F5F5',
          tertiary: '#E5E5E5',
        },
        foreground: {
          DEFAULT: '#000000',
          secondary: '#666666',
          tertiary: '#999999',
        },
        border: {
          DEFAULT: '#D1D1D1',
          light: '#E5E5E5',
          dark: '#999999',
        },
        // 强调色
        primary: '#000000',
        secondary: '#666666',
        accent: '#333333',
        // 功能色
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',
      },
    },
  },
};
```

### 6.2 组件样式规范

```typescript
// 按钮
<Button variant="primary">   // 黑色背景，白色文字
<Button variant="secondary"> // 白色背景，黑色边框
<Button variant="ghost">     // 透明背景，黑色文字

// 输入框
<Input className="border-gray-300 focus:border-black" />

// 卡片
<Card className="border border-gray-200 shadow-sm hover:shadow-md" />
```

### 6.3 布局规范

- **三段式布局**：
  - 左侧核心控制区：200-250px 固定宽度
  - 中间预览区：弹性宽度（min-width: 400px）
  - 右侧详细配置区：300-350px 固定宽度，可滚动
- **网格系统**：12列栅格
- **间距**：4px 基准（Tailwind spacing）
- **圆角**：2px-4px（轻微圆角，保持商务感）
- **阴影**：轻微阴影，避免过重
- **字体**：
  - 标题：font-semibold
  - 正文：font-normal
  - 代码：font-mono

**布局组件结构**：
```typescript
// components/chart/ChartEditor.tsx
const ChartEditor = () => {
  return (
    <div className="flex h-screen">
      {/* 左侧：核心设置区 */}
      <aside className="w-60 border-r border-gray-200 p-4 flex flex-col gap-4">
        <SubplotSelector />
        <ChartTypeSelector />
        <DatasetSelector />
        <ActionButtons />
      </aside>
      
      {/* 中间：预览区 */}
      <main className="flex-1 min-w-[400px] p-6 bg-gray-50">
        <ChartPreview />
        <PreviewControls />
      </main>
      
      {/* 右侧：详细设置区 */}
      <aside className="w-80 border-l border-gray-200 overflow-y-auto">
        <div className="p-4 space-y-6">
          <BasicSettings />
          <AdvancedSettings />
          <StyleCustomization />
        </div>
      </aside>
    </div>
  );
};
```

### 6.4 核心组件详细设计

#### 6.4.1 左侧核心设置区组件

```typescript
// components/chart/CoreSetup/SubplotSelector.tsx
const SubplotSelector = () => {
  const { currentSubplotId, subplots, setCurrentSubplot } = useCanvasStore();
  
  return (
    <div className="space-y-2">
      <label className="text-sm font-semibold">当前子图</label>
      <Select value={currentSubplotId} onValueChange={setCurrentSubplot}>
        <SelectTrigger>
          <SelectValue placeholder="选择子图" />
        </SelectTrigger>
        <SelectContent>
          {subplots.map((subplot, idx) => (
            <SelectItem key={subplot.id} value={subplot.id}>
              子图 {idx} - {subplot.chart_type || '未设置'}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

// components/chart/CoreSetup/ActionButtons.tsx
const ActionButtons = () => {
  const { applyChanges, saveProject, resetChanges } = useChartStore();
  
  return (
    <div className="flex flex-col gap-2 mt-auto">
      <Button onClick={applyChanges} className="w-full">
        应用更改
      </Button>
      <Button onClick={saveProject} variant="secondary" className="w-full">
        保存项目
      </Button>
      <Button onClick={resetChanges} variant="ghost" className="w-full">
        重置
      </Button>
    </div>
  );
};
```

#### 6.4.2 中间预览区组件

```typescript
// components/chart/Preview/ChartPreview.tsx
const ChartPreview = () => {
  const { previewImage, isLoading, error } = useChartStore();
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 min-h-[500px] flex items-center justify-center">
      {isLoading && (
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin" />
          <p className="text-sm text-gray-600">正在渲染图表...</p>
        </div>
      )}
      
      {error && (
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
      
      {previewImage && !isLoading && (
        <img 
          src={previewImage} 
          alt="Chart Preview" 
          className="max-w-full h-auto"
        />
      )}
    </div>
  );
};

// components/chart/Preview/PreviewControls.tsx
const PreviewControls = () => {
  const { refreshPreview, downloadChart, copyToClipboard } = useChartStore();
  
  return (
    <div className="flex items-center justify-between mt-4">
      <div className="flex items-center gap-2">
        <Badge variant="outline">✓ 已渲染</Badge>
        <span className="text-xs text-gray-500">最后更新: 2分钟前</span>
      </div>
      
      <div className="flex gap-2">
        <Button onClick={refreshPreview} variant="ghost" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新预览
        </Button>
        <Button onClick={downloadChart} variant="ghost" size="sm">
          <Download className="w-4 h-4 mr-2" />
          下载
        </Button>
        <Button onClick={copyToClipboard} variant="ghost" size="sm">
          <Copy className="w-4 h-4 mr-2" />
          复制
        </Button>
      </div>
    </div>
  );
};
```

#### 6.4.3 右侧详细设置区组件

```typescript
// components/chart/DetailSettings/BasicSettings.tsx
const BasicSettings = () => {
  const { chartParams, updateParams } = useChartStore();
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold border-b pb-2">基础设置</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm">堆叠显示</label>
          <Switch 
            checked={chartParams.stacked}
            onCheckedChange={(val) => updateParams({ stacked: val })}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <label className="text-sm">显示标签</label>
          <Switch 
            checked={chartParams.show_label}
            onCheckedChange={(val) => updateParams({ show_label: val })}
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-sm">标签格式</label>
          <Select 
            value={chartParams.label_formatter}
            onValueChange={(val) => updateParams({ label_formatter: val })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="{abs}">{'{abs}'} - 绝对值</SelectItem>
              <SelectItem value="{share}">{'{share}'} - 占比</SelectItem>
              <SelectItem value="{abs}\n{share}">{'{abs}\\n{share}'} - 双行</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

// components/chart/DetailSettings/AdvancedSettings.tsx
const AdvancedSettings = () => {
  const { chartParams, updateParams } = useChartStore();
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold border-b pb-2">高级设置</h3>
      
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="totals">
          <AccordionTrigger className="text-sm">总计显示</AccordionTrigger>
          <AccordionContent className="space-y-3 pt-3">
            <div className="flex items-center justify-between">
              <label className="text-xs">显示总计柱</label>
              <Switch 
                checked={chartParams.show_total_bar}
                onCheckedChange={(val) => updateParams({ show_total_bar: val })}
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs">显示总计标签</label>
              <Switch 
                checked={chartParams.show_total_label}
                onCheckedChange={(val) => updateParams({ show_total_label: val })}
              />
            </div>
          </AccordionContent>
        </AccordionItem>
        
        <AccordionItem value="growth">
          <AccordionTrigger className="text-sm">增长率</AccordionTrigger>
          <AccordionContent className="space-y-3 pt-3">
            <div className="flex items-center justify-between">
              <label className="text-xs">显示增长率文本</label>
              <Switch 
                checked={chartParams.show_gr_text}
                onCheckedChange={(val) => updateParams({ show_gr_text: val })}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs">对比周期</label>
              <Select 
                value={String(chartParams.period_change)}
                onValueChange={(val) => updateParams({ period_change: Number(val) })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">环比（1期）</SelectItem>
                  <SelectItem value="12">同比（12期）</SelectItem>
                  <SelectItem value="3">3期对比</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

// components/chart/DetailSettings/StyleCustomization.tsx
const StyleCustomization = () => {
  const { chartParams, updateParams } = useChartStore();
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold border-b pb-2">样式定制</h3>
      
      <div className="space-y-3">
        <div className="space-y-1">
          <label className="text-xs">柱体宽度</label>
          <div className="flex items-center gap-2">
            <Slider 
              value={[chartParams.style?.bar_width || 0.8]}
              onValueChange={([val]) => updateParams({ 
                style: { ...chartParams.style, bar_width: val }
              })}
              min={0.1}
              max={1.0}
              step={0.1}
              className="flex-1"
            />
            <span className="text-xs text-gray-600 w-10">
              {chartParams.style?.bar_width || 0.8}
            </span>
          </div>
        </div>
        
        <div className="space-y-1">
          <label className="text-xs">标签字体大小</label>
          <Input 
            type="number"
            value={chartParams.style?.label_fontsize || 12}
            onChange={(e) => updateParams({
              style: { ...chartParams.style, label_fontsize: Number(e.target.value) }
            })}
            min={8}
            max={24}
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs">配色方案</label>
          <Select 
            value={chartParams.color_scheme || 'default'}
            onValueChange={(val) => updateParams({ color_scheme: val })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="default">默认</SelectItem>
              <SelectItem value="pastel">柔和</SelectItem>
              <SelectItem value="vibrant">鲜艳</SelectItem>
              <SelectItem value="monochrome">单色</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};
```

---

## 开发阶段规划

### 🚀 Phase 0: MVP（最小可行产品）开发（1-2周）

**目标**：快速打通前后端，验证桥接层架构，实现基础的单子图柱状图渲染。

#### 功能范围限定
- ✅ **单子图画布**：固定 1x1 网格，单个子图
- ✅ **仅支持柱状图**：chart_type 固定为 "bar"
- ✅ **最小参数集**：仅实现 3-5 个关键参数
  - `stacked`: 是否堆叠
  - `show_label`: 是否显示标签
  - `label_formatter`: 标签格式（固定 `{abs}`）
- ✅ **手动输入数据**：不实现文件上传，前端直接输入 JSON 数据
- ✅ **无持久化**：不使用数据库，所有数据保存在前端状态

#### MVP 任务清单

**后端（2-3天）**：

```python
# 目录结构（最小化）
web_bridge/
  ├── __init__.py
  └── adapters/
      ├── __init__.py
      └── chart_adapter.py    # 仅实现 bar 图渲染

web_api/
  ├── __init__.py
  └── main.py                 # 单文件 FastAPI 应用
```

- [ ] **Day 1: 桥接层核心**
  - [ ] 创建 `web_bridge/adapters/chart_adapter.py`
  - [ ] 实现 `WebChartAdapter` 类
    ```python
    class WebChartAdapter:
        def render_bar_chart(self, data_json: dict, params: dict) -> bytes:
            """仅支持 bar 图的简化版本"""
            # JSON → DataFrame
            # 调用 GridFigure + f.plot(kind='bar')
            # 返回 PNG bytes
    ```
  - [ ] 测试：用示例数据验证能正常生成柱状图

- [ ] **Day 2: FastAPI 最小接口**
  - [ ] 创建 `web_api/main.py`
  - [ ] 实现 `/api/render` POST 端点
    ```python
    @app.post("/api/render")
    async def render(request: dict):
        # request: { "data": {...}, "params": {...} }
        adapter = WebChartAdapter()
        image_bytes = adapter.render_bar_chart(
            request["data"], 
            request["params"]
        )
        return Response(content=image_bytes, media_type="image/png")
    ```
  - [ ] 配置 CORS（允许 localhost:3000）
  - [ ] 测试：用 Postman/curl 验证接口

- [ ] **Day 3: 调试和优化**
  - [ ] 错误处理（捕获 Matplotlib 异常）
  - [ ] 添加基础日志
  - [ ] 验证不影响现有库（运行 `example/bar.py`）

**前端（3-4天）**：

```typescript
// 目录结构（最小化）
frontend/
  ├── app/
  │   ├── page.tsx              // 主页面（All-in-One）
  │   └── layout.tsx
  ├── components/
  │   ├── DataInput.tsx         // JSON 数据输入
  │   ├── ParamControls.tsx     // 3个参数的开关/选择
  │   └── ChartPreview.tsx      // 图片显示
  └── lib/
      └── api.ts                // API 调用封装
```

- [ ] **Day 1: Next.js 初始化**
  - [ ] `npx create-next-app@latest frontend`
  - [ ] 安装 Tailwind CSS 和 shadcn/ui
  - [ ] 创建基础布局（无复杂路由）

- [ ] **Day 2: 简单三段式界面**
  - [ ] 左侧：JSON 数据输入框（Textarea）
    ```tsx
    <textarea 
      placeholder='{"columns": [...], "data": [...]}' 
      onChange={handleDataChange}
    />
    ```
  - [ ] 中间：图表预览区（显示后端返回的图片）
  - [ ] 右侧：3个参数控制
    ```tsx
    <Switch label="堆叠显示" checked={stacked} />
    <Switch label="显示标签" checked={showLabel} />
    ```

- [ ] **Day 3: API 集成**
  - [ ] 实现 `lib/api.ts`
    ```typescript
    export async function renderChart(data: any, params: any) {
      const res = await fetch('http://localhost:8000/api/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data, params })
      });
      return await res.blob();
    }
    ```
  - [ ] 连接按钮点击 → API 调用 → 显示图片

- [ ] **Day 4: UI 优化**
  - [ ] 添加加载状态
  - [ ] 错误提示
  - [ ] 示例数据按钮（一键填充测试数据）

**集成测试（1天）**：
- [ ] 端到端测试
  - [ ] 启动后端：`uvicorn web_api.main:app --reload`
  - [ ] 启动前端：`npm run dev`
  - [ ] 输入测试数据，调整参数，验证图表更新
- [ ] 验证现有库未受影响
  - [ ] 运行 `python example/bar.py`，确保输出一致

#### MVP 数据格式示例

**前端输入的 JSON 数据**：
```json
{
  "columns": ["品牌A", "品牌B", "品牌C"],
  "index": ["2024-01", "2024-02", "2024-03"],
  "data": [
    [1000, 800, 600],
    [1200, 900, 700],
    [1100, 1000, 800]
  ]
}
```

**参数**：
```json
{
  "stacked": true,
  "show_label": true
}
```

#### MVP 成功标准

✅ 能在浏览器中输入数据和参数  
✅ 点击"渲染"按钮后，看到柱状图  
✅ 调整参数后，图表能实时更新  
✅ 现有的 `example/bar.py` 仍能正常运行  
✅ 代码清晰，易于扩展到完整功能

#### MVP 之后的扩展路径

MVP 验证成功后，按以下顺序逐步扩展：
1. 添加更多图表类型（line, pie, area...）
2. 增加参数数量（从 3 个扩展到完整参数集）
3. 实现多子图支持（网格布局）
4. 添加文件上传功能
5. 引入数据库持久化
6. 完善 UI/UX（Phase 1-6 的完整功能）

---

### Phase 1: 基础架构搭建（2-3周）

> **注意**：如果 MVP 成功，本阶段可复用 MVP 的代码，重点是补充完整功能。

**桥接层开发（重点）**：
- [x] ~~创建 `web_bridge/` 目录结构~~ （MVP 已完成）
- [ ] 扩展 WebChartAdapter 支持所有 17 种图表
- [ ] 实现 DataAdapter（文件上传支持）
- [ ] 完善 Pydantic 模型定义

**后端**：
- [x] ~~FastAPI 基础应用~~ （MVP 已完成）
- [ ] 数据库集成
- [ ] 完整的 API 端点
- [ ] 错误处理中间件

**前端**：
- [x] ~~Next.js 项目和基础 UI~~ （MVP 已完成）
- [ ] 路由系统（画布管理、项目管理）
- [ ] 状态管理（Zustand）
- [ ] 完整的组件库

**测试**：
- [x] ~~桥接层基础测试~~ （MVP 已完成）
- [ ] 完整的单元测试和集成测试

---

### Phase 2: 数据准备模块（2周）

**桥接层**：
- [ ] 扩展 DatasetService
  - [ ] 文件上传和存储
  - [ ] 数据验证和清洗
  - [ ] 数据库持久化

**后端**：
- [ ] 文件上传 API（通过 DataAdapter）
  - Excel 解析（openpyxl/pandas）
  - CSV 解析
  - 数据验证
- [ ] 数据集管理 API
  - 增删改查（使用 DatasetService）
  - 数据统计

**前端**：
- [ ] DataTable 组件（AG Grid 集成）
- [ ] 文件上传组件
- [ ] 剪贴板粘贴功能
- [ ] 数据集管理界面
- [ ] 数据验证和错误提示

---

### Phase 3: 画布布局模块（2周）

**后端**：
- [ ] Canvas 配置存储
- [ ] 网格布局验证逻辑

**前端**：
- [ ] GridPreview 组件
- [ ] 拖拽布局（react-grid-layout）
- [ ] 子图编辑器
- [ ] 网格参数配置表单
- [ ] 布局持久化

---

### Phase 4: 图表配置模块（3-4周）

**桥接层**：
- [ ] 实现 ChartService
  - [ ] 图表参数 Schema 生成
  - [ ] 参数验证逻辑
  - [ ] 缓存机制

**后端**：
- [ ] 图表参数 Schema API（通过 ChartService）
- [ ] 单图预览 API（通过 WebChartAdapter）
  - 参数验证
  - 调用适配器渲染
  - 图片返回（Base64）
- [ ] 错误处理和日志

**前端**：
- [ ] ChartTypeSelector 组件
- [ ] 动态参数表单生成
  - 17种图表类型的参数映射
  - 条件显示逻辑
- [ ] ChartPreview 组件
- [ ] 参数验证和提示
- [ ] 防抖优化

---

### Phase 5: 最终渲染模块（2周）

**桥接层**：
- [ ] 优化 WebChartAdapter 的 render_canvas
  - [ ] 性能优化
  - [ ] 错误处理
  - [ ] 多格式支持（PNG/PDF）

**后端**：
- [ ] 完整画布渲染 API（通过适配器）
  - 整合所有子图
  - 高分辨率输出
- [ ] 多格式导出
- [ ] 渲染队列（可选，处理大批量）

**前端**：
- [ ] 渲染请求组装
- [ ] 进度指示器
- [ ] 结果展示页面
- [ ] 下载功能
- [ ] 剪贴板复制

---

### Phase 6: 优化与测试（2周）

- [ ] 性能优化
  - [ ] 前端代码分割
  - [ ] 图片压缩
  - [ ] 桥接层缓存策略
  - [ ] API 响应时间优化
- [ ] 错误处理完善
- [ ] 单元测试
  - [ ] 桥接层测试（重点）
  - [ ] 后端 API 测试
  - [ ] 前端组件测试
- [ ] 集成测试
  - [ ] 端到端测试
  - [ ] 兼容性测试（确保不影响现有库）
- [ ] 用户体验优化
  - [ ] 加载状态
  - [ ] 错误提示
  - [ ] 快捷键
- [ ] 文档编写
  - [ ] 桥接层 API 文档
  - [ ] 部署指南

---

## 数据库设计

### 7.1 表结构

```sql
-- 项目表
CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 数据集表
CREATE TABLE datasets (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    columns JSON NOT NULL,           -- 列定义
    data JSON NOT NULL,               -- 数据内容
    metadata JSON,                    -- 元数据（行数、列数等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 画布表
CREATE TABLE canvases (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255),
    width FLOAT DEFAULT 15,
    height FLOAT DEFAULT 6,
    rows INT DEFAULT 1,
    cols INT DEFAULT 1,
    style JSON,                       -- 样式配置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 子图表
CREATE TABLE subplots (
    id VARCHAR(36) PRIMARY KEY,
    canvas_id VARCHAR(36) REFERENCES canvases(id) ON DELETE CASCADE,
    dataset_id VARCHAR(36) REFERENCES datasets(id) ON DELETE SET NULL,
    ax_index INT NOT NULL,
    chart_type VARCHAR(50) NOT NULL,
    params JSON NOT NULL,             -- 图表参数
    rowspan INT DEFAULT 1,
    colspan INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 部署方案

### 8.1 开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/chartdb
    volumes:
      - ./backend:/app
    depends_on:
      - db
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=chartdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 8.2 生产环境

**方案 1：传统部署**
- 后端：Gunicorn + Nginx（反向代理）
- 前端：Next.js 静态导出 + Nginx
- 数据库：PostgreSQL（托管服务）

**方案 2：容器化部署**
- Docker + Kubernetes
- 后端：FastAPI 容器
- 前端：Next.js 容器
- 数据库：云数据库

**方案 3：Serverless**
- 后端：AWS Lambda / Vercel Functions
- 前端：Vercel / Netlify
- 数据库：Supabase / PlanetScale

---

## 预估工作量

### 开发时间（单人）
- Phase 1（基础架构）：2-3周
- Phase 2（数据模块）：2周
- Phase 3（画布模块）：2周
- Phase 4（图表配置）：3-4周
- Phase 5（渲染模块）：2周
- Phase 6（优化测试）：2周
- **总计**：13-17周（约3-4个月）

### 团队配置建议
- **后端开发**：1人（Python/FastAPI）
- **前端开发**：1-2人（React/Next.js）
- **UI/UX 设计**：0.5人（兼职）
- **测试**：0.5人（兼职）

---

## 风险与挑战

### 9.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Matplotlib 渲染性能 | 高 | 使用桥接层缓存、异步任务队列 |
| 大数据集处理 | 中 | 分页加载、数据采样、桥接层优化 |
| 前后端数据同步 | 中 | 使用 Pydantic 严格验证、DataAdapter 保证一致性 |
| 桥接层数据转换开销 | 低 | 缓存转换结果、优化 DataFrame 序列化 |
| 影响现有库使用 | 高 | **严格隔离桥接层，禁止修改 chart/ 和 utils/** |
| 浏览器兼容性 | 低 | 使用现代浏览器，polyfill |

### 9.2 用户体验风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 渲染等待时间长 | 高 | 进度指示、预览优化、桥接层缓存 |
| 参数配置复杂 | 中 | 分步向导、预设模板 |
| 数据导入错误 | 中 | 详细错误提示、示例数据 |

---

## 扩展功能（未来）

### 10.1 Phase 2 功能
- [ ] 多用户协作
- [ ] 项目分享和权限管理
- [ ] 图表模板库
- [ ] 批量渲染任务
- [ ] 数据源连接（API、数据库）
- [ ] 导出为 Python 脚本

### 10.2 高级功能
- [ ] 交互式图表（Plotly 集成）
- [ ] 动画图表
- [ ] 实时数据更新
- [ ] AI 辅助参数推荐
- [ ] 图表风格迁移

---

## 桥接层开发最佳实践

### 11.1 设计原则

**DO（推荐做法）**：
- ✅ 所有 Web 功能通过桥接层调用 chart_class2
- ✅ 使用 Pydantic 模型进行严格的数据验证
- ✅ 在适配器中捕获所有异常，转换为 Web 友好的错误
- ✅ 对频繁使用的渲染结果进行缓存
- ✅ 为桥接层编写详细的单元测试
- ✅ 使用类型注解确保类型安全

**DON'T（禁止做法）**：
- ❌ 绝对不要修改 `chart/` 或 `utils/` 目录下的任何文件
- ❌ 不要在 chart_class2 库中添加 Web 特定的依赖
- ❌ 不要在前端直接导入 chart_class2 的类
- ❌ 不要在桥接层中引入复杂的业务逻辑（应在 Service 层）
- ❌ 不要绕过适配器直接调用原库

### 11.2 代码规范

```python
# ✅ 正确示例：使用桥接层

# web_api/routers/charts.py
from web_bridge.adapters.chart_adapter import WebChartAdapter
from web_bridge.adapters.data_adapter import DataAdapter

@app.post("/api/charts/preview")
async def preview(dataset: DatasetModel, chart_type: str, params: dict):
    adapter = WebChartAdapter()
    df = DataAdapter.json_to_dataframe(dataset.dict())
    return adapter.render_single_chart(chart_type, df, params)
```

```python
# ❌ 错误示例：直接使用原库

# web_api/routers/charts.py
from chart import GridFigure  # ❌ 不要在 web_api 中直接导入

@app.post("/api/charts/preview")
async def preview(dataset: DatasetModel):
    f = plt.figure(FigureClass=GridFigure)  # ❌ 不要在路由中直接使用
    # ...
```

### 11.3 测试策略

```python
# tests/test_bridge/test_chart_adapter.py

import pytest
import pandas as pd
from web_bridge.adapters.chart_adapter import WebChartAdapter

def test_render_single_chart():
    """测试单图渲染"""
    adapter = WebChartAdapter()
    
    # 准备测试数据
    df = pd.DataFrame({
        'Month': ['2024-01', '2024-02'],
        'Sales': [1000, 1200]
    })
    
    params = {'stacked': True, 'show_label': True}
    
    # 调用适配器
    result = adapter.render_single_chart('bar', df, params)
    
    # 验证结果
    assert isinstance(result, bytes)
    assert len(result) > 0

def test_bridge_does_not_modify_original_lib():
    """验证桥接层不影响原库"""
    # 直接使用原库
    from chart import GridFigure
    import matplotlib.pyplot as plt
    
    f = plt.figure(FigureClass=GridFigure, width=10, height=6)
    assert f is not None  # 原库仍然正常工作
```

### 11.4 版本兼容性

为了确保桥接层的向后兼容性：

```python
# web_bridge/adapters/chart_adapter.py

class WebChartAdapter:
    """
    版本：1.0.0
    兼容 chart_class2 版本：>= 2.0
    """
    
    COMPATIBLE_VERSIONS = ['2.0', '2.1', '2.2']
    
    def __init__(self):
        self._check_compatibility()
    
    def _check_compatibility(self):
        """检查与 chart_class2 的兼容性"""
        try:
            import chart
            # 可以添加版本检查逻辑
        except ImportError:
            raise RuntimeError("chart_class2 未安装")
```

### 11.5 监控和日志

```python
# web_bridge/utils/logger.py

import logging
from functools import wraps

logger = logging.getLogger('web_bridge')

def log_adapter_call(func):
    """装饰器：记录适配器调用"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"调用适配器方法: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"适配器方法 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"适配器方法 {func.__name__} 失败: {str(e)}")
            raise
    return wrapper

# 使用示例
class WebChartAdapter:
    @log_adapter_call
    def render_single_chart(self, chart_type, data, params):
        # ...
```

---

## 参考资源

### 技术文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Next.js 文档](https://nextjs.org/docs)
- [shadcn/ui 组件库](https://ui.shadcn.com/)
- [AG Grid React](https://www.ag-grid.com/react-data-grid/)
- [react-grid-layout](https://github.com/react-grid-layout/react-grid-layout)
- [Pydantic 文档](https://docs.pydantic.dev/)

### 设计模式参考
- 适配器模式（Adapter Pattern）
- 桥接模式（Bridge Pattern）
- 门面模式（Facade Pattern）

### 类似项目参考
- Plotly Dash
- Streamlit
- Observable
- Grafana

---

## 总结

本开发计划详细规划了一个完整的 Web 可视化工具，核心目标是：

1. ✅ **保护现有库**：通过桥接层实现完全隔离，不影响现有代码
2. ✅ **保留现有能力**：充分利用 chart_class2 的绘图功能
3. ✅ **提升用户体验**：可视化配置，降低使用门槛
4. ✅ **商务风格**：黑白简约设计，专业可靠
5. ✅ **模块化设计**：前后端分离，易于维护扩展

**关键成功因素**：
- **桥接层设计质量**：直接决定现有代码是否受影响
- 前后端参数映射的准确性
- 实时预览的性能优化
- 数据处理的鲁棒性
- 用户界面的直观性

**架构优势**：
- 🔒 **风险隔离**：Web 应用问题不会影响其他使用 chart_class2 的项目
- 🔄 **独立演进**：桥接层可以随 Web 需求迭代，原库保持稳定
- 🧪 **易于测试**：桥接层和原库可独立测试
- 📦 **清晰边界**：职责明确，代码组织清晰

**下一步行动**：
1. 评审本开发计划（尤其是桥接层设计）
2. 确定技术栈细节
3. 搭建开发环境（创建 web_bridge/ 和 web_api/ 目录）
4. 开始 Phase 1 开发（优先实现桥接层）
5. 编写桥接层测试，验证不影响现有库

---

*文档版本*：v1.0  
*创建日期*：2024年  
*负责人*：待定  
*状态*：待评审
