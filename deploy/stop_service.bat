@echo off
REM NSSM 服务卸载脚本

set SERVICE_NAME=ChartClassAPI

REM 检查 NSSM 是否在 PATH 中
where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到 nssm.exe，请确保 NSSM 已安装并在 PATH 中
    pause
    exit /b 1
)

REM 检查服务是否存在
nssm status %SERVICE_NAME% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 服务 %SERVICE_NAME% 不存在
    pause
    exit /b 0
)

echo 正在停止服务 %SERVICE_NAME%...
nssm stop %SERVICE_NAME%

timeout /t 2 >nul

echo 正在删除服务 %SERVICE_NAME%...
nssm remove %SERVICE_NAME% confirm

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 服务已成功停止并删除
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo 服务删除失败
    echo ========================================
    echo.
    pause
    exit /b 1
)

pause

