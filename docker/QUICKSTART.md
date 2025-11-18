# Docker 快速开始

## 🚀 一键启动（推荐）

### Windows
```bash
cd docker
docker-start.bat
```

### Linux/Mac
```bash
cd docker
./docker-start.sh
```

## 📝 手动启动

```bash
# 1. 进入 docker 目录
cd docker

# 2. 构建并启动服务
docker-compose up -d --build

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

## 🌐 访问服务

启动成功后，访问以下地址：

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## ⚙️ 配置环境变量

```bash
# 在 docker/ 目录下
cp env.example .env
# 编辑 .env 文件，修改配置
```

## 🛑 停止服务

```bash
cd docker
docker-compose down
```

## 📚 更多信息

查看 [README.md](README.md) 获取详细文档。


