# 本地 Python 包目录

## 用途

此目录用于存放本地修改过的 Python 包，Docker 构建时会优先使用这些包，而不是从 PyPI 安装。

## 使用方法

### 方法 1: 使用 Wheel 文件（推荐）

1. 将修改过的包打包成 wheel 文件：
   ```bash
   # 在包的源码目录下
   python setup.py bdist_wheel
   # 或使用 build
   python -m build --wheel
   ```

2. 将生成的 `.whl` 文件复制到此目录：
   ```bash
   cp dist/package_name-version-custom.whl docker/local_packages/
   ```

3. 创建 `docker/requirements-local.txt` 文件：
   ```
   # 使用本地 wheel 文件
   file:///app/docker/local_packages/package_name-version-custom.whl
   ```

### 方法 2: 使用源码目录

1. 将修改过的包源码目录复制到此目录：
   ```bash
   cp -r /path/to/modified/package docker/local_packages/package_name
   ```

2. 创建 `docker/requirements-local.txt` 文件：
   ```
   # 使用本地源码目录（开发模式）
   file:///app/docker/local_packages/package_name
   ```

   或者使用可编辑安装（推荐用于开发）：
   ```
   # 可编辑安装，修改代码后无需重新构建镜像
   -e file:///app/docker/local_packages/package_name
   ```

### 方法 3: 使用 Git 仓库

如果修改过的包在 Git 仓库中：

1. 创建 `docker/requirements-local.txt` 文件：
   ```
   # 使用 Git 仓库
   git+https://github.com/your-username/package-name.git@your-branch
   ```

## 注意事项

1. **路径说明**：
   - 在 `requirements-local.txt` 中，路径是容器内的路径（`/app/docker/local_packages/`）
   - 不是主机路径

2. **安装顺序**：
   - Dockerfile 会先安装本地包，再安装标准依赖
   - 如果本地包和标准依赖中有同名包，本地包会优先使用

3. **版本冲突**：
   - 如果本地包版本与 `requirements-*.txt` 中的版本不同，pip 会使用已安装的版本
   - 如需强制重新安装，可以在 Dockerfile 中使用 `--force-reinstall`

4. **文件大小**：
   - 大型包（如 numpy, pandas）的 wheel 文件可能很大
   - 考虑使用 `.dockerignore` 排除不必要的文件

## 示例

假设你修改了 `matplotlib` 包：

1. 打包 wheel 文件：
   ```bash
   cd matplotlib-source
   python -m build --wheel
   cp dist/matplotlib-3.10.5-custom-py3-none-any.whl ../docker/local_packages/
   ```

2. 创建 `docker/requirements-local.txt`：
   ```
   file:///app/docker/local_packages/matplotlib-3.10.5-custom-py3-none-any.whl
   ```

3. 重新构建 Docker 镜像：
   ```bash
   cd docker
   docker-compose build backend
   ```

## 验证

构建完成后，可以进入容器验证本地包是否已安装：

```bash
docker-compose exec backend pip list | grep package_name
docker-compose exec backend python -c "import package_name; print(package_name.__file__)"
```

如果显示的是 `/app/docker/local_packages/` 路径，说明使用的是本地包。

