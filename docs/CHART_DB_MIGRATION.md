# 图表数据库迁移文档

## 概述

将图表存储从内存迁移到数据库，实现数据持久化和用户隔离。

## 变更内容

### 1. 数据库模型

在 `web_api/database.py` 中新增 `SavedChart` 模型：

- **表名**: `saved_charts`
- **字段**:
  - `id`: String(36) - UUID 字符串，主键
  - `user_id`: Integer - 用户ID，支持用户隔离
  - `name`: String(200) - 图表名称
  - `tags`: String(1000) - 标签列表（JSON 字符串）
  - `canvas`: Text - 画布配置（JSON 字符串）
  - `subplots`: Text - 子图列表（JSON 字符串）
  - `version`: String(20) - 数据格式版本
  - `created_at`: DateTime - 创建时间
  - `updated_at`: DateTime - 更新时间

- **唯一约束**: `(user_id, id)` - 确保同一用户不能有重复的图表ID

### 2. 图表管理器

新增 `web_api/chart_db_manager.py`，实现：

- `ChartDBManager` 类：数据库版本的图表管理器
- 支持 CRUD 操作（创建、读取、更新、删除）
- 支持用户隔离（所有操作都基于 `user_id`）
- 支持标签筛选（AND 逻辑）
- 自动 JSON 序列化/反序列化

### 3. API 路由更新

更新 `web_api/routers/charts.py`：

- 移除内存存储 `_charts_storage`
- 所有 API 端点添加 `db: Session = Depends(get_db)` 依赖
- 使用 `ChartDBManager` 替代内存字典操作

## 数据迁移

### 自动迁移

数据库表会在应用启动时自动创建（通过 `init_db()` 调用）。

### 手动迁移（如果需要）

如果需要从内存数据迁移到数据库，可以创建迁移脚本：

```python
# scripts/migrate_charts_to_db.py
from web_api.database import get_db_sync, SavedChart
from web_api.chart_db_manager import ChartDBManager
import json

# 注意：这需要手动从内存中提取数据
# 由于内存存储已移除，此脚本仅作为参考

def migrate_charts():
    db = get_db_sync()
    # ... 迁移逻辑
```

## 优势

1. **数据持久化**: 图表数据存储在数据库中，容器重启不会丢失
2. **用户隔离**: 每个用户只能访问自己的图表
3. **可扩展性**: 支持水平扩展（多实例共享数据库）
4. **数据完整性**: 数据库事务保证数据一致性
5. **查询能力**: 支持标签筛选、排序等查询操作

## 兼容性

- API 接口保持不变，前端无需修改
- 数据格式保持不变（JSON 序列化）
- 向后兼容：新版本自动创建数据库表

## 注意事项

1. **数据库文件位置**: `data/chart_class.db`（与颜色管理使用同一数据库）
2. **JSON 存储**: 大型图表数据可能影响性能，建议定期清理旧数据
3. **备份**: 定期备份数据库文件
4. **索引**: `user_id` 和 `id` 已建立索引，查询性能良好

## 测试

测试以下功能：

1. ✅ 创建图表
2. ✅ 获取图表列表
3. ✅ 获取图表详情
4. ✅ 更新图表
5. ✅ 删除图表
6. ✅ 标签筛选
7. ✅ 用户隔离（不同用户看不到彼此的图表）

