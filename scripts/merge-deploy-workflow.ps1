<#!
    合并 develop 到 deploy/prod 的标准流程脚本。
    - Merge 模式：在非生产环境执行合并、测试并推送。
    - Deploy 模式：在部署服务器执行快进更新。
    所有关键步骤都需要人工确认才能继续。
#>

param(
    [ValidateSet("Merge","Deploy")]
    [string]$Mode = "Merge",
    [string]$Remote = "origin",
    [string]$SourceBranch = "develop",
    [string]$TargetBranch = "deploy/prod",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$script:StepIndex = 0

function Confirm-Step {
    param([string]$Message)

    $script:StepIndex++
    Write-Host ""
    Write-Host ("[{0}] {1}" -f $script:StepIndex, $Message) -ForegroundColor Cyan

    if (-not $Force) {
        $response = Read-Host "按 Enter 确认继续，输入 q 取消执行"
        if ($response -match '^(q|quit|exit)$') {
            Write-Host "用户取消，流程已结束。" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "已启用 Force 模式，自动继续。" -ForegroundColor DarkGray
    }
}

function Invoke-Git {
    param([string[]]$Arguments, [string]$Action)

    git @Arguments
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        Write-Error ("{0} 失败，退出码 {1}" -f $Action, $exit)
        exit $exit
    }
}

function Show-SectionHeader {
    param([string]$Header)
    Write-Host ""
    Write-Host ("==== {0} ====\n" -f $Header) -ForegroundColor Green
}

$sourceRef = "{0}/{1}" -f $Remote, $SourceBranch

switch ($Mode) {
    "Merge" {
        Show-SectionHeader "合并流程 (在安全环境执行)"

        Confirm-Step ("确认并切换到 {0} 分支" -f $TargetBranch)
        $current = (git rev-parse --abbrev-ref HEAD).Trim()
        if ($current -ne $TargetBranch) {
            Write-Host ("当前分支为 {0}，将切换到 {1}。" -f $current, $TargetBranch) -ForegroundColor Yellow
            Invoke-Git -Arguments @("checkout", $TargetBranch) -Action "切换分支"
        } else {
            Write-Host ("已位于 {0}。" -f $TargetBranch) -ForegroundColor DarkGreen
        }

        Confirm-Step "检查未提交修改"
        $status = git status --short
        if ($LASTEXITCODE -ne 0) {
            Write-Error "无法读取 git 状态。"
            exit $LASTEXITCODE
        }
        if ($status) {
            Write-Host "检测到未提交修改，请评估是否需要 stash 或提交后再继续：" -ForegroundColor Yellow
            Write-Host $status
            Confirm-Step "确认继续执行后续操作"
        } else {
            Write-Host "工作区干净。" -ForegroundColor DarkGreen
        }

        Confirm-Step ("抓取远端 {0}" -f $Remote)
        Invoke-Git -Arguments @("fetch", "--prune", $Remote) -Action "git fetch"

        Confirm-Step ("查看 {0} 相对于 {1} 的新增提交" -f $sourceRef, $TargetBranch)
        git log --oneline ("{0}..{1}" -f $TargetBranch, $sourceRef)
        if ($LASTEXITCODE -ne 0) {
            Write-Error "无法获取日志。"
            exit $LASTEXITCODE
        }

        Confirm-Step "查看差异统计"
        git diff --stat ("{0}...{1}" -f $TargetBranch, $sourceRef)
        if ($LASTEXITCODE -ne 0) {
            Write-Error "无法显示 diff。"
            exit $LASTEXITCODE
        }

        Confirm-Step ("执行合并 (git merge --no-ff --no-commit {0})" -f $sourceRef)
        Invoke-Git -Arguments @("merge", "--no-ff", "--no-commit", $sourceRef) -Action "git merge"
        Write-Host "合并已完成但尚未提交，请在继续前验证代码与测试。" -ForegroundColor Yellow

        Confirm-Step "确认创建合并提交"
        $defaultMessage = "Merge {0} into {1}" -f $SourceBranch, $TargetBranch
        $commitMessage = Read-Host ("输入合并提交信息 (默认: {0})" -f $defaultMessage)
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = $defaultMessage
        }
        Invoke-Git -Arguments @("commit", "-m", $commitMessage) -Action "git commit"

        Confirm-Step "再次查看状态"
        git status --short
        if ($LASTEXITCODE -ne 0) {
            Write-Error "无法读取 git 状态。"
            exit $LASTEXITCODE
        }

        Confirm-Step ("推送 {0} 到远端 {1}" -f $TargetBranch, $Remote)
        Invoke-Git -Arguments @("push", $Remote, $TargetBranch) -Action "git push"

        Write-Host ""
        Write-Host "合并流程完成。请在部署服务器上执行 Deploy 模式以更新代码。" -ForegroundColor Green
    }
    "Deploy" {
        Show-SectionHeader "部署服务器快进更新"

        Confirm-Step ("确认当前分支为 {0}" -f $TargetBranch)
        $current = (git rev-parse --abbrev-ref HEAD).Trim()
        if ($current -ne $TargetBranch) {
            Write-Host ("当前分支为 {0}，将切换到 {1}。" -f $current, $TargetBranch) -ForegroundColor Yellow
            Invoke-Git -Arguments @("checkout", $TargetBranch) -Action "切换分支"
        } else {
            Write-Host ("已位于 {0}。" -f $TargetBranch) -ForegroundColor DarkGreen
        }

        Confirm-Step "检查未提交修改"
        $status = git status --short
        if ($LASTEXITCODE -ne 0) {
            Write-Error "无法读取 git 状态。"
            exit $LASTEXITCODE
        }
        if ($status) {
            Write-Host "部署分支存在未提交修改，请先处理后再继续。" -ForegroundColor Red
            Write-Host $status
            exit 1
        } else {
            Write-Host "工作区干净。" -ForegroundColor DarkGreen
        }

        Confirm-Step ("抓取远端 {0}" -f $Remote)
        Invoke-Git -Arguments @("fetch", "--prune", $Remote) -Action "git fetch"

        Confirm-Step ("执行快进拉取 (git pull --ff-only {0} {1})" -f $Remote, $TargetBranch)
        Invoke-Git -Arguments @("pull", "--ff-only", $Remote, $TargetBranch) -Action "git pull --ff-only"

        Confirm-Step "更新后查看状态"
        git status --short
        if ($LASTEXITCODE -ne 0) {
            Write-Error "无法读取 git 状态。"
            exit $LASTEXITCODE
        }

        Write-Host ""
        Write-Host "部署更新完成。如需重启服务请根据项目流程执行。" -ForegroundColor Green
    }
    default {
        Write-Error "未知 Mode: $Mode"
        exit 1
    }
}
