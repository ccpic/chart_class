# 调色板与颜色映射分离实现计划

## 需求概述

将颜色管理中的**调色板**和**颜色映射**完全分离：
- **颜色映射**：定义颜色名称到颜色值的映射（字典）
- **调色板**：定义颜色的使用顺序（列表）

### 目标

1. **后端**：使用不同的数据表管理
2. **前端**：显示为 Sheet 的两个 Tabs
3. **API**：分离的端点，清晰的职责划分

## 当前架构分析

### 现状

- **数据模型**：`ColorMapping` 表包含 `palette_order` 字段，混合了两种概念
- **API 路由**：`/api/colors/palette` 和 `/api/colors` 在同一路由文件中
- **前端组件**：`ColorManagerSheet.tsx` 在一个界面中混合显示两种功能

### 问题

1. **概念混淆**：调色板顺序存储在颜色映射表中，逻辑耦合
2. **扩展性差**：无法支持多个调色板（如"主题1"、"主题2"）
3. **查询复杂**：需要 JOIN 或复杂查询才能获取调色板信息

## 设计方案

### 1. 数据库设计

#### 1.1 新增调色板表

```python
class ColorPalette(Base):
    """调色板模型"""
    __tablename__ = "color_palettes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    name = Column(String(100), nullable=False)  # 调色板名称（如"默认"、"主题1"）
    is_default = Column(Boolean, default=False, nullable=False)  # 是否默认调色板
    color_names = Column(String(2000), nullable=False)  # 颜色名称列表（JSON字符串）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 唯一约束：同一用户不能有重复的调色板名称
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_palette_name"),
    )
```

#### 1.2 修改颜色映射表

从 `ColorMapping` 表中移除 `palette_order` 字段：

