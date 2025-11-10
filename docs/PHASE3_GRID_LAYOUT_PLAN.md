# Phase 3: 网格布局（Grid Layout）开发计划

## 项目背景

### MVP 现状（已完成）
✅ **后端**：
- FastAPI 应用运行在 http://localhost:8000
- 桥接层 `WebChartAdapter` 支持单子图 bar 图渲染
- `/api/render` 端点接收数据并返回 PNG 图片

✅ **前端**：
- Next.js 应用运行在 http://localhost:3000
- 左中右三段布局
- 数据输入（JSON） + 参数控制（3个参数） + 图表预览

✅ **功能限制**：
- 仅支持 1x1 单子图画布
- 仅支持 bar 图表类型
- 参数有限（stacked, show_label, label_formatter）

### Phase 3 目标

🎯 **核心目标**：扩展到支持多子图网格布局（GridFigure 的核心能力）

**功能范围**：
- ✅ 支持 M×N 网格布局（如 2×2, 1×3, 3×2 等）
- ✅ 每个子图独立配置数据和参数
- ✅ 支持多种图表类型组合（bar + line + pie 等）
- ✅ 可视化网格编辑器（拖拽、添加、删除子图）
- ✅ 保持桥接层隔离，不修改原有 chart_class2 代码

**非目标**（暂不实现）**：
- ❌ 跨行跨列（rowspan/colspan）- 留待后续 Phase
- ❌ 数据库持久化 - 仍使用前端状态
- ❌ 项目保存/加载 - 留待后续 Phase
- ❌ 复杂样式定制 - 仅实现基础样式

---

## 架构设计

### 数据流更新

```
前端 (Grid Editor)
    ↓ 网格配置 (rows, cols) + 子图列表 (subplots[])
API (/api/render)
    ↓ RenderRequestModel (Pydantic)
桥接层 (WebChartAdapter.render_canvas)
    ↓ 循环调用 f.plot(kind=..., ax_index=...)
GridFigure (原库)
    ↓ 返回 PNG bytes
```

### 核心数据模型

#### 后端数据模型（Pydantic）

```python
# web_api/models.py (新建文件)

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class ChartType(str, Enum):
    """支持的图表类型"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    # Phase 4 可扩展更多类型

class ChartDataModel(BaseModel):
    """图表数据"""
    columns: List[str] = Field(..., description="列名列表")
    index: Optional[List[str]] = Field(None, description="索引列表")
    data: List[List[Any]] = Field(..., description="数据矩阵")

class SubplotConfigModel(BaseModel):
    """单个子图配置"""
    subplot_id: str = Field(..., description="子图唯一ID")
    ax_index: int = Field(..., description="子图位置索引")
    chart_type: ChartType = Field(..., description="图表类型")
    data: ChartDataModel = Field(..., description="数据")
    params: Dict[str, Any] = Field(default_factory=dict, description="图表参数")
    
class CanvasConfigModel(BaseModel):
    """画布配置"""
    width: float = Field(15, description="画布宽度")
    height: float = Field(6, description="画布高度")
    rows: int = Field(1, ge=1, le=6, description="网格行数")
    cols: int = Field(1, ge=1, le=6, description="网格列数")
    style: Optional[Dict[str, Any]] = Field(None, description="全局样式")

class RenderRequestModel(BaseModel):
    """完整渲染请求"""
    canvas: CanvasConfigModel = Field(..., description="画布配置")
    subplots: List[SubplotConfigModel] = Field(..., description="子图列表")
```

#### 前端数据模型（TypeScript）

```typescript
// frontend/types/canvas.ts (新建文件)

export type ChartType = 'bar' | 'line' | 'pie' | 'area' | 'scatter';

export interface ChartData {
  columns: string[];
  index?: string[];
  data: any[][];
}

export interface SubplotConfig {
  subplotId: string;
  axIndex: number;
  chartType: ChartType;
  data: ChartData;
  params: Record<string, any>;
}

export interface CanvasConfig {
  width: number;
  height: number;
  rows: number;
  cols: number;
  style?: Record<string, any>;
}

export interface RenderRequest {
  canvas: CanvasConfig;
  subplots: SubplotConfig[];
}
```

---

## 后端实现计划

### 任务 1: 扩展桥接层（2-3天）

**目标**：让 `WebChartAdapter` 支持多子图渲染

#### 文件：`web_bridge/adapters/chart_adapter.py`

