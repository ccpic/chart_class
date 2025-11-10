# 前端布局重构计划

## 📋 重构目标

将当前的单页面布局重构为三栏式应用架构：
- **左栏**：全局导航侧边栏（显示画布和子图的层级关系）
- **中栏**：主编辑区（画布编辑或子图预览）
- **右栏**：参数配置面板

## 🎯 核心需求

### 1. 左侧栏 - 全局导航（使用 shadcn/ui Sidebar）
- 展示画布和子图的树形结构
- 画布作为父节点
- 每个子图作为子节点（显示图表类型图标 + 位置）
- 点击画布 → 跳转到 `/canvas` 编辑页面
- 点击子图 → 跳转到 `/subplot/[id]` 编辑页面
- 支持折叠/展开
- 显示数据完整性状态（✅/⚠️）

### 2. 画布编辑页面 `/canvas`
- **中间栏**：网格布局预览（GridPreview）
  - 可视化展示当前网格配置
  - 点击空白格子添加新子图
  - 点击已有子图跳转到子图编辑页面
- **右侧栏**：画布参数配置
  - 网格设置（rows, cols, spacing）
  - 画布尺寸（width, height）
  - 全局样式（title, ytitle, legend）
  - 渲染按钮

### 3. 子图编辑页面 `/subplot/[id]`（使用 shadcn/ui Tabs）
- **中间栏**：Tabs 切换式内容区
  - **Tab 1 - 预览**: 单个子图渲染预览
    - 显示当前子图的实时渲染效果
    - 提供刷新/重新渲染按钮
    - 显示渲染状态和错误
  - **Tab 2 - 数据**: 数据编辑器（独占整个中间栏）
    - JSON 编辑器（更大的编辑空间）
    - 示例数据加载
    - 数据验证和格式化
    - 从文件导入（未来扩展）
    - 数据预览表格（未来扩展）
  - **Tab 3+** - 未来扩展预留
    - 数据源连接器
    - 历史版本
    - AI 数据生成器
- **右侧栏**：参数配置（固定显示）
  - 图表类型选择器
  - 图表特定参数（根据类型动态显示）
  - 返回画布按钮
  - 删除子图按钮

## 🏗️ 技术架构

### 目录结构（重构后）

```
frontend/
├── app/
│   ├── layout.tsx                    # 根布局（包含全局 Sidebar）
│   ├── page.tsx                      # 首页（重定向到 /canvas）
│   ├── canvas/
│   │   └── page.tsx                  # 画布编辑页面
│   └── subplot/
│       └── [id]/
│           └── page.tsx              # 子图编辑页面（使用 Tabs）
├── components/
│   ├── layout/
│   │   ├── AppSidebar.tsx           # 全局侧边栏（shadcn Sidebar）
│   │   ├── MainContent.tsx          # 中间内容区容器
│   │   └── RightPanel.tsx           # 右侧参数面板容器
│   ├── canvas/
│   │   ├── GridPreview.tsx          # ✅ 已存在，需调整
│   │   ├── CanvasParams.tsx         # 新建：画布参数编辑器
│   │   └── RenderButton.tsx         # 新建：独立的渲染按钮组件
│   ├── subplot/
│   │   ├── SubplotTabs.tsx          # 🆕 新建：子图 Tabs 容器
│   │   ├── SubplotPreview.tsx       # 🆕 新建：预览 Tab 内容
│   │   ├── SubplotDataTab.tsx       # 🆕 新建：数据 Tab 内容（整合 DataEditor）
│   │   ├── SubplotParams.tsx        # 新建：右侧参数面板
│   │   ├── ChartTypeSelector.tsx    # ✅ 已存在
│   │   ├── DataEditor.tsx           # ✅ 已存在，将被包装到 SubplotDataTab
│   │   └── ParamsEditor.tsx         # ✅ 已存在
│   └── sidebar/
│       ├── CanvasItem.tsx           # 画布节点组件
│       └── SubplotItem.tsx          # 子图节点组件
├── store/
│   └── canvasStore.ts               # ✅ 已存在，需扩展
├── types/
│   └── canvas.ts                    # ✅ 已存在
└── lib/
    ├── utils.ts                     # ✅ 已存在
    └── api.ts                       # 新建：API 调用封装
```

