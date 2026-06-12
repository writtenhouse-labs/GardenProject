param(
  [switch]$Install,
  [int]$ApiPort = 8000,
  [int]$FrontendPort = 8501
)

$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$BackendVenv = Join-Path $BackendDir ".venv"
$FrontendVenv = Join-Path $FrontendDir ".venv"

function New-ProjectVenv {
  param([string]$ProjectDir, [string]$VenvDir)

  if (Test-Path $VenvDir) {
    return
  }

  Write-Host "Creating virtual environment: $VenvDir"
  Push-Location $ProjectDir
  try {
    if (Get-Command py -ErrorAction SilentlyContinue) {
      py -3.10 -m venv .venv
    } else {
      python -m venv .venv
    }
  } finally {
    Pop-Location
  }
}

function Install-Requirements {
  param([string]$ProjectDir, [string]$VenvDir)

  $Python = Join-Path $VenvDir "Scripts\python.exe"
  $Requirements = Join-Path $ProjectDir "requirements.txt"

  if (-not (Test-Path $Python)) {
    throw "Python executable not found in $VenvDir"
  }

  Write-Host "Installing requirements for $ProjectDir"
  & $Python -m pip install -r $Requirements
}

function Test-PythonPackage {
  param(
    [string]$VenvDir,
    [string]$PackageName
  )

  $Python = Join-Path $VenvDir "Scripts\python.exe"
  & $Python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('$PackageName') else 1)" 2>$null
  return $LASTEXITCODE -eq 0
}

New-ProjectVenv -ProjectDir $BackendDir -VenvDir $BackendVenv
New-ProjectVenv -ProjectDir $FrontendDir -VenvDir $FrontendVenv

if ($Install) {
  Install-Requirements -ProjectDir $BackendDir -VenvDir $BackendVenv
  Install-Requirements -ProjectDir $FrontendDir -VenvDir $FrontendVenv
}

if (-not (Test-PythonPackage -VenvDir $BackendVenv -PackageName "fastapi") -or
    -not (Test-PythonPackage -VenvDir $FrontendVenv -PackageName "streamlit")) {
  Write-Host "GardenProject dependencies are not installed yet." -ForegroundColor Yellow
  Write-Host "Run this once:"
  Write-Host "  .\start.ps1 -Install"
  exit 1
}

$ApiBaseUrl = "http://127.0.0.1:$ApiPort"

$BackendCommand = @"
Set-Location '$BackendDir'
`$host.UI.RawUI.WindowTitle = 'GardenProject API'
& '.\.venv\Scripts\Activate.ps1'
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port $ApiPort
"@

$FrontendCommand = @"
Set-Location '$FrontendDir'
`$host.UI.RawUI.WindowTitle = 'GardenProject Frontend'
& '.\.venv\Scripts\Activate.ps1'
`$env:GARDENPROJECT_API_BASE_URL = '$ApiBaseUrl'
streamlit run app.py --server.port $FrontendPort
"@

Write-Host "Starting GardenProject API at $ApiBaseUrl"
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy",
  "Bypass",
  "-Command",
  $BackendCommand
)

Start-Sleep -Seconds 2

Write-Host "Starting GardenProject frontend at http://localhost:$FrontendPort"
Start-Process powershell -WindowStyle Hidden -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy",
  "Bypass",
  "-Command",
  $FrontendCommand
)

Write-Host ""
Write-Host "GardenProject is starting."
Write-Host "API:      $ApiBaseUrl"
Write-Host "Frontend: http://localhost:$FrontendPort"
