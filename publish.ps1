# 一键发布：构建网站 → 提交 → 推送
# 用法: .\publish.ps1 "提交信息"
# 示例: .\publish.ps1 "新增: 前端笔记"

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Message
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "`n🚀 开始发布..." -ForegroundColor Cyan

# Step 1: 构建网站
Write-Host "`n[1/3] 正在构建网站..." -ForegroundColor Yellow
python build.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 构建失败，请检查 build.py 输出" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 构建完成" -ForegroundColor Green

# Step 2: 提交
Write-Host "`n[2/3] 正在提交..." -ForegroundColor Yellow
git add -A
$diff = git diff --cached --quiet 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️  没有文件变动，跳过提交" -ForegroundColor Yellow
} else {
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 提交失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ 提交成功" -ForegroundColor Green
}

# Step 3: 推送
Write-Host "`n[3/3] 正在推送..." -ForegroundColor Yellow
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 推送失败，请检查网络或远程仓库配置" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 推送成功" -ForegroundColor Green

Write-Host "`n🎉 发布完成！等待 GitHub Actions 自动部署..." -ForegroundColor Cyan