## 📦 Phase 1: 安装依赖与配置

### 1.1 安装 shadcn/ui 组件
```bash
# 安装 Sidebar 组件
npx shadcn@latest add sidebar

# 安装 Tabs 组件
npx shadcn@latest add tabs
```

### 1.2 安装所需的图标库（如果未安装）
```bash
npm install lucide-react
```

### 1.3 安装路由相关依赖（Next.js 14 已内置，无需额外安装）

## 🔨 Phase 2: 创建全局布局

### 2.1 重构 `app/layout.tsx`
- 引入 `AppSidebar` 组件
- 使用 shadcn/ui 的 `SidebarProvider` 和 `SidebarInset`
- 设置三栏布局结构

### 2.2 创建 `components/layout/AppSidebar.tsx`
**功能**：
- 使用 shadcn Sidebar 组件
- 显示画布信息（标题、网格大小）
- 显示子图列表（图标 + 名称 + 状态）
- 实现导航逻辑（Next.js Link）
- 集成 Zustand store 获取数据

**数据源**：
```typescript
const { canvas, subplots } = useCanvasStore();
```

**UI 结构**：
```tsx
<Sidebar>
  <SidebarHeader>
    <h2>画布项目</h2>
  </SidebarHeader>
  <SidebarContent>
    {/* 画布节点 */}
    <CanvasItem canvas={canvas} />
    
    {/* 子图列表 */}
    <SidebarGroup>
      <SidebarGroupLabel>子图 ({subplots.length})</SidebarGroupLabel>
      <SidebarGroupContent>
        {subplots.map(subplot => (
          <SubplotItem key={subplot.subplotId} subplot={subplot} />
        ))}
      </SidebarGroupContent>
    </SidebarGroup>
  </SidebarContent>
</Sidebar>
```

### 2.3 创建 `components/sidebar/CanvasItem.tsx`
```tsx
// 画布节点：显示画布图标、标题、网格信息
// 点击跳转到 /canvas
<SidebarMenuItem>
  <SidebarMenuButton asChild>
    <Link href="/canvas">
      <LayoutGrid className="w-4 h-4" />
      <span>{canvas.title || "画布"}</span>
      <span className="text-xs text-gray-500">
        {canvas.rows}×{canvas.cols}
      </span>
    </Link>
  </SidebarMenuButton>
</SidebarMenuItem>
```

### 2.4 创建 `components/sidebar/SubplotItem.tsx`
```tsx
// 子图节点：显示图表类型图标、位置、数据状态
// 点击跳转到 /subplot/[id]
<SidebarMenuItem>
  <SidebarMenuButton asChild>
    <Link href={`/subplot/${subplot.subplotId}`}>
      <ChartIcon type={subplot.chartType} />
      <span>子图 {subplot.axIndex + 1}</span>
      <StatusBadge hasData={isDataComplete(subplot)} />
    </Link>
  </SidebarMenuButton>
</SidebarMenuItem>
```

## 🔨 Phase 3: 重构画布编辑页面

### 3.1 重构 `app/canvas/page.tsx`
**新布局**：
```tsx
export default function CanvasPage() {
  return (
    <div className="flex h-full">
      {/* 中间栏：网格预览 */}
      <MainContent>
        <div className="p-6">
          <h1>画布编辑</h1>
          <GridPreview />
        </div>
      </MainContent>
      
      {/* 右侧栏：参数配置 */}
      <RightPanel>
        <CanvasParams />
        <RenderButton />
      </RightPanel>
    </div>
  );
}
```

**移除的内容**：
- ❌ 左侧的 GridControls（移到右侧栏）
- ❌ 中间的渲染预览和渲染按钮（移到独立的渲染页面或模态框）
- ❌ 右侧的 SubplotEditor（移到 `/subplot/[id]` 页面）

