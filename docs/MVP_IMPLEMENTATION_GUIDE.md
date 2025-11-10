# MVP 实施指南 - Chart Class Web 可视化工具

## 🎯 目标

在 **1-2 周内**快速实现一个最小可行产品，验证：
1. 桥接层架构的可行性
2. 前后端数据流通畅
3. 不影响现有 chart_class2 库

## 📋 功能清单

### ✅ 包含功能
- 单子图柱状图渲染（1x1 画布）
- 手动输入 JSON 数据
- 3 个基础参数控制（stacked, show_label, label_formatter）
- 实时预览

### ❌ 不包含功能
- ~~多子图/网格布局~~
- ~~其他图表类型~~
- ~~文件上传~~
- ~~数据库持久化~~
- ~~项目管理~~
- ~~复杂参数配置~~

---

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│ Frontend (Next.js)                                       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ JSON Input  │ │   Preview   │ │  Param Form │        │
│ │ (Textarea)  │ │   (Image)   │ │  (3 inputs) │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
│                        │                                 │
│                        ▼                                 │
│              fetch('/api/render', {data, params})       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP POST
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Backend (FastAPI)                                        │
│ ┌───────────────────────────────────────────────────┐  │
│ │ POST /api/render                                   │  │
│ │   ├─ 接收 JSON 请求                                │  │
│ │   ├─ 调用 WebChartAdapter.render_bar_chart()     │  │
│ │   └─ 返回 PNG 图片                                 │  │
│ └────────────────────┬──────────────────────────────┘  │
│                      │                                   │
│ ┌────────────────────▼──────────────────────────────┐  │
│ │ WebChartAdapter (桥接层)                          │  │
│ │   ├─ JSON → DataFrame                             │  │
│ │   ├─ plt.figure(FigureClass=GridFigure)          │  │
│ │   ├─ f.plot(kind='bar', data=df, **params)       │  │
│ │   └─ 返回 PNG bytes                               │  │
│ └────────────────────┬──────────────────────────────┘  │
│                      │                                   │
│                      ▼                                   │
│ ┌────────────────────────────────────────────────────┐ │
│ │ chart_class2 (现有库 - 不修改)                     │ │
│ │   GridFigure, PlotBar, COLOR_DICT...              │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 项目结构

```
chart_class2/                    # 项目根目录
├── chart/                       # ✅ 现有库（不动）
├── utils/                       # ✅ 现有库（不动）
├── example/                     # ✅ 现有示例（不动）
│
├── web_bridge/                  # 🆕 桥接层（MVP 最小化）
│   ├── __init__.py
│   └── adapters/
│       ├── __init__.py
│       └── chart_adapter.py    # 仅 130 行代码
│
├── web_api/                     # 🆕 后端 API（MVP 最小化）
│   ├── __init__.py
│   └── main.py                 # 单文件，约 80 行代码
│
└── frontend/                    # 🆕 前端（MVP 最小化）
    ├── app/
    │   ├── layout.tsx
    │   └── page.tsx            # 主页面（All-in-One）
    ├── components/
    │   ├── DataInput.tsx
    │   ├── ParamControls.tsx
    │   └── ChartPreview.tsx
    └── lib/
        └── api.ts
```

---

## 💻 代码实现

### 1️⃣ 后端实现

#### `web_bridge/adapters/chart_adapter.py`（桥接层核心）

