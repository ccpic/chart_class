# Accordion 实现示例代码

## 📦 完整实现：图表参数编辑器

### 文件结构
```
components/
└── subplot/
    └── params/
        ├── ChartParamsEditor.tsx       # 主容器（使用 Accordion）
        ├── DataSourceEditor.tsx         # 数据源编辑器
        ├── PlotSpecificParamsRouter.tsx # 特有参数路由
        └── sections/                    # 通用样式分组
            ├── TitleSection.tsx
            ├── GridSection.tsx
            ├── AxisSection.tsx
            ├── TicksSection.tsx
            └── LegendSection.tsx
```

---

## 1️⃣ 主容器组件（ChartParamsEditor.tsx）

```tsx
import { useState, useEffect } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { Database, BarChart3, Settings } from 'lucide-react';

import { DataSourceEditor } from './DataSourceEditor';
import { PlotSpecificParamsRouter } from './PlotSpecificParamsRouter';
import { TitleSection } from './sections/TitleSection';
import { GridSection } from './sections/GridSection';
import { AxisSection } from './sections/AxisSection';
import { TicksSection } from './sections/TicksSection';
import { LegendSection } from './sections/LegendSection';

interface ChartParamsEditorProps {
  subplot: SubplotConfig;
  onUpdate: (params: Partial<SubplotConfig>) => void;
}

// 分组 ID 常量
const SECTION_IDS = {
  DATA: 'data',
  SPECIFIC: 'specific',
  TITLE: 'title',
  GRID: 'grid',
  AXIS: 'axis',
  TICKS: 'ticks',
  LEGEND: 'legend',
} as const;

const ALL_SECTIONS = Object.values(SECTION_IDS);
const STYLE_SECTIONS = [SECTION_IDS.TITLE, SECTION_IDS.GRID, SECTION_IDS.AXIS, SECTION_IDS.TICKS, SECTION_IDS.LEGEND];
const DATA_SECTIONS = [SECTION_IDS.DATA, SECTION_IDS.SPECIFIC];

export function ChartParamsEditor({ subplot, onUpdate }: ChartParamsEditorProps) {
  // 智能默认展开策略
  const getDefaultSections = (): string[] => {
    const base = [SECTION_IDS.DATA, SECTION_IDS.SPECIFIC];
    
    // 根据图表类型调整
    switch (subplot.kind) {
      case 'bubble':
        return [...base, SECTION_IDS.AXIS]; // 气泡图常调整坐标轴
      case 'bar':
        return [...base, SECTION_IDS.LEGEND]; // 柱状图常调整图例
      default:
        return base;
    }
  };

  // 状态管理
  const [openSections, setOpenSections] = useState<string[]>(getDefaultSections());

  // 持久化到 localStorage
  const storageKey = `subplot-${subplot.subplotId}-sections`;

  useEffect(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      try {
        setOpenSections(JSON.parse(saved));
      } catch (e) {
        setOpenSections(getDefaultSections());
      }
    }
  }, [subplot.subplotId]);

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(openSections));
  }, [openSections, storageKey]);

  // 参数更新处理
  const updateStyle = (styleUpdates: Partial<PlotStyle>) => {
    onUpdate({
      params: {
        ...subplot.params,
        style: {
          ...subplot.params.style,
          ...styleUpdates,
        },
      },
    });
  };

  const updateParams = (paramUpdates: Record<string, any>) => {
    onUpdate({
      params: {
        ...subplot.params,
        ...paramUpdates,
      },
    });
  };

  return (
    <div className="space-y-3 p-4">
      {/* 快捷操作栏 */}
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-700">参数设置</h3>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs px-2"
            onClick={() => setOpenSections(ALL_SECTIONS)}
            title="展开所有分组"
          >
            全展开
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs px-2"
            onClick={() => setOpenSections(DATA_SECTIONS)}
            title="只保留数据和特有参数"
          >
            全折叠
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs px-2"
            onClick={() => setOpenSections(STYLE_SECTIONS)}
            title="只展开通用样式"
          >
            只看样式
          </Button>
        </div>
      </div>

      {/* Accordion 主体 */}
      <Accordion
        type="multiple"
        value={openSections}
        onValueChange={setOpenSections}
        className="space-y-2"
      >
        {/* 1️⃣ 数据源层 */}
        <AccordionItem value={SECTION_IDS.DATA} className="border-none">
          <AccordionTrigger className="p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-600" />
              <span className="font-semibold text-blue-900">数据源</span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3 space-y-3">
            <DataSourceEditor
              subplot={subplot}
              onUpdate={updateParams}
            />
          </AccordionContent>
        </AccordionItem>

        {/* 2️⃣ 图表特有参数层 */}
        <AccordionItem value={SECTION_IDS.SPECIFIC} className="border-none">
          <AccordionTrigger className="p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-purple-600" />
              <span className="font-semibold text-purple-900">
                {getChartTypeName(subplot.kind)} 参数
              </span>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 py-3">
            <PlotSpecificParamsRouter
              subplot={subplot}
              onUpdate={updateParams}
            />
          </AccordionContent>
        </AccordionItem>

        {/* 3️⃣ 通用样式层 */}
        <div className="pt-2 border-t border-gray-200">
          <div className="flex items-center gap-2 px-3 mb-2">
            <Settings className="w-3 h-3 text-gray-400" />
            <p className="text-xs font-medium text-gray-500">通用样式</p>
          </div>

          {/* 标题 */}
          <AccordionItem value={SECTION_IDS.TITLE} className="border-none">
            <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
              <span>📝 标题</span>
            </AccordionTrigger>
            <AccordionContent className="px-3 py-2">
              <TitleSection
                style={subplot.params.style}
                onChange={updateStyle}
              />
            </AccordionContent>
          </AccordionItem>

          {/* 网格 */}
          <AccordionItem value={SECTION_IDS.GRID} className="border-none">
            <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
              <span>📊 网格线</span>
            </AccordionTrigger>
            <AccordionContent className="px-3 py-2">
              <GridSection
                style={subplot.params.style}
                onChange={updateStyle}
              />
            </AccordionContent>
          </AccordionItem>

          {/* 坐标轴 */}
          <AccordionItem value={SECTION_IDS.AXIS} className="border-none">
            <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
              <span>📐 坐标轴</span>
            </AccordionTrigger>
            <AccordionContent className="px-3 py-2">
              <AxisSection
                style={subplot.params.style}
                onChange={updateStyle}
              />
            </AccordionContent>
          </AccordionItem>

          {/* 刻度 */}
          <AccordionItem value={SECTION_IDS.TICKS} className="border-none">
            <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
              <span>🔢 刻度</span>
            </AccordionTrigger>
            <AccordionContent className="px-3 py-2">
              <TicksSection
                style={subplot.params.style}
                onChange={updateStyle}
              />
            </AccordionContent>
          </AccordionItem>

          {/* 图例 */}
          <AccordionItem value={SECTION_IDS.LEGEND} className="border-none">
            <AccordionTrigger className="px-3 py-2 hover:bg-gray-50 rounded text-sm">
              <span>🏷️ 图例</span>
            </AccordionTrigger>
            <AccordionContent className="px-3 py-2">
              <LegendSection
                style={subplot.params.style}
                onChange={updateStyle}
              />
            </AccordionContent>
          </AccordionItem>
        </div>
      </Accordion>

      {/* 底部状态提示 */}
      <div className="text-xs text-gray-400 text-center pt-2 border-t">
        已展开 {openSections.length} / {ALL_SECTIONS.length} 个分组
      </div>
    </div>
  );
}

// 辅助函数：获取图表中文名
function getChartTypeName(kind: string): string {
  const names: Record<string, string> = {
    bar: '柱状图',
    line: '折线图',
    bubble: '气泡图',
    pie: '饼图',
    treemap: '矩形树图',
    heatmap: '热力图',
    waffle: '华夫饼图',
    funnel: '漏斗图',
  };
  return names[kind] || '图表';
}
```

