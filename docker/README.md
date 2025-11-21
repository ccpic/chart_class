# Docker 部署指南

## 📁 文件结构

所有 Docker 相关文件已整理到 `docker/` 目录：

```
docker/
├── Dockerfile.backend          # 后端 Dockerfile
├── Dockerfile.frontend          # 前端 Dockerfile
├── docker-compose.yml           # 开发环境配置
├── docker-compose.prod.yml      # 生产环境配置
├── env.example                  # 环境变量示例
├── docker-start.sh              # Linux/Mac 启动脚本
├── docker-start.bat             # Windows 启动脚本（中文，已修复乱码）
├── docker-start.ps1             # PowerShell 启动脚本（推荐，中文支持更好）
├── docker-start-en.bat          # Windows 启动脚本（英文版本，兼容性更好）
└── README.md                    # 本文档

项目根目录/
├── .dockerignore                # Docker 忽略规则（在根目录）
└── docker/                      # Docker 配置目录
```

## 快速开始

### 开发环境

```bash
# 进入 docker 目录
cd docker

# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境

```bash
# 进入 docker 目录
cd docker

# 使用生产配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 服务访问

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8001
- **API 文档**: http://localhost:8001/docs

## 环境变量配置

### 方式1: 使用 .env 文件（推荐）

```bash
# 在 docker/ 目录下
cp env.example .env
# 编辑 .env 文件，修改相应配置
```

### 方式2: 直接在 docker-compose.yml 中设置

编辑 `docker/docker-compose.yml` 文件，修改环境变量部分。

### 环境变量说明

- `BACKEND_PORT`: 后端端口（默认 8001）
- `FRONTEND_PORT`: 前端端口（默认 3000）
- `NEXT_PUBLIC_API_URL`: 前端访问后端的地址（默认 http://localhost:8001）
- `CORS_ORIGINS`: CORS 允许的来源，逗号分隔

## 数据持久化

数据文件存储在项目根目录的 `data/` 目录，通过 volume 挂载到容器中。

## 常见问题

### 1. 端口冲突

如果 3000 或 8001 端口被占用，修改 `docker-compose.yml` 中的端口映射，或设置环境变量：

```bash
# 在 docker/ 目录下
export BACKEND_PORT=8001
export FRONTEND_PORT=3001
docker-compose up -d
```

### 2. 前端无法连接后端

确保 `NEXT_PUBLIC_API_URL` 环境变量正确设置。在 Docker 环境中，浏览器访问的是 `localhost:8001`，所以通常使用 `http://localhost:8001`。

### 3. 构建失败

如果构建失败，检查：

1. `requirements.txt` 是否包含所有依赖
2. `frontend/package.json` 是否正确
3. Docker 镜像是否正确下载
4. 确保在项目根目录运行（构建上下文需要访问项目文件）

### 4. Windows 服务器部署

在 Windows 服务器上：

1. 确保安装了 Docker Desktop for Windows
2. 启用 WSL2 后端（推荐）
3. 确保防火墙允许 3000 和 8001 端口
4. 使用 PowerShell 或 Git Bash 运行命令
5. 使用 `docker-start.bat` 脚本（在 docker/ 目录下）

## 单独构建服务

```bash
# 进入 docker 目录
cd docker

# 只构建后端
docker-compose build backend

# 只构建前端
docker-compose build frontend

# 重新构建（不使用缓存）
docker-compose build --no-cache
```

## 查看容器日志

```bash
# 进入 docker 目录
cd docker

# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时跟踪日志
docker-compose logs -f backend
```

## 进入容器调试

```bash
# 进入 docker 目录
cd docker

# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

## 清理

```bash
# 进入 docker 目录
cd docker

# 停止并删除容器
docker-compose down

# 删除容器、网络和卷
docker-compose down -v

# 删除镜像
docker-compose down --rmi all
```

## 使用启动脚本

### Windows

**方式 1: PowerShell 脚本（推荐，中文显示正常）**
```powershell
# 在 docker/ 目录下
.\docker-start.ps1
```

如果遇到执行策略限制，先运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**方式 2: 批处理文件（已修复乱码）**
```cmd
# 在 docker/ 目录下
docker-start.bat
```

**方式 3: 英文版本（如果中文仍有问题）**
```cmd
# 在 docker/ 目录下
docker-start-en.bat
```

### Linux/Mac

```bash
# 在 docker/ 目录下
chmod +x docker-start.sh
./docker-start.sh
```

## 注意事项

1. **构建上下文**: Docker Compose 的构建上下文是项目根目录（`..`），所以需要在 `docker/` 目录下运行 `docker-compose` 命令
2. **路径引用**: 所有路径都是相对于项目根目录的
3. **数据持久化**: `data/` 目录在项目根目录，会自动挂载到容器中

