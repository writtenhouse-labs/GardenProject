param(
  [string]$Project = "gardenproject-dev",
  [string]$Region = "us-central1",
  [string]$Gcloud = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
  [string]$ApiUrl = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

if (-not (Test-Path $Gcloud)) {
  throw "gcloud was not found at $Gcloud"
}

Write-Host "Deploying GardenProject API..."
& $Gcloud run deploy gardenproject-api `
  --project $Project `
  --region $Region `
  --source $BackendDir `
  --timeout 120 `
  --update-env-vars "PYTHONPATH=/workspace" `
  --quiet

if (-not $ApiUrl) {
  $ApiUrl = & $Gcloud run services describe gardenproject-api `
    --project $Project `
    --region $Region `
    --format "value(status.url)"
}

Write-Host "Deploying GardenProject frontend..."
& $Gcloud run deploy gardenproject-frontend `
  --project $Project `
  --region $Region `
  --source $FrontendDir `
  --timeout 3600 `
  --session-affinity `
  --min 1 `
  --max 3 `
  --concurrency 10 `
  --update-env-vars "GARDENPROJECT_API_BASE_URL=$ApiUrl" `
  --quiet

Write-Host "GardenProject deployment complete."
Write-Host "API: $ApiUrl"
Write-Host "Frontend:"
& $Gcloud run services describe gardenproject-frontend `
  --project $Project `
  --region $Region `
  --format "value(status.url)"
