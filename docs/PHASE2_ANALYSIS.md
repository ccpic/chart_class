# Phase 2: 代码重复分析与优化方案

## 📊 重复模式识别

经过详细分析17个图表类的代码，发现以下**主要重复模式**：

### 1️⃣ **样式参数处理模式** (HIGH PRIORITY)
**重复次数**: 15个类中都有
**代码模式**:
```python
d_style = {
    "param1": default_value1,
    "param2": default_value2,
    ...
}
d_style = {k: kwargs[k] if k in kwargs else v for k, v in d_style.items()}
```
**出现位置**:
- PlotBar, PlotBarh, PlotLine, PlotArea, PlotBubble, PlotStripdot
- PlotHist, PlotBoxdot, PlotHeatmap, PlotTreemap, PlotPie
- PlotWaffle, PlotFunnel, PlotVenn2, PlotVenn3

**优化方案**: 提取为基类方法 `_merge_style_kwargs(default_style, **kwargs)`

---

### 2️⃣ **颜色获取逻辑** (HIGH PRIORITY)
**重复次数**: 10个类
**代码模式**:
```python
# Pattern 1: 从color_dict或迭代器获取颜色
if col in self._color_dict.keys():
    color = self._colors.get_color(col)
else:
    color = next(self._colors.iter_colors)

# Pattern 2: 批量颜色映射
cmap, colors = self._colors.get_colors(
    labels=df.index, hue=self.hue, random_color=d_style["random_color"]
)
```
**出现位置**:
- PlotBar (2种模式混合)
- PlotBarh (模式1)
- PlotBubble (模式2 + colorbar逻辑)
- PlotStripdot (模式2 + colorbar逻辑)
- PlotLine, PlotArea (简化版模式1)
- PlotPie, PlotTreemap, PlotWaffle (变体)

**优化方案**: 
- 基类添加 `_get_color_for_item(item, stacked=True)` 
- 基类添加 `_setup_colorbar(scatter, hue_name, show_hist=False)`

---

### 3️⃣ **坐标轴格式化** (MEDIUM PRIORITY)
**重复次数**: 8个类
**代码模式**:
```python
# X轴格式化
self.ax.xaxis.set_major_formatter(
    FuncFormatter(lambda x, _: self.fmt.format(x))
)

# Y轴格式化
self.ax.yaxis.set_major_formatter(
    FuncFormatter(lambda y, _: self.fmt.format(y))
)
```
**出现位置**:
- PlotBar, PlotBarh (都有x/y轴格式化)
- PlotLine, PlotArea (y轴)
- PlotBubble (x/y轴，使用自定义fmt)

**优化方案**: 基类添加 `_format_axis(axis='both', formatter=None)`

---

### 4️⃣ **标签文本创建** (MEDIUM PRIORITY)
**重复次数**: 10个类
**代码模式**:
```python
# Pattern 1: 字典格式化标签
d_label = {
    "abs": fmt_abs.format(value),
    "share": fmt_share.format(share),
    "index": index,
    "col": col,
}
label_text = label_formatter.format(**d_label)

# Pattern 2: 直接格式化
self.ax.text(x, y, self.fmt.format(value), ...)
```
**出现位置**:
- PlotBar, PlotBarh (模式1，复杂的d_label)
- PlotBubble, PlotStripdot (模式1)
- PlotLine, PlotArea (模式2，带bbox)
- PlotPie (模式1的变体)

**优化方案**: 基类添加 `_create_label_dict(**fields)` 和 `_add_text_label(x, y, text, **style)`

---

### 5️⃣ **图例处理逻辑** (MEDIUM PRIORITY)
**重复次数**: 3个类（但逻辑复杂）
**代码模式**:
```python
if self.style._show_legend is True and self.hue is not None:
    if pd.api.types.is_numeric_dtype(self.hue) is False:
        handles = [
            Line2D([0], [0], marker="o", markerfacecolor=cmap(i), ...)
            for i, c in enumerate(pd.factorize(self.hue)[1])
        ]
        handles = sorted(handles, key=lambda h: h.get_label())
        ax.legend(handles=handles, title=self.hue.name, ...)
        self.style._show_legend = False
```
**出现位置**:
- PlotBubble (完整版 + bbox_to_anchor逻辑)
- PlotStripdot (完整版)
- Plot.Style.legend (基类已有但功能不同)

**优化方案**: 优化基类的 `Style.legend()` 方法，支持 hue-based 图例

---

### 6️⃣ **Colorbar添加逻辑** (LOW PRIORITY)
**重复次数**: 2个类（但完全一致）
**代码模式**:
```python
if self.hue is not None:
    if pd.api.types.is_numeric_dtype(self.hue.dtype):
        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="5%", pad=...)
        cbar = self.figure.colorbar(scatter, cax=cax, orientation="vertical")
        cbar.set_label(self.hue.name)
        cbar.ax.set_zorder(0)
        self.figure.style._label_outer = False
        warnings.warn("画布存在colorbar，label_outer风格不生效", UserWarning)
```
**出现位置**:
- PlotBubble (pad=1.65 if show_hist else 0.05)
- PlotStripdot (pad=0.05)

**优化方案**: 基类添加 `_add_colorbar(scatter, pad=0.05)`

---

