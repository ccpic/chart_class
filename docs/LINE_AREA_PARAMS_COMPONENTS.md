# 折线图和面积图参数编辑器组件

## 概述

新增了两个前端参数编辑器组件，用于配置折线图（PlotLine）和面积图（PlotArea）的参数。这两个组件遵循项目现有的设计风格，使用 Shadcn UI 组件库，与其他图表参数编辑器保持一致。

## 组件文件

- `frontend/components/subplot/params/LineParamsEditor.tsx` - 折线图参数编辑器
- `frontend/components/subplot/params/AreaParamsEditor.tsx` - 面积图参数编辑器

## LineParamsEditor (折线图参数编辑器)

### 参数映射

对应后端 `PlotLine` 类的以下参数：

| 后端参数 | 类型 | 默认值 | 说明 |
|---------|------|--------|------|
| `show_label` | List[str] | [] | 指定要显示标签的系列 |
| `endpoint_label_only` | bool | False | 标签是否只显示首尾节点 |
| `adjust_labels` | bool | True | 是否自动调整标签位置 |
| `linewidth` | int | 2 | 线宽 |
| `linestyle` | str | "-" | 线型 |
| `marker` | str | "o" | 标记形状 |
| `markersize` | int | 5 | 标记大小 |
| `line_color` | str | None | 线条颜色 |

### UI 布局

使用 Tabs 组件分为 3 个标签页：

#### Tab 1: 基础设置
- **线条样式**
  - 线型选择：实线、虚线、点线、点划线
  - 线宽调整：0.5-10 范围
  
- **标记点样式**
  - 标记形状：圆形、方形、三角形、菱形、星形等
  - 标记大小：1-20 范围

#### Tab 2: 样式选项
- **颜色设置**
  - 统一线条颜色输入框（文本 + 颜色选择器）
  - 留空则使用默认颜色方案
  - 清除颜色按钮

#### Tab 3: 标签设置
- **数据标签**
  - 多选框：选择要显示标签的系列（基于数据框的列）
  - 已选系列的标签展示（带删除按钮）
  
- **标签显示选项**
  - 仅显示首尾节点标签（checkbox）
  - 自动调整标签位置（checkbox，基于 textalloc 库）

### 交互特性

1. **系列选择**：通过 checkbox 多选要显示标签的系列
2. **已选展示**：已选系列以标签形式展示，可点击 X 删除
3. **实时预览**：参数值旁边显示说明（例如：线宽值、透明度百分比）
4. **提示信息**：底部显示使用提示（黄色提示框）

## AreaParamsEditor (面积图参数编辑器)

### 参数映射

对应后端 `PlotArea` 类的以下参数：

| 后端参数 | 类型 | 默认值 | 说明 |
|---------|------|--------|------|
| `stacked` | bool | True | 是否堆积 |
| `show_label` | List[str] | [] | 指定要显示标签的系列 |
| `endpoint_label_only` | bool | False | 标签是否只显示首尾节点 |
| `linewidth` | int | 2 | 线宽 |
| `alpha` | float | 1 | 透明度 |

### UI 布局

使用 Tabs 组件分为 2 个标签页：

#### Tab 1: 基础设置
- **图表类型**
  - 堆积面积图 checkbox（控制 stacked 参数）
  - 说明文字：堆积/并列模式差异
  
- **样式设置**
  - 透明度滑块：0-1 范围，步长 0.05
  - 线宽输入框：0.5-10 范围
  
- **提示**：蓝色提示框说明堆积顺序

#### Tab 2: 标签设置
- **数据标签**
  - 多选框：选择要显示标签的系列
  - 已选系列的标签展示
  
- **标签显示选项**
  - 仅显示首尾节点标签（checkbox）
  
- **标签位置说明**
  - 灰色信息框：说明堆积模式和并列模式下标签位置的差异
  
- **提示**：黄色提示框说明标签样式

### 交互特性

1. **堆积模式切换**：实时切换堆积/并列模式，并更新说明文字
2. **透明度滑块**：显示当前值（两位小数）
3. **系列选择**：与折线图相同的多选机制
4. **位置说明**：详细说明不同模式下标签的位置计算逻辑

## 集成到路由器

已更新 `PlotSpecificParamsRouter.tsx`：

```tsx
// 新增导入
import LineParamsEditor from './LineParamsEditor';
import AreaParamsEditor from './AreaParamsEditor';

// 新增路由规则
if (subplot.chartType === 'line') {
  return <LineParamsEditor subplot={subplot} />;
}

if (subplot.chartType === 'area') {
  return <AreaParamsEditor subplot={subplot} />;
}
```

当 `subplot.chartType` 为 `'line'` 或 `'area'` 时，会自动渲染对应的参数编辑器。

## 设计亮点

### 1. 一致性设计
- 使用相同的 Tabs 布局结构
- 统一的配色方案（蓝色、黄色、灰色信息框）
- 一致的间距和排版

### 2. 用户体验优化
- **参数分组**：相关参数归类到同一 Tab
- **实时反馈**：输入框旁显示当前值和说明
- **智能提示**：根据配置显示相关提示信息
- **视觉反馈**：已选项使用标签形式展示，便于管理

### 3. Shadcn UI 组件使用
- `Tabs`：组织多个参数分组
- `Checkbox`：布尔值参数
- `Input`：数值输入
- `Slider`：连续值调整
- `Select`：枚举值选择
- `Label`：标签说明
- `Button`：操作按钮

### 4. 状态管理
- 使用 Zustand 的 `useCanvasStore` 管理全局状态
- `updateParam` 函数统一处理参数更新
- 支持嵌套参数结构

## 使用示例

### 折线图配置

```typescript
// 配置一个带标签的折线图
subplot.params = {
  show_label: ['销售额', '利润'],  // 显示这两个系列的标签
  endpoint_label_only: true,       // 只显示首尾
  adjust_labels: true,             // 自动调整位置
  linewidth: 2.5,
  linestyle: '-',
  marker: 'o',
  markersize: 6,
  line_color: null                 // 使用默认颜色
};
```

### 面积图配置

```typescript
// 配置一个半透明堆积面积图
subplot.params = {
  stacked: true,                   // 堆积模式
  show_label: ['系列A'],           // 只显示系列A的标签
  endpoint_label_only: false,      // 显示所有点
  linewidth: 2,
  alpha: 0.7                       // 70% 不透明度
};
```

## 后续优化建议

1. **颜色映射**：面积图可以考虑添加自定义颜色设置（类似折线图的 line_color）
2. **标签格式化**：可以添加标签格式化选项（类似柱状图的 label_formatter）
3. **预设方案**：提供常用配置的快捷按钮（如"简约模式"、"详细模式"）
4. **实时预览**：在参数编辑器右侧显示小型预览图

## 技术细节

### 数据源
- `subplot.data.columns`：获取数据框的列名，用于系列选择
- 确保数组类型安全（使用 `Array.isArray()` 检查）

### 参数默认值
使用 `??` 运算符提供默认值：
```typescript
const linewidth = params.linewidth ?? 2;
const alpha = params.alpha ?? 1;
```

### 颜色选择器
组合文本输入和颜色选择器：
```tsx
<Input type="text" value={lineColor || ''} />
<Input type="color" value={lineColor || '#1f77b4'} />
```

## 测试建议

1. **参数验证**：确保所有参数正确传递到后端
2. **边界测试**：测试极值（如透明度 0/1，线宽极小/极大）
3. **数据测试**：使用不同列数的数据框测试系列选择
4. **交互测试**：验证 checkbox、slider、select 的交互逻辑