```python
# 现有代码基础上扩展

class WebChartAdapter:
    """Web 图表适配器 - 桥接 chart_class2 库"""
    
    # 保留现有的 render_bar_chart() 方法
    
    def render_canvas(
        self, 
        canvas_config: Dict[str, Any],
        subplots: List[Dict[str, Any]]
    ) -> bytes:
        """
        渲染多子图画布
        
        Args:
            canvas_config: 画布配置 {width, height, rows, cols, style}
            subplots: 子图列表 [{subplot_id, ax_index, chart_type, data, params}, ...]
        
        Returns:
            PNG 图片字节
        """
        import matplotlib.pyplot as plt
        from chart import GridFigure
        import pandas as pd
        from io import BytesIO
        
        # 1. 创建 GridFigure
        f = plt.figure(
            FigureClass=GridFigure,
            width=canvas_config.get('width', 15),
            height=canvas_config.get('height', 6),
            nrows=canvas_config.get('rows', 1),
            ncols=canvas_config.get('cols', 1),
            style=canvas_config.get('style')
        )
        
        # 2. 按 ax_index 排序子图，确保顺序正确
        sorted_subplots = sorted(subplots, key=lambda x: x['ax_index'])
        
        # 3. 循环渲染每个子图
        for subplot in sorted_subplots:
            try:
                # 转换数据为 DataFrame
                data_dict = subplot['data']
                df = pd.DataFrame(
                    data=data_dict['data'],
                    columns=data_dict['columns']
                )
                if data_dict.get('index'):
                    df.index = data_dict['index']
                
                # 获取图表类型和参数
                chart_type = subplot['chart_type']
                params = subplot['params'].copy()
                ax_index = subplot['ax_index']
                
                # 调用 f.plot() 绘制子图
                f.plot(
                    kind=chart_type,
                    data=df,
                    ax_index=ax_index,
                    **params
                )
                
            except Exception as e:
                # 错误处理：在对应位置显示错误信息
                print(f"子图 {subplot['subplot_id']} 渲染失败: {str(e)}")
                # 可选：在图表上显示错误文本
                ax = f.axes[ax_index]
                ax.text(0.5, 0.5, f"渲染错误\n{str(e)}", 
                       ha='center', va='center', color='red')
        
        # 4. 保存为 PNG
        buf = BytesIO()
        f.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.read()
        buf.close()
        plt.close(f)
        
        return image_bytes
    
    def get_supported_chart_types(self) -> List[str]:
        """返回支持的图表类型列表"""
        return ['bar', 'line', 'pie', 'area', 'scatter']
    
    def get_default_params(self, chart_type: str) -> Dict[str, Any]:
        """
        返回指定图表类型的默认参数
        
        用于前端表单初始化
        """
        defaults = {
            'bar': {
                'stacked': True,
                'show_label': True,
                'label_formatter': '{abs}'
            },
            'line': {
                'marker': 'o',
                'show_label': False,
                'linewidth': 2
            },
            'pie': {
                'show_label': True,
                'autopct': '%1.1f%%'
            },
            'area': {
                'stacked': True,
                'alpha': 0.7
            },
            'scatter': {
                'marker': 'o',
                'size': 50
            }
        }
        return defaults.get(chart_type, {})
```

**测试代码**：

```python
# test_grid_adapter.py (新建)

from web_bridge.adapters.chart_adapter import WebChartAdapter

def test_render_2x2_grid():
    """测试 2x2 网格渲染"""
    adapter = WebChartAdapter()
    
    canvas_config = {
        'width': 15,
        'height': 12,
        'rows': 2,
        'cols': 2
    }
    
    subplots = [
        {
            'subplot_id': 'subplot-1',
            'ax_index': 0,
            'chart_type': 'bar',
            'data': {
                'columns': ['A', 'B', 'C'],
                'index': ['Q1', 'Q2'],
                'data': [[100, 200, 150], [120, 180, 160]]
            },
            'params': {'stacked': True, 'show_label': True}
        },
        {
            'subplot_id': 'subplot-2',
            'ax_index': 1,
            'chart_type': 'line',
            'data': {
                'columns': ['X', 'Y'],
                'index': ['M1', 'M2', 'M3'],
                'data': [[10, 20], [15, 25], [12, 22]]
            },
            'params': {'marker': 'o'}
        },
        {
            'subplot_id': 'subplot-3',
            'ax_index': 2,
            'chart_type': 'pie',
            'data': {
                'columns': ['Category'],
                'index': ['Cat1', 'Cat2', 'Cat3'],
                'data': [[30], [50], [20]]
            },
            'params': {'show_label': True}
        },
        {
            'subplot_id': 'subplot-4',
            'ax_index': 3,
            'chart_type': 'area',
            'data': {
                'columns': ['Sales'],
                'index': ['Jan', 'Feb', 'Mar'],
                'data': [[100], [120], [110]]
            },
            'params': {'stacked': False}
        }
    ]
    
    result = adapter.render_canvas(canvas_config, subplots)
    
    # 保存测试结果
    with open('test_grid_2x2.png', 'wb') as f:
        f.write(result)
    
    assert len(result) > 0
    print("✅ 2x2 网格测试通过！")

if __name__ == '__main__':
    test_render_2x2_grid()
```

