<#
install-frontend-service.ps1

示例脚本：在 Windows 上使用 nssm 将 Next.js 前端作为服务运行。
功能：可选择执行 `npm ci`、`npm run build`，并使用 nssm 创建服务来运行 `npm start`。

用法示例（以管理员 PowerShell 运行）：
.\install-frontend-service.ps1 `
  -NssmPath 'C:\tools\nssm\nssm.exe' `
  -ServiceName 'ChartClass2Frontend' `
  -ProjectFrontend 'D:\Projects\chart_class2\frontend' `
  -NpmPath 'C:\Program Files\nodejs\npm.cmd' `
  -RunInstall:$true `
  -RunBuild:$true

注意：构建时需要的公开环境变量（以 NEXT_PUBLIC_ 开头）应在传入脚本前设置，或在脚本中添加环境项。
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string] $NssmPath = 'C:\tools\nssm\nssm.exe',
    [Parameter(Mandatory=$false)] [string] $ServiceName = 'ChartClass2Frontend',
    [Parameter(Mandatory=$false)] [string] $ProjectFrontend = 'D:\Projects\chart_class2\frontend',
    [Parameter(Mandatory=$false)] [string] $NpmPath = 'C:\Program Files\nodejs\npm.cmd',
    [Parameter(Mandatory=$false)] [switch] $RunInstall = $false,
    [Parameter(Mandatory=$false)] [switch] $RunBuild = $false,
    [Parameter(Mandatory=$false)] [string] $Port = '3000'
)

function Assert-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Error "请以管理员身份运行 PowerShell（Run as Administrator）。"
        exit 1
    }
}

Assert-Admin

if (-not (Test-Path -Path $NssmPath)) {
    Write-Error "找不到 nssm: $NssmPath 。请检查路径或安装 nssm。"
    exit 1
}

if (-not (Test-Path -Path $ProjectFrontend)) {
    Write-Error "找不到前端目录: $ProjectFrontend"
    exit 1
}

Write-Output "工作目录: $ProjectFrontend"

# 可选：安装依赖
if ($RunInstall.IsPresent) {
    Write-Output "运行 npm ci 安装依赖..."
    Push-Location $ProjectFrontend
    & $NpmPath ci
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -ne 0) { Write-Error "npm ci 返回代码 $rc"; exit 1 }
}

# 可选：构建生产产物
if ($RunBuild.IsPresent) {
    Write-Output "运行 npm run build 构建前端..."
    Push-Location $ProjectFrontend
    & $NpmPath run build
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -ne 0) { Write-Error "npm run build 返回代码 $rc"; exit 1 }
}

# 创建日志目录
$logsDir = Join-Path (Split-Path $ProjectFrontend -Parent) 'logs\frontend'
if (-not (Test-Path -Path $logsDir)) {
    New-Item -Path $logsDir -ItemType Directory -Force | Out-Null
    Write-Output "已创建日志目录: $logsDir"
} else {
    Write-Output "日志目录已存在: $logsDir"
}

Write-Output "使用 nssm 创建/更新服务 '$ServiceName'，AppPath=$NpmPath, 参数=start"
& $NssmPath install $ServiceName $NpmPath 'start'

# 工作目录
& $NssmPath set $ServiceName AppDirectory $ProjectFrontend

# 日志
$stdout = Join-Path $logsDir 'frontend-out.log'
$stderr = Join-Path $logsDir 'frontend-err.log'
& $NssmPath set $ServiceName AppStdout $stdout
& $NssmPath set $ServiceName AppStderr $stderr
& $NssmPath set $ServiceName AppRotateFiles 1

# 环境变量（运行时）
$envList = @()
$envList += "PORT=$Port"
$envList += "NODE_ENV=production"

$envExtra = [String]::Join("`n", $envList)
& $NssmPath set $ServiceName AppEnvironmentExtra $envExtra

Write-Output "启动服务..."
& $NssmPath start $ServiceName
Start-Sleep -Seconds 2
try {
    $svc = Get-Service -Name $ServiceName -ErrorAction Stop
    Write-Output "服务当前状态: $($svc.Status)"
} catch {
    Write-Error "无法查询服务状态：$($_.Exception.Message)"; exit 1
}

Write-Output "安装/启动完成。查看日志: $stdout , $stderr"
Write-Output "若需要修改环境变量或参数，可使用: & $NssmPath set $ServiceName <Option> <Value> 然后 & $NssmPath restart $ServiceName"
