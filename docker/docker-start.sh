#!/bin/bash
# Docker 快速启动脚本

echo "🚀 启动 Chart Class Docker 服务..."

# 检查是否在 docker 目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 请在 docker/ 目录下运行此脚本"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 构建并启动服务
docker-compose up -d --build

echo ""
echo "✅ 服务已启动！"
echo ""
echo "📊 前端: http://localhost:3000"
echo "🔧 后端 API: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"