---

### 任务 2: 更新 API 端点（1天）

#### 文件：`web_api/models.py`（新建）

```python
# 将上面定义的 Pydantic 模型放到这个文件
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

# （粘贴前面定义的所有模型）
```

#### 文件：`web_api/main.py`（更新）

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn

# 导入模型
from web_api.models import (
    RenderRequestModel,
    ChartType,
    CanvasConfigModel,
    SubplotConfigModel
)
from web_bridge.adapters.chart_adapter import WebChartAdapter

app = FastAPI(title="Chart Class Web API", version="0.2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化适配器（单例）
chart_adapter = WebChartAdapter()

# ============ 新端点：多子图渲染 ============

@app.post("/api/render/canvas")
async def render_canvas(request: RenderRequestModel):
    """
    渲染多子图画布
    
    Request Body:
    {
      "canvas": {
        "width": 15,
        "height": 12,
        "rows": 2,
        "cols": 2
      },
      "subplots": [
        {
          "subplot_id": "subplot-1",
          "ax_index": 0,
          "chart_type": "bar",
          "data": {...},
          "params": {...}
        },
        ...
      ]
    }
    """
    try:
        # 验证子图数量
        total_grids = request.canvas.rows * request.canvas.cols
        if len(request.subplots) > total_grids:
            raise HTTPException(
                status_code=400,
                detail=f"子图数量 ({len(request.subplots)}) 超过网格容量 ({total_grids})"
            )
        
        # 验证 ax_index 范围
        for subplot in request.subplots:
            if subplot.ax_index >= total_grids:
                raise HTTPException(
                    status_code=400,
                    detail=f"子图索引 {subplot.ax_index} 超出范围 (0-{total_grids-1})"
                )
        
        # 调用桥接层渲染
        canvas_dict = request.canvas.dict()
        subplots_list = [s.dict() for s in request.subplots]
        
        image_bytes = chart_adapter.render_canvas(canvas_dict, subplots_list)
        
        return Response(content=image_bytes, media_type="image/png")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"渲染失败: {str(e)}")

# ============ 工具端点 ============

@app.get("/api/chart-types")
async def get_chart_types():
    """获取支持的图表类型列表"""
    return {
        "chart_types": chart_adapter.get_supported_chart_types()
    }

@app.get("/api/chart-types/{chart_type}/defaults")
async def get_default_params(chart_type: ChartType):
    """获取指定图表类型的默认参数"""
    return chart_adapter.get_default_params(chart_type.value)

# ============ 保留原有的单图端点（向后兼容）============

@app.post("/api/render")
async def render_single_chart(request: dict):
    """
    单图渲染（MVP 兼容端点）
    
    保留此端点以确保 MVP 前端仍能工作
    """
    try:
        data = request.get("data")
        params = request.get("params", {})
        
        # 使用原有的 render_bar_chart 方法
        image_bytes = chart_adapter.render_bar_chart(data, params)
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**API 测试脚本**：

```python
# test_grid_api.py (新建)

import requests
import json

url = "http://localhost:8000/api/render/canvas"

payload = {
    "canvas": {
        "width": 15,
        "height": 12,
        "rows": 2,
        "cols": 2
    },
    "subplots": [
        {
            "subplot_id": "subplot-1",
            "ax_index": 0,
            "chart_type": "bar",
            "data": {
                "columns": ["品牌A", "品牌B"],
                "index": ["Q1", "Q2"],
                "data": [[100, 200], [120, 180]]
            },
            "params": {"stacked": True, "show_label": True}
        },
        {
            "subplot_id": "subplot-2",
            "ax_index": 1,
            "chart_type": "line",
            "data": {
                "columns": ["销售额"],
                "index": ["1月", "2月", "3月"],
                "data": [[100], [120], [110]]
            },
            "params": {"marker": "o"}
        }
    ]
}

print(f"发送请求到: {url}")
response = requests.post(url, json=payload)

if response.status_code == 200:
    with open("test_grid_output.png", "wb") as f:
        f.write(response.content)
    print("✅ 成功！图片已保存到 test_grid_output.png")
else:
    print(f"❌ 错误: {response.status_code}")
    print(response.text)
```

---

## 前端实现计划

### 任务 3: 状态管理（2天）

#### 文件：`frontend/store/canvasStore.ts`（新建）