### 3.2 创建 `components/canvas/CanvasParams.tsx`
**功能**：整合原 `GridControls.tsx` 的所有功能
- 网格设置表单
- 画布尺寸输入
- 全局样式配置
- 图例设置

### 3.3 创建 `components/canvas/RenderButton.tsx`
**功能**：
- 渲染整个画布
- 显示进度状态
- 在模态框或新页面显示渲染结果
- 提供下载功能

### 3.4 调整 `components/canvas/GridPreview.tsx`
**新行为**：
- 点击空白格子 → 创建新子图并跳转到 `/subplot/[newId]`
- 点击已有子图 → 跳转到 `/subplot/[id]`
- 使用 `useRouter` 实现导航

```tsx
const router = useRouter();

const handleCellClick = (index: number) => {
  const existing = getSubplotByAxIndex(index);
  if (existing) {
    router.push(`/subplot/${existing.subplotId}`);
  } else {
    const newId = addSubplot(index);
    router.push(`/subplot/${newId}`);
  }
};
```

## 🔨 Phase 4: 创建子图编辑页面（使用 Tabs）

### 4.1 创建 `app/subplot/[id]/page.tsx`
```tsx
'use client';

import { useParams, useRouter } from 'next/navigation';
import { useCanvasStore } from '@/store/canvasStore';
import SubplotTabs from '@/components/subplot/SubplotTabs';
import SubplotParams from '@/components/subplot/SubplotParams';
import MainContent from '@/components/layout/MainContent';
import RightPanel from '@/components/layout/RightPanel';

export default function SubplotEditPage() {
  const params = useParams();
  const router = useRouter();
  const subplotId = params.id as string;
  const { subplots, deleteSubplot } = useCanvasStore();
  
  const subplot = subplots.find(s => s.subplotId === subplotId);
  
  if (!subplot) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">子图不存在</h2>
          <button 
            onClick={() => router.push('/canvas')}
            className="px-4 py-2 bg-black text-white rounded-md"
          >
            返回画布
          </button>
        </div>
      </div>
    );
  }
  
  const handleDelete = () => {
    if (confirm('确定要删除这个子图吗？')) {
      deleteSubplot(subplotId);
      router.push('/canvas');
    }
  };
  
  return (
    <div className="flex h-full">
      {/* 中间栏：Tabs */}
      <MainContent>
        <SubplotTabs subplot={subplot} />
      </MainContent>
      
      {/* 右侧栏：参数 */}
      <RightPanel>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">子图配置</h2>
            <span className="text-sm text-gray-500">
              位置: {subplot.axIndex + 1}
            </span>
          </div>
          
          <SubplotParams subplot={subplot} />
          
          {/* 操作按钮 */}
          <div className="pt-6 border-t space-y-2">
            <button
              onClick={() => router.push('/canvas')}
              className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              返回画布
            </button>
            <button
              onClick={handleDelete}
              className="w-full px-4 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50"
            >
              删除子图
            </button>
          </div>
        </div>
      </RightPanel>
    </div>
  );
}
```

### 4.2 创建 `components/subplot/SubplotTabs.tsx`
**功能**：管理子图编辑的 Tabs 切换
```tsx
'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import SubplotPreview from './SubplotPreview';
import SubplotDataTab from './SubplotDataTab';
import { SubplotConfig } from '@/types/canvas';

interface Props {
  subplot: SubplotConfig;
}

export default function SubplotTabs({ subplot }: Props) {
  return (
    <Tabs defaultValue="preview" className="h-full flex flex-col">
      <div className="border-b px-6 pt-6">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="preview">
            📊 预览
          </TabsTrigger>
          <TabsTrigger value="data">
            📝 数据编辑
          </TabsTrigger>
          {/* 未来扩展 */}
          {/* <TabsTrigger value="datasource">🔌 数据源</TabsTrigger> */}
          {/* <TabsTrigger value="history">🕐 历史</TabsTrigger> */}
        </TabsList>
      </div>
      
      <div className="flex-1 overflow-auto">
        <TabsContent value="preview" className="h-full m-0 p-6">
          <SubplotPreview subplot={subplot} />
        </TabsContent>
        
        <TabsContent value="data" className="h-full m-0 p-6">
          <SubplotDataTab subplot={subplot} />
        </TabsContent>
      </div>
    </Tabs>
  );
}
```