```python
class ColorMapping(Base):
    """颜色映射模型（移除 palette_order）"""
    __tablename__ = "color_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), nullable=False)
    named_color = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    description = Column(String(255), nullable=True)
    aliases = Column(String(500), nullable=True)
    # 移除：palette_order
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### 2. 后端实现

#### 2.1 创建调色板管理器

**文件**: `web_api/palette_db_manager.py`

```python
class PaletteDBManager:
    """调色板管理器（独立于颜色映射）"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self._ensure_default_palette()
    
    def get_default_palette(self) -> List[str]:
        """获取默认调色板"""
    
    def set_default_palette(self, color_names: List[str]) -> bool:
        """设置默认调色板"""
    
    def create_palette(self, name: str, color_names: List[str]) -> bool:
        """创建新调色板"""
    
    def list_palettes(self) -> List[Dict]:
        """列出所有调色板"""
    
    def delete_palette(self, name: str) -> bool:
        """删除调色板"""
```

#### 2.2 创建调色板路由

**文件**: `web_api/routers/palettes.py`（新建）

```python
router = APIRouter()

@router.get("/palettes", response_model=List[PaletteResponse])
async def list_palettes(...):
    """获取所有调色板"""

@router.get("/palettes/default", response_model=List[str])
async def get_default_palette(...):
    """获取默认调色板"""

@router.put("/palettes/default", response_model=MessageResponse)
async def update_default_palette(...):
    """更新默认调色板"""

@router.post("/palettes", response_model=PaletteResponse)
async def create_palette(...):
    """创建新调色板"""

@router.delete("/palettes/{name}", response_model=MessageResponse)
async def delete_palette(...):
    """删除调色板"""
```

#### 2.3 更新颜色映射路由

**文件**: `web_api/routers/colors.py`

- 移除调色板相关端点（`/colors/palette`）
- 专注于颜色映射的 CRUD 操作

#### 2.4 更新颜色管理器

**文件**: `web_api/color_db_manager.py`

- 移除 `palette_order` 相关逻辑
- 移除 `get_palette()` 和 `set_palette()` 方法
- 简化 `list_all()` 方法（不再按调色板顺序排序）

#### 2.5 更新主应用

**文件**: `web_api/main.py`

- 更新 `_build_user_color_config()` 使用新的调色板管理器
- 注册新的调色板路由

### 3. 前端实现

#### 3.1 更新 API 客户端

**文件**: `frontend/lib/api/colorAPI.ts`

```typescript
// 分离调色板 API
class PaletteAPIClient {
  async getDefaultPalette(): Promise<string[]>
  async updateDefaultPalette(palette: string[]): Promise<MessageResponse>
  async listPalettes(): Promise<Palette[]>
  async createPalette(name: string, colorNames: string[]): Promise<Palette>
  async deletePalette(name: string): Promise<MessageResponse>
}

// 颜色映射 API（移除调色板相关方法）
class ColorAPIClient {
  // 移除 getPalette() 和 updatePalette()
  // 保留其他颜色映射方法
}
```

#### 3.2 更新颜色管理组件

**文件**: `frontend/components/color/ColorManagerSheet.tsx`

使用 Tabs 组件分离两个功能：

```tsx
<Tabs defaultValue="mappings" className="w-full">
  <TabsList>
    <TabsTrigger value="mappings">颜色映射</TabsTrigger>
    <TabsTrigger value="palette">调色板</TabsTrigger>
  </TabsList>
  
  <TabsContent value="mappings">
    {/* 颜色映射管理 UI */}
  </TabsContent>
  
  <TabsContent value="palette">
    {/* 调色板管理 UI */}
  </TabsContent>
</Tabs>
```

### 4. 数据迁移

#### 4.1 迁移脚本

**文件**: `scripts/migrate_palette_to_separate_table.py`

1. 从 `color_mappings` 表中提取所有 `palette_order` 数据
2. 按 `user_id` 分组，构建调色板列表
3. 创建 `color_palettes` 表记录
4. 从 `color_mappings` 表中删除 `palette_order` 列（SQLite 需要重建表）

#### 4.2 迁移步骤

```python
# 1. 创建新表
# 2. 迁移数据：从 color_mappings.palette_order 到 color_palettes.color_names
# 3. 验证数据完整性
# 4. 删除旧字段（SQLite 需要重建表）
```

## 实施步骤

### 阶段 1：数据库层（后端）

1. ✅ 创建 `ColorPalette` 模型
2. ✅ 创建 `PaletteDBManager` 类
3. ✅ 创建调色板路由 `routers/palettes.py`
4. ✅ 更新 `ColorDBManager`，移除调色板逻辑
5. ✅ 更新 `ColorMapping` 模型，移除 `palette_order`
6. ✅ 更新主应用，注册新路由

### 阶段 2：API 层

1. ✅ 测试调色板 API
2. ✅ 测试颜色映射 API
3. ✅ 更新 API 文档

### 阶段 3：数据迁移

1. ✅ 创建迁移脚本
2. ✅ 备份数据库
3. ✅ 运行迁移
4. ✅ 验证数据完整性

### 阶段 4：前端层

1. ✅ 更新 API 客户端
2. ✅ 更新 `ColorManagerSheet` 组件，添加 Tabs
3. ✅ 创建调色板管理子组件
4. ✅ 测试 UI 交互

### 阶段 5：集成测试

1. ✅ 端到端测试
2. ✅ 性能测试
3. ✅ 向后兼容性验证

## API 端点设计

### 颜色映射端点

```
GET    /api/colors              # 获取所有颜色映射
GET    /api/colors/{name}       # 获取指定颜色映射
POST   /api/colors              # 创建颜色映射
PUT    /api/colors/{name}       # 更新颜色映射
DELETE /api/colors/{name}        # 删除颜色映射
GET    /api/colors/meta/stats   # 获取统计信息
```

### 调色板端点

```
GET    /api/palettes                    # 获取所有调色板
GET    /api/palettes/default            # 获取默认调色板
PUT    /api/palettes/default            # 更新默认调色板
POST   /api/palettes                    # 创建新调色板
GET    /api/palettes/{name}             # 获取指定调色板
PUT    /api/palettes/{name}             # 更新指定调色板
DELETE /api/palettes/{name}             # 删除指定调色板
```

## 数据模型关系

```
User (1) ──< (N) ColorMapping
User (1) ──< (N) ColorPalette

ColorMapping: 颜色名称 -> 颜色值的映射
ColorPalette: 调色板名称 -> 颜色名称列表的映射
```

## 优势

1. **概念清晰**：调色板和颜色映射职责分离
2. **扩展性强**：支持多个调色板（未来可扩展）
3. **查询简单**：不需要 JOIN，直接查询调色板表
4. **维护方便**：修改调色板不影响颜色映射

## 注意事项

1. **向后兼容**：迁移时需要确保现有数据不丢失
2. **默认调色板**：每个用户必须有一个默认调色板
3. **数据验证**：调色板中的颜色名称必须在颜色映射中存在
4. **SQLite 限制**：删除列需要重建表，迁移脚本需要处理

## 风险评估

| 风险 | 影响 | 缓解措施 |
| --- | --- | --- |
| 数据迁移失败 | 高 | 完整备份 + 回滚脚本 |
| API 变更破坏前端 | 中 | 分阶段部署，保持旧 API 一段时间 |
| 性能影响 | 低 | 调色板表数据量小，查询简单 |

## 后续扩展

1. **多调色板支持**：用户可以创建多个调色板（"主题1"、"主题2"等）
2. **调色板模板**：提供预设调色板模板
3. **调色板导入/导出**：支持 JSON 格式导入导出

