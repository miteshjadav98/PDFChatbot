# ============================================================
# redeploy.ps1 — Rebuild, push, and update the running Container App
# ============================================================
# Use this AFTER the app is already deployed, whenever you change code
# or add a feature. It does NOT recreate Azure resources.
#
# Usage:
#   .\redeploy.ps1                 # builds & pushes :latest, updates the app
#   .\redeploy.ps1 -ImageTag v2    # use a specific tag instead of 'latest'
# ============================================================

param(
    [string]$ResourceGroup = "rg-miteshaiservice-dev",
    [string]$AcrName        = "pychatbot",
    [string]$AppName        = "pdfchatbot",
    [string]$ImageName      = "pdfchatbot",
    [string]$ImageTag       = "latest"
)

$ErrorActionPreference = "Stop"

$AcrLoginServer = "$AcrName.azurecr.io"
$FullImage      = "$AcrLoginServer/$ImageName`:$ImageTag"

Write-Host "`n=== Redeploying $FullImage ===`n" -ForegroundColor Cyan

# --- 1. Build the image ---
Write-Host "[1/4] Building image..." -ForegroundColor Yellow
docker build -t $FullImage .

# --- 2. Log in to ACR and push ---
Write-Host "[2/4] Pushing to ACR..." -ForegroundColor Yellow
az acr login --name $AcrName
docker push $FullImage

# --- 3. Update the Container App to pull the new image ---
Write-Host "[3/4] Updating Container App..." -ForegroundColor Yellow
az containerapp update `
    --name $AppName `
    --resource-group $ResourceGroup `
    --image $FullImage `
    --output none

# --- 4. Show the live URL ---
Write-Host "[4/4] Done. Fetching URL..." -ForegroundColor Yellow
$Fqdn = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" -o tsv

Write-Host "`n=== Deployed ===" -ForegroundColor Green
Write-Host "Live at: https://$Fqdn" -ForegroundColor Cyan
Write-Host "Logs:    az containerapp logs show --name $AppName --resource-group $ResourceGroup --follow" -ForegroundColor Gray
Write-Host ""
