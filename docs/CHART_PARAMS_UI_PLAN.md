# 图表参数编辑器 UI 开发计划

## 📋 项目概述

### 目标
构建一个**分层、可复用、空间高效**的图表参数编辑器系统，支持所有图表类型的参数配置，提供最佳用户体验。

### 核心挑战
1. **参数数量多**：每个图表有 20-40+ 个参数（通用 + 特有）
2. **空间有限**：右侧边栏宽度约 300-400px
3. **认知负担**：避免参数过载，提供渐进式展示
4. **一致性**：跨图表类型保持 UI 一致

---

## 🏗️ 架构设计（2025-11-11 更新）

### 新架构：左右分离 + SubplotPanel Tabs

**重要说明**：这里指的是**单个子图的编辑面板**（SubplotPanel），不是画布页面（Canvas Page）！

```
┌────────────────────────────────────────────────────────────────────┐
│  SubplotPanel - 选中子图后展开的编辑界面                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────┐  ┌────────────────────────┐ │
│  │  MainContent (子图中心区域)      │  │  RightPanel (400px)    │ │
│  │                                  │  │                        │ │
│  │  ┌─ Tabs ─────────────────────┐ │  │  ┌──────────────────┐ │ │
│  │  │ [渲染预览] [表格编辑]       │ │  │  │ 通用样式参数     │ │ │
│  │  │ [JSON编辑] [📊 图表参数]    │ │  │  │                  │ │ │
│  │  │            ↑ 新增第4个Tab   │ │  │  │ ▼ 📝 标题        │ │ │
│  │  └───────────────────────────┘ │  │  │ ▼ 📊 网格线      │ │ │
│  │                                  │  │  │ ▶ 📐 坐标轴      │ │ │
│  │  ┌─ TabContent ───────────────┐ │  │  │ ▶ 🔢 刻度        │ │ │
│  │  │                            │ │  │  │ ▶ 🏷️ 图例        │ │ │
│  │  │  Tab1: 渲染预览 (PNG)      │ │  │  │                  │ │ │
│  │  │  Tab2: 表格编辑 (Data)     │ │  │  │ （Accordion）    │ │ │
│  │  │  Tab3: JSON编辑 (Config)   │ │  │  └──────────────────┘ │ │
│  │  │  Tab4: 📊 图表参数 ← NEW   │ │  │                        │ │
│  │  │       ↓                    │ │  │                        │ │
│  │  │  ┌──────────────────────┐ │ │  │                        │ │
│  │  │  │ 数据源配置           │ │ │  │                        │ │
│  │  │  │ • X轴字段            │ │ │  │                        │ │
│  │  │  │ • Y轴字段            │ │ │  │                        │ │
│  │  │  │ • 分组字段           │ │ │  │                        │ │
│  │  │  └──────────────────────┘ │ │  │                        │ │
│  │  │                            │ │  │                        │ │
│  │  │  ┌──────────────────────┐ │ │  │                        │ │
│  │  │  │ 气泡图专有参数        │ │  │                        │ │
│  │  │  │ • 气泡缩放           │ │  │                        │ │
│  │  │  │ • 透明度             │ │  │                        │ │
│  │  │  │ • 边框颜色           │ │  │                        │ │
│  │  │  │ • 回归线/相关系数    │ │  │                        │ │
│  │  │  │ • 参考线             │ │  │                        │ │
│  │  │  └──────────────────────┘ │ │  │                        │ │
│  │  │                            │ │  │                        │ │
│  │  └────────────────────────────┘ │  └────────────────────────┘ │
│  └──────────────────────────────────┘                            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Canvas Page（画布页面）架构**：
```
Canvas Page (画布级别，不同于 SubplotPanel)
├── 网格布局编辑 (GridLayoutEditor)
└── 画布级别设置 (CanvasSettings)
```
│  └──────────────────────────────────┘                            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 三层参数架构调整

```
原架构（已废弃）:
ChartParamsEditor（右侧边栏）
├── DataSourceEditor（数据源）
├── PlotSpecificEditor（图表特有参数）
└── BaseStyleEditor（通用样式）

新架构（2025-11-11）- SubplotPanel 层级:
├── RightPanel（右侧边栏 400px）
│   └── 通用样式参数（BaseStyleEditor）
│       ├── TitleSection
│       ├── GridSection
│       ├── AxisSection
│       ├── TicksSection
│       └── LegendSection
│
└── MainContent（子图中心区域 flex-1）
    └── Tabs（4个Tab）
        ├── Tab 1: 渲染预览（RenderedImage）
        ├── Tab 2: 表格编辑（TableEditor）
        ├── Tab 3: JSON编辑（JSONEditor）
        └── Tab 4: 📊 图表参数（PlotSpecificParamsTab）← 新增
            ├── DataSourceEditor（数据源配置）
            └── PlotSpecificParamsRouter（图表特有参数）
                ├── BubbleSpecificParams
                ├── BarSpecificParams
                └── ...

注意：这是 SubplotPanel（选中单个子图后的编辑界面），
      不是 Canvas Page（画布页面的网格布局）！
