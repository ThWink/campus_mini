$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$web = Join-Path $root "frontend\web-client"
$ai = Join-Path $root "ai-rag"
$dbScript = Join-Path $PSScriptRoot "start-local-db.ps1"
$backendEnv = Join-Path $root "deploy\env\backend.env"

function Test-Port {
    param([int] $Port)
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1)
}

function Import-EnvFile {
    param([string] $Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Warning "Backend env file not found: $Path"
        return
    }

    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $index = $line.IndexOf("=")
        if ($index -lt 1) {
            return
        }

        $key = $line.Substring(0, $index).Trim()
        $value = $line.Substring($index + 1).Trim()

        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        Set-Item -Path "Env:$key" -Value $value
    }

    Write-Host "Loaded backend environment: $Path"
}

function Wait-Port {
    param(
        [int] $Port,
        [int] $Seconds = 30
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

function Invoke-Step {
    param(
        [string] $FilePath,
        [string[]] $ArgumentList,
        [string] $WorkingDirectory
    )

    $process = Start-Process -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -Wait `
        -PassThru `
        -NoNewWindow

    if ($process.ExitCode -ne 0) {
        throw "$FilePath failed with exit code $($process.ExitCode)"
    }
}

Import-EnvFile $backendEnv

if (Test-Path -LiteralPath $dbScript) {
    Write-Host "Starting local MariaDB..."
    & powershell -ExecutionPolicy Bypass -File $dbScript
}

Write-Host "Building backend..."
Push-Location $backend
try {
    .\mvnw.cmd -DskipTests package

    if (-not (Test-Port 8080)) {
        $backendOut = Join-Path $backend "target\backend.out.log"
        $backendErr = Join-Path $backend "target\backend.err.log"
        Remove-Item $backendOut, $backendErr -ErrorAction SilentlyContinue
        Start-Process -FilePath "java" `
            -ArgumentList @("-jar", "target\runner-0.0.1-SNAPSHOT.jar") `
            -WorkingDirectory $backend `
            -RedirectStandardOutput $backendOut `
            -RedirectStandardError $backendErr | Out-Null
    }
}
finally {
    Pop-Location
}

if (-not (Wait-Port 8080 30)) {
    throw "Backend did not start on http://localhost:8080. Check backend\target\backend.err.log and backend\target\backend.out.log."
}

if (Test-Path -LiteralPath $ai) {
    Write-Host "Starting AI/RAG service..."
    Push-Location $ai
    try {
        if (-not (Test-Port 8000)) {
            $venvPython = Join-Path $ai ".venv\Scripts\python.exe"
            if (-not (Test-Path -LiteralPath $venvPython)) {
                Write-Host "Creating AI/RAG virtual environment..."
                Invoke-Step -FilePath "python" -ArgumentList @("-m", "venv", ".venv") -WorkingDirectory $ai
                Invoke-Step -FilePath $venvPython -ArgumentList @("-m", "pip", "install", "--upgrade", "pip") -WorkingDirectory $ai
                Invoke-Step -FilePath $venvPython -ArgumentList @("-m", "pip", "install", "-r", "requirements.txt") -WorkingDirectory $ai
            }

            $logDir = Join-Path $ai "logs"
            New-Item -ItemType Directory -Force -Path $logDir | Out-Null
            $aiOut = Join-Path $logDir "fastapi.out.log"
            $aiErr = Join-Path $logDir "fastapi.err.log"
            Remove-Item $aiOut, $aiErr -ErrorAction SilentlyContinue
            Start-Process -FilePath $venvPython `
                -ArgumentList @("src\main.py") `
                -WorkingDirectory $ai `
                -RedirectStandardOutput $aiOut `
                -RedirectStandardError $aiErr | Out-Null
        }
    }
    finally {
        Pop-Location
    }

    if (-not (Wait-Port 8000 45)) {
        throw "AI/RAG service did not start on http://127.0.0.1:8000. Check ai-rag\logs\fastapi.err.log and ai-rag\logs\fastapi.out.log."
    }
}
else {
    Write-Warning "AI/RAG directory not found: $ai"
}

Write-Host "Starting web client..."
Push-Location $web
try {
    if (-not (Test-Path "node_modules")) {
        npm install
    }

    if (-not (Test-Port 5173)) {
        $webOut = Join-Path $web "vite.out.log"
        $webErr = Join-Path $web "vite.err.log"
        Remove-Item $webOut, $webErr -ErrorAction SilentlyContinue
        Start-Process -FilePath "npm.cmd" `
            -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1") `
            -WorkingDirectory $web `
            -RedirectStandardOutput $webOut `
            -RedirectStandardError $webErr | Out-Null
    }
}
finally {
    Pop-Location
}

if (-not (Wait-Port 5173 30)) {
    throw "Web client did not start on http://127.0.0.1:5173. Check frontend\web-client\vite.err.log and frontend\web-client\vite.out.log."
}

Write-Host ""
Write-Host "Campus Runner is running:"
Write-Host "  Backend: http://localhost:8080"
Write-Host "  AI/RAG:  http://127.0.0.1:8000"
Write-Host "  Web:     http://127.0.0.1:5173/"
Write-Host ""
Write-Host "Dev accounts:"
Write-Host "  Admin: admin / sc031215"
Write-Host "  Users: user1 / user1, user2 / user2"