```python
"""
MVP 版本的图表适配器
仅支持柱状图渲染
"""
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, Any

# 导入现有库（只读引用）
from chart import GridFigure


class WebChartAdapter:
    """Web 图表适配器 - MVP 版本"""
    
    def render_bar_chart(
        self, 
        data_json: Dict[str, Any], 
        params: Dict[str, Any]
    ) -> bytes:
        """
        渲染柱状图
        
        Args:
            data_json: {
                "columns": ["品牌A", "品牌B"],
                "index": ["2024-01", "2024-02"],
                "data": [[1000, 800], [1200, 900]]
            }
            params: {
                "stacked": True,
                "show_label": True,
                "label_formatter": "{abs}"  # MVP 固定值
            }
        
        Returns:
            PNG 图片的字节流
        """
        try:
            # 1. 转换为 DataFrame
            df = self._json_to_dataframe(data_json)
            
            # 2. 创建画布（固定 1x1）
            f = plt.figure(
                FigureClass=GridFigure, 
                width=10, 
                height=6
            )
            
            # 3. 调用原生 plot 方法
            f.plot(
                kind='bar',
                data=df,
                ax_index=0,
                stacked=params.get('stacked', True),
                show_label=params.get('show_label', True),
                label_formatter=params.get('label_formatter', '{abs}')
            )
            
            # 4. 保存为字节流
            buf = BytesIO()
            f.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close(f)
            
            return buf.getvalue()
            
        except Exception as e:
            # 简单错误处理
            plt.close('all')
            raise ValueError(f"图表渲染失败: {str(e)}")
    
    def _json_to_dataframe(self, data_json: Dict[str, Any]) -> pd.DataFrame:
        """JSON 转 DataFrame"""
        df = pd.DataFrame(
            data_json['data'],
            columns=data_json['columns']
        )
        
        if 'index' in data_json:
            df.index = data_json['index']
        
        return df


# 单例模式（可选优化）
_adapter_instance = None

def get_adapter() -> WebChartAdapter:
    """获取适配器实例"""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = WebChartAdapter()
    return _adapter_instance
```

#### `web_api/main.py`（FastAPI 应用）

```python
"""
MVP 版本的 FastAPI 应用
单文件，仅一个渲染端点
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Any, Dict, List
import logging

# 导入桥接层
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_bridge.adapters.chart_adapter import get_adapter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Chart Class Web API - MVP",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class ChartDataModel(BaseModel):
    """图表数据模型"""
    columns: List[str]
    index: List[str]
    data: List[List[Any]]

class ChartParamsModel(BaseModel):
    """图表参数模型"""
    stacked: bool = True
    show_label: bool = True
    label_formatter: str = "{abs}"

class RenderRequest(BaseModel):
    """渲染请求"""
    data: ChartDataModel
    params: ChartParamsModel

# ============ API 端点 ============

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "Chart Class Web API - MVP",
        "version": "0.1.0"
    }

@app.post("/api/render")
async def render_chart(request: RenderRequest):
    """
    渲染柱状图
    
    示例请求：
    ```json
    {
        "data": {
            "columns": ["品牌A", "品牌B"],
            "index": ["2024-01", "2024-02"],
            "data": [[1000, 800], [1200, 900]]
        },
        "params": {
            "stacked": true,
            "show_label": true,
            "label_formatter": "{abs}"
        }
    }
    ```
    """
    try:
        logger.info("收到渲染请求")
        
        # 调用适配器
        adapter = get_adapter()
        image_bytes = adapter.render_bar_chart(
            data_json=request.data.dict(),
            params=request.params.dict()
        )
        
        logger.info(f"渲染成功，图片大小: {len(image_bytes)} bytes")
        
        # 返回图片
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"渲染失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# 启动命令
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

---

### 2️⃣ 前端实现

#### `frontend/app/page.tsx`（主页面）

```typescript
'use client';

import { useState } from 'react';
import DataInput from '@/components/DataInput';
import ParamControls from '@/components/ParamControls';
import ChartPreview from '@/components/ChartPreview';
import { renderChart } from '@/lib/api';