```

### 组件职责划分

| 组件 | 位置 | 职责 | 状态 |
|------|------|------|------|
| **SubplotPanel** | 选中子图后弹出 | 子图编辑面板容器 | ✅ 已有 |
| **RightPanel** | SubplotPanel 右侧 400px | 通用样式参数容器 | ✅ 已有 |
| **BaseStyleEditor** | RightPanel 内 | 通用样式分组（Accordion） | ⏳ 待创建 |
| **MainContent** | SubplotPanel 中心 flex-1 | 子图内容容器 | ✅ 已有 |
| **Tabs** | MainContent 内 | 4个Tab切换 | ✅ 已有（需扩展） |
| **PlotSpecificParamsTab** | Tab 4 | 图表特有参数页 | ⏳ 待创建 |
| **DataSourceEditor** | Tab 4 内 | 数据源字段配置 | ✅ 已创建（占位） |
| **PlotSpecificParamsRouter** | Tab 4 内 | 路由到具体图表参数 | ⏳ 待创建 |

---

## 🎨 UI 组件策略

### 1. 右侧边栏：BaseStyleEditor（Accordion 布局）

**位置**: `SubplotPanel` 的 `RightPanel` 内

**实现方案**：

```tsx
// frontend/components/subplot/SubplotPanel.tsx（或类似组件）
import { BaseStyleEditor } from '@/components/subplot/params/BaseStyleEditor';

export default function SubplotPanel({ subplot }: Props) {
  return (
    <div className="flex h-full">
      {/* 中心内容区：4个Tab */}
      <MainContent>
        <Tabs defaultValue="preview">
          <TabsList>
            <TabsTrigger value="preview">渲染预览</TabsTrigger>
            <TabsTrigger value="table">表格编辑</TabsTrigger>
            <TabsTrigger value="json">JSON编辑</TabsTrigger>
            <TabsTrigger value="params">📊 图表参数</TabsTrigger>
          </TabsList>
          
          <TabsContent value="preview">...</TabsContent>
          <TabsContent value="table">...</TabsContent>
          <TabsContent value="json">...</TabsContent>
          <TabsContent value="params">
            <PlotSpecificParamsTab subplot={subplot} />
          </TabsContent>
        </Tabs>
      </MainContent>

      {/* 右侧边栏：通用样式 */}
      <RightPanel>
        <div className="w-[400px] border-l bg-white overflow-y-auto">
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4">通用样式</h2>
            <BaseStyleEditor subplot={subplot} />
          </div>
        </div>
      </RightPanel>
    </div>
  );
}
```

**BaseStyleEditor 组件**：

```tsx
// frontend/components/subplot/params/BaseStyleEditor.tsx
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { TitleSection, GridSection, AxisSection, TicksSection, LegendSection } from './sections';

