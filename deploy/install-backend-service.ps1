<#
install-backend-service.ps1

在 Windows (PowerShell) 上使用 nssm 为后端 FastAPI 创建服务的示例脚本。
用途：创建名为 `$ServiceName` 的 Windows 服务，执行虚拟环境中的 Python 启动 uvicorn。

注意：请以管理员权限运行此脚本。
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string] $NssmPath = 'C:\tools\nssm\nssm.exe',
    [Parameter(Mandatory=$false)] [string] $ServiceName = 'ChartClass2API',
    [Parameter(Mandatory=$false)] [string] $ProjectRoot = 'D:\Projects\chart_class2',
    [Parameter(Mandatory=$false)] [string] $PythonExe = 'D:\Projects\chart_class2\.venv\Scripts\python.exe',
    [Parameter(Mandatory=$false)] [string] $UvicornArgs = '-m uvicorn web_api.main:app --host 127.0.0.1 --port 8001',
    [Parameter(Mandatory=$false)] [string] $EnvEnvironment = 'production',
    [Parameter(Mandatory=$false)] [string] $JwtSecret = ''
)

function Assert-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Error "请以管理员身份运行 PowerShell（Run as Administrator）。"
        exit 1
    }
}

Assert-Admin

# 确认 nssm 可执行
if (-not (Test-Path -Path $NssmPath)) {
    Write-Error "找不到 nssm: $NssmPath 。请检查路径或安装 nssm。"
    exit 1
}

# 创建 logs 目录
$logsDir = Join-Path $ProjectRoot 'logs'
if (-not (Test-Path -Path $logsDir)) {
    New-Item -Path $logsDir -ItemType Directory -Force | Out-Null
    Write-Output "已创建日志目录: $logsDir"
} else {
    Write-Output "日志目录已存在: $logsDir"
}

# 手动测试提示（可跳过）
Write-Output "可选步骤：在开始前手动测试 uvicorn 命令："
Write-Output "& '$PythonExe' $UvicornArgs"

# 安装服务
Write-Output "正在使用 nssm 创建服务 '$ServiceName'..."
& $NssmPath install $ServiceName $PythonExe $UvicornArgs

# 设置工作目录
& $NssmPath set $ServiceName AppDirectory $ProjectRoot

# 设置日志文件
$stdout = Join-Path $logsDir 'chart_class2-out.log'
$stderr = Join-Path $logsDir 'chart_class2-err.log'
& $NssmPath set $ServiceName AppStdout $stdout
& $NssmPath set $ServiceName AppStderr $stderr
& $NssmPath set $ServiceName AppRotateFiles 1

# 设置环境变量（追加形式）
$envList = @()
$envList += "ENVIRONMENT=$EnvEnvironment"
if ($JwtSecret -ne '') {
    $envList += "JWT_SECRET_KEY=$JwtSecret"
} else {
    Write-Warning "未提供 JWT_SECRET_KEY（生产环境请务必设置强密钥）。"
}
$envList += "PYTHONUNBUFFERED=1"

$envExtra = [String]::Join("`n", $envList)
& $NssmPath set $ServiceName AppEnvironmentExtra $envExtra

Write-Output "服务配置已写入（名称: $ServiceName）。尝试启动服务..."

# 启动服务并检查状态
& $NssmPath start $ServiceName
Start-Sleep -Seconds 2
try {
    $svc = Get-Service -Name $ServiceName -ErrorAction Stop
    Write-Output "服务当前状态: $($svc.Status)"
} catch {
    Write-Error "无法查询服务状态：$($_.Exception.Message)"; exit 1
}

Write-Output "安装完成。查看日志: $stdout , $stderr"
Write-Output "如果需要修改配置，可使用：& $NssmPath set $ServiceName <Option> <Value> 然后 & $NssmPath restart $ServiceName"