### 4.3 创建 `components/subplot/SubplotPreview.tsx`
**功能**：显示子图渲染预览（Tab 1）
```tsx
'use client';

import { useState, useEffect } from 'react';
import { SubplotConfig } from '@/types/canvas';
import { renderSubplot } from '@/lib/api';
import { Loader2, RefreshCw } from 'lucide-react';

interface Props {
  subplot: SubplotConfig;
}

export default function SubplotPreview({ subplot }: Props) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const handleRender = async () => {
    // 检查数据完整性
    if (!subplot.data.columns || subplot.data.columns.length === 0) {
      setError('请先配置数据');
      return;
    }
    if (!subplot.data.data || subplot.data.data.length === 0) {
      setError('数据不能为空');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const blob = await renderSubplot(subplot);
      const url = URL.createObjectURL(blob);
      
      // 清理旧的 URL
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
      
      setImageUrl(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : '渲染失败');
      console.error('渲染错误:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 自动渲染（数据变化时）
  useEffect(() => {
    if (autoRefresh) {
      handleRender();
    }
    
    // 清理函数
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [subplot.data, subplot.chartType, subplot.params]);

  const hasData = subplot.data.columns.length > 0 && subplot.data.data.length > 0;

  return (
    <div className="space-y-4">
      {/* 控制栏 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          {subplot.chartType === 'bar' && '📊 柱状图'}
          {subplot.chartType === 'line' && '📈 折线图'}
          {subplot.chartType === 'pie' && '🥧 饼图'}
          {subplot.chartType === 'area' && '📉 面积图'}
          {subplot.chartType === 'scatter' && '⚫ 散点图'}
        </h3>
        
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            自动刷新
          </label>
          
          <button
            onClick={handleRender}
            disabled={isLoading || !hasData}
            className="flex items-center gap-2 px-3 py-1.5 border rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            {isLoading ? '渲染中...' : '刷新'}
          </button>
        </div>
      </div>

      {/* 预览区域 */}
      <div className="border rounded-lg overflow-hidden bg-white">
        {error && (
          <div className="p-4 bg-red-50 border-b border-red-200">
            <p className="text-sm text-red-600">⚠️ {error}</p>
          </div>
        )}

        {!hasData && !error && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center text-gray-400">
              <div className="text-4xl mb-2">📝</div>
              <p>请在"数据编辑"标签页配置数据</p>
            </div>
          </div>
        )}

        {hasData && !imageUrl && !isLoading && !error && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center text-gray-400">
              <div className="text-4xl mb-2">🎨</div>
              <p>点击"刷新"按钮生成预览</p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex items-center justify-center h-96">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        )}

        {imageUrl && !isLoading && (
          <div className="p-4">
            <img
              src={imageUrl}
              alt="子图预览"
              className="w-full h-auto"
            />
          </div>
        )}
      </div>

      {/* 数据信息 */}
      {hasData && (
        <div className="text-sm text-gray-500">
          数据: {subplot.data.data.length} 行 × {subplot.data.columns.length} 列
        </div>
      )}
    </div>
  );
}
```