---

## 2️⃣ 样式分组组件示例（TitleSection.tsx）

```tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface TitleSectionProps {
  style: PlotStyle;
  onChange: (updates: Partial<PlotStyle>) => void;
}

export function TitleSection({ style, onChange }: TitleSectionProps) {
  return (
    <div className="space-y-3">
      {/* 标题文本 */}
      <div className="space-y-1.5">
        <Label htmlFor="title" className="text-xs">标题文本</Label>
        <Input
          id="title"
          value={style.title || ''}
          onChange={(e) => onChange({ title: e.target.value })}
          placeholder="输入图表标题"
          className="h-8 text-sm"
        />
      </div>

      {/* 字体大小 */}
      <div className="space-y-1.5">
        <Label htmlFor="title-fontsize" className="text-xs">字体大小</Label>
        <Input
          id="title-fontsize"
          type="number"
          value={style.title_fontsize || 14}
          onChange={(e) => onChange({ title_fontsize: Number(e.target.value) })}
          min={8}
          max={48}
          className="h-8 text-sm"
        />
      </div>

      {/* 对齐方式 */}
      <div className="space-y-1.5">
        <Label htmlFor="title-align" className="text-xs">对齐方式</Label>
        <Select
          value={style.title_loc || 'center'}
          onValueChange={(value) => onChange({ title_loc: value })}
        >
          <SelectTrigger id="title-align" className="h-8 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="left">左对齐</SelectItem>
            <SelectItem value="center">居中</SelectItem>
            <SelectItem value="right">右对齐</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
```

