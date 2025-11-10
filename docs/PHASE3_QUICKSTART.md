# Phase 3 画布功能快速启动指南

## 🚀 快速开始

### 1. 运行本地测试（最简单）
**无需启动任何服务，直接测试画布功能**

```bash
cd d:\PyProjects\chart_class2
python test_local_canvas.py
```

**测试内容**：
- ✅ 2x2 网格 + 完整画布功能（标题、图例、间距、label_outer）
- ✅ 1x3 横向布局
- ✅ 1x1 单子图 + 画布功能

**测试结果**：
- 图片保存在 `test_outputs/` 目录
- 控制台显示详细的功能验证信息

---

### 2. 测试适配器（不需要 API）

```bash
python test_grid_adapter.py
```

**测试内容**：
- 2x2 网格
- 1x1 单子图
- 2x3 部分填充网格

---

### 3. 测试完整 API（需要启动后端）

#### Step 1: 启动后端
**方法 A - 使用脚本**：
```bash
.\start_backend.bat
```

**方法 B - 直接命令**：
```bash
python -m uvicorn web_api.main:app --host 0.0.0.0 --port 8000
```

#### Step 2: 运行 API 测试
在另一个终端：
```bash
python test_grid_api.py
```

或者快速测试：
```bash
python quick_test.py
```

---

## 📊 查看测试结果

所有测试图片保存在 `test_outputs/` 目录：

```
test_outputs/
├── final_test_2x2_full.png    # 2x2 网格 + 完整画布功能 ⭐推荐查看
├── final_test_1x3.png          # 1x3 横向布局
├── final_test_1x1_full.png     # 1x1 单子图 + 画布功能
├── test_grid_2x2_canvas.png    # 适配器测试 - 2x2
├── test_grid_1x1_canvas.png    # 适配器测试 - 1x1
└── test_grid_partial.png       # 部分网格测试
```

**推荐先查看**：`final_test_2x2_full.png`
- 包含所有画布级别功能展示
- 4 种不同图表类型
- 画布标题、Y轴标题、图例、label_outer 全部启用

---

## 🎨 画布功能演示

### 功能 1: 画布总标题
```python
canvas_config = {
    'title': '2024年度数据分析看板',
    'title_fontsize': 20
}
```
效果：在整个画布顶部显示统一标题

### 功能 2: Y轴总标题
```python
canvas_config = {
    'ytitle': '销售额（万元）',
    'ytitle_fontsize': 16
}
```
效果：在画布左侧显示统一的 Y 轴标签

### 功能 3: 画布总图例
```python
canvas_config = {
    'show_legend': True,
    'legend_loc': 'center left',
    'legend_ncol': 1,
    'bbox_to_anchor': (1, 0.5)
}
```
效果：自动汇总所有子图的图例，放置在画布右侧

### 功能 4: Label Outer
```python
canvas_config = {
    'label_outer': True
}
```
效果：仅在网格外围显示刻度标签，减少视觉混乱

### 功能 5: 子图间距
```python
canvas_config = {
    'wspace': 0.15,  # 水平间距
    'hspace': 0.2    # 垂直间距
}
```
效果：精确控制子图之间的间距

---

## 📡 API 端点说明

### 1. 画布渲染 (核心端点)
```
POST http://localhost:8000/api/render/canvas
```

**请求体示例**：见 `docs/PHASE3_CANVAS_MVP_IMPLEMENTATION.md`

### 2. 获取图表类型
```
GET http://localhost:8000/api/chart-types
```

**响应**：
```json
{
  "chart_types": ["bar", "line", "pie", "area", "scatter"]
}
```

### 3. 获取默认参数
```
GET http://localhost:8000/api/chart-types/bar/defaults
```

**响应**：
```json
{
  "stacked": true,
  "show_label": true,
  "label_formatter": "{abs}"
}
```

### 4. 单图渲染（MVP 兼容）
```
POST http://localhost:8000/api/render
```

---

## 🔧 常见问题

### Q: 测试图片在哪里？
A: `test_outputs/` 目录，运行测试后自动生成。

### Q: 后端启动失败？
A: 确保端口 8000 未被占用，检查是否已安装依赖：
```bash
pip install -r requirements.txt
```

### Q: API 测试连接失败？
A: 先确保后端已启动并监听 8000 端口：
```bash
python -m uvicorn web_api.main:app --host 0.0.0.0 --port 8000
```

### Q: 如何验证原库未受影响？
A: 运行原有示例：
```bash
python example/bar.py
```
应该正常生成 `example/plots/柱状图.png`

---

## 📚 进一步阅读

- **完整实施报告**：`docs/PHASE3_CANVAS_MVP_IMPLEMENTATION.md`
- **开发计划**：`docs/PHASE3_GRID_LAYOUT_PLAN.md`
- **项目架构**：`.github/copilot-instructions.md`

---

## ✅ 验证清单

运行以下命令，确保一切正常：

```bash
# 1. 本地测试
python test_local_canvas.py

# 2. 适配器测试
python test_grid_adapter.py

# 3. 验证原库
python example/bar.py

# 4. 查看测试图片
explorer test_outputs
```

**预期结果**：
- ✅ 3 个测试脚本全部通过
- ✅ 生成至少 6 张测试图片
- ✅ 原有示例仍正常工作

---

**状态**: ✅ 所有功能已实现并测试通过  
**推荐操作**: 先运行 `python test_local_canvas.py`，查看 `test_outputs/final_test_2x2_full.png`
