@echo off
chcp 65001 >nul
REM 从本地 .venv 导出依赖到 requirements-venv.txt

echo 正在从 .venv 导出 Python 包依赖...

REM 检查 .venv 是否存在
if not exist "..\.venv\Scripts\pip.exe" (
    echo ❌ 错误: 未找到 .venv 虚拟环境
    echo 请确保在项目根目录下已创建并激活 .venv
    pause
    exit /b 1
)

REM 激活虚拟环境并导出依赖
call ..\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 错误: 无法激活虚拟环境
    pause
    exit /b 1
)

REM 导出依赖到 requirements-venv.txt
echo 正在导出依赖列表...
pip freeze > requirements-venv.txt

if errorlevel 1 (
    echo ❌ 导出失败
    pause
    exit /b 1
)

REM 统计导出的包数量
for /f %%i in ('type requirements-venv.txt ^| find /c /v ""') do set count=%%i

echo.
echo ✅ 成功导出 %count% 个包到 requirements-venv.txt
echo.
echo 📝 文件位置: docker\requirements-venv.txt
echo.
echo 💡 提示: Docker 构建时会自动使用此文件中的包版本
echo.

pause

