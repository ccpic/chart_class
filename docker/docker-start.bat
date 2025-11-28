@echo off
chcp 65001 >nul
REM Docker 快速启动脚本 (Windows)

echo 🚀 启动 Chart Class Docker 服务...

REM 检查是否在 docker 目录
if not exist "docker-compose.yml" (
    echo ❌ 请在 docker/ 目录下运行此脚本
    pause
    exit /b 1
)

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

REM 检查环境变量（如果使用生产配置）
if exist "docker-compose.prod.yml" (
    echo.
    echo 🔍 检查环境配置...
    python ..\scripts\check_env.py
    if errorlevel 1 (
        echo.
        echo ❌ 环境检查失败，请修复问题后重试
        echo 提示：检查 docker/.env 文件中的配置
        pause
        exit /b 1
    )
    echo.
)

REM 构建并启动服务
docker-compose up -d --build

echo.
echo ✅ 服务已启动！
echo.
echo 📊 前端: http://localhost:3000
echo 🔧 后端 API: http://localhost:8001
echo 📚 API 文档: http://localhost:8001/docs
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down

pause


