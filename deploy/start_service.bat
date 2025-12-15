@echo off
REM NSSM 服务安装脚本
REM 用于将 FastAPI 应用注册为 Windows 服务

setlocal enabledelayedexpansion

for /f "tokens=2 delims=: " %%i in ('chcp') do set "OLD_CP=%%i"
chcp 65001 >nul

set "SERVICE_NAME=ChartClass2API"
set "APP_PATH=%~dp0.."
set "UVICORN_CMD=-m uvicorn web_api.main:app --host 127.0.0.1 --port 8001 --workers 4"
set "NSSM_EXE=C:\tools\nssm\nssm.exe"
for %%i in ("%APP_PATH%") do set "APP_PATH=%%~fi"
set "PYTHON_PATH=%APP_PATH%\.venv\Scripts\python.exe"
set "ENV_FILE=%~dp0env.production"

if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1* delims==" %%A in ("%ENV_FILE%") do (
        set "KEY=%%~A"
        if defined KEY (
            if /I not "!KEY:~0,1!"=="#" (
                set "VALUE=%%~B"
                set "!KEY!=!VALUE!"
            )
        )
    )
) else (
    echo 警告: 未找到配置文件 %ENV_FILE% ，将读取当前环境变量。
)

if "%JWT_SECRET_KEY%"=="" (
    echo 错误: 未检测到 JWT_SECRET_KEY 环境变量。
    echo 请先运行: set "JWT_SECRET_KEY=<生成的随机密钥>"
    pause
    goto :restore
)

REM 检查 NSSM 是否存在
if not exist "%NSSM_EXE%" (
    echo 错误: 未找到 NSSM 可执行文件: "%NSSM_EXE%"
    echo 请确认已安装 NSSM 或修改脚本中的 NSSM_EXE 路径。
    pause
    exit /b 1
)

REM 检查 Python 环境
if not exist "%PYTHON_PATH%" (
    echo 错误: 未找到 Python 解释器: %PYTHON_PATH%
    pause
    exit /b 1
)

REM 确认 FastAPI 入口模块存在
if not exist "%APP_PATH%\web_api\main.py" (
    echo 错误: 未找到 FastAPI 入口模块: %APP_PATH%\web_api\main.py
    pause
    exit /b 1
)

REM 创建日志目录
if not exist "%APP_PATH%\logs" mkdir "%APP_PATH%\logs"

REM 如果服务已存在，先停止并删除
"%NSSM_EXE%" status %SERVICE_NAME% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo 服务已存在，正在停止并移除...
    "%NSSM_EXE%" stop %SERVICE_NAME% >nul 2>&1
    timeout /t 2 >nul
    "%NSSM_EXE%" remove %SERVICE_NAME% confirm >nul 2>&1
    timeout /t 1 >nul
)

REM 安装服务
echo 正在安装服务...
"%NSSM_EXE%" install %SERVICE_NAME% %PYTHON_PATH% %UVICORN_CMD%

REM 设置工作目录
"%NSSM_EXE%" set %SERVICE_NAME% AppDirectory %APP_PATH%

REM 设置环境变量
"%NSSM_EXE%" set %SERVICE_NAME% AppEnvironmentExtra "ENVIRONMENT=production" "PYTHONUNBUFFERED=1" "PYTHONPATH=%APP_PATH%" "JWT_SECRET_KEY=%JWT_SECRET_KEY%" "UVICORN_WORKERS=4"

REM 设置日志
"%NSSM_EXE%" set %SERVICE_NAME% AppStdout %APP_PATH%\logs\service_stdout.log
"%NSSM_EXE%" set %SERVICE_NAME% AppStderr %APP_PATH%\logs\service_stderr.log

REM 设置日志轮转（每天轮转，保留 7 天）
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateFiles 1
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateOnline 1
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateSeconds 86400
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateBytes 10485760

REM 设置服务描述与启动类型
"%NSSM_EXE%" set %SERVICE_NAME% Description "Chart Class Web API Service"
"%NSSM_EXE%" set %SERVICE_NAME% Start SERVICE_AUTO_START

REM 启动服务
echo 正在启动服务...
"%NSSM_EXE%" start %SERVICE_NAME%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 服务安装成功！
    echo ========================================
    echo 服务名称: %SERVICE_NAME%
    echo 服务状态: 运行中
    echo 日志目录: %APP_PATH%\logs\
    echo.
    echo 查看服务状态: "%NSSM_EXE%" status %SERVICE_NAME%
    echo 查看日志: type %APP_PATH%\logs\service_stdout.log
    echo 停止服务: "%NSSM_EXE%" stop %SERVICE_NAME%
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

:restore
if defined OLD_CP chcp %OLD_CP% >nul
endlocal