export function BaseStyleEditor() {
  const [openSections, setOpenSections] = useState<string[]>(['title']); // 默认展开标题

  return (
    <Accordion 
      type="multiple" 
      value={openSections} 
      onValueChange={setOpenSections}
      className="space-y-2"
    >
      {/* 标题 */}
      <AccordionItem value="title" className="border-none">
        <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
          📝 标题
        </AccordionTrigger>
        <AccordionContent className="px-3 py-2">
          <TitleSection />
        </AccordionContent>
      </AccordionItem>

      {/* 网格 */}
      <AccordionItem value="grid" className="border-none">
        <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
          📊 网格线
        </AccordionTrigger>
        <AccordionContent className="px-3 py-2">
          <GridSection />
        </AccordionContent>
      </AccordionItem>

      {/* 坐标轴 */}
      <AccordionItem value="axis" className="border-none">
        <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
          📐 坐标轴
        </AccordionTrigger>
        <AccordionContent className="px-3 py-2">
          <AxisSection />
        </AccordionContent>
      </AccordionItem>

      {/* 刻度 */}
      <AccordionItem value="ticks" className="border-none">
        <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
          🔢 刻度
        </AccordionTrigger>
        <AccordionContent className="px-3 py-2">
          <TicksSection />
        </AccordionContent>
      </AccordionItem>

      {/* 图例 */}
      <AccordionItem value="legend" className="border-none">
        <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
          🏷️ 图例
        </AccordionTrigger>
        <AccordionContent className="px-3 py-2">
          <LegendSection />
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
```

### 2. 中心区域：PlotSpecificParamsTab（第4个Tab）

**位置**: `SubplotPanel` 的 `MainContent` 的 Tabs 中，作为**第4个Tab**

**实现方案**：

```tsx
// frontend/components/subplot/SubplotPanel.tsx（或类似组件）
<Tabs defaultValue="preview" className="flex flex-col h-full w-full">
  <div className="border-b bg-white px-4 py-2 flex-shrink-0">
    <TabsList className="grid w-full grid-cols-4">
      <TabsTrigger value="preview">渲染预览</TabsTrigger>
      <TabsTrigger value="table">表格编辑</TabsTrigger>
      <TabsTrigger value="json">JSON编辑</TabsTrigger>
      <TabsTrigger value="params">📊 图表参数</TabsTrigger> {/* 新增第4个Tab */}
    </TabsList>
  </div>

  {/* Tab 1: 渲染预览 */}
  <TabsContent value="preview" className="m-0 p-6 flex-1">
    <RenderedImage subplot={subplot} />
  </TabsContent>

  {/* Tab 2: 表格编辑 */}
  <TabsContent value="table" className="m-0 p-6 flex-1">
    <TableEditor subplot={subplot} />
  </TabsContent>

  {/* Tab 3: JSON编辑 */}
  <TabsContent value="json" className="m-0 p-6 flex-1">
    <JSONEditor subplot={subplot} />
  </TabsContent>

  {/* Tab 4: 图表参数（新增）*/}
  <TabsContent value="params" className="m-0 p-6 flex-1">
    <PlotSpecificParamsTab subplot={subplot} />
  </TabsContent>
</Tabs>
```

**PlotSpecificParamsTab 组件**：

```tsx
// frontend/components/subplot/params/PlotSpecificParamsTab.tsx
import { DataSourceEditor } from './DataSourceEditor';
import { PlotSpecificParamsRouter } from './PlotSpecificParamsRouter';
import { useCanvasStore } from '@/store/canvasStore';

export function PlotSpecificParamsTab() {
  const { selectedSubplot } = useCanvasStore();

  if (!selectedSubplot) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-lg font-medium text-gray-700 mb-2">
            请先选择一个子图
          </p>
          <p className="text-sm text-gray-500">
            在"网格布局"标签页点击子图进行选择
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto space-y-6">
      {/* 数据源配置 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-3">数据源配置</h3>
        <DataSourceEditor subplot={selectedSubplot} />
      </div>

      {/* 图表特有参数 */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-purple-900 mb-3">
          {getChartTypeName(selectedSubplot.kind)} 参数
        </h3>
        <PlotSpecificParamsRouter subplot={selectedSubplot} />
      </div>
    </div>
  );
}
```

---

## 📦 组件开发清单

### Phase 1: 基础设施（Week 1）

#### 1.0 安装 Accordion 组件
- [ ] 运行 `npx shadcn@latest add accordion`
  - 安装 Radix UI Accordion 组件
  - 自动生成 `components/ui/accordion.tsx`

#### 1.1 创建通用样式分组组件
- [ ] `TitleSection.tsx` - 标题设置
  - 标题文本、字体大小、对齐方式
- [ ] `GridSection.tsx` - 网格线设置
  - 主网格、次网格、网格方向
- [ ] `AxisSection.tsx` - 坐标轴设置
  - 轴标题、字体大小、范围、隐藏边框
- [ ] `TicksSection.tsx` - 刻度设置
  - 刻度字体、旋转、间隔、显示/隐藏
- [ ] `LegendSection.tsx` - 图例设置
  - 显示、位置、列数、边界框

#### 1.2 创建数据源编辑器
- [ ] `DataSourceEditor.tsx`
  - 字段选择下拉框
  - 数据范围过滤
  - 数据排序

#### 1.3 创建容器组件
- [ ] `ChartParamsEditor.tsx` - 主编辑器容器
  - 使用 Accordion type="multiple" 管理展开状态
  - 参数更新逻辑
  - 快捷操作按钮（全展开/全折叠）
  - 布局和样式

### Phase 2: 图表特有参数编辑器（Week 2-3）

#### 2.1 基于 `chart/plots/` 创建对应编辑器

| 后端文件 | 前端组件 | 特有参数 | 优先级 |
|---------|---------|---------|--------|
| `bar.py` | `BarSpecificParams.tsx` | `stacked`, `show_label`, `width`, `label_formatter` | P0 |
| `line.py` | `LineSpecificParams.tsx` | `marker`, `linestyle`, `linewidth`, `fill_between` | P0 |
| `scatter.py` (bubble) | `BubbleSpecificParams.tsx` | `bubble_scale`, `alpha`, `show_reg`, `corr` | P0 |
| `pie.py` | `PieSpecificParams.tsx` | `autopct`, `startangle`, `explode`, `shadow` | P1 |
| `specialty.py` | `TreemapParams.tsx`, `HeatmapParams.tsx`, `WaffleParams.tsx`, `FunnelParams.tsx` | 各自特有参数 | P1 |
| `statistical.py` | `BoxplotParams.tsx`, `ViolinParams.tsx` | 统计图特有参数 | P2 |
| `wordcloud.py` | `WordCloudParams.tsx` | `max_words`, `background_color`, `colormap` | P2 |
| `venn.py` | `VennParams.tsx` | `set_labels`, `set_colors` | P2 |
| `table.py` | `TableParams.tsx` | 表格样式参数 | P2 |

#### 2.2 参数路由组件
- [ ] `PlotSpecificParamsRouter.tsx`
  - 根据 `subplot.kind` 动态加载对应编辑器
  - 类型安全的参数传递

### Phase 3: 集成与优化（Week 4）

#### 3.1 集成到现有系统
- [ ] 更新 `SubplotPanel.tsx` 使用新编辑器
- [ ] 迁移现有 `BubbleParamsEditor.tsx` 到新架构
- [ ] 确保与 `canvasStore` 状态管理兼容

#### 3.2 UX 优化
- [ ] 实现智能折叠逻辑
- [ ] 添加参数搜索功能
- [ ] 添加参数重置按钮
- [ ] 添加参数预设（样式模板）
- [ ] 响应式布局适配

#### 3.3 性能优化
- [ ] 参数变化防抖（debounce）
- [ ] 组件懒加载（React.lazy）
- [ ] 虚拟滚动（如果参数列表过长）

---

## 🎯 参数映射表

### 通用样式参数（基于 `base.py::Plot.Style`）

| 前端分组 | 后端字段 | 组件类型 | 默认值 |
|---------|---------|---------|--------|
| **标题** | | | |
| 标题文本 | `style.title` | Input | `''` |
| 标题字体 | `style.title_fontsize` | NumberInput | `14` |
| | | | |
| **网格** | | | |
| 主网格 | `style.major_grid` | Checkbox + Select | `null` |
| 主网格方向 | `style.major_grid.axis` | Select | `'both'` |
| 次网格 | `style.minor_grid` | Checkbox + Select | `null` |
| | | | |
| **坐标轴** | | | |
| X 轴标题 | `style.xlabel` | Input | `''` |
| Y 轴标题 | `style.ylabel` | Input | `''` |
| X 轴字体 | `style.xlabel_fontsize` | NumberInput | `14` |
| Y 轴字体 | `style.ylabel_fontsize` | NumberInput | `14` |
| X 轴范围 | `style.xlim` | [NumberInput, NumberInput] | `[null, null]` |
| Y 轴范围 | `style.ylim` | [NumberInput, NumberInput] | `[null, null]` |
| 隐藏上右边框 | `style.hide_top_right_spines` | Checkbox | `false` |
| | | | |
| **刻度** | | | |
| 显示所有X刻度 | `style.all_xticks` | Checkbox | `false` |
| X 刻度字体 | `style.xticklabel_fontsize` | NumberInput | `14` |
| Y 刻度字体 | `style.yticklabel_fontsize` | NumberInput | `14` |
| X 刻度旋转 | `style.xticklabel_rotation` | Slider (0-90) | `0` |
| Y 刻度旋转 | `style.yticklabel_rotation` | Slider (0-90) | `0` |
| 隐藏 X 刻度 | `style.remove_xticks` | Checkbox | `false` |
| 隐藏 Y 刻度 | `style.remove_yticks` | Checkbox | `false` |
| X 刻度间隔 | `style.xticks_interval` | NumberInput | `null` |
| Y 刻度间隔 | `style.yticks_interval` | NumberInput | `null` |
| | | | |
| **图例** | | | |
| 显示图例 | `style.show_legend` | Checkbox | `true` |
| 图例位置 | `style.legend_loc` | Select | `'center left'` |
| 图例列数 | `style.legend_ncol` | NumberInput | `1` |
| 图例边界框 | `style.legend_bbox_to_anchor` | [NumberInput, NumberInput] | `null` |

### 图表特有参数示例

#### 柱状图 (bar.py)
| 参数 | 后端字段 | 组件 | 默认值 |
|------|---------|------|--------|
| 堆叠显示 | `params.stacked` | Checkbox | `true` |
| 显示标签 | `params.show_label` | Checkbox | `true` |
| 标签格式 | `params.label_formatter` | Input | `'{abs}'` |
| 柱宽 | `params.width` | Slider (0.1-1) | `0.8` |

#### 气泡图 (scatter.py)
| 参数 | 后端字段 | 组件 | 默认值 |
|------|---------|------|--------|
| 气泡缩放 | `params.bubble_scale` | Slider (0.1-10) | `1` |
| 透明度 | `params.alpha` | Slider (0-1) | `0.6` |
| 边框颜色 | `params.edgecolor` | ColorPicker | `'#000000'` |
| 显示回归线 | `params.show_reg` | Checkbox | `false` |
| 显示相关系数 | `params.corr` | Checkbox | `false` |
| X 参考线 | `params.x_avg` | NumberInput | `null` |
| Y 参考线 | `params.y_avg` | NumberInput | `null` |
| 参考线颜色 | `params.avg_color` | ColorPicker | `'#808080'` |

---

## 🎨 UI 设计规范

### 颜色编码

使用一致的颜色系统区分不同类型参数：

```scss
// 分组背景色
$color-data-source: #EFF6FF;     // 蓝色 - 数据相关
$color-plot-specific: #F3E8FF;   // 紫色 - 图表特有
$color-style-title: #F1F5F9;     // 灰色 - 标题
$color-style-grid: #F0F9FF;      // 浅蓝 - 网格
$color-style-axis: #F0FDF4;      // 绿色 - 坐标轴
$color-style-ticks: #FFFBEB;     // 黄色 - 刻度
$color-style-legend: #FAF5FF;    // 淡紫 - 图例

// 触发器悬停色
$hover-opacity: 0.8;
```

### 间距规范

```scss
// 垂直间距
$section-gap: 8px;           // 分组之间
$item-gap: 12px;             // 参数项之间
$group-padding: 12px;        // 分组内边距

// 水平间距
$label-input-gap: 8px;       // 标签和输入框
$inline-control-gap: 16px;   // 同行控件间距
```

### 字体规范

```scss
// 字体大小
$font-section-title: 14px;   // 分组标题
$font-param-label: 13px;     // 参数标签
$font-helper-text: 11px;     // 辅助文本

// 字重
$weight-section: 600;        // 分组标题
$weight-label: 500;          // 参数标签
$weight-normal: 400;         // 常规文本
```

### 图标使用

```tsx
import {
  Database,        // 数据源
  BarChart3,       // 柱状图
  LineChart,       // 折线图
  ScatterChart,    // 气泡图
  PieChart,        // 饼图
  Grid3x3,         // 网格
  Ruler,           // 坐标轴
  Hash,            // 刻度
  Tag,             // 图例
  Type,            // 标题
} from 'lucide-react';
```

---

## 🚀 开发优先级（2025-11-11 重大更新）

### ⭐ 新架构开发计划

基于左右分离的架构设计：
- **右侧边栏（RightPanel）**: 通用样式参数（所有图表共享）
- **中心区域第5个Tab**: 图表特有参数（每种图表独立）

#### ✅ 已完成工作（Phase 0）

1. **通用样式分组组件** - ✅ 5个组件全部完成
   - `sections/TitleSection.tsx` - 标题设置（3参数）
   - `sections/GridSection.tsx` - 网格线设置（6参数）
   - `sections/AxisSection.tsx` - 坐标轴设置（10参数）
   - `sections/TicksSection.tsx` - 刻度设置（12参数）
   - `sections/LegendSection.tsx` - 图例设置（4参数）

2. **数据源编辑器占位符** - ⚠️ 基础结构完成
   - `DataSourceEditor.tsx` - 显示"开发中"提示

3. **UI 依赖安装** - ✅ 全部完成
   - Accordion, Checkbox, Slider, Input, Label, Select

4. **文档** - ✅ 完成
   - `CHART_PARAMS_UI_PLAN.md` - 架构设计文档（本文档）
   - `PARAMS_COMPONENTS_PROGRESS.md` - 进度报告
   - `ACCORDION_VS_COLLAPSIBLE.md` - 技术决策文档
   - `ACCORDION_CODE_EXAMPLES.md` - 实现示例

#### Phase 1: 右侧边栏 - 通用样式编辑器（1-2天）

**目标**: 在 RightPanel 中实现完整的通用样式参数编辑

**任务 1.1: 创建 BaseStyleEditor 容器** ⏳
- 文件：`frontend/components/subplot/params/BaseStyleEditor.tsx`
- 功能：
  - 使用 Accordion type="multiple" 组织 5 个样式分组
  - 默认展开"标题"分组
  - 集成所有已完成的 Section 组件
  - 从 `canvasStore` 获取选中子图并传递给 Section
  - 实现参数更新回调（调用 API 更新后端）
- 依赖：✅ 所有 Section 组件已完成
- 估时：**1 小时**

**任务 1.2: 集成到 RightPanel** ⏳
- 文件：`frontend/components/layout/RightPanel.tsx`
- 修改：
  - 在 `GridControls` 下方添加分隔线和"通用样式"标题
  - 渲染 `<BaseStyleEditor />`
  - 确保滚动条正常工作
- 估时：**30 分钟**

**任务 1.3: 测试通用样式参数更新** ⏳
- 验证每个参数都能正确读取和写入
- 测试参数更新触发图表重新渲染
- 检查 Accordion 展开/折叠状态
- 估时：**30 分钟**

**Phase 1 总计**: **2 小时**

---

#### Phase 2: 中心区域 - 图表特有参数 Tab（2-3天）

**目标**: 在主内容区添加第5个 Tab，显示图表特有参数和数据源配置

**任务 2.1: 创建 PlotSpecificParamsTab** ⏳
- 文件：`frontend/components/subplot/params/PlotSpecificParamsTab.tsx`
- 功能：
  - 检查是否选中子图（无选中时显示空状态提示）
  - 两个区域：
    - 数据源配置区（蓝色背景）
    - 图表特有参数区（紫色背景）
  - 调用 `DataSourceEditor` 和 `PlotSpecificParamsRouter`
- 估时：**1 小时**

**任务 2.2: 创建 PlotSpecificParamsRouter** ⏳
- 文件：`frontend/components/subplot/params/PlotSpecificParamsRouter.tsx`
- 功能：
  - 根据 `subplot.kind` 路由到对应组件
  - 初始仅支持 `kind === 'bubble'` → `BubbleSpecificParams`
  - 其他图表类型显示"开发中，敬请期待"提示
  - 包含图表类型到中文名的映射函数
- 估时：**30 分钟**

**任务 2.3: 优化 BubbleSpecificParams** ⏳
- 文件：
  - 重命名：`BubbleParamsEditor.tsx` → `BubbleSpecificParams.tsx`
  - 移动到：`components/subplot/params/` 目录
- 改进：
  - 移除外层标题（由 PlotSpecificParamsTab 显示）
  - 移除外层卡片样式（父组件已有背景色）
  - 优化参数分组：
    - **基础**: bubble_scale, alpha, edgecolor
    - **统计**: show_reg, corr, show_hist
    - **参考线**: x_avg, y_avg, avg_color, avg_width
    - **标签**: limit_label
  - 确保 ColorPicker 和 NumberFormatEditor 正常工作
- 估时：**2 小时**

**任务 2.4: 集成到 SubplotPanel Tabs** ⏳
- 文件：`frontend/components/subplot/SubplotPanel.tsx`（或类似文件）
- 修改：
  - `TabsList` 的 `grid-cols-3` → `grid-cols-4`
  - 添加第4个 `<TabsTrigger value="params">📊 图表参数</TabsTrigger>`
  - 添加对应的 `<TabsContent value="params">` 渲染 `PlotSpecificParamsTab`
- 估时：**30 分钟**

**任务 2.5: 测试图表特有参数 Tab** ⏳
- 验证无选中子图时的空状态显示
- 测试气泡图参数的读取和更新
- 检查 Tab 切换流畅性
- 估时：**30 分钟**

**Phase 2 总计**: **4.5 小时**

---

#### Phase 3: 完善数据源编辑器（3-4天）

**目标**: 实现完整的数据源字段映射和配置功能

**任务 3.1: 设计数据源配置接口** ⏳
- 分析后端数据结构（DataFrame 列名）
- 定义字段类型：
  - 数值字段（可用于 X/Y/Z 轴）
  - 分类字段（可用于分组、颜色映射）
  - 日期字段（可用于时间序列）
- 估时：**1 小时**

**任务 3.2: 实现 DataSourceEditor 核心功能** ⏳
- 文件：`frontend/components/subplot/params/DataSourceEditor.tsx`
- 功能：
  - 字段选择下拉框：
    - X 轴字段（数值/日期）
    - Y 轴字段（数值）
    - Z 轴字段（可选，气泡图用于大小）
    - 分组字段（分类）
    - 颜色映射字段（分类）
  - 数据预览：显示前5行数据
  - 数据统计：显示字段的最小值、最大值、平均值等
- 估时：**4 小时**

**任务 3.3: 添加数据过滤功能（可选）** ⏸️
- 简单条件过滤（大于、小于、等于、包含）
- 多条件组合（AND/OR）
- 过滤后数据预览
- 估时：**3 小时**（暂缓，未来版本）

**任务 3.4: 添加数据排序功能（可选）** ⏸️
- 按字段升序/降序
- 多字段排序
- 估时：**2 小时**（暂缓，未来版本）

**Phase 3 总计**: **5 小时**（核心功能）

---

#### Phase 4: 其他图表类型参数组件（按需开发）

**说明**: 在完成 Phase 1-3 并验证架构稳定后，逐步添加其他图表类型

**优先级排序**（基于使用频率和复用度）:

1. **BarSpecificParams**（柱状图）- P0 高频使用
   - 参数：stacked, bar_width, show_label, label_fmt, orientation
   - 估时：**2 小时**

2. **LineSpecificParams**（折线图）- P0 高频使用
   - 参数：linestyle, linewidth, marker, markersize, fill_between
   - 估时：**2 小时**

3. **PieSpecificParams**（饼图）- P1 简单
   - 参数：autopct, startangle, explode, radius, wedgeprops
   - 估时：**1.5 小时**

4. **ScatterSpecificParams**（散点图）- P1 类似气泡图
   - 参数：s（大小）, alpha, edgecolor, marker
   - 估时：**1 小时**

5. **HeatmapSpecificParams**（热力图）- P2 专业图表
   - 参数：cmap, annot, fmt, linewidths, cbar
   - 估时：**2 小时**

6. **TreemapSpecificParams**（矩形树图）- P2
   - 参数：sizes, colors, labels, pad
   - 估时：**2 小时**

7. **WaffleSpecificParams**（华夫饼图）- P3
   - 估时：**1.5 小时**

8. **FunnelSpecificParams**（漏斗图）- P3
   - 估时：**1.5 小时**

9. **VennSpecificParams**（韦恩图）- P3
   - 估时：**1 小时**

10. **WordCloudSpecificParams**（词云）- P3
    - 估时：**2 小时**

**Phase 4 总计**: **16.5+ 小时**（按需渐进）

---

### 📅 总体时间估算

| Phase | 描述 | 任务数 | 估时 | 优先级 |
|-------|------|--------|------|--------|
| Phase 0 | 基础准备（已完成）| 4 | - | ✅ |
| Phase 1 | 右侧边栏 - 通用样式 | 3 | **2h** | 🔴 立即 |
| Phase 2 | 中心区域 - 图表参数 Tab | 5 | **4.5h** | 🔴 立即 |
| Phase 3 | 数据源编辑器 | 2 | **5h** | 🟡 重要 |
| Phase 4 | 其他图表类型 | 10+ | **16.5h+** | 🟢 渐进 |

**总计**: 约 **28 小时**（不含测试和调优）

**当前建议**: 先完成 Phase 1-2（约 **6.5 小时**），验证新架构的可行性和用户体验，然后再推进 Phase 3-4。

---

## 🚀 开发优先级（原计划 - 归档）

<details>
<summary>点击展开原计划（已过时）</summary>

**优先级 P0 - 立即开始**

1. **安装依赖**
   - [ ] 运行 `npx shadcn@latest add accordion`
   - [ ] 验证 `components/ui/accordion.tsx` 生成成功

2. **通用样式分组组件**（优先）
   - [ ] `sections/TitleSection.tsx` - 标题设置
     - 标题文本、字体大小、对齐方式
   - [ ] `sections/GridSection.tsx` - 网格线设置
     - 主网格、次网格、网格方向、线型、透明度
   - [ ] `sections/AxisSection.tsx` - 坐标轴设置
     - X/Y 轴标题、字体大小、范围、隐藏边框
   - [ ] `sections/TicksSection.tsx` - 刻度设置
     - 刻度字体、旋转角度、间隔、显示/隐藏
   - [ ] `sections/LegendSection.tsx` - 图例设置
     - 显示开关、位置、列数、边界框

3. **数据源编辑器**（优先）
   - [ ] `DataSourceEditor.tsx` - 数据映射
     - 字段选择下拉框（X/Y/Z 轴）
     - 数据范围过滤
     - 数据排序选项

4. **优化现有气泡图参数编辑器**（基于现有代码）
   - [ ] 重构 `BubbleParamsEditor.tsx`
     - ✅ 已集成 ColorPicker（边框颜色、参考线颜色）
     - ✅ 已集成 NumberFormatEditor（X/Y 轴格式）
     - [ ] 调整布局，使用统一的 Label + 控件模式
     - [ ] 添加参数分组（基础/统计/高级）
     - [ ] 添加参数说明 Tooltip

5. **主容器组件**（整合所有分组）
   - [ ] `ChartParamsEditor.tsx`
     - 使用 Accordion type="multiple" 管理状态
     - 整合数据源、气泡图特有参数、通用样式
     - 实现快捷操作（全展开/全折叠）
     - 状态持久化到 localStorage

6. **集成到现有系统**
   - [ ] 更新 `SubplotPanel.tsx` 使用新编辑器
   - [ ] 确保与 `canvasStore` 状态管理兼容
   - [ ] 测试参数更新流程

#### Phase 2: 其他图表类型（Week 2-3）**暂缓**

**说明**: 先完成上述通用组件和气泡图优化，验证架构可行性后再扩展其他图表类型。

- [ ] `BarSpecificParams.tsx` - 柱状图
- [ ] `LineSpecificParams.tsx` - 折线图
- [ ] `PieSpecificParams.tsx` - 饼图
- [ ] 其他图表类型...

---

### 原开发优先级（归档）

<details>
<summary>点击展开原计划</summary>

### P0 - 核心功能（Week 1-2）
- [x] NumberFormatEditor 组件
- [x] ColorPicker 组件
- [ ] ChartParamsEditor 容器（Accordion 布局）
- [ ] DataSourceEditor
- [ ] BarSpecificParams（最常用）
- [ ] LineSpecificParams（最常用）
- [ ] BubbleSpecificParams（已有基础，需迁移）
- [ ] 5个通用样式分组组件

### P1 - 扩展图表（Week 3）
- [ ] PieSpecificParams
- [ ] TreemapParams
- [ ] HeatmapParams
- [ ] WaffleParams
- [ ] FunnelParams

### P2 - 高级功能（Week 4）
- [ ] 统计图参数编辑器
- [ ] 词云参数编辑器
- [ ] 维恩图参数编辑器
- [ ] 参数搜索功能
- [ ] 参数预设系统
- [ ] 导入/导出配置

</details>

---

## 💡 UX 增强建议

### 1. 智能参数组织

**常用参数上浮：**
```tsx
// 根据使用频率动态调整参数顺序
const COMMON_PARAMS = {
  bar: ['stacked', 'show_label'],        // 柱状图最常调
  bubble: ['bubble_scale', 'alpha'],     // 气泡图最常调
  line: ['marker', 'linestyle'],         // 折线图最常调
};

// 首次使用默认展开常用参数
useEffect(() => {
  const commonParams = COMMON_PARAMS[subplot.kind] || [];
  // 自动展开包含这些参数的分组
}, [subplot.kind]);
```

### 2. 参数搜索/筛选

```tsx
<Input
  placeholder="搜索参数..."
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
  className="mb-2 sticky top-0 z-10"
/>

{/* 根据搜索结果自动展开/折叠分组 */}
{filteredSections.map(section => (
  <Collapsible open={true} key={section.id}>
    {/* ... */}
  </Collapsible>
))}
```

### 3. 快速重置

```tsx
<div className="flex items-center justify-between mb-2">
  <span className="text-sm font-medium">参数设置</span>
  <div className="space-x-2">
    <Button variant="ghost" size="sm" onClick={resetToDefault}>
      重置默认
    </Button>
    <Button variant="ghost" size="sm" onClick={resetToLastSaved}>
      撤销修改
    </Button>
  </div>
</div>
```

### 4. 参数预设

```tsx
<Select onValueChange={applyPreset}>
  <SelectTrigger className="mb-4">
    <SelectValue placeholder="选择样式预设" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="default">默认样式</SelectItem>
    <SelectItem value="minimal">极简风格（无网格、无图例）</SelectItem>
    <SelectItem value="academic">学术风格（完整坐标轴、网格）</SelectItem>
    <SelectItem value="presentation">演示风格（大字体、醒目）</SelectItem>
  </SelectContent>
</Select>
```

### 5. 实时预览提示

```tsx
// 在参数输入框旁显示当前效果预览
<div className="flex items-center gap-2">
  <Input type="number" value={titleFontsize} />
  <div 
    className="text-xs border px-2 py-1 rounded"
    style={{ fontSize: `${titleFontsize}px` }}
  >
    预览
  </div>
</div>
```

### 6. 批量操作

```tsx
// 对称参数批量设置
<div className="flex items-center gap-2">
  <Checkbox
    id="sync-axis-font"
    checked={syncAxisFont}
    onCheckedChange={setSyncAxisFont}
  />
  <label htmlFor="sync-axis-font" className="text-xs">
    X/Y 轴字体同步
  </label>
</div>

{syncAxisFont ? (
  <Input
    value={axisFontsize}
    onChange={(e) => {
      setXAxisFontsize(e.target.value);
      setYAxisFontsize(e.target.value);
    }}
  />
) : (
  <>
    <Input label="X 轴" value={xAxisFontsize} />
    <Input label="Y 轴" value={yAxisFontsize} />
  </>
)}
```

---

## 📊 性能优化策略

### 1. 参数更新防抖

```tsx
import { useDebouncedCallback } from 'use-debounce';

const updateParam = useDebouncedCallback(
  (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value },
    });
  },
  300 // 300ms 防抖
);
```

### 2. 组件懒加载

```tsx
const BubbleSpecificParams = lazy(() => import('./params/BubbleSpecificParams'));
const BarSpecificParams = lazy(() => import('./params/BarSpecificParams'));