### 4.4 创建 `components/subplot/SubplotDataTab.tsx`
**功能**：数据编辑专用 Tab（Tab 2），独占中间栏以提供更大空间
```tsx
'use client';

import { SubplotConfig } from '@/types/canvas';
import DataEditor from './DataEditor';

interface Props {
  subplot: SubplotConfig;
}

export default function SubplotDataTab({ subplot }: Props) {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">数据配置</h3>
        <p className="text-sm text-gray-600">
          在这里编辑图表数据。数据格式为 DataFrame 结构（columns + index + data 矩阵）。
        </p>
      </div>
      
      {/* 复用现有的 DataEditor，但给它更大的空间 */}
      <div className="bg-white rounded-lg border p-6">
        <DataEditor subplot={subplot} />
      </div>
      
      {/* 未来扩展区域 */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="border rounded-lg p-4 bg-gray-50">
          <h4 className="font-semibold mb-2">📥 数据导入</h4>
          <p className="text-sm text-gray-500 mb-3">
            从文件导入数据（未来功能）
          </p>
          <button
            disabled
            className="px-4 py-2 bg-gray-200 text-gray-400 rounded-md cursor-not-allowed"
          >
            从 CSV 导入
          </button>
        </div>
        
        <div className="border rounded-lg p-4 bg-gray-50">
          <h4 className="font-semibold mb-2">🤖 AI 辅助</h4>
          <p className="text-sm text-gray-500 mb-3">
            使用 AI 生成示例数据（未来功能）
          </p>
          <button
            disabled
            className="px-4 py-2 bg-gray-200 text-gray-400 rounded-md cursor-not-allowed"
          >
            AI 生成数据
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 4.5 创建 `components/subplot/SubplotParams.tsx`
**功能**：整合图表类型选择器和参数编辑器（右侧栏固定显示）
```tsx
'use client';

import { SubplotConfig } from '@/types/canvas';
import ChartTypeSelector from './ChartTypeSelector';
import ParamsEditor from './ParamsEditor';

interface Props {
  subplot: SubplotConfig;
}

export default function SubplotParams({ subplot }: Props) {
  return (
    <div className="space-y-6">
      {/* 图表类型选择 */}
      <ChartTypeSelector subplot={subplot} />
      
      {/* 分隔线 */}
      <div className="border-t" />
      
      {/* 图表参数 */}
      <ParamsEditor subplot={subplot} />
    </div>
  );
}
```

## 🔨 Phase 5: 扩展 Zustand Store

### 5.1 更新 `store/canvasStore.ts`
**新增方法**：
```typescript
interface CanvasStore {
  // ... 现有方法
  
  // 新增：返回新创建的子图ID
  addSubplot: (axIndex: number) => string;
  
  // 新增：检查子图数据完整性
  isSubplotDataComplete: (subplotId: string) => boolean;
  
  // 新增：批量操作
  clearAllSubplots: () => void;
  duplicateSubplot: (subplotId: string) => string;
}
```

**实现示例**：
```typescript
addSubplot: (axIndex) => {
  const newId = `subplot-${Date.now()}`;
  const newSubplot: SubplotConfig = {
    subplotId: newId,
    axIndex,
    chartType: "bar",
    data: { columns: [], data: [] },
    params: {},
  };
  set((state) => ({
    subplots: [...state.subplots, newSubplot],
  }));
  return newId; // 返回ID用于导航
},

isSubplotDataComplete: (subplotId) => {
  const state = get();
  const subplot = state.subplots.find(s => s.subplotId === subplotId);
  if (!subplot) return false;
  return (
    subplot.data.columns.length > 0 &&
    subplot.data.data.length > 0
  );
},
```

## 🔨 Phase 6: 创建 API 工具库

### 6.1 创建 `lib/api.ts`
```typescript
import { CanvasConfig, SubplotConfig } from '@/types/canvas';

// 转换工具函数（从 page.tsx 移到这里）
function toSnakeCase(str: string): string { ... }
function convertKeysToSnakeCase(obj: any): any { ... }

// 渲染整个画布
export async function renderCanvas(
  canvas: CanvasConfig,
  subplots: SubplotConfig[]
): Promise<Blob> {
  const requestData = convertKeysToSnakeCase({ canvas, subplots });
  
  const response = await fetch('http://localhost:8000/api/render/canvas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '渲染失败');
  }
  
  return response.blob();
}

// 渲染单个子图
export async function renderSubplot(
  subplot: SubplotConfig
): Promise<Blob> {
  const requestData = convertKeysToSnakeCase({
    chart_type: subplot.chartType,
    data: subplot.data,
    params: subplot.params,
  });
  
  const response = await fetch('http://localhost:8000/api/render/subplot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '渲染失败');
  }
  
  return response.blob();
}
```

## 🔨 Phase 7: 样式优化

### 7.1 调整容器组件样式
```tsx
// components/layout/MainContent.tsx
export default function MainContent({ children }: Props) {
  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      {children}
    </div>
  );
}

