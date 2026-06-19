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
$RunDir = Join-Path $Root ".run"
$StatePath = Join-Path $RunDir "processes.json"

function Get-PortConflicts {
  param(
    [int]$Port,
    [string]$ServiceName
  )

  $Listeners = @(
    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
      Sort-Object OwningProcess -Unique
  )
  $ProcessSnapshot = @(Get-CimInstance Win32_Process)

  foreach ($Listener in $Listeners) {
    $Owner = $ProcessSnapshot | Where-Object { $_.ProcessId -eq $Listener.OwningProcess }
    $ApplicationName = $null
    $CurrentProcess = $Owner
    for ($Depth = 0; $CurrentProcess -and $Depth -lt 6; $Depth++) {
      if ($CurrentProcess.CommandLine -like "*\GardenProject\*") {
        $ApplicationName = "GardenProject"
        break
      }
      if ($CurrentProcess.CommandLine -like "*\PelagicSeer\*") {
        $ApplicationName = "PelagicSeer"
        break
      }
      $ParentId = $CurrentProcess.ParentProcessId
      $CurrentProcess = $ProcessSnapshot | Where-Object { $_.ProcessId -eq $ParentId }
    }
    if (-not $ApplicationName) {
      $ApplicationName = if ($Owner.Name) { $Owner.Name } else { "an unknown application" }
    }

    [pscustomobject]@{
      Service = $ServiceName
      Port = $Port
      Application = $ApplicationName
      ProcessId = $Listener.OwningProcess
    }
  }
}

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

if (Test-Path $StatePath) {
  $TrackedState = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
  $ProcessSnapshot = @(Get-CimInstance Win32_Process)
  $RunningProcesses = @(
    $TrackedState.processes | ForEach-Object {
      $TrackedProcess = $ProcessSnapshot | Where-Object { $_.ProcessId -eq [int]$_.id }
      if ($TrackedProcess -and $TrackedProcess.CommandLine -like "*$Root*") {
        $TrackedProcess
      }
    }
  )
  if ($RunningProcesses.Count -gt 0) {
    throw "GardenProject is already running. Use .\stop.ps1 before starting it again."
  }
  Remove-Item -LiteralPath $StatePath -Force
}

$PortConflicts = @(
  Get-PortConflicts -Port $ApiPort -ServiceName "API"
  Get-PortConflicts -Port $FrontendPort -ServiceName "frontend"
)
if ($PortConflicts.Count -gt 0) {
  Write-Host ""
  Write-Host "GardenProject cannot start because another application is using a required port:" -ForegroundColor Yellow
  foreach ($Conflict in $PortConflicts) {
    Write-Host "  $($Conflict.Service) port $($Conflict.Port): $($Conflict.Application) (PID $($Conflict.ProcessId))"
  }
  Write-Host ""
  Write-Host "Stop the conflicting application or choose different ports, for example:"
  Write-Host "  .\start.ps1 -ApiPort 8001 -FrontendPort 8502"
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
$BackendProcess = Start-Process powershell -WindowStyle Hidden -PassThru -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy",
  "Bypass",
  "-Command",
  $BackendCommand
)

Start-Sleep -Seconds 2

Write-Host "Starting GardenProject frontend at http://localhost:$FrontendPort"
$FrontendProcess = Start-Process powershell -WindowStyle Hidden -PassThru -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy",
  "Bypass",
  "-Command",
  $FrontendCommand
)

New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
@{
  project = "GardenProject"
  root = $Root
  startedAt = (Get-Date).ToUniversalTime().ToString("o")
  processes = @(
    @{ name = "api"; id = $BackendProcess.Id }
    @{ name = "frontend"; id = $FrontendProcess.Id }
  )
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatePath -Encoding UTF8

Write-Host ""
Write-Host "GardenProject is starting."
Write-Host "API:      $ApiBaseUrl"
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "Stop:     .\stop.ps1"