<Suspense fallback={<LoadingSpinner />}>
  <PlotSpecificParamsRouter subplot={subplot} />
</Suspense>
```

### 3. 虚拟滚动（如需要）

```tsx
import { FixedSizeList } from 'react-window';

// 如果参数列表超过 50 项，使用虚拟滚动
{paramsList.length > 50 ? (
  <FixedSizeList
    height={600}
    itemCount={paramsList.length}
    itemSize={60}
  >
    {({ index, style }) => (
      <div style={style}>{renderParam(paramsList[index])}</div>
    )}
  </FixedSizeList>
) : (
  paramsList.map(renderParam)
)}
```

---

## 🧪 测试策略

### 单元测试
```typescript
// tests/components/params/TitleSection.test.tsx
describe('TitleSection', () => {
  it('应该正确更新标题文本', () => {
    // ...
  });

  it('应该验证字体大小范围', () => {
    // ...
  });
});
```

### 集成测试
```typescript
// tests/integration/ChartParamsEditor.test.tsx
describe('ChartParamsEditor Integration', () => {
  it('应该正确路由到对应的图表参数编辑器', () => {
    // ...
  });

  it('通用样式更改应该反映到所有图表类型', () => {
    // ...
  });
});
```

### E2E 测试
```typescript
// e2e/chart-params-workflow.spec.ts
test('用户应该能完成完整的图表配置流程', async ({ page }) => {
  // 1. 选择数据源
  // 2. 配置特有参数
  // 3. 调整通用样式
  // 4. 预览图表
  // 5. 保存配置
});
```

---

## 📝 文档计划

- [ ] 组件 API 文档（每个分组组件）
- [ ] 参数映射完整表格
- [ ] 开发者指南：如何添加新图表类型
- [ ] Accordion vs Collapsible 技术决策文档（本文档）
- [ ] 用户手册：参数设置教程
- [ ] 样式预设使用指南

---

## 🔄 迭代计划

### v1.0 - MVP（4 weeks）
- 完成 P0 优先级功能
- 支持 3 种常用图表（柱状图、折线图、气泡图）
- 基础 Collapsible 布局

### v1.1 - 扩展（2 weeks）
- 完成 P1 优先级图表类型
- 添加参数搜索功能
- 优化布局和交互

### v1.2 - 高级功能（2 weeks）
- 参数预设系统
- 批量操作
- 导入/导出配置

### v2.0 - 智能化（未来）
- AI 辅助参数推荐
- 自动样式优化
- 历史配置管理

---

## 📎 相关资源

- **shadcn/ui 组件库**: https://ui.shadcn.com/
  - Collapsible: https://ui.shadcn.com/docs/components/collapsible
  - Tabs: https://ui.shadcn.com/docs/components/tabs
  - Select: https://ui.shadcn.com/docs/components/select
- **后端参数定义**: `chart/plots/base.py::Plot.Style`
- **现有实现**: `frontend/components/subplot/params/BubbleParamsEditor.tsx`
- **设计参考**: Figma、Tableau、PowerBI 参数面板

---

## ✅ 验收标准

- [ ] 所有图表类型都有对应的参数编辑器
- [ ] 通用样式在所有图表间行为一致
- [ ] 参数更改实时反映到图表预览
- [ ] 右侧边栏宽度 300-400px 内完整展示
- [ ] 支持折叠/展开，默认展开常用参数
- [ ] 参数值验证和错误提示
- [ ] 响应式布局适配不同屏幕
- [ ] 性能：参数更改到渲染 < 500ms
- [ ] 测试覆盖率 > 80%

---

## 📌 技术决策记录

### ADR-001: 选择 Accordion（type="multiple"）而非 Collapsible

**日期**: 2025-11-11

**决策**: 使用 `shadcn/ui` 的 **Accordion** 组件（多选模式）作为图表参数编辑器的主布局控件。

**理由**:

1. **统一状态管理**: 单个 `string[]` 数组管理所有展开状态，代码更简洁
   ```typescript
   // Accordion: 简洁
   const [openSections, setOpenSections] = useState<string[]>(['data', 'specific']);
   
   // Collapsible: 分散
   const [openData, setOpenData] = useState(true);
   const [openSpecific, setOpenSpecific] = useState(true);
   const [openTitle, setOpenTitle] = useState(false);
   // ... 每个分组一个状态
   ```

2. **快捷操作便利**: 全展开/全折叠只需一行代码
   ```typescript
   // Accordion
   setOpenSections(['data', 'specific', 'title', 'grid', 'axis', 'ticks', 'legend']);
   
   // Collapsible 需要逐个更新
   setOpenData(true); setOpenSpecific(true); setOpenTitle(true); ...
   ```

3. **语义化更强**: Accordion 明确表达"参数分组"的层级结构

4. **可访问性**: 内置键盘导航（方向键切换分组）

5. **扩展性**: 未来添加新分组只需在数组中添加新值

**备选方案**: Collapsible 独立控制每个分组
- 优势: 每个分组完全独立
- 劣势: 状态管理复杂，快捷操作难实现

**影响范围**: 
- `ChartParamsEditor.tsx` 主容器
- 所有参数分组组件
- 状态持久化逻辑

---

**最后更新**: 2025-11-11  
**负责人**: Frontend Team  
**审核**: Product Team  
**技术决策**: Accordion (type="multiple") for parameter sections
