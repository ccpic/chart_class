# Accordion vs Collapsible 技术对比

## 📊 快速决策表

| 需求场景 | 推荐控件 | 理由 |
|---------|---------|------|
| 参数分组，需要同时展开多个 | **Accordion (type="multiple")** | 统一状态管理，快捷操作 |
| 参数分组，只能展开一个 | **Accordion (type="single")** | 互斥展开，节省空间 |
| 独立信息区块，互不关联 | **Collapsible** | 每个独立控制，解耦合 |
| FAQ/帮助文档 | **Accordion (type="single")** | 经典 FAQ 交互模式 |
| 可选信息披露（如高级选项） | **Collapsible** | 简单直观 |

---

## 🔍 深度对比

### 1. 状态管理

#### Accordion (type="multiple")
```typescript
// ✅ 单个数组，集中管理
const [openSections, setOpenSections] = useState<string[]>(['data', 'specific']);

// 全展开
setOpenSections(['data', 'specific', 'title', 'grid', 'axis', 'ticks', 'legend']);

// 全折叠
setOpenSections([]);

// 切换特定分组
setOpenSections(prev => 
  prev.includes('title') 
    ? prev.filter(s => s !== 'title') 
    : [...prev, 'title']
);
```

#### Collapsible
```typescript
// ❌ 分散状态，难以统一操作
const [openData, setOpenData] = useState(true);
const [openSpecific, setOpenSpecific] = useState(true);
const [openTitle, setOpenTitle] = useState(false);
const [openGrid, setOpenGrid] = useState(false);
const [openAxis, setOpenAxis] = useState(false);
const [openTicks, setOpenTicks] = useState(false);
const [openLegend, setOpenLegend] = useState(false);

// 全展开 - 需要逐个设置
setOpenData(true);
setOpenSpecific(true);
setOpenTitle(true);
setOpenGrid(true);
setOpenAxis(true);
setOpenTicks(true);
setOpenLegend(true);
```

---

### 2. 代码量对比

#### Accordion
```tsx
<Accordion type="multiple" value={openSections} onValueChange={setOpenSections}>
  <AccordionItem value="data">
    <AccordionTrigger>数据源</AccordionTrigger>
    <AccordionContent>{/* ... */}</AccordionContent>
  </AccordionItem>
  
  <AccordionItem value="specific">
    <AccordionTrigger>特有参数</AccordionTrigger>
    <AccordionContent>{/* ... */}</AccordionContent>
  </AccordionItem>
  
  {/* 添加新分组只需复制粘贴 */}
</Accordion>
```

**代码行数**: ~3 行/分组

#### Collapsible
```tsx
<Collapsible open={openData} onOpenChange={setOpenData}>
  <CollapsibleTrigger className="flex items-center justify-between w-full">
    <span>数据源</span>
    <ChevronDown className={`transition-transform ${openData ? 'rotate-180' : ''}`} />
  </CollapsibleTrigger>
  <CollapsibleContent>{/* ... */}</CollapsibleContent>
</Collapsible>

<Collapsible open={openSpecific} onOpenChange={setOpenSpecific}>
  <CollapsibleTrigger className="flex items-center justify-between w-full">
    <span>特有参数</span>
    <ChevronDown className={`transition-transform ${openSpecific ? 'rotate-180' : ''}`} />
  </CollapsibleTrigger>
  <CollapsibleContent>{/* ... */}</CollapsibleContent>
</Collapsible>

{/* 每个分组都需要独立状态和事件处理 */}
```

**代码行数**: ~8 行/分组，需要手动实现箭头旋转

---

### 3. 快捷操作实现

#### Accordion
```tsx
// ✅ 简洁高效
<div className="flex gap-2">
  <Button onClick={() => setOpenSections(ALL_SECTIONS)}>全展开</Button>
  <Button onClick={() => setOpenSections([])}>全折叠</Button>
  <Button onClick={() => setOpenSections(STYLE_SECTIONS)}>只看样式</Button>
  <Button onClick={() => setOpenSections(DATA_SECTIONS)}>只看数据</Button>
</div>
```

#### Collapsible
```tsx
// ❌ 繁琐重复
<div className="flex gap-2">
  <Button onClick={() => {
    setOpenData(true);
    setOpenSpecific(true);
    setOpenTitle(true);
    setOpenGrid(true);
    setOpenAxis(true);
    setOpenTicks(true);
    setOpenLegend(true);
  }}>全展开</Button>
  
  <Button onClick={() => {
    setOpenData(false);
    setOpenSpecific(false);
    setOpenTitle(false);
    setOpenGrid(false);
    setOpenAxis(false);
    setOpenTicks(false);
    setOpenLegend(false);
  }}>全折叠</Button>
</div>
```

---

### 4. 持久化存储

#### Accordion
```typescript
// ✅ 一次性存储/读取
useEffect(() => {
  const saved = localStorage.getItem('openSections');
  if (saved) setOpenSections(JSON.parse(saved));
}, []);

useEffect(() => {
  localStorage.setItem('openSections', JSON.stringify(openSections));
}, [openSections]);
```