### 7️⃣ **数据列选择逻辑** (LOW PRIORITY)
**重复次数**: 6个类
**代码模式**:
```python
# Pattern: 如果不指定则使用默认列
x = df.iloc[:, 0] if x is None else df.loc[:, x]
y = df.iloc[:, 1] if y is None else df.loc[:, y]
z = df.iloc[:, 2] if z is None else df.loc[:, z]
size = df.iloc[:, 0] if size is None else df.loc[:, size]
```
**出现位置**:
- PlotBubble (x, y, z三列)
- PlotStripdot (start, end两列)
- PlotBoxdot (x, y两列)
- PlotPie, PlotWaffle, PlotFunnel (size一列)

**优化方案**: 基类添加 `_get_column(col_name, default_index=0)`

---

### 8️⃣ **占比计算** (LOW PRIORITY)
**重复次数**: 4个类
**代码模式**:
```python
# 总和占比
df_share = df.div(df.sum(axis=1), axis=0)

# 列占比
share = size.transform(lambda x: x / x.sum())
```
**出现位置**:
- PlotBar, PlotBarh (df_share行占比)
- PlotPie (share列占比)
- PlotWaffle (share列占比转百分比)

**优化方案**: 基类添加 `_calculate_share(data, axis=1)`

---

### 9️⃣ **颜色迭代器重置** (LOW PRIORITY)
**重复次数**: 3个类
**代码模式**:
```python
self._colors.iter_colors = cycle(
    self._colors.cmap_qual(i) for i in range(self._colors.cmap_qual.N)
)
```
**出现位置**:
- PlotBar (每个bar重置)
- PlotBarh (每个bar重置)

**优化方案**: 基类添加 `_reset_color_cycle()`

---

## 🎯 优化优先级

### 🔴 HIGH PRIORITY (立即优化)
1. **样式参数处理** - 影响15个类，代码重复最严重
2. **颜色获取逻辑** - 影响10个类，逻辑复杂且易出错

### 🟡 MEDIUM PRIORITY (第二阶段)
3. **坐标轴格式化** - 影响8个类，提升一致性
4. **标签文本创建** - 影响10个类，但逻辑差异较大
5. **图例处理** - 影响3个类，但逻辑复杂

### 🟢 LOW PRIORITY (可选优化)
6. **Colorbar添加** - 仅2个类，但逻辑完全一致
7. **数据列选择** - 6个类，简单但实用
8. **占比计算** - 4个类，简单工具方法
9. **颜色迭代器重置** - 仅2个类使用

---

## 📋 实施计划

### Step 1: 基类方法添加 (base.py)
```python
# 1. 样式合并
def _merge_style_kwargs(self, default_style: Dict, **kwargs) -> Dict:
    """合并默认样式和用户提供的kwargs"""
    
# 2. 颜色管理
def _get_color_for_item(self, item, use_dict=True, use_iter=True) -> str:
    """智能获取单个item的颜色"""
    
def _reset_color_cycle(self) -> None:
    """重置颜色迭代器"""
    
def _add_colorbar(self, scatter, hue_name: str, pad: float = 0.05) -> None:
    """为scatter图添加colorbar（用于连续型hue）"""

# 3. 坐标轴格式化
def _format_axis(self, axis: Literal['x', 'y', 'both'] = 'both', 
                 formatter: Optional[str] = None) -> None:
    """格式化坐标轴刻度标签"""

# 4. 数据处理
def _get_column(self, col: Optional[str], default_index: int = 0):
    """获取列数据，支持列名或默认索引"""
    
def _calculate_share(self, data, axis: int = 1):
    """计算占比"""

# 5. 文本标签
def _create_label_dict(self, **fields) -> Dict[str, str]:
    """创建标签格式化字典"""
    
def _add_text_with_bbox(self, x, y, text, color='white', 
                        bgcolor='auto', **kwargs):
    """添加带背景框的文本标签"""
```

### Step 2: 逐类重构
1. 先重构使用频率最高的方法
2. 每次重构一个类，运行测试确保功能不变
3. 记录重构前后的代码行数对比

### Step 3: 测试验证
- 运行现有测试套件
- 确保所有图表输出一致
- 性能测试（不应有明显下降）

---

## 📈 预期效果

### 代码行数减少
- **PlotBar**: 543行 → ~420行 (-23%)
- **PlotBarh**: 约-20%
- **PlotBubble**: 514行 → ~400行 (-22%)
- **PlotStripdot**: 约-25%
- **其他类**: 平均-15%~20%

### 总体改进
- **代码行数**: ~3500行 → ~2800行 (-20%)
- **重复代码**: 减少60%+
- **可维护性**: 显著提升
- **一致性**: 行为更统一

### 副作用
- **学习成本**: 需要了解基类新方法
- **调试难度**: 部分逻辑在基类中
- **灵活性**: 可能限制某些特殊定制

---

## ⚠️ 注意事项

1. **向后兼容**: 必须保持100%兼容
2. **测试覆盖**: 每个重构都需要测试验证
3. **文档更新**: 基类方法需要完善文档
4. **渐进式**: 不要一次性改太多，分批进行
5. **性能**: 注意方法调用开销不要过大

---

**准备就绪，等待用户确认开始实施！** 🚀