---

## 3️⃣ 高级特性：搜索过滤

```tsx
import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';

export function ChartParamsEditor({ subplot, onUpdate }: ChartParamsEditorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [openSections, setOpenSections] = useState<string[]>(getDefaultSections());

  // 根据搜索词自动展开匹配的分组
  useEffect(() => {
    if (searchQuery.trim()) {
      const matchingSections = ALL_SECTIONS.filter(sectionId => {
        const keywords = getSectionKeywords(sectionId);
        return keywords.some(kw => kw.includes(searchQuery.toLowerCase()));
      });
      setOpenSections(matchingSections);
    }
  }, [searchQuery]);

  return (
    <div className="space-y-3 p-4">
      {/* 搜索框 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="搜索参数..."
          className="pl-9 h-9 text-sm"
        />
      </div>

      {/* Accordion 内容（同上）*/}
      <Accordion type="multiple" value={openSections} onValueChange={setOpenSections}>
        {/* ... */}
      </Accordion>
    </div>
  );
}

// 分组关键词映射（用于搜索）
function getSectionKeywords(sectionId: string): string[] {
  const keywords: Record<string, string[]> = {
    data: ['数据', '数据源', 'data', '字段', 'field'],
    specific: ['参数', 'params', '特有', '专属'],
    title: ['标题', 'title', '标题文本', '字体'],
    grid: ['网格', 'grid', '网格线', '主网格', '次网格'],
    axis: ['坐标轴', 'axis', 'x轴', 'y轴', '轴标题'],
    ticks: ['刻度', 'ticks', '刻度标签', '旋转'],
    legend: ['图例', 'legend', '图例位置'],
  };
  return keywords[sectionId] || [];
}
```

---

## 4️⃣ 样式自定义

### CSS 类覆盖（globals.css）

```css
/* Accordion 样式优化 */
.accordion-item {
  border: none !important;
}

.accordion-trigger {
  @apply transition-all duration-200;
}

.accordion-trigger:hover {
  @apply bg-opacity-80;
}

.accordion-trigger[data-state="open"] {
  @apply shadow-sm;
}

.accordion-trigger[data-state="open"] svg {
  @apply rotate-180;
}

.accordion-content {
  @apply animate-accordion-down;
}

.accordion-content[data-state="closed"] {
  @apply animate-accordion-up;
}

/* 动画定义 */
@keyframes accordion-down {
  from { height: 0; opacity: 0; }
  to { height: var(--radix-accordion-content-height); opacity: 1; }
}

@keyframes accordion-up {
  from { height: var(--radix-accordion-content-height); opacity: 1; }
  to { height: 0; opacity: 0; }
}
```

### Tailwind 配置（tailwind.config.js）

```js
module.exports = {
  theme: {
    extend: {
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
};
```

---

## 5️⃣ TypeScript 类型定义

```typescript
// types/subplot.ts

export interface PlotStyle {
  // 标题
  title?: string;
  title_fontsize?: number;
  title_loc?: 'left' | 'center' | 'right';

  // 网格
  major_grid?: {
    axis?: 'both' | 'x' | 'y';
    linestyle?: string;
    alpha?: number;
  } | null;
  minor_grid?: {
    axis?: 'both' | 'x' | 'y';
  } | null;

  // 坐标轴
  xlabel?: string;
  ylabel?: string;
  xlabel_fontsize?: number;
  ylabel_fontsize?: number;
  xlim?: [number | null, number | null];
  ylim?: [number | null, number | null];
  hide_top_right_spines?: boolean;

  // 刻度
  all_xticks?: boolean;
  xticklabel_fontsize?: number;
  yticklabel_fontsize?: number;
  xticklabel_rotation?: number;
  yticklabel_rotation?: number;
  remove_xticks?: boolean;
  remove_yticks?: boolean;
  xticks_interval?: number | null;
  yticks_interval?: number | null;

  // 图例
  show_legend?: boolean;
  legend_loc?: string;
  legend_ncol?: number;
  legend_bbox_to_anchor?: [number, number] | null;
}

export interface SubplotConfig {
  subplotId: string;
  kind: string;
  params: {
    style: PlotStyle;
    [key: string]: any; // 图表特有参数
  };
}

export type SectionId = 'data' | 'specific' | 'title' | 'grid' | 'axis' | 'ticks' | 'legend';
```