#### Collapsible
```typescript
// ❌ 每个状态都需要独立处理
useEffect(() => {
  const savedData = localStorage.getItem('openData');
  const savedSpecific = localStorage.getItem('openSpecific');
  const savedTitle = localStorage.getItem('openTitle');
  // ... 7 个状态
  
  if (savedData) setOpenData(JSON.parse(savedData));
  if (savedSpecific) setOpenSpecific(JSON.parse(savedSpecific));
  // ...
}, []);

// 需要 7 个 useEffect 监听各自的状态
```

---

### 5. 可访问性（A11y）

| 特性 | Accordion | Collapsible |
|------|-----------|-------------|
| 键盘导航 | ✅ 内置方向键支持 | ❌ 需手动实现 |
| ARIA 角色 | ✅ `role="region"` 等完整语义 | ⚠️ 基础语义 |
| 焦点管理 | ✅ 自动管理焦点循环 | ❌ 需手动实现 |
| 屏幕阅读器 | ✅ "展开 X，共 Y 项"提示 | ⚠️ 基础提示 |

**测试**: 按 Tab 键导航到 Accordion，按 ↓/↑ 可切换分组焦点

---

### 6. 性能对比

#### 渲染性能
- **Accordion**: 单个组件实例，7 个子项 → 更少的 React 节点
- **Collapsible**: 7 个独立组件实例 → 更多的事件监听器

#### 状态更新
```typescript
// Accordion: 1 次状态更新
setOpenSections(prev => [...prev, 'title']); // ✅ 触发 1 次渲染

// Collapsible: N 次状态更新（如需批量操作）
setOpenTitle(true);    // 渲染 1
setOpenGrid(true);     // 渲染 2
setOpenAxis(true);     // 渲染 3
// ❌ 触发 N 次渲染（虽然 React 18 会批处理，但状态仍分散）
```

---

## 🎯 图表参数编辑器的最终选择

### ✅ 选择：Accordion (type="multiple")

#### 原因总结

1. **需求匹配度 100%**
   - ✅ 需要同时展开多个分组（对比调整参数）
   - ✅ 需要快捷全展开/全折叠
   - ✅ 7 个分组需要统一管理

2. **开发效率提升 60%**
   - 代码量减少：~3 行/分组 vs ~8 行/分组
   - 状态管理简化：1 个数组 vs 7 个布尔值
   - 快捷操作便利：1 行代码 vs 7 行重复

3. **用户体验提升**
   - 键盘导航支持（方向键切换）
   - 完整的无障碍支持
   - 更好的语义化结构

4. **可维护性**
   - 添加新分组：只需添加数组元素
   - 批量操作：直接操作数组
   - 状态同步：自动保持一致

---

## 📋 实施清单

### Phase 1: 安装组件
```bash
npx shadcn@latest add accordion
```

### Phase 2: 创建主容器
```tsx
// components/subplot/params/ChartParamsEditor.tsx
const [openSections, setOpenSections] = useState<string[]>(['data', 'specific']);

<Accordion type="multiple" value={openSections} onValueChange={setOpenSections}>
  {/* 分组内容 */}
</Accordion>
```

### Phase 3: 迁移现有组件
- [ ] 将 BubbleParamsEditor 迁移到新架构
- [ ] 创建通用样式分组组件（5个）
- [ ] 创建数据源编辑器

---

## 💡 最佳实践

### 1. 分组命名规范
```typescript
const SECTION_IDS = {
  DATA: 'data',
  SPECIFIC: 'specific',
  TITLE: 'title',
  GRID: 'grid',
  AXIS: 'axis',
  TICKS: 'ticks',
  LEGEND: 'legend',
} as const;

// 使用常量避免拼写错误
<AccordionItem value={SECTION_IDS.DATA}>
```

### 2. 默认展开策略
```typescript
// 根据图表类型智能默认展开
const getDefaultOpenSections = (chartKind: string): string[] => {
  const base = ['data', 'specific'];
  
  // 气泡图常需要调整坐标轴
  if (chartKind === 'bubble') return [...base, 'axis'];
  
  // 柱状图常需要调整图例
  if (chartKind === 'bar') return [...base, 'legend'];
  
  return base;
};
```

### 3. 状态持久化
```typescript
// 每个子图独立记住展开状态
const storageKey = `subplot-${subplot.subplotId}-sections`;

useEffect(() => {
  const saved = localStorage.getItem(storageKey);
  if (saved) {
    setOpenSections(JSON.parse(saved));
  } else {
    setOpenSections(getDefaultOpenSections(subplot.kind));
  }
}, [subplot.subplotId, subplot.kind]);

useEffect(() => {
  localStorage.setItem(storageKey, JSON.stringify(openSections));
}, [openSections, storageKey]);
```

---

## 📚 参考资源

- **Radix UI Accordion**: https://www.radix-ui.com/primitives/docs/components/accordion
- **shadcn/ui Accordion**: https://ui.shadcn.com/docs/components/accordion
- **ARIA Accordion Pattern**: https://www.w3.org/WAI/ARIA/apg/patterns/accordion/
- **项目开发计划**: `CHART_PARAMS_UI_PLAN.md`

---

**决策日期**: 2025-11-11  
**决策人**: Frontend Team  
**审核状态**: ✅ 已批准
