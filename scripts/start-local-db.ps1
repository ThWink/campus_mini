$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $env:USERPROFILE ".campus-runner\mariadb"
$downloads = Join-Path $root ".local\downloads"
$msi = Join-Path $downloads "mariadb-12.2.2-winx64.msi"
$extract = Join-Path $runtime "extract"
$server = Join-Path $extract "MariaDB 12.2"
$bin = Join-Path $server "bin"
$data = Join-Path $runtime "data"
$logs = Join-Path $runtime "logs"
$client = Join-Path $bin "mariadb.exe"
$schema = Join-Path $root "deploy\sql\schema.sql"

function Test-Port {
    param([int] $Port)
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1)
}

function Wait-Port {
    param(
        [int] $Port,
        [int] $Seconds = 45
    )

    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port $Port) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

New-Item -ItemType Directory -Force -Path $runtime, $downloads, $logs | Out-Null

if (-not (Test-Path -LiteralPath $msi)) {
    $url = "https://mirrors.tuna.tsinghua.edu.cn/mariadb/mariadb-12.2.2/winx64-packages/mariadb-12.2.2-winx64.msi"
    Write-Host "Downloading MariaDB from Tsinghua mirror..."
    & curl.exe -L --fail --retry 3 --connect-timeout 20 -o $msi $url
    if ($LASTEXITCODE -ne 0) {
        throw "MariaDB download failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $bin "mariadbd.exe"))) {
    Write-Host "Extracting MariaDB..."
    Remove-Item -LiteralPath $extract -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $extract | Out-Null
    $process = Start-Process -FilePath "msiexec.exe" `
        -ArgumentList @("/a", $msi, "/qn", "TARGETDIR=$extract") `
        -Wait `
        -PassThru
    if ($process.ExitCode -ne 0) {
        throw "MariaDB MSI extraction failed with exit code $($process.ExitCode)"
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $data "mysql"))) {
    Write-Host "Initializing local MariaDB data directory..."
    Remove-Item -LiteralPath $data -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $data | Out-Null
    & (Join-Path $bin "mariadb-install-db.exe") --datadir=$data --password=sc031215 --port=3306
    if ($LASTEXITCODE -ne 0) {
        throw "MariaDB initialization failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Port 3306)) {
    Write-Host "Starting local MariaDB on 3306..."
    Start-Process -FilePath (Join-Path $bin "mariadbd.exe") `
        -ArgumentList @("--defaults-file=$(Join-Path $data 'my.ini')", "--console") `
        -WorkingDirectory $server `
        -RedirectStandardOutput (Join-Path $logs "mariadb.out.log") `
        -RedirectStandardError (Join-Path $logs "mariadb.err.log") | Out-Null
}

if (-not (Wait-Port 3306 45)) {
    Get-Content -LiteralPath (Join-Path $logs "mariadb.err.log") -Tail 120 -ErrorAction SilentlyContinue
    throw "MariaDB did not start on 3306"
}

& $client --protocol=tcp --host=127.0.0.1 --port=3306 --user=root --password=sc031215 --execute="CREATE USER IF NOT EXISTS 'runner'@'%' IDENTIFIED BY 'sc031215'; CREATE USER IF NOT EXISTS 'runner'@'localhost' IDENTIFIED BY 'sc031215'; GRANT ALL PRIVILEGES ON campus_runner.* TO 'runner'@'%'; GRANT ALL PRIVILEGES ON campus_runner.* TO 'runner'@'localhost'; FLUSH PRIVILEGES;"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to prepare runner database user"
}

Get-Content -LiteralPath $schema -Raw -Encoding UTF8 | & $client --protocol=tcp --host=127.0.0.1 --port=3306 --user=root --password=sc031215
if ($LASTEXITCODE -ne 0) {
    throw "Failed to import schema.sql"
}

Write-Host "Local MariaDB is ready: 127.0.0.1:3306 / campus_runner / runner"