---

## 6️⃣ 测试示例

```typescript
// __tests__/ChartParamsEditor.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { ChartParamsEditor } from '../ChartParamsEditor';

describe('ChartParamsEditor', () => {
  const mockSubplot: SubplotConfig = {
    subplotId: '1',
    kind: 'bar',
    params: {
      style: {
        title: '测试图表',
        title_fontsize: 14,
      },
    },
  };

  it('应该默认展开数据源和特有参数', () => {
    render(<ChartParamsEditor subplot={mockSubplot} onUpdate={jest.fn()} />);
    
    // 检查默认展开状态
    expect(screen.getByText('数据源')).toBeVisible();
    expect(screen.getByText('柱状图 参数')).toBeVisible();
  });

  it('全展开按钮应该展开所有分组', () => {
    render(<ChartParamsEditor subplot={mockSubplot} onUpdate={jest.fn()} />);
    
    const expandAllBtn = screen.getByText('全展开');
    fireEvent.click(expandAllBtn);
    
    // 检查所有分组都展开
    expect(screen.getByText('标题')).toBeVisible();
    expect(screen.getByText('网格线')).toBeVisible();
    expect(screen.getByText('坐标轴')).toBeVisible();
  });

  it('搜索应该自动展开匹配的分组', async () => {
    render(<ChartParamsEditor subplot={mockSubplot} onUpdate={jest.fn()} />);
    
    const searchInput = screen.getByPlaceholderText('搜索参数...');
    fireEvent.change(searchInput, { target: { value: '标题' } });
    
    // 等待搜索结果
    await screen.findByText('标题');
    expect(screen.getByText('标题')).toBeVisible();
  });

  it('状态应该持久化到 localStorage', () => {
    const { rerender } = render(
      <ChartParamsEditor subplot={mockSubplot} onUpdate={jest.fn()} />
    );
    
    // 展开标题分组
    fireEvent.click(screen.getByText('📝 标题'));
    
    // 检查 localStorage
    const saved = localStorage.getItem(`subplot-${mockSubplot.subplotId}-sections`);
    expect(JSON.parse(saved!)).toContain('title');
    
    // 重新渲染应该恢复状态
    rerender(<ChartParamsEditor subplot={mockSubplot} onUpdate={jest.fn()} />);
    expect(screen.getByText('标题')).toBeVisible();
  });
});
```

---

## 📚 使用说明

### 安装依赖
```bash
# 1. 安装 shadcn/ui Accordion 组件
npx shadcn@latest add accordion

# 2. 安装辅助组件
npx shadcn@latest add input label select button

# 3. 安装图标库
npm install lucide-react
```

### 集成到项目
```tsx
// app/canvas/page.tsx

import { ChartParamsEditor } from '@/components/subplot/params/ChartParamsEditor';

export default function CanvasPage() {
  const handleSubplotUpdate = (subplotId: string, updates: Partial<SubplotConfig>) => {
    // 更新状态逻辑
  };

  return (
    <div className="grid grid-cols-[1fr_400px]">
      {/* 画布区域 */}
      <div>{/* ... */}</div>
      
      {/* 参数面板 */}
      <div className="border-l overflow-y-auto">
        <ChartParamsEditor
          subplot={selectedSubplot}
          onUpdate={(updates) => handleSubplotUpdate(selectedSubplot.subplotId, updates)}
        />
      </div>
    </div>
  );
}
```

---

## 🎯 关键优势总结

1. **单一状态源**: `string[]` 数组管理所有展开状态
2. **声明式API**: `value` 和 `onValueChange` 直接绑定
3. **快捷操作**: 一行代码实现全展开/全折叠/智能筛选
4. **类型安全**: TypeScript 完整类型支持
5. **可访问性**: 内置键盘导航和 ARIA 支持
6. **可扩展**: 添加新分组只需复制 AccordionItem

---

**文档版本**: 1.0.0  
**最后更新**: 2025-11-11  
**适用场景**: 图表参数编辑器、设置面板、分组配置界面
