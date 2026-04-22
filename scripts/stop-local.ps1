$ports = @(5173, 8080, 8000)

foreach ($port in $ports) {
    $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        try {
            Stop-Process -Id $listener.OwningProcess -Force
            Write-Host "Stopped process $($listener.OwningProcess) on port $port"
        }
        catch {
            Write-Host "Could not stop process $($listener.OwningProcess) on port ${port}: $($_.Exception.Message)"
        }
    }
}

$dbScript = Join-Path $PSScriptRoot "stop-local-db.ps1"
if (Test-Path -LiteralPath $dbScript) {
    & powershell -ExecutionPolicy Bypass -File $dbScript
}
