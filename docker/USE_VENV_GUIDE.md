# 使用本地 .venv 虚拟环境中的 Python 包

## 概述

Docker 现在支持直接使用本地 `.venv` 虚拟环境中已安装的 Python 包版本，确保 Docker 容器中的包版本与本地开发环境完全一致。

## 快速开始

### 步骤 1: 导出 .venv 依赖

在 `docker/` 目录下运行导出脚本：

**Windows:**
```bash
cd docker
.\export-venv-requirements.bat
```

**Linux/Mac:**
```bash
cd docker
chmod +x export-venv-requirements.sh
./export-venv-requirements.sh
```

这会在 `docker/` 目录下生成 `requirements-venv.txt` 文件，包含 `.venv` 中所有已安装的包及其版本。

### 步骤 2: 重新构建 Docker 镜像

```bash
cd docker
docker-compose build backend
```

Docker 会自动检测 `requirements-venv.txt` 并使用其中的包版本。

## 工作原理

### 依赖安装优先级

Dockerfile 按以下优先级安装依赖：

1. **requirements-venv.txt**（最高优先级）
   - 如果存在，会安装文件中列出的所有包和版本
   - 完全匹配本地 `.venv` 环境
   - 跳过标准依赖文件安装

2. **requirements-local.txt**
   - 仅在未使用 `requirements-venv.txt` 时生效
   - 用于安装本地修改过的特定包

3. **requirements-core.txt, requirements-plot.txt, requirements-other.txt**
   - 仅在未使用 `requirements-venv.txt` 时生效
   - 标准依赖文件

### 为什么这样设计？

- **requirements-venv.txt**: 确保 Docker 环境与本地开发环境完全一致
- **requirements-local.txt**: 用于测试修改过的特定包
- **标准依赖文件**: 作为后备方案，确保项目可以独立构建

## 使用场景

### 场景 1: 完全匹配本地环境

当你想要 Docker 容器使用与本地 `.venv` 完全相同的包版本时：

1. 导出依赖：
   ```bash
   cd docker
   .\export-venv-requirements.bat
   ```

2. 构建镜像：
   ```bash
   docker-compose build backend
   ```

3. 验证版本：
   ```bash
   docker-compose exec backend pip list
   ```

### 场景 2: 混合使用

如果你只想让某些包使用 `.venv` 的版本，其他包使用标准版本：

1. 手动编辑 `requirements-venv.txt`，只保留需要的包
2. 或者不使用 `requirements-venv.txt`，改用 `requirements-local.txt` 指定特定包

### 场景 3: 禁用 .venv 依赖

如果不想使用 `.venv` 的依赖：

1. 删除或重命名 `docker/requirements-venv.txt`
2. 重新构建镜像

Docker 会自动回退到使用标准依赖文件。

## 注意事项

### 1. 平台兼容性

`.venv` 中的包可能包含 Windows 特定的二进制文件，这些在 Linux Docker 容器中无法使用。Docker 构建时会自动处理：

- 纯 Python 包：可以直接使用
- 包含 C 扩展的包：pip 会在 Linux 环境中重新编译
- 预编译的 wheel 文件：如果平台不匹配，pip 会下载或编译适合 Linux 的版本

### 2. 构建时间

使用 `requirements-venv.txt` 时，Docker 需要安装所有包，构建时间可能较长（特别是包含大型包如 numpy, pandas, matplotlib 时）。

### 3. 版本更新

当 `.venv` 中的包更新后，需要重新导出：

```bash
cd docker
.\export-venv-requirements.bat
docker-compose build backend
```

### 4. Git 管理

建议将 `requirements-venv.txt` 添加到 `.gitignore`：

```
docker/requirements-venv.txt
```

因为：
- 每个人的 `.venv` 可能不同
- 文件可能很大
- 应该使用标准依赖文件作为项目依赖的单一来源

## 常见问题

### Q: 导出失败怎么办？

A: 检查：
1. `.venv` 是否存在且已激活
2. `pip` 是否可用
3. 虚拟环境是否损坏（尝试重新创建）

### Q: Docker 构建时显示"未找到 requirements-venv.txt"正常吗？

A: 正常。如果文件不存在，Docker 会使用标准依赖文件。

### Q: 可以使用 requirements-venv.txt 和 requirements-local.txt 同时吗？

A: 不可以。如果存在 `requirements-venv.txt`，会优先使用它，忽略 `requirements-local.txt`。

### Q: 如何知道 Docker 使用了哪个依赖文件？

A: 查看构建日志，会显示：
- `=== 检测到 requirements-venv.txt，将使用 .venv 中的包版本 ===`
- 或 `=== 未找到 requirements-venv.txt，将使用标准依赖文件 ===`

### Q: 导出后 requirements-venv.txt 文件很大？

A: 正常。`pip freeze` 会列出所有依赖（包括间接依赖），文件可能包含数百行。

## 最佳实践

1. **开发阶段**: 使用 `requirements-venv.txt` 确保环境一致
2. **生产部署**: 使用标准依赖文件（`requirements-core.txt` 等）
3. **版本控制**: 将 `requirements-venv.txt` 添加到 `.gitignore`
4. **定期更新**: 当 `.venv` 更新后，重新导出依赖

## 示例

### 完整工作流程

```bash
# 1. 在本地开发，安装/更新包
.venv\Scripts\activate
pip install some-package==1.2.3

# 2. 导出依赖
cd docker
.\export-venv-requirements.bat

# 3. 构建 Docker 镜像（使用 .venv 的版本）
docker-compose build backend

# 4. 启动服务
docker-compose up -d

# 5. 验证版本
docker-compose exec backend pip list | grep some-package
```

