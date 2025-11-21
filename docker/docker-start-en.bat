@echo off
REM Docker Quick Start Script (Windows) - English Version
REM Use this if Chinese characters display incorrectly

echo Starting Chart Class Docker services...

REM Check if in docker directory
if not exist "docker-compose.yml" (
    echo Error: Please run this script in the docker/ directory
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Build and start services
docker-compose up -d --build

echo.
echo Services started successfully!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo View logs: docker-compose logs -f
echo Stop services: docker-compose down

pause

