# Web API 统一架构

## 📋 概述

Chart Class Web API 已经整合为**统一服务**，提供两大功能：
1. **图表渲染 API** - 单图/多子图画布渲染
2. **颜色管理 API** - 颜色字典的增删改查

---

## 🚀 启动服务

### 方式 1：直接运行
```bash
python -m web_api.main
```

### 方式 2：通过管理脚本
```bash
.\color_manager.bat
# 选择选项 [2] 启动统一 Web API 服务
```

### 启动信息
```
🚀 启动 Chart Class Web API 服务...
📊 图表渲染 API: http://localhost:8000/api/render/*
🎨 颜色管理 API: http://localhost:8000/api/colors/*
📚 API 文档: http://localhost:8000/docs
```

---

## 📊 API 端点概览

### 根端点
- `GET /` - 健康检查，返回服务信息

### 图表渲染 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/render/canvas` | POST | 渲染多子图画布 |
| `/api/render/subplot` | POST | 渲染单个子图（独立预览）|
| `/api/render` | POST | 单图渲染（向后兼容 MVP）|
| `/api/chart-types` | GET | 获取支持的图表类型列表 |
| `/api/chart-types/{type}/defaults` | GET | 获取指定图表类型的默认参数 |

### 颜色管理 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/colors` | GET | 获取所有颜色（支持分类/搜索）|
| `/api/colors/{name}` | GET | 获取指定颜色 |
| `/api/colors` | POST | 添加新颜色 |
| `/api/colors/{name}` | PUT | 更新颜色 |
| `/api/colors/{name}` | DELETE | 删除颜色 |
| `/api/colors/meta/categories` | GET | 获取所有分类 |
| `/api/colors/meta/stats` | GET | 获取统计信息 |
| `/api/colors/export/typescript` | POST | 导出 TypeScript 文件 |

---

## 🔧 配置

### CORS 设置
允许以下来源访问：
- `http://localhost:3000` (Next.js)
- `http://localhost:5173` (Vite)

### 端口
- 默认端口：`8000`
- 可通过 `uvicorn.run(app, port=xxx)` 修改

---

## 📖 API 文档

启动服务后，访问以下地址查看交互式文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 优势

### 1. **统一管理**
- 单一入口，一次启动
- 统一的日志和错误处理
- 共享的 CORS 和中间件配置

### 2. **简化部署**
- 只需部署一个服务
- 减少端口占用
- 统一的版本管理

### 3. **便于开发**
- 集中的 API 文档
- 统一的健康检查
- 更清晰的模块结构

---

## 📝 示例调用

### 图表渲染示例
```bash
# 渲染多子图画布
curl -X POST http://localhost:8000/api/render/canvas \
  -H "Content-Type: application/json" \
  -d '{
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
      }
    ]
  }'
```

### 颜色管理示例
```bash
# 获取所有颜色
curl http://localhost:8000/api/colors

# 按分类过滤
curl "http://localhost:8000/api/colors?category=品牌"

# 搜索颜色
curl "http://localhost:8000/api/colors?search=红色"

# 添加新颜色
curl -X POST http://localhost:8000/api/colors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "自定义红",
    "color": "#FF0000",
    "category": "自定义",
    "description": "我的红色"
  }'

# 删除颜色
curl -X DELETE http://localhost:8000/api/colors/自定义红
```

---

## 🔄 迁移说明

### 从旧版本迁移

**旧方式**（已废弃）：
```bash
# 需要分别启动两个服务
python -m web_api.main          # 图表渲染
python -m web_api.color_api     # 颜色管理
```

**新方式**（推荐）：
```bash
# 统一启动
python -m web_api.main
```

### 代码更新
前端调用无需修改，所有端点路径保持不变：
- ✅ `/api/render/*` - 继续工作
- ✅ `/api/colors/*` - 继续工作

---

## 📦 文件结构

```
web_api/
├── __init__.py
├── main.py              # 统一 API 服务（合并后）
├── color_api.py         # 已废弃，功能已合并到 main.py
└── models.py            # Pydantic 数据模型
```

---

## 🛠️ 开发建议

### 添加新 API 端点
在 `web_api/main.py` 中添加：

```python
@app.get("/api/your-endpoint")
async def your_handler():
    """端点说明"""
    return {"data": "..."}
```

### 添加新数据模型
在 `web_api/models.py` 或 `main.py` 顶部定义：

```python
class YourModel(BaseModel):
    field1: str
    field2: int
```

### 日志记录
使用全局 logger：

```python
logger.info("操作成功")
logger.error(f"操作失败: {error}")
```

---

## 🐛 故障排查

### 问题：端口 8000 已被占用
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或修改端口
uvicorn.run(app, port=8001)
```

### 问题：CORS 错误
检查 `allow_origins` 是否包含你的前端地址：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 添加你的地址
    ...
)
```

### 问题：颜色管理 API 返回 404
确保路由顺序正确（具体路径在动态参数前）：
```python
# ✅ 正确顺序
@app.get("/api/colors/meta/categories")  # 具体路径在前
@app.get("/api/colors/{name}")            # 动态参数在后
```

---

## 📅 版本历史

- **v0.3.0** - 统一 API 架构（图表渲染 + 颜色管理）
- **v0.2.0** - 添加多子图画布渲染
- **v0.1.0** - 单图渲染 MVP

---

## 🎯 下一步

- [ ] 添加认证中间件
- [ ] 实现 API 速率限制
- [ ] 添加请求日志记录
- [ ] 实现数据缓存
- [ ] 添加更多图表类型支持