export default function Home() {
  // 状态管理
  const [chartData, setChartData] = useState<any>(null);
  const [params, setParams] = useState({
    stacked: true,
    show_label: true,
    label_formatter: '{abs}'
  });
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 渲染图表
  const handleRender = async () => {
    if (!chartData) {
      setError('请先输入数据');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const blob = await renderChart(chartData, params);
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
      {/* 左侧：数据输入 */}
      <aside className="w-80 bg-white border-r p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">数据输入</h2>
        <DataInput onChange={setChartData} />
      </aside>

      {/* 中间：预览区 */}
      <main className="flex-1 p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Chart Class - MVP</h1>
          <button
            onClick={handleRender}
            disabled={isLoading || !chartData}
            className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 disabled:bg-gray-300"
          >
            {isLoading ? '渲染中...' : '渲染图表'}
          </button>
        </div>
        
        <ChartPreview 
          imageUrl={previewUrl} 
          isLoading={isLoading}
          error={error}
        />
      </main>

      {/* 右侧：参数控制 */}
      <aside className="w-80 bg-white border-l p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">参数设置</h2>
        <ParamControls params={params} onChange={setParams} />
      </aside>
    </div>
  );
}
```

#### `frontend/components/DataInput.tsx`

```typescript
'use client';

import { useState } from 'react';

const EXAMPLE_DATA = {
  columns: ["品牌A", "品牌B", "品牌C"],
  index: ["2024-01", "2024-02", "2024-03"],
  data: [
    [1000, 800, 600],
    [1200, 900, 700],
    [1100, 1000, 800]
  ]
};

interface Props {
  onChange: (data: any) => void;
}

export default function DataInput({ onChange }: Props) {
  const [jsonText, setJsonText] = useState(
    JSON.stringify(EXAMPLE_DATA, null, 2)
  );
  const [error, setError] = useState<string | null>(null);

  const handleChange = (text: string) => {
    setJsonText(text);
    setError(null);

    try {
      const parsed = JSON.parse(text);
      onChange(parsed);
    } catch (err) {
      setError('JSON 格式错误');
      onChange(null);
    }
  };

  const loadExample = () => {
    const text = JSON.stringify(EXAMPLE_DATA, null, 2);
    setJsonText(text);
    handleChange(text);
  };

  return (
    <div className="space-y-3">
      <button
        onClick={loadExample}
        className="w-full px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
      >
        加载示例数据
      </button>

      <textarea
        value={jsonText}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full h-96 p-3 border border-gray-300 rounded font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-black"
        placeholder='{"columns": [...], "data": [...]}'
      />

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      <div className="text-xs text-gray-500 space-y-1">
        <p>格式示例：</p>
        <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
{`{
  "columns": ["列1", "列2"],
  "index": ["行1", "行2"],
  "data": [[100, 200], [300, 400]]
}`}
        </pre>
      </div>
    </div>
  );
}
```

#### `frontend/components/ParamControls.tsx`

```typescript
'use client';

interface Params {
  stacked: boolean;
  show_label: boolean;
  label_formatter: string;
}

interface Props {
  params: Params;
  onChange: (params: Params) => void;
}

export default function ParamControls({ params, onChange }: Props) {
  const updateParam = (key: keyof Params, value: any) => {
    onChange({ ...params, [key]: value });
  };

  return (
    <div className="space-y-4">
      {/* 堆叠显示 */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">堆叠显示</label>
        <input
          type="checkbox"
          checked={params.stacked}
          onChange={(e) => updateParam('stacked', e.target.checked)}
          className="w-5 h-5"
        />
      </div>

      {/* 显示标签 */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">显示标签</label>
        <input
          type="checkbox"
          checked={params.show_label}
          onChange={(e) => updateParam('show_label', e.target.checked)}
          className="w-5 h-5"
        />
      </div>

      {/* 标签格式 */}
      <div className="space-y-2">
        <label className="text-sm font-medium">标签格式</label>
        <select
          value={params.label_formatter}
          onChange={(e) => updateParam('label_formatter', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black"
        >
          <option value="{abs}">绝对值</option>
          <option value="{share}">占比</option>
          <option value="{abs}\n{share}">双行显示</option>
        </select>
      </div>

      {/* 参数说明 */}
      <div className="mt-6 p-3 bg-gray-50 rounded text-xs text-gray-600 space-y-2">
        <p><strong>堆叠显示</strong>: 是否堆叠柱体</p>
        <p><strong>显示标签</strong>: 是否在柱体上显示数值</p>
        <p><strong>标签格式</strong>: 标签的显示格式</p>
      </div>
    </div>
  );
}
```

#### `frontend/components/ChartPreview.tsx`

```typescript
interface Props {
  imageUrl: string | null;
  isLoading: boolean;
  error: string | null;
}

export default function ChartPreview({ imageUrl, isLoading, error }: Props) {
  return (
    <div className="flex-1 bg-white border border-gray-200 rounded-lg p-6 flex items-center justify-center">
      {isLoading && (
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">正在渲染图表...</p>
        </div>
      )}

      {error && (
        <div className="text-center text-red-600">
          <p className="text-xl mb-2">⚠️</p>
          <p>{error}</p>
        </div>
      )}

      {imageUrl && !isLoading && !error && (
        <img 
          src={imageUrl} 
          alt="Chart Preview" 
          className="max-w-full h-auto shadow-lg"
        />
      )}

      {!imageUrl && !isLoading && !error && (
        <div className="text-center text-gray-400">
          <p className="text-xl mb-2">📊</p>
          <p>输入数据后点击"渲染图表"</p>
        </div>
      )}
    </div>
  );
}
```

#### `frontend/lib/api.ts`

```typescript
const API_BASE = 'http://localhost:8000';

export async function renderChart(data: any, params: any): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/render`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data, params }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '渲染失败');
  }

  return await response.blob();
}
```

---

## 🚀 启动步骤

### 1. 后端启动

```bash
# 1. 确保在项目根目录
cd d:\PyProjects\chart_class2

# 2. 创建目录结构
mkdir web_bridge\adapters
mkdir web_api

# 3. 创建文件（复制上面的代码）
# web_bridge/__init__.py (空文件)
# web_bridge/adapters/__init__.py (空文件)
# web_bridge/adapters/chart_adapter.py
# web_api/__init__.py (空文件)
# web_api/main.py

# 4. 安装 FastAPI 依赖（如果还没安装）
pip install fastapi uvicorn python-multipart

# 5. 启动后端
cd web_api
python main.py

# 或者使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端**：访问 http://localhost:8000 应该看到 `{"status": "ok", ...}`

### 2. 前端启动

```bash
# 1. 创建 Next.js 项目
cd d:\PyProjects\chart_class2
npx create-next-app@latest frontend

# 选项：
# ✔ TypeScript? Yes
# ✔ ESLint? Yes
# ✔ Tailwind CSS? Yes
# ✔ App Router? Yes

# 2. 进入前端目录
cd frontend

# 3. 创建组件文件（复制上面的代码）
# app/page.tsx
# components/DataInput.tsx
# components/ParamControls.tsx
# components/ChartPreview.tsx
# lib/api.ts

# 4. 启动前端
npm run dev
```

**访问应用**：http://localhost:3000

### 3. 测试流程

1. 点击"加载示例数据"按钮
2. 调整右侧参数（如取消"堆叠显示"）
3. 点击"渲染图表"按钮
4. 查看中间预览区的图表

---

## ✅ 验证清单

### 功能验证
- [ ] 示例数据能正常加载
- [ ] 修改 JSON 数据后能渲染新图表
- [ ] 切换"堆叠显示"开关，图表有变化
- [ ] 切换"显示标签"开关，图表有变化
- [ ] 更改"标签格式"，图表标签有变化
- [ ] 输入错误 JSON 有错误提示

### 架构验证
- [ ] 运行 `python example/bar.py`，确保现有库未受影响
- [ ] 检查 `chart/` 目录，确保无任何修改
- [ ] 后端日志显示正常（无异常）
- [ ] 前端控制台无错误

### 性能验证
- [ ] 渲染时间 < 3 秒
- [ ] 图片大小合理（< 500KB）
- [ ] 多次渲染无内存泄漏

---

## 🐛 常见问题

### 1. CORS 错误
```
Access to fetch at 'http://localhost:8000/api/render' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

**解决**：确保 `web_api/main.py` 中的 CORS 配置正确：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 确保这一行正确
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 模块导入错误
```
ModuleNotFoundError: No module named 'chart'
```

**解决**：确保在项目根目录启动后端：
```bash
cd d:\PyProjects\chart_class2
python web_api/main.py
```

### 3. 图表中文乱码
确保 `chart/figure.py` 中已配置中文字体（现有库应该已配置）。

### 4. 图片不显示
检查浏览器控制台，确认：
1. API 请求成功（200 状态码）
2. 返回的是 `image/png` 类型
3. Blob URL 正确生成

---

## 📈 下一步扩展

MVP 成功后，按以下顺序扩展：

### 阶段 1：更多图表类型（+1 周）
- [ ] 添加 line 图支持
- [ ] 添加 pie 图支持
- [ ] 前端添加图表类型选择器

### 阶段 2：更多参数（+1 周）
- [ ] 添加颜色配置
- [ ] 添加字体大小配置
- [ ] 添加标题配置

### 阶段 3：多子图（+2 周）
- [ ] 支持 2x2 网格布局
- [ ] 前端添加网格设计器

### 阶段 4：数据持久化（+1 周）
- [ ] 集成 SQLite 数据库
- [ ] 实现项目保存/加载

---

## 📝 总结

这个 MVP 实施方案：
- ✅ 代码量少（后端 ~200 行，前端 ~300 行）
- ✅ 功能聚焦（仅柱状图 + 3 个参数）
- ✅ 架构清晰（验证桥接层模式）
- ✅ 易于扩展（为完整功能打基础）

预计 **1-2 周**即可完成，快速验证想法！🚀
