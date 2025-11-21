# Docker 快速启动脚本 (PowerShell)
# 使用方式: .\docker-start.ps1

Write-Host "🚀 启动 Chart Class Docker 服务..." -ForegroundColor Green

# 检查是否在 docker 目录
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ 请在 docker/ 目录下运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查 Docker 是否运行
$dockerCheck = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker 未运行，请先启动 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 构建并启动服务
docker-compose up -d --build

Write-Host ""
Write-Host "✅ 服务已启动！" -ForegroundColor Green
Write-Host ""
Write-Host "📊 前端: http://localhost:3000"
Write-Host "🔧 后端 API: http://localhost:8001"
Write-Host "📚 API 文档: http://localhost:8001/docs"
Write-Host ""
Write-Host "查看日志: docker-compose logs -f"
Write-Host "停止服务: docker-compose down"

