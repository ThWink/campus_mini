$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$web = Join-Path $root "frontend\web-client"
$miniprogram = Join-Path $root "frontend\miniprogram"

Write-Host "Checking backend..."
Push-Location $backend
try {
    .\mvnw.cmd test
}
finally {
    Pop-Location
}

Write-Host "Checking web client..."
Push-Location $web
try {
    npm run build
}
finally {
    Pop-Location
}

Write-Host "Checking mini program JavaScript..."
$jsFiles = rg --files $miniprogram -g "*.js"
foreach ($file in $jsFiles) {
    node --check $file
}

Write-Host ""
Write-Host "Pre-deploy checks passed."
