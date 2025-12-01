# 部署：使用 NSSM 在 Windows 上为后端创建服务

本说明介绍如何在 Windows 上使用 `nssm` 将后端 FastAPI（通过 `uvicorn`）作为系统服务运行。假设项目位于 `D:\Projects\chart_class2`。

重要前提
- `nssm.exe` 已安装并可用（示例路径 `C:\tools\nssm\nssm.exe`）。
- 已创建并可用的 Python 虚拟环境（示例：`D:\Projects\chart_class2\.venv\Scripts\python.exe`）。
- 需要以管理员权限运行 PowerShell 来安装/管理服务。

包含文件
- `install-backend-service.ps1`：可执行脚本，会根据参数创建并启动名为 `ChartClass2API`（可自定义）的服务，并设置日志与环境变量。

快速开始（示例）
1. 以管理员身份打开 PowerShell。
2. 切换到仓库 `deploy` 目录：
```powershell
Set-Location "D:\Projects\chart_class2\deploy"
```
3. 运行示例安装命令（示例会提示并替换 JWT_SECRET_KEY 等）：
```powershell
.\install-backend-service.ps1 `
  -NssmPath 'C:\tools\nssm\nssm.exe' `
  -ServiceName 'ChartClass2API' `
  -ProjectRoot 'D:\Projects\chart_class2' `
  -PythonExe 'D:\Projects\chart_class2\.venv\Scripts\python.exe' `
  -UvicornArgs '-m uvicorn web_api.main:app --host 127.0.0.1 --port 8001'
```

脚本会完成以下操作：
- 在项目根创建 `logs` 目录（如果不存在）。
- 使用 `nssm install` 创建服务条目，运行命令为 `python -m uvicorn web_api.main:app ...`。
- 将 stdout/stderr 重定向到 `logs` 下的文件，并开启 nssm 的日志轮转。
- 将环境变量（例如 `ENVIRONMENT`、`JWT_SECRET_KEY`）写入服务（可在脚本参数中修改）。

安全提示
- 请勿在脚本中硬编码生产 `JWT_SECRET_KEY`；最好从安全存储或通过交互输入设置。
- 在生产环境中检查 `uvicorn` 启动参数（建议移除 `--reload`，并调整 `--log-level`）。

调试
- 若服务未启动，先查看 `D:\Projects\chart_class2\logs\chart_class2-err.log`。
- 可在 shell 中手动运行：
```powershell
& 'D:\Projects\chart_class2\.venv\Scripts\python.exe' -m uvicorn web_api.main:app --host 127.0.0.1 --port 8001
```
以确认应用可在不通过服务的情况下运行。

更多
- 如果希望同时以服务方式运行前端（`next start`），我可以为前端生成一个类似的 `nssm` 安装脚本，或建议在 Windows 上使用进程管理工具（例如 `pm2`）或 Docker 容器化部署。

如果你准备好了，我可以现在把这个脚本写到仓库（我已经准备好），然后演示如何运行（仅生成，不会自动执行）。