// components/layout/RightPanel.tsx
export default function RightPanel({ children }: Props) {
  return (
    <div className="w-[400px] border-l bg-white overflow-y-auto">
      <div className="p-6 space-y-6">
        {children}
      </div>
    </div>
  );
}
```

### 7.2 响应式设计
- 移动端：隐藏右侧栏，使用抽屉式面板
- 平板：缩小右侧栏宽度至 320px
- 桌面：保持 400px

## 📋 实施步骤（优先级排序）

### Step 1: 基础设施 ✅
1. 安装 shadcn/ui Sidebar 和 Tabs 组件
2. 创建布局容器组件（MainContent, RightPanel）
3. 创建 `lib/api.ts` 工具库

### Step 2: 全局布局 🔥
4. 重构 `app/layout.tsx` 集成 Sidebar
5. 创建 `AppSidebar.tsx`
6. 创建 `CanvasItem.tsx` 和 `SubplotItem.tsx`

### Step 3: 画布页面重构 🔥
7. 重构 `app/canvas/page.tsx` 为两栏布局
8. 创建 `CanvasParams.tsx`（整合 GridControls）
9. 调整 `GridPreview.tsx` 添加路由跳转
10. 创建 `RenderButton.tsx`

### Step 4: 子图页面（使用 Tabs）🔥
11. 创建 `app/subplot/[id]/page.tsx`
12. 创建 `SubplotTabs.tsx`（Tabs 容器）
13. 创建 `SubplotPreview.tsx`（预览 Tab）
14. 创建 `SubplotDataTab.tsx`（数据编辑 Tab）
15. 创建 `SubplotParams.tsx`（右侧参数面板）

### Step 5: Store 扩展
16. 更新 `canvasStore.ts` 添加新方法
17. 添加数据验证工具函数

### Step 6: 后端支持（可选）
18. 后端添加 `/api/render/subplot` 端点（单子图渲染）
19. 优化渲染性能

### Step 7: 优化与测试
20. 样式细节调整
21. 添加加载状态和错误处理
22. 端到端测试
23. Tabs 扩展功能预留（数据源、历史记录等）

## 🎨 UI/UX 改进建议

### 1. 侧边栏交互
- ✅ 数据完整的子图显示绿色勾
- ⚠️ 数据不完整显示黄色警告
- 🔵 当前选中的项高亮显示
- 支持键盘导航（↑↓ 切换，Enter 选中）

### 2. 网格预览增强
- 鼠标悬停显示详细信息（图表类型、数据行数）
- 拖拽调整子图位置（Phase 2 功能）
- 右键菜单（复制、删除、属性）

### 3. Tabs 交互优化 🆕
- **智能 Tab 切换**：数据为空时自动跳转到"数据编辑" Tab
- **Tab 徽章**：显示数据完整性状态（✅ 完整 / ⚠️ 待完善）
- **键盘快捷键**：
  - `Ctrl+1`: 切换到预览 Tab
  - `Ctrl+2`: 切换到数据编辑 Tab
- **未来扩展 Tabs**：
  - 📌 **数据源 Tab**: 连接数据库、API、文件
  - 🕐 **历史 Tab**: 查看和恢复历史版本
  - 🤖 **AI 助手 Tab**: 智能数据生成和建议
  - 🎨 **样式 Tab**: 高级样式自定义

### 4. 数据编辑器改进（在 DataTab 中）
- **更大的编辑空间**：独占整个中间栏
- 语法高亮和自动补全
- 数据预览表格（实时显示）
- 从 CSV/Excel 导入（未来功能）
- 数据验证和错误提示
- 示例数据模板库

## 🚀 迁移注意事项

### 保留的组件
- ✅ `types/canvas.ts` - 无需修改
- ✅ `store/canvasStore.ts` - 仅扩展
- ✅ `components/subplot/ChartTypeSelector.tsx`
- ✅ `components/subplot/DataEditor.tsx`
- ✅ `components/subplot/ParamsEditor.tsx`
- ✅ `components/canvas/GridPreview.tsx` - 需调整

### 废弃的组件
- ❌ `components/canvas/GridControls.tsx` → 合并到 `CanvasParams.tsx`
- ❌ `components/subplot/SubplotEditor.tsx` → 拆分到 Tabs 结构

### 调整的组件
- 🔄 `components/subplot/DataEditor.tsx` → 被 `SubplotDataTab.tsx` 包装，获得更大空间

### 数据兼容性
- Zustand store 数据结构保持不变
- API 请求格式保持不变
- 本地存储（如有）需要迁移

## 📊 预期收益

1. **代码组织**：更清晰的关注点分离
2. **用户体验**：
   - 更直观的导航（左侧树形结构）
   - 专注的编辑界面（中/右两栏）
   - **Tab 切换式工作流**：预览 ↔ 数据编辑无缝切换
   - **更大的数据编辑空间**：DataEditor 独占中间栏
   - 更好的空间利用
3. **可维护性**：
   - 组件职责单一
   - Tabs 结构易于扩展新功能
   - 更容易添加新功能
   - 更好的代码复用
4. **可扩展性**：
   - **Tabs 扩展空间**：可轻松添加数据源、历史、AI 等功能
   - 易于添加新页面（如数据源管理）
   - 支持多画布项目
   - 为协作功能打基础

## 🔍 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 路由复杂度增加 | 中 | 使用 Next.js App Router 的最佳实践 |
| 状态管理复杂化 | 低 | Zustand 已经很简洁，扩展有限 |
| 后端 API 不足 | 高 | 先用前端模拟，后端逐步补充 |
| 用户学习曲线 | 低 | 新界面更符合常规应用习惯 |

## ✅ 验收标准

- [ ] 左侧栏正确显示画布和所有子图
- [ ] 点击侧边栏项能正确跳转
- [ ] 画布页面能添加/删除子图
- [ ] 子图页面的 Tabs 切换流畅
- [ ] "预览" Tab 显示实时渲染效果
- [ ] "数据编辑" Tab 提供足够的编辑空间
- [ ] 数据编辑器支持示例数据加载
- [ ] 右侧参数面板在所有 Tab 下固定显示
- [ ] 所有参数修改实时同步到 store
- [ ] 自动刷新功能正常工作
- [ ] 渲染功能正常工作
- [ ] 响应式布局在不同屏幕尺寸下正常
- [ ] 无 console 错误
- [ ] TypeScript 类型检查通过

## 📅 预估时间

- Phase 1-2（基础+布局）: 4-6 小时
- Phase 3（画布页）: 3-4 小时
- Phase 4（子图页 + Tabs）: 4-6 小时
- Phase 5-7（优化测试）: 4-6 小时

**总计**: 15-22 小时（约 2-3 个工作日）

---

## 🎯 Tabs 功能扩展路线图（未来）

基于您的需求，这里是 Tabs 的未来扩展建议：

### Phase 1（当前）
- ✅ Tab 1: 预览
- ✅ Tab 2: 数据编辑

### Phase 2（短期）
- 📌 Tab 3: 数据源连接
  - 连接 CSV/Excel 文件
  - 连接数据库（MySQL, PostgreSQL）
  - 连接 API 端点
  - 数据刷新和同步

### Phase 3（中期）
- 🕐 Tab 4: 历史版本
  - 自动保存编辑历史
  - 版本对比
  - 一键恢复

### Phase 4（长期）
- 🤖 Tab 5: AI 助手
  - 智能数据生成
  - 图表类型推荐
  - 数据异常检测
  - 自动配色建议

- 🎨 Tab 6: 高级样式
  - 颜色主题编辑器
  - 字体和排版设置
  - 动画效果配置

---

**准备好开始了吗？我可以立即开始执行 Phase 1（安装依赖和创建基础组件），您觉得如何？**
