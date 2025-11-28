# 颜色管理数据库迁移说明

## 概述

将颜色管理从 JSON 文件存储迁移到 SQLite 数据库，解决并发写问题和数据备份困难。

## 变更内容

### 1. 数据库模型 ✅

**文件**: `web_api/database.py`

新增 `ColorMapping` 模型：
- `user_id`: 用户ID（支持用户隔离）
- `name`: 颜色名称
- `color`: HEX 颜色值
- `named_color`: matplotlib 命名颜色
- `category`: 分类
- `description`: 描述
- `aliases`: 别名列表（JSON 字符串）
- `palette_order`: 调色板顺序
- 唯一约束：`(user_id, name)` 确保同一用户不能有重复颜色名称

### 2. 数据库颜色管理器 ✅

**文件**: `web_api/color_db_manager.py`

新增 `ColorDBManager` 类：
- 使用数据库会话进行所有操作
- 支持事务，解决并发写问题
- 自动确保默认调色板颜色
- 完全兼容原有的 `ColorManager` API

### 3. API 路由更新 ✅

**文件**: `web_api/routers/colors.py`

- 所有端点改为使用 `ColorDBManager`
- 添加数据库会话依赖
- 保持 API 接口不变（向后兼容）

### 4. 主应用更新 ✅

**文件**: `web_api/main.py`

- 更新 `_build_user_color_config` 使用数据库版本
- 移除全局 `ColorManager` 实例
- 所有渲染端点添加数据库依赖

### 5. 数据迁移脚本 ✅

**文件**: `scripts/migrate_colors_to_db.py`

- 自动扫描 `data/colors/<user_id>/color_dict.json`
- 迁移到数据库
- 跳过已存在的记录
- 保留调色板顺序

## 使用方法

### 1. 初始化数据库

数据库表会在服务启动时自动创建（通过 `init_db()`）。

### 2. 迁移现有数据（可选）

如果有现有的 JSON 颜色文件，运行迁移脚本：

```bash
python scripts/migrate_colors_to_db.py
```

脚本会：
- 扫描 `data/colors/` 目录
- 为每个用户迁移颜色数据
- 跳过已存在的记录
- 显示迁移进度

### 3. 验证迁移

启动服务后，通过 API 检查颜色数据：

```bash
# 登录获取 token
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 获取颜色列表
curl http://localhost:8001/api/colors \
  -H "Authorization: Bearer <token>"
```

## 优势

### 1. 解决并发写问题 ✅

- **之前**: JSON 文件无锁，多请求并发写会损坏文件
- **现在**: 数据库事务保证原子性，SQLite 自动处理并发

### 2. 数据备份简化 ✅

- **之前**: 需要备份多个 JSON 文件（每个用户一个）
- **现在**: 只需备份一个 SQLite 数据库文件

### 3. 查询性能提升 ✅

- **之前**: 每次操作需要读取整个 JSON 文件
- **现在**: 数据库索引加速查询

### 4. 数据一致性 ✅

- **之前**: 文件损坏风险，无版本控制
- **现在**: 数据库 ACID 特性保证一致性

## 向后兼容

- API 接口完全兼容，前端无需修改
- 迁移脚本支持从 JSON 迁移到数据库
- 旧的 JSON 文件可以保留作为备份

## 注意事项

1. **数据库初始化**: 服务启动时会自动创建表，无需手动操作

2. **迁移时机**: 
   - 新部署：直接使用数据库，无需迁移
   - 现有部署：运行迁移脚本后再启动服务

3. **数据备份**: 
   - 定期备份 `data/chart_class.db` 文件
   - 旧的 JSON 文件可以删除（迁移完成后）

4. **性能考虑**: 
   - SQLite 适合中小规模部署
   - 如需水平扩展，可考虑迁移到 PostgreSQL

## 故障排查

### 问题：迁移脚本报错 "用户不存在"

**解决**: 确保用户已创建，或先创建用户再运行迁移

### 问题：数据库表未创建

**解决**: 检查 `init_db()` 是否在启动时被调用，查看日志确认

### 问题：颜色数据丢失

**解决**: 
1. 检查是否有 JSON 备份文件
2. 运行迁移脚本重新导入
3. 检查数据库文件权限

## 相关文件

- `web_api/database.py` - 数据库模型
- `web_api/color_db_manager.py` - 数据库颜色管理器
- `web_api/routers/colors.py` - API 路由
- `scripts/migrate_colors_to_db.py` - 迁移脚本
- `chart/color/color_manager.py` - 原始 JSON 版本（保留用于兼容）

