# Docker 使用本地 Python 包指南

## 概述

Dockerfile 已配置支持使用本地修改过的 Python 包，而不是从 PyPI 安装。这对于以下场景很有用：

- 修改了第三方包的源码
- 使用自定义版本的包
- 开发时快速测试修改

## 快速开始

### 步骤 1: 准备本地包

选择以下方式之一：

#### 方式 A: 使用 Wheel 文件（推荐）

1. 打包修改过的包：
   ```bash
   cd /path/to/modified/package
   python -m build --wheel
   # 或
   python setup.py bdist_wheel
   ```

2. 复制 wheel 文件到项目：
   ```bash
   mkdir -p docker/local_packages
   cp dist/package_name-version-custom.whl docker/local_packages/
   ```

#### 方式 B: 使用源码目录

1. 复制修改过的包源码：
   ```bash
   mkdir -p docker/local_packages
   cp -r /path/to/modified/package docker/local_packages/package_name
   ```

### 步骤 2: 创建 requirements-local.txt

1. 复制示例文件：
   ```bash
   cp docker/requirements-local.txt.example docker/requirements-local.txt
   ```

2. 编辑 `docker/requirements-local.txt`，添加本地包路径：

   **使用 Wheel 文件：**
   ```
   file:///app/docker/local_packages/package_name-version-custom.whl
   ```

   **使用源码目录：**
   ```
   file:///app/docker/local_packages/package_name
   ```

   **使用可编辑安装（开发模式，推荐）：**
   ```
   -e file:///app/docker/local_packages/package_name
   ```

### 步骤 3: 重新构建镜像

```bash
cd docker
docker-compose build backend
```

## 详细说明

### 工作原理

1. Dockerfile 会先复制 `docker/local_packages/` 目录到容器
2. 如果存在 `docker/requirements-local.txt`，会先安装本地包
3. 然后安装标准依赖（`requirements-core.txt` 等）
4. 如果本地包和标准依赖中有同名包，本地包会优先使用

### 路径说明

- **主机路径**：`docker/local_packages/package.whl`
- **容器内路径**：`/app/docker/local_packages/package.whl`
- **requirements-local.txt 中的路径**：使用容器内路径（`/app/docker/local_packages/...`）

### 示例

假设你修改了 `matplotlib` 包：

1. **打包 wheel 文件**：
   ```bash
   cd matplotlib-source
   python -m build --wheel
   cp dist/matplotlib-3.10.5-custom-py3-none-any.whl ../docker/local_packages/
   ```

2. **创建 requirements-local.txt**：
   ```bash
   echo "file:///app/docker/local_packages/matplotlib-3.10.5-custom-py3-none-any.whl" > docker/requirements-local.txt
   ```

3. **重新构建**：
   ```bash
   cd docker
   docker-compose build backend
   ```

4. **验证**：
   ```bash
   docker-compose exec backend pip list | grep matplotlib
   docker-compose exec backend python -c "import matplotlib; print(matplotlib.__file__)"
   ```

   如果显示 `/app/docker/local_packages/` 路径，说明使用的是本地包。

### 多个本地包

在 `requirements-local.txt` 中每行一个包：

```
file:///app/docker/local_packages/package1-1.0.0-custom.whl
file:///app/docker/local_packages/package2-2.0.0-custom.whl
-e file:///app/docker/local_packages/package3
```

### 开发模式（可编辑安装）

如果使用可编辑安装（`-e`），修改代码后无需重新构建镜像，只需重启容器：

```bash
# 修改代码后
docker-compose restart backend
```

### 禁用本地包

如果不想使用本地包，只需：

1. 删除或重命名 `docker/requirements-local.txt`
2. 重新构建镜像

Dockerfile 会自动检测并跳过本地包安装。

## 常见问题

### Q: 如何知道本地包是否生效？

A: 检查包的安装路径：
```bash
docker-compose exec backend python -c "import package_name; print(package_name.__file__)"
```

如果路径包含 `/app/docker/local_packages/`，说明使用的是本地包。

### Q: 本地包和标准依赖版本冲突怎么办？

A: 本地包会优先使用。如果标准依赖中也有同名包，pip 会跳过已安装的版本。

### Q: 可以使用 Git 仓库吗？

A: 可以，在 `requirements-local.txt` 中使用：
```
git+https://github.com/your-username/package.git@your-branch
```

### Q: 构建时显示"未找到本地包目录"正常吗？

A: 正常。如果 `docker/local_packages/` 目录不存在，Dockerfile 会显示此消息并继续使用 PyPI 安装。

## 注意事项

1. **文件大小**：大型包（如 numpy, pandas）的 wheel 文件可能很大，会增加镜像大小
2. **构建时间**：本地包安装可能比从 PyPI 安装慢（特别是源码安装）
3. **版本管理**：建议在 `requirements-local.txt` 中注释说明使用的本地包版本和修改原因
4. **Git 忽略**：如果不想将本地包提交到 Git，在 `.gitignore` 中添加：
   ```
   docker/local_packages/
   docker/requirements-local.txt
   ```

