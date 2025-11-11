# 快速启动指南

## 🚀 一键启动 Web API

### Windows 用户

**方法 1：使用批处理脚本**
```bash
.\color_manager.bat
# 选择 [2] 启动统一 Web API 服务
```

**方法 2：直接命令**
```bash
python -m web_api.main
```

### 验证启动成功
访问 http://localhost:8000/

预期响应：
```json
{
  "status": "ok",
  "message": "Chart Class Web API",
  "version": "0.3.0",
  "services": {
    "chart_rendering": "/api/render/*",
    "color_management": "/api/colors/*"
  },
  "docs": "/docs"
}
```

---

## 📚 查看 API 文档

启动服务后，访问：
- **交互式文档（推荐）**: http://localhost:8000/docs
- **备用文档**: http://localhost:8000/redoc

---

## 🎯 常用端点

### 图表渲染
```bash
# 渲染多子图画布
POST http://localhost:8000/api/render/canvas

# 渲染单个子图
POST http://localhost:8000/api/render/subplot

# 获取支持的图表类型
GET http://localhost:8000/api/chart-types
```

### 颜色管理
```bash
# 获取所有颜色
GET http://localhost:8000/api/colors

# 搜索颜色
GET http://localhost:8000/api/colors?search=红色

# 添加颜色
POST http://localhost:8000/api/colors

# 获取统计信息
GET http://localhost:8000/api/colors/meta/stats
```

---

## 🔧 配置前端

确保前端配置指向正确的 API 地址：

**frontend/lib/api/colorAPI.ts**:
```typescript
const API_BASE_URL = "http://localhost:8000";
```

**frontend/next.config.js** (如需代理):
```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}
```

---

## ✅ 功能检查清单

启动服务后，测试以下功能：

- [ ] API 健康检查：`GET /`
- [ ] 图表类型列表：`GET /api/chart-types`
- [ ] 颜色列表：`GET /api/colors`
- [ ] 颜色分类：`GET /api/colors/meta/categories`
- [ ] API 文档访问：http://localhost:8000/docs

---

## 🛑 停止服务

按 `Ctrl + C` 停止服务

---

## 📖 详细文档

更多信息请参考：
- [Web API 统一架构文档](./WEB_API_UNIFIED_ARCHITECTURE.md)
- [颜色管理指南](./COLOR_MANAGER_GUIDE.md)
- [文件重组说明](./FILE_REORGANIZATION_SUMMARY.md)
