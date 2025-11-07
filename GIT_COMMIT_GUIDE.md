# Git 提交建议

## 建议的提交信息

```bash
git add plots/ figure.py test_modular.py test_all_plots.py split_plots.py
git add *.md test_outputs/

git commit -m "refactor: 重构plots模块为清晰的模块化结构

- 将2840行的plots.py拆分为11个专职模块文件
- 创建plots包目录，按功能组织图表类
- 更新figure.py的导入方式
- 保持100%向后兼容性
- 添加完整的测试覆盖（7个图表类型）
- 添加详细的文档说明

模块分类：
- base.py: Plot基类和Style类
- utils.py: 公共工具函数
- bar.py: 柱状图类 (PlotBar, PlotBarh)
- line.py: 线图类 (PlotLine, PlotArea)
- scatter.py: 散点图类 (PlotBubble, PlotStripdot)
- statistical.py: 统计图类 (PlotHist, PlotBoxdot)
- heatmap.py: 热力图类 (PlotHeatmap)
- specialty.py: 特殊图表类 (PlotTreemap, PlotPie, PlotWaffle, PlotFunnel)
- text.py: 文本图表类 (PlotWordcloud, PlotTable)
- venn.py: 维恩图类 (PlotVenn2, PlotVenn3)

测试结果: ✅ 7/7 通过
文档: 添加README和完整的重构说明

关闭 #优化第一阶段
"
```

## 可选：分步提交

如果你想更细致的提交历史，可以分步提交：

### 步骤1：创建plots模块结构
```bash
git add plots/__init__.py plots/base.py plots/utils.py
git commit -m "refactor: 创建plots模块基础结构

- 添加plots包目录
- 提取Plot基类到base.py
- 提取工具函数到utils.py
"
```

### 步骤2：拆分图表类
```bash
git add plots/bar.py plots/line.py plots/scatter.py plots/statistical.py
git add plots/heatmap.py plots/specialty.py plots/text.py plots/venn.py
git commit -m "refactor: 将图表类按功能拆分到独立模块

- bar.py: 柱状图类
- line.py: 线图类
- scatter.py: 散点图类
- statistical.py: 统计图类
- heatmap.py: 热力图类
- specialty.py: 特殊图表类
- text.py: 文本图表类
- venn.py: 维恩图类
"
```

### 步骤3：更新导入
```bash
git add figure.py
git commit -m "refactor: 更新figure.py使用新的模块化导入"
```

### 步骤4：添加测试
```bash
git add test_modular.py test_all_plots.py test_outputs/
git commit -m "test: 添加模块化结构的测试覆盖

- test_modular.py: 基础功能测试
- test_all_plots.py: 7种图表类型的完整测试
- 所有测试通过 (7/7)
"
```

### 步骤5：添加文档
```bash
git add plots/README.md REFACTORING_*.md README_REFACTORING.md
git commit -m "docs: 添加重构说明文档

- plots/README.md: 模块详细说明
- REFACTORING_SUMMARY.md: 重构总结
- REFACTORING_COMPLETE.md: 完整报告
"
```

### 步骤6：添加辅助文件
```bash
git add split_plots.py
git commit -m "chore: 添加plots拆分脚本"
```

## .gitignore 建议

确保以下内容在 .gitignore 中：

```
# 测试输出
test_outputs/
test_modular_structure.png

# Python缓存
__pycache__/
*.pyc
*.pyo

# 虚拟环境
.venv/
venv/
```

## 注意事项

1. **保留原文件**: 原始的 `plots.py` 已保留作为备份，可以选择是否提交
   
2. **测试输出**: `test_outputs/` 目录包含测试生成的图片，可以选择不提交或添加到 .gitignore

3. **split_plots.py**: 这是一次性使用的拆分脚本，可以选择是否提交

## 推荐做法

```bash
# 1. 查看改动
git status

# 2. 添加核心文件
git add plots/ figure.py

# 3. 提交核心改动
git commit -m "refactor: 重构plots模块为模块化结构"

# 4. 添加测试
git add test_modular.py test_all_plots.py
git commit -m "test: 添加模块化测试"

# 5. 添加文档
git add *.md plots/README.md
git commit -m "docs: 添加重构文档"

# 6. 推送
git push origin master
```

## 创建Tag（可选）

标记这次重要的重构：

```bash
git tag -a v1.0.0-refactor -m "完成plots模块化重构

- 将单文件拆分为11个模块
- 提升代码可维护性和可读性
- 保持100%向后兼容
"

git push origin v1.0.0-refactor
```