```typescript
import { create } from 'zustand';
import { CanvasConfig, SubplotConfig, ChartType } from '@/types/canvas';

interface CanvasStore {
  // 状态
  canvas: CanvasConfig;
  subplots: SubplotConfig[];
  selectedSubplotId: string | null;
  
  // Canvas Actions
  updateCanvas: (config: Partial<CanvasConfig>) => void;
  
  // Subplot Actions
  addSubplot: (axIndex: number) => void;
  updateSubplot: (subplotId: string, updates: Partial<SubplotConfig>) => void;
  deleteSubplot: (subplotId: string) => void;
  selectSubplot: (subplotId: string | null) => void;
  
  // 工具方法
  getSubplotByAxIndex: (axIndex: number) => SubplotConfig | undefined;
  getEmptyGridCells: () => number[];
  
  // 重置
  reset: () => void;
}

const defaultCanvas: CanvasConfig = {
  width: 15,
  height: 6,
  rows: 1,
  cols: 1,
};

export const useCanvasStore = create<CanvasStore>((set, get) => ({
  canvas: defaultCanvas,
  subplots: [],
  selectedSubplotId: null,
  
  updateCanvas: (config) => 
    set((state) => ({
      canvas: { ...state.canvas, ...config }
    })),
  
  addSubplot: (axIndex) => {
    const newSubplot: SubplotConfig = {
      subplotId: `subplot-${Date.now()}`,
      axIndex,
      chartType: 'bar',
      data: {
        columns: [],
        data: []
      },
      params: {}
    };
    set((state) => ({
      subplots: [...state.subplots, newSubplot],
      selectedSubplotId: newSubplot.subplotId
    }));
  },
  
  updateSubplot: (subplotId, updates) =>
    set((state) => ({
      subplots: state.subplots.map(subplot =>
        subplot.subplotId === subplotId
          ? { ...subplot, ...updates }
          : subplot
      )
    })),
  
  deleteSubplot: (subplotId) =>
    set((state) => ({
      subplots: state.subplots.filter(s => s.subplotId !== subplotId),
      selectedSubplotId: state.selectedSubplotId === subplotId 
        ? null 
        : state.selectedSubplotId
    })),
  
  selectSubplot: (subplotId) =>
    set({ selectedSubplotId: subplotId }),
  
  getSubplotByAxIndex: (axIndex) => {
    const state = get();
    return state.subplots.find(s => s.axIndex === axIndex);
  },
  
  getEmptyGridCells: () => {
    const state = get();
    const total = state.canvas.rows * state.canvas.cols;
    const occupied = state.subplots.map(s => s.axIndex);
    const empty: number[] = [];
    for (let i = 0; i < total; i++) {
      if (!occupied.includes(i)) {
        empty.push(i);
      }
    }
    return empty;
  },
  
  reset: () =>
    set({
      canvas: defaultCanvas,
      subplots: [],
      selectedSubplotId: null
    })
}));
```

---

### 任务 4: 网格预览组件（3天）

#### 文件：`frontend/components/canvas/GridPreview.tsx`（新建）

```typescript
'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';

export default function GridPreview() {
  const { canvas, subplots, selectedSubplotId, selectSubplot, addSubplot, getSubplotByAxIndex } = useCanvasStore();
  
  const { rows, cols } = canvas;
  const totalCells = rows * cols;
  
  // 生成网格单元格
  const cells = Array.from({ length: totalCells }, (_, i) => i);
  
  const handleCellClick = (axIndex: number) => {
    const subplot = getSubplotByAxIndex(axIndex);
    if (subplot) {
      // 如果已有子图，选中它
      selectSubplot(subplot.subplotId);
    } else {
      // 如果为空，添加新子图
      addSubplot(axIndex);
    }
  };
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">网格布局 ({rows}×{cols})</h3>
        <div className="text-xs text-gray-500">
          已用 {subplots.length}/{totalCells} 个单元格
        </div>
      </div>
      
      <div 
        className="grid gap-2 bg-gray-50 p-4 rounded-lg"
        style={{
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
          aspectRatio: `${cols}/${rows}`
        }}
      >
        {cells.map((axIndex) => {
          const subplot = getSubplotByAxIndex(axIndex);
          const isSelected = subplot?.subplotId === selectedSubplotId;
          
          return (
            <div
              key={axIndex}
              onClick={() => handleCellClick(axIndex)}
              className={`
                border-2 rounded-md p-3 cursor-pointer transition-all
                flex flex-col items-center justify-center
                min-h-[100px]
                ${subplot 
                  ? 'bg-white border-gray-300 hover:border-gray-400' 
                  : 'bg-gray-100 border-dashed border-gray-300 hover:border-gray-400'
                }
                ${isSelected ? 'ring-2 ring-black border-black' : ''}
              `}
            >
              {subplot ? (
                <>
                  <div className="text-xs font-semibold text-gray-700 mb-1">
                    {subplot.chartType.toUpperCase()}
                  </div>
                  <div className="text-xs text-gray-500">
                    子图 {axIndex + 1}
                  </div>
                  {subplot.data.columns.length > 0 && (
                    <div className="text-xs text-green-600 mt-1">
                      ✓ 已配置数据
                    </div>
                  )}
                </>
              ) : (
                <>
                  <div className="text-2xl text-gray-400 mb-1">+</div>
                  <div className="text-xs text-gray-500">
                    添加子图
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

#### 文件：`frontend/components/canvas/GridControls.tsx`（新建）

```typescript
'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';

