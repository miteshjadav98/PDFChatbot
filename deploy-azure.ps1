# ============================================================
# deploy-azure.ps1 — Deploy PDFChatbot to Azure Container Apps
# ============================================================
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - Docker installed and running
# Usage:
#   .\deploy-azure.ps1
# ============================================================

param(
    [string]$ResourceGroup = "rg-miteshaiservice-dev",
    [string]$Location = "southeastasia",
    [string]$AcrName = "pychatbot",
    [string]$AppName = "pdfchatbot",
    [string]$EnvName = "pdfchatbot-env",
    [string]$ImageName = "pdfchatbot",
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PDFChatbot Azure Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# --- 0. Check prerequisites ---
Write-Host "[0/6] Checking prerequisites..." -ForegroundColor Yellow
try { az --version | Out-Null } catch {
    Write-Error "Azure CLI is not installed. Install it from https://aka.ms/installazurecliwindows"
    exit 1
}
try { docker --version | Out-Null } catch {
    Write-Error "Docker is not installed or not running."
    exit 1
}

# --- 1. Create Resource Group ---
Write-Host "[1/6] Creating Resource Group '$ResourceGroup' in '$Location'..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none

# --- 2. Create Azure Container Registry ---
Write-Host "[2/6] Creating Azure Container Registry '$AcrName'..." -ForegroundColor Yellow
az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --admin-enabled true --output none

# Get ACR credentials
$AcrLoginServer = az acr show --name $AcrName --query loginServer --output tsv
$AcrUsername = az acr credential show --name $AcrName --query username --output tsv
$AcrPassword = az acr credential show --name $AcrName --query "passwords[0].value" --output tsv

Write-Host "  ACR Login Server: $AcrLoginServer" -ForegroundColor Gray

# --- 3. Build and Push Docker Image ---
Write-Host "[3/6] Building Docker image..." -ForegroundColor Yellow
$FullImageName = "${AcrLoginServer}/${ImageName}:${ImageTag}"

docker build -t $FullImageName .
Write-Host "  Image built: $FullImageName" -ForegroundColor Gray

Write-Host "[3/6] Pushing image to ACR..." -ForegroundColor Yellow
az acr login --name $AcrName
docker push $FullImageName
Write-Host "  Image pushed successfully" -ForegroundColor Gray

# --- 4. Load environment variables from .env ---
Write-Host "[4/6] Loading environment variables from .env..." -ForegroundColor Yellow
$EnvVars = @()
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            # Remove surrounding quotes from values
            if ($line -match '^([^=]+)=(.*)$') {
                $key = $Matches[1].Trim()
                $value = $Matches[2].Trim().Trim('"').Trim("'")
                $EnvVars += "${key}=${value}"
            }
        }
    }
    Write-Host "  Loaded $($EnvVars.Count) environment variables" -ForegroundColor Gray
} else {
    Write-Warning "No .env file found. Environment variables will not be set."
}

# --- 5. Create Container Apps Environment ---
Write-Host "[5/6] Creating Container Apps Environment '$EnvName'..." -ForegroundColor Yellow

# Ensure the containerapp extension is installed
az extension add --name containerapp --upgrade --yes 2>$null
az provider register --namespace Microsoft.App --wait 2>$null
az provider register --namespace Microsoft.OperationalInsights --wait 2>$null

az containerapp env create `
    --name $EnvName `
    --resource-group $ResourceGroup `
    --location $Location `
    --output none

# --- 6. Deploy Container App ---
Write-Host "[6/6] Deploying Container App '$AppName'..." -ForegroundColor Yellow

$createArgs = @(
    "containerapp", "create",
    "--name", $AppName,
    "--resource-group", $ResourceGroup,
    "--environment", $EnvName,
    "--image", $FullImageName,
    "--registry-server", $AcrLoginServer,
    "--registry-username", $AcrUsername,
    "--registry-password", $AcrPassword,
    "--target-port", "8501",
    "--ingress", "external",
    "--cpu", "2",
    "--memory", "4Gi",
    "--min-replicas", "0",
    "--max-replicas", "3",
    "--output", "none"
)

# Add env vars if we have them
if ($EnvVars.Count -gt 0) {
    $createArgs += "--env-vars"
    $createArgs += $EnvVars
}

& az @createArgs

# --- Done! Get the URL ---
$AppUrl = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n  Your app is live at:" -ForegroundColor White
Write-Host "  https://$AppUrl" -ForegroundColor Cyan
Write-Host "`n  Resource Group:  $ResourceGroup" -ForegroundColor Gray
Write-Host "  Container App:   $AppName" -ForegroundColor Gray
Write-Host "  ACR:             $AcrLoginServer" -ForegroundColor Gray
Write-Host ""

Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:     az containerapp logs show --name $AppName --resource-group $ResourceGroup --follow" -ForegroundColor Gray
Write-Host "  Update image:  az containerapp update --name $AppName --resource-group $ResourceGroup --image $FullImageName" -ForegroundColor Gray
Write-Host "  Delete all:    az group delete --name $ResourceGroup --yes --no-wait" -ForegroundColor Gray
Write-Host ""
