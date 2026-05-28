# Azure Deployment Script for AI Security Reviewer
# Run this script with proper Azure permissions

param(
    [string]$ResourceGroup = "rg-aisecreviewer-dev",
    [string]$Location = "japaneast",
    [string]$SwaLocation = "eastasia",
    [string]$AcrName = "craisecreviewer",
    [string]$CaeName = "cae-aisecreviewer-dev",
    [string]$CaName = "ca-aisecreviewer-api-dev",
    [string]$SwaName = "swa-aisecreviewer-dev"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "AI Security Reviewer - Azure Deployment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Step 1: Create Resource Group
Write-Host "`n[1/8] Creating Resource Group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location -o none
Write-Host "✓ Resource Group created: $ResourceGroup" -ForegroundColor Green

# Step 2: Create Container Registry
Write-Host "`n[2/8] Creating Container Registry..." -ForegroundColor Yellow
az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --admin-enabled true -o none
$AcrLoginServer = az acr show --name $AcrName --query loginServer -o tsv
Write-Host "✓ ACR created: $AcrLoginServer" -ForegroundColor Green

# Step 3: Build and Push Docker Image
Write-Host "`n[3/8] Building and pushing Docker image..." -ForegroundColor Yellow
Push-Location $PSScriptRoot\..\backend
az acr build --registry $AcrName --image aisecreviewer-api:latest .
Pop-Location
Write-Host "✓ Docker image pushed" -ForegroundColor Green

# Step 4: Create Container Apps Environment
Write-Host "`n[4/8] Creating Container Apps Environment..." -ForegroundColor Yellow
az containerapp env create --name $CaeName --resource-group $ResourceGroup --location $Location -o none
Write-Host "✓ Container Apps Environment created" -ForegroundColor Green

# Step 5: Get ACR credentials
$AcrPassword = az acr credential show --name $AcrName --query "passwords[0].value" -o tsv

# Step 6: Create Container App
Write-Host "`n[5/8] Deploying Container App..." -ForegroundColor Yellow
az containerapp create `
    --name $CaName `
    --resource-group $ResourceGroup `
    --environment $CaeName `
    --image "$AcrLoginServer/aisecreviewer-api:latest" `
    --target-port 8000 `
    --ingress external `
    --registry-server $AcrLoginServer `
    --registry-username $AcrName `
    --registry-password $AcrPassword `
    --cpu 0.5 `
    --memory 1.0Gi `
    --min-replicas 1 `
    --max-replicas 3 `
    -o none

$BackendUrl = az containerapp show --name $CaName --resource-group $ResourceGroup --query "properties.configuration.ingress.fqdn" -o tsv
$BackendUrl = "https://$BackendUrl"
Write-Host "✓ Container App deployed: $BackendUrl" -ForegroundColor Green

# Step 7: Update CORS settings
Write-Host "`n[6/8] Updating CORS settings..." -ForegroundColor Yellow
# CORS will be updated after SWA deployment

# Step 8: Build Frontend
Write-Host "`n[7/8] Building Frontend..." -ForegroundColor Yellow
Push-Location $PSScriptRoot\..\frontend

# Update .env.production with backend URL (preserve existing settings)
$EnvPath = ".env.production"
$EnvContent = Get-Content $EnvPath -ErrorAction SilentlyContinue
if ($EnvContent) {
  $EnvContent = ($EnvContent | Where-Object { $_ -notmatch "^VITE_API_BASE_URL=" }) -join "`n"
  $EnvContent = "VITE_API_BASE_URL=$BackendUrl`n$EnvContent"
} else {
  $EnvContent = "VITE_API_BASE_URL=$BackendUrl"
}
Set-Content -Path $EnvPath -Value $EnvContent

# Build
npm run build
Pop-Location
Write-Host "✓ Frontend built" -ForegroundColor Green

# Step 9: Deploy Static Web App
Write-Host "`n[8/8] Deploying Static Web App..." -ForegroundColor Yellow
az staticwebapp create `
    --name $SwaName `
    --resource-group $ResourceGroup `
    --location $SwaLocation `
    --sku Free `
    -o none

# Get deployment token
$DeployToken = az staticwebapp secrets list --name $SwaName --resource-group $ResourceGroup --query "properties.apiKey" -o tsv

# Deploy using SWA CLI (if available) or Azure CLI
Push-Location $PSScriptRoot\..\frontend
npx @azure/static-web-apps-cli deploy ./dist --deployment-token $DeployToken --env production
Pop-Location

$FrontendUrl = az staticwebapp show --name $SwaName --resource-group $ResourceGroup --query "defaultHostname" -o tsv
$FrontendUrl = "https://$FrontendUrl"
Write-Host "✓ Static Web App deployed: $FrontendUrl" -ForegroundColor Green

# Summary
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor White
Write-Host "Backend URL:  $BackendUrl" -ForegroundColor White
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "`nTo delete all resources:" -ForegroundColor Yellow
Write-Host "az group delete --name $ResourceGroup --yes --no-wait" -ForegroundColor Gray
