@echo off
REM NSSM 服务安装脚本
REM 用于将 FastAPI 应用注册为 Windows 服务

set SERVICE_NAME=ChartClassAPI
set APP_PATH=%~dp0..
set PYTHON_PATH=%APP_PATH%\.venv\Scripts\python.exe
set SCRIPT_PATH=%APP_PATH%\web_api\main.py

REM 检查 NSSM 是否在 PATH 中
where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到 nssm.exe，请确保 NSSM 已安装并在 PATH 中
    echo 下载地址: https://nssm.cc/download
    pause
    exit /b 1
)

REM 检查 Python 环境
if not exist "%PYTHON_PATH%" (
    echo 错误: 未找到 Python 解释器: %PYTHON_PATH%
    pause
    exit /b 1
)

REM 检查脚本文件
if not exist "%SCRIPT_PATH%" (
    echo 错误: 未找到脚本文件: %SCRIPT_PATH%
    pause
    exit /b 1
)

REM 创建日志目录
if not exist "%APP_PATH%\logs" mkdir "%APP_PATH%\logs"

REM 如果服务已存在，先停止并删除
nssm status %SERVICE_NAME% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo 服务已存在，正在停止...
    nssm stop %SERVICE_NAME%
    timeout /t 2 >nul
    nssm remove %SERVICE_NAME% confirm
    timeout /t 1 >nul
)

REM 安装服务
echo 正在安装服务...
nssm install %SERVICE_NAME% %PYTHON_PATH% "%SCRIPT_PATH%"

REM 设置工作目录
nssm set %SERVICE_NAME% AppDirectory %APP_PATH%

REM 设置环境变量
nssm set %SERVICE_NAME% AppEnvironmentExtra "UVICORN_WORKERS=4" "THREAD_POOL_SIZE=4" "PYTHONPATH=%APP_PATH%" "UVICORN_PORT=8001" "UVICORN_HOST=127.0.0.1"

REM 设置启动参数
nssm set %SERVICE_NAME% AppParameters ""

REM 设置日志
nssm set %SERVICE_NAME% AppStdout %APP_PATH%\logs\service_stdout.log
nssm set %SERVICE_NAME% AppStderr %APP_PATH%\logs\service_stderr.log

REM 设置日志轮转（每天轮转，保留 7 天）
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateOnline 1
nssm set %SERVICE_NAME% AppRotateSeconds 86400
nssm set %SERVICE_NAME% AppRotateBytes 10485760

REM 设置服务描述
nssm set %SERVICE_NAME% Description "Chart Class Web API Service - FastAPI 图表渲染服务"

REM 设置启动类型为自动
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START

REM 启动服务
echo 正在启动服务...
nssm start %SERVICE_NAME%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 服务安装成功！
    echo ========================================
    echo 服务名称: %SERVICE_NAME%
    echo 服务状态: 运行中
    echo 日志目录: %APP_PATH%\logs\
    echo.
    echo 查看服务状态: nssm status %SERVICE_NAME%
    echo 查看日志: type %APP_PATH%\logs\service_stdout.log
    echo 停止服务: nssm stop %SERVICE_NAME%
    echo.
) else (
    echo.
    echo ========================================
    echo 服务启动失败！
    echo ========================================
    echo 请检查日志: %APP_PATH%\logs\service_stderr.log
    echo.
    pause
    exit /b 1
)

pause

