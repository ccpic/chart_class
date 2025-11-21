@echo off
chcp 65001 >nul
echo 使用 docker build 直接构建后端（避免超时问题）...
echo.

REM 检查是否在 docker 目录
if not exist "Dockerfile.backend" (
    echo ❌ 请在 docker/ 目录下运行此脚本
    pause
    exit /b 1
)

REM 使用 docker build 直接构建，显示详细输出
docker build -f Dockerfile.backend --progress=plain --no-cache -t chart-class-backend ..

if errorlevel 1 (
    echo.
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo.
echo ✅ 构建成功！
echo.
echo 现在可以使用 docker-compose up -d 启动服务
pause


