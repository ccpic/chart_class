# NumberFormatEditor 组件

## 概述

`NumberFormatEditor` 是一个可视化的 Python 数值格式化字符串编辑器，提供直观的 UI 界面来配置格式化参数，而无需手动编写格式字符串。

## 功能特性

- ✅ **可视化配置**：通过复选框和输入框配置格式化选项
- ✅ **实时预览**：即时显示格式化效果示例
- ✅ **格式解析**：自动解析现有格式字符串到 UI 状态
- ✅ **格式生成**：根据 UI 状态自动生成标准 Python 格式字符串
- ✅ **帮助提示**：悬停显示详细说明和示例

## 支持的格式选项

| 选项 | 说明 | 示例 |
|------|------|------|
| **+号** | 正数显示加号 | `+1234` |
| **千位符** | 使用逗号分隔千位 | `1,234` |
| **百分号** | 数值乘100后显示% | `12.34%` |
| **小数位** | 保留的小数位数 (0-10) | `1234.56` |

## 生成的格式模式

```
{:[+][,][.precision][%]}f
```

### 示例格式

- `{:,.0f}` → `1,234` (千位符，0位小数)
- `{:+,.2f}` → `+1,234.56` (加号、千位符、2位小数)
- `{:.1%}` → `12.3%` (1位小数百分比)
- `{:+.2%}` → `+12.35%` (加号、2位小数百分比)

## 使用方法

### 基本用法

```tsx
import NumberFormatEditor from '@/components/ui/number-format-editor';

function MyComponent() {
  const [format, setFormat] = useState('{:,.0f}');

  return (
    <NumberFormatEditor
      value={format}
      onChange={setFormat}
      label="数值格式"
    />
  );
}
```

### 在表单中使用

```tsx
function ChartParamsEditor({ params, updateParam }) {
  return (
    <div className="space-y-4">
      {/* X 轴格式化 */}
      <NumberFormatEditor
        label="X 轴格式化"
        value={params.x_fmt || '{:,.0f}'}
        onChange={(fmt) => updateParam('x_fmt', fmt)}
      />

      {/* Y 轴格式化 */}
      <NumberFormatEditor
        label="Y 轴格式化"
        value={params.y_fmt || '{:,.0f}'}
        onChange={(fmt) => updateParam('y_fmt', fmt)}
      />
    </div>
  );
}
```

### 隐藏帮助提示

```tsx
<NumberFormatEditor
  value={format}
  onChange={setFormat}
  showHelp={false}
/>
```

## Props API

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `value` | `string` | 必需 | 当前格式字符串 |
| `onChange` | `(format: string) => void` | 必需 | 格式变化回调 |
| `label` | `string` | `'数值格式'` | 显示的标签文本 |
| `showHelp` | `boolean` | `true` | 是否显示帮助图标和提示 |

## 组件结构

```
┌─────────────────────────────────────────┐
│ 数值格式 ⓘ                              │
├─────────────────────────────────────────┤
│  +号   千位符  百分号   小数位          │
│   ☐      ☑      ☐      [0]             │
├─────────────────────────────────────────┤
│ 格式: {:,.0f} → 示例: 1,235            │
└─────────────────────────────────────────┘
```

## 技术实现

### 格式解析

使用正则表达式解析格式字符串：

```typescript
/\{:([+])?(,)?\.(\d+)([f%])\}/
```

匹配组：
1. `([+])?` - 可选的加号
2. `(,)?` - 可选的千位符
3. `\.(\d+)` - 必需的小数位数
4. `([f%])` - 浮点数或百分比标记

### 格式生成

根据 UI 状态组装格式字符串：

```typescript
const buildFormat = (plus, thousands, percent, decimals) => {
  let fmt = '{:';
  if (plus) fmt += '+';
  if (thousands) fmt += ',';
  fmt += `.${decimals}`;
  fmt += percent ? '%' : 'f';
  return fmt + '}';
};
```

### 示例生成

使用固定数值 `1234.5678` 模拟 Python 格式化：

```typescript
const getExample = () => {
  let result = 1234.5678;
  
  if (showPercent) {
    result = result / 100;
    result = result.toFixed(decimals);
    // 添加千位符、加号、百分号
  } else {
    result = result.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
    // 添加加号
  }
  
  return result;
};
```

## 应用场景

### 图表参数编辑器

在各类图表参数编辑器中替代原有的文本输入框：

- ✅ 气泡图：X/Y 轴格式化
- ✅ 柱状图：数值标签格式化
- ✅ 折线图：数据点标签格式化
- ✅ 热力图：色标格式化

### 已应用示例

- `BubbleParamsEditor.tsx` - X 轴格式化、Y 轴格式化

## 设计优势

### 用户体验

1. **降低学习成本**：无需了解 Python 格式化语法
2. **即时反馈**：实时预览格式化效果
3. **减少错误**：通过 UI 约束避免语法错误
4. **紧凑布局**：4个控件在一行显示，节省空间

### 技术优势

1. **双向绑定**：解析 → UI → 生成完整闭环
2. **类型安全**：TypeScript 接口保证类型正确
3. **可复用**：单一组件适配所有格式化场景
4. **可维护**：集中管理格式化逻辑

## 未来扩展

可能的功能增强：

- [ ] 支持更多格式选项（如科学计数法）
- [ ] 自定义示例数值
- [ ] 预设格式模板（货币、百分比等）
- [ ] 格式验证和错误提示
- [ ] 国际化支持（不同语言的千位符）

## 相关文件

- 组件源码: `frontend/components/ui/number-format-editor.tsx`
- 应用示例: `frontend/components/subplot/params/BubbleParamsEditor.tsx`
- UI 组件库: `frontend/components/ui/`

## 许可

与项目主许可协议一致。