export default function GridControls() {
  const { canvas, updateCanvas, reset } = useCanvasStore();
  
  const handleRowsChange = (value: number) => {
    if (value >= 1 && value <= 6) {
      updateCanvas({ rows: value });
    }
  };
  
  const handleColsChange = (value: number) => {
    if (value >= 1 && value <= 6) {
      updateCanvas({ cols: value });
    }
  };
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">画布设置</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs text-gray-600">行数</label>
          <input
            type="number"
            min={1}
            max={6}
            value={canvas.rows}
            onChange={(e) => handleRowsChange(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">列数</label>
          <input
            type="number"
            min={1}
            max={6}
            value={canvas.cols}
            onChange={(e) => handleColsChange(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">宽度 (英寸)</label>
          <input
            type="number"
            min={5}
            max={30}
            step={1}
            value={canvas.width}
            onChange={(e) => updateCanvas({ width: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <div className="space-y-1">
          <label className="text-xs text-gray-600">高度 (英寸)</label>
          <input
            type="number"
            min={3}
            max={20}
            step={1}
            value={canvas.height}
            onChange={(e) => updateCanvas({ height: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
      </div>
      
      <button
        onClick={reset}
        className="w-full px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
      >
        重置画布
      </button>
    </div>
  );
}
```

---

### 任务 5: 子图编辑器（3天）

#### 文件：`frontend/components/subplot/SubplotEditor.tsx`（新建）

```typescript
'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import ChartTypeSelector from './ChartTypeSelector';
import DataEditor from './DataEditor';
import ParamsEditor from './ParamsEditor';

export default function SubplotEditor() {
  const { selectedSubplotId, subplots, deleteSubplot } = useCanvasStore();
  
  const currentSubplot = subplots.find(s => s.subplotId === selectedSubplotId);
  
  if (!currentSubplot) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="text-center">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-sm">选择或添加一个子图开始编辑</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6 h-full overflow-y-auto">
      {/* 头部 */}
      <div className="flex items-center justify-between pb-3 border-b">
        <div>
          <h2 className="text-lg font-semibold">子图编辑器</h2>
          <p className="text-xs text-gray-500">
            位置: 第 {currentSubplot.axIndex + 1} 个单元格
          </p>
        </div>
        <button
          onClick={() => deleteSubplot(currentSubplot.subplotId)}
          className="px-3 py-1 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50"
        >
          删除
        </button>
      </div>
      
      {/* 图表类型选择 */}
      <ChartTypeSelector subplot={currentSubplot} />
      
      {/* 数据编辑 */}
      <DataEditor subplot={currentSubplot} />
      
      {/* 参数编辑 */}
      <ParamsEditor subplot={currentSubplot} />
    </div>
  );
}
```

#### 文件：`frontend/components/subplot/ChartTypeSelector.tsx`

```typescript
'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig, ChartType } from '@/types/canvas';

const CHART_TYPES: { value: ChartType; label: string; icon: string }[] = [
  { value: 'bar', label: '柱状图', icon: '📊' },
  { value: 'line', label: '折线图', icon: '📈' },
  { value: 'pie', label: '饼图', icon: '🥧' },
  { value: 'area', label: '面积图', icon: '📉' },
  { value: 'scatter', label: '散点图', icon: '⚫' },
];

interface Props {
  subplot: SubplotConfig;
}

export default function ChartTypeSelector({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const handleTypeChange = (chartType: ChartType) => {
    updateSubplot(subplot.subplotId, { chartType });
  };
  
  return (
    <div className="space-y-2">
      <label className="text-sm font-semibold">图表类型</label>
      <div className="grid grid-cols-3 gap-2">
        {CHART_TYPES.map((type) => (
          <button
            key={type.value}
            onClick={() => handleTypeChange(type.value)}
            className={`
              px-3 py-2 text-sm rounded-md border-2 transition-all
              ${subplot.chartType === type.value
                ? 'border-black bg-black text-white'
                : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <div className="text-lg mb-1">{type.icon}</div>
            <div className="text-xs">{type.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
```

#### 文件：`frontend/components/subplot/DataEditor.tsx`

```typescript
'use client';

import React, { useState } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';

interface Props {
  subplot: SubplotConfig;
}

export default function DataEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  const [jsonInput, setJsonInput] = useState(
    JSON.stringify(subplot.data, null, 2)
  );
  const [error, setError] = useState<string | null>(null);
  
  const handleApply = () => {
    try {
      const parsed = JSON.parse(jsonInput);
      
      // 验证格式
      if (!parsed.columns || !parsed.data) {
        throw new Error('数据必须包含 columns 和 data 字段');
      }
      
      updateSubplot(subplot.subplotId, { data: parsed });
      setError(null);
    } catch (e: any) {
      setError(e.message);
    }
  };
  
  const loadExample = () => {
    const example = {
      columns: ['品牌A', '品牌B', '品牌C'],
      index: ['Q1', 'Q2', 'Q3'],
      data: [
        [100, 200, 150],
        [120, 180, 160],
        [110, 220, 170]
      ]
    };
    setJsonInput(JSON.stringify(example, null, 2));
  };
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold">数据</label>
        <button
          onClick={loadExample}
          className="text-xs text-blue-600 hover:underline"
        >
          加载示例
        </button>
      </div>
      
      <textarea
        value={jsonInput}
        onChange={(e) => setJsonInput(e.target.value)}
        className="w-full h-48 px-3 py-2 text-xs font-mono border border-gray-300 rounded-md"
        placeholder='{"columns": [...], "data": [...]}'
      />
      
      {error && (
        <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}
      
      <button
        onClick={handleApply}
        className="w-full px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800"
      >
        应用数据
      </button>
    </div>
  );
}
```

#### 文件：`frontend/components/subplot/ParamsEditor.tsx`

```typescript
'use client';

import React from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import { SubplotConfig } from '@/types/canvas';

interface Props {
  subplot: SubplotConfig;
}

export default function ParamsEditor({ subplot }: Props) {
  const { updateSubplot } = useCanvasStore();
  
  const updateParam = (key: string, value: any) => {
    updateSubplot(subplot.subplotId, {
      params: { ...subplot.params, [key]: value }
    });
  };
  
  // 根据图表类型显示不同参数
  const renderParams = () => {
    switch (subplot.chartType) {
      case 'bar':
        return (
          <>
            <div className="flex items-center justify-between">
              <label className="text-xs">堆叠显示</label>
              <input
                type="checkbox"
                checked={subplot.params.stacked ?? true}
                onChange={(e) => updateParam('stacked', e.target.checked)}
                className="rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs">显示标签</label>
              <input
                type="checkbox"
                checked={subplot.params.show_label ?? true}
                onChange={(e) => updateParam('show_label', e.target.checked)}
                className="rounded"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs">标签格式</label>
              <select
                value={subplot.params.label_formatter ?? '{abs}'}
                onChange={(e) => updateParam('label_formatter', e.target.value)}
                className="w-full px-2 py-1 text-xs border rounded"
              >
                <option value="{abs}">绝对值</option>
                <option value="{share}">占比</option>
                <option value="{gr}">增长率</option>
              </select>
            </div>
          </>
        );
      
      case 'line':
        return (
          <>
            <div className="space-y-1">
              <label className="text-xs">标记样式</label>
              <select
                value={subplot.params.marker ?? 'o'}
                onChange={(e) => updateParam('marker', e.target.value)}
                className="w-full px-2 py-1 text-xs border rounded"
              >
                <option value="o">圆形</option>
                <option value="s">方形</option>
                <option value="^">三角形</option>
                <option value="">无</option>
              </select>
            </div>
          </>
        );
      
      case 'pie':
        return (
          <div className="flex items-center justify-between">
            <label className="text-xs">显示百分比</label>
            <input
              type="checkbox"
              checked={subplot.params.show_label ?? true}
              onChange={(e) => updateParam('show_label', e.target.checked)}
              className="rounded"
            />
          </div>
        );
      
      default:
        return <p className="text-xs text-gray-500">此图表类型暂无可配置参数</p>;
    }
  };
  
  return (
    <div className="space-y-3">
      <label className="text-sm font-semibold">参数设置</label>
      <div className="space-y-3">
        {renderParams()}
      </div>
    </div>
  );
}
```

---

### 任务 6: 主页面集成（2天）

#### 文件：`frontend/app/canvas/page.tsx`（新建）

```typescript
'use client';

import React, { useState } from 'react';
import { useCanvasStore } from '@/store/canvasStore';
import GridControls from '@/components/canvas/GridControls';
import GridPreview from '@/components/canvas/GridPreview';
import SubplotEditor from '@/components/subplot/SubplotEditor';
import { renderCanvasAPI } from '@/lib/api';

export default function CanvasPage() {
  const { canvas, subplots } = useCanvasStore();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleRender = async () => {
    if (subplots.length === 0) {
      setError('请至少添加一个子图');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const blob = await renderCanvasAPI({ canvas, subplots });
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
    } catch (err: any) {
      setError(err.message || '渲染失败');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧：网格控制 + 网格预览 */}
      <aside className="w-80 bg-white border-r p-4 overflow-y-auto space-y-6">
        <h1 className="text-xl font-bold">多子图画布</h1>
        <GridControls />
        <GridPreview />
      </aside>
      
      {/* 中间：最终渲染预览 */}
      <main className="flex-1 p-6 flex flex-col">
        <div className="mb-4">
          <button
            onClick={handleRender}
            disabled={isLoading || subplots.length === 0}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isLoading ? '渲染中...' : '渲染完整画布'}
          </button>
        </div>
        
        <div className="flex-1 bg-white border border-gray-200 rounded-lg p-6 flex items-center justify-center">
          {isLoading && (
            <div className="text-center">
              <div className="text-4xl mb-2">⏳</div>
              <p className="text-sm text-gray-500">渲染中...</p>
            </div>
          )}
          
          {error && (
            <div className="text-center text-red-600">
              <div className="text-4xl mb-2">⚠️</div>
              <p className="text-sm">{error}</p>
            </div>
          )}
          
          {previewUrl && !isLoading && (
            <img 
              src={previewUrl} 
              alt="Canvas Preview" 
              className="max-w-full max-h-full object-contain"
            />
          )}
          
          {!previewUrl && !isLoading && !error && (
            <div className="text-center text-gray-400">
              <div className="text-4xl mb-2">🖼️</div>
              <p className="text-sm">添加子图后点击"渲染完整画布"</p>
            </div>
          )}
        </div>
      </main>
      
      {/* 右侧：子图编辑器 */}
      <aside className="w-96 bg-white border-l p-4 overflow-y-auto">
        <SubplotEditor />
      </aside>
    </div>
  );
}
```

#### 文件：`frontend/lib/api.ts`（更新）

```typescript
const API_BASE = 'http://localhost:8000';

// 原有的单图渲染（保留）
export async function renderChart(data: any, params: any): Promise<Blob> {
  console.log('发送数据到 API:', { data, params });
  
  const response = await fetch(`${API_BASE}/api/render`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data, params }),
  });

  console.log('API 响应状态:', response.status);

  if (!response.ok) {
    let errorMsg = '渲染失败';
    try {
      const error = await response.json();
      errorMsg = error.detail || JSON.stringify(error);
    } catch (e) {
      errorMsg = `HTTP ${response.status}: ${response.statusText}`;
    }
    console.error('API 错误:', errorMsg);
    throw new Error(errorMsg);
  }

  return await response.blob();
}

// 新增：多子图画布渲染
export async function renderCanvasAPI(request: {
  canvas: any;
  subplots: any[];
}): Promise<Blob> {
  console.log('发送画布渲染请求:', request);
  
  const response = await fetch(`${API_BASE}/api/render/canvas`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  console.log('画布渲染响应状态:', response.status);
  
  if (!response.ok) {
    let errorMsg = '渲染失败';
    try {
      const error = await response.json();
      errorMsg = error.detail || JSON.stringify(error);
    } catch (e) {
      errorMsg = `HTTP ${response.status}: ${response.statusText}`;
    }
    console.error('画布渲染错误:', errorMsg);
    throw new Error(errorMsg);
  }
  
  return await response.blob();
}

// 获取图表类型列表
export async function getChartTypes(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/chart-types`);
  const data = await response.json();
  return data.chart_types;
}

// 获取默认参数
export async function getDefaultParams(chartType: string): Promise<Record<string, any>> {
  const response = await fetch(`${API_BASE}/api/chart-types/${chartType}/defaults`);
  return await response.json();
}
```

---

## 测试计划

### 后端测试（2天）

**单元测试**：
```python
# tests/test_grid_adapter.py

def test_1x1_grid():
    """测试 1x1 网格（向后兼容）"""
    pass

def test_2x2_grid():
    """测试 2x2 网格"""
    pass

def test_mixed_chart_types():
    """测试混合图表类型"""
    pass

def test_empty_subplots():
    """测试部分空白网格"""
    pass

def test_invalid_ax_index():
    """测试无效的 ax_index"""
    pass
```

**API 测试**：
```python
# tests/test_api_endpoints.py

def test_render_canvas_endpoint():
    """测试 /api/render/canvas 端点"""
    pass

def test_get_chart_types():
    """测试 /api/chart-types 端点"""
    pass

def test_backward_compatibility():
    """测试 MVP 端点仍然可用"""
    pass
```

### 前端测试（1天）

**组件测试**：
- GridPreview 组件渲染
- 子图添加/删除交互
- 状态同步验证

**集成测试**：
- 端到端流程：创建网格 → 添加子图 → 配置数据 → 渲染

---

## 时间估算

| 任务 | 时间 | 依赖 |
|------|------|------|
| 任务1: 扩展桥接层 | 2-3天 | 无 |
| 任务2: 更新 API 端点 | 1天 | 任务1 |
| 任务3: 状态管理 | 2天 | 无 |
| 任务4: 网格预览组件 | 3天 | 任务3 |
| 任务5: 子图编辑器 | 3天 | 任务3 |
| 任务6: 主页面集成 | 2天 | 任务4, 任务5 |
| 后端测试 | 2天 | 任务1, 任务2 |
| 前端测试 | 1天 | 任务6 |
| **总计** | **16-17天** | - |

**建议开发顺序**：
1. Week 1: 任务1 → 任务2 → 后端测试
2. Week 2: 任务3 → 任务4 → 任务5
3. Week 3: 任务6 → 前端测试 → 集成测试

---

## 成功标准

✅ **功能完整性**：
- [ ] 支持 1×1 到 6×6 的任意网格布局
- [ ] 支持至少 5 种图表类型（bar, line, pie, area, scatter）
- [ ] 每个子图可独立配置数据和参数
- [ ] 可视化网格编辑器正常工作

✅ **向后兼容**：
- [ ] MVP 的 `/api/render` 端点仍可用
- [ ] 现有 chart_class2 库未被修改
- [ ] `python example/bar.py` 仍正常运行

✅ **用户体验**：
- [ ] 网格操作流畅（添加/删除/选择子图）
- [ ] 参数修改实时反馈
- [ ] 渲染速度可接受（< 3秒）
- [ ] 错误提示清晰

✅ **代码质量**：
- [ ] 桥接层和 API 层有单元测试
- [ ] 前端组件可复用
- [ ] 代码注释完整

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 多子图渲染性能问题 | 中 | 高 | 限制最大网格 6×6，优化 DataFrame 转换 |
| 前端状态管理复杂度 | 中 | 中 | 使用 Zustand 简化，早期测试 |
| 图表类型参数差异大 | 低 | 中 | 先实现 5 种常用类型，逐步扩展 |
| 桥接层数据转换错误 | 低 | 高 | 严格的 Pydantic 验证 + 单元测试 |

---

## 后续扩展路径

### Phase 4: 高级布局（2-3周）
- 支持 rowspan/colspan（跨行跨列）
- 子图尺寸微调
- 自定义间距（wspace, hspace）

### Phase 5: 数据管理（2周）
- 数据集上传和存储
- 数据集复用（多个子图共享数据）
- 数据预处理（筛选、聚合）

### Phase 6: 项目持久化（2周）
- 数据库集成（PostgreSQL）
- 项目保存/加载
- 版本历史

### Phase 7: 完整参数支持（3周）
- 所有 17 种图表类型
- 完整参数集（样式、颜色、字体等）
- 参数预设模板

---

## 附录

### A. 示例请求

**2×2 网格示例**：
```json
{
  "canvas": {
    "width": 15,
    "height": 12,
    "rows": 2,
    "cols": 2
  },
  "subplots": [
    {
      "subplot_id": "subplot-1",
      "ax_index": 0,
      "chart_type": "bar",
      "data": {
        "columns": ["产品A", "产品B"],
        "index": ["Q1", "Q2"],
        "data": [[100, 200], [120, 180]]
      },
      "params": {"stacked": true, "show_label": true}
    },
    {
      "subplot_id": "subplot-2",
      "ax_index": 1,
      "chart_type": "line",
      "data": {
        "columns": ["销售额"],
        "index": ["1月", "2月", "3月"],
        "data": [[100], [120], [110]]
      },
      "params": {"marker": "o"}
    },
    {
      "subplot_id": "subplot-3",
      "ax_index": 2,
      "chart_type": "pie",
      "data": {
        "columns": ["份额"],
        "index": ["类别1", "类别2", "类别3"],
        "data": [[30], [50], [20]]
      },
      "params": {"show_label": true}
    },
    {
      "subplot_id": "subplot-4",
      "ax_index": 3,
      "chart_type": "area",
      "data": {
        "columns": ["趋势"],
        "index": ["W1", "W2", "W3", "W4"],
        "data": [[10], [15], [12], [18]]
      },
      "params": {"stacked": false}
    }
  ]
}
```

### B. 参考资源

- **Zustand 文档**: https://zustand-demo.pmnd.rs/
- **chart_class2 架构**: `docs/PROJECT_RESTRUCTURE_SUMMARY.md`
- **MVP 实施报告**: `docs/MVP_IMPLEMENTATION.md`
- **完整计划**: `docs/WEB_VISUALIZATION_TOOL_PLAN.md`

---

**文档版本**: v1.0  
**创建日期**: 2025-11-07  
**状态**: 待审核  
**预计完成**: 3周后
