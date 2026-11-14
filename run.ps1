# PRW-Wild PowerShell One-Click Launcher
Set-Location -Path $PSScriptRoot
$env:PYTHONPATH = "src"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Launching PRW-Wild 3D Digital Twin & Hardware Lab" -ForegroundColor Green
Write-Host "  URL: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
python -m prw_wild.web --port 8000 --open
