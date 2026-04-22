$listeners = Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue

foreach ($listener in $listeners) {
    $process = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -match "mariadbd|mysqld") {
        try {
            Stop-Process -Id $listener.OwningProcess -Force
            Write-Host "Stopped local MariaDB process $($listener.OwningProcess) on port 3306"
        }
        catch {
            Write-Host "Could not stop local MariaDB process $($listener.OwningProcess): $($_.Exception.Message)"
        }
    }
}
