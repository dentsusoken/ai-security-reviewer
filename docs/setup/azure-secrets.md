# Azure Setup Guide - AI Security Reviewer

## GitHub Secrets Configuration

Add the following secrets to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Value |
|------------|-------|
| `AZURE_CREDENTIALS` | See JSON below |
| `AZURE_TENANT_ID` | `8f3313f1-9097-4b77-b87f-3fa8f097e0dc` |
| `AZURE_CLIENT_ID` | `66d3536c-fdd4-45df-91ab-c94e947c4018` |
| `SWA_DEPLOYMENT_TOKEN` | Get from Azure Portal after first deploy |

### AZURE_CREDENTIALS JSON

```json
{
  "clientId": "0cd68eb1-c806-42a0-be5e-4870c35a3146",
  "clientSecret": "*** REDACTED - Check terminal output ***",
  "subscriptionId": "063b10f6-e9bc-48c1-af62-61028897f1c2",
  "tenantId": "8f3313f1-9097-4b77-b87f-3fa8f097e0dc"
}
```

## Entra ID App Registration

- **App Name**: AI Security Reviewer
- **Application (client) ID**: `66d3536c-fdd4-45df-91ab-c94e947c4018`
- **Directory (tenant) ID**: `8f3313f1-9097-4b77-b87f-3fa8f097e0dc`
- **Application ID URI**: `api://66d3536c-fdd4-45df-91ab-c94e947c4018`

### Configured Redirect URIs
- http://localhost:5173
- http://localhost:5174
- https://lively-rock-0490c3d00.7.azurestaticapps.net

## Frontend Environment Variables

Create `frontend/.env.local`:
```env
VITE_AZURE_CLIENT_ID=66d3536c-fdd4-45df-91ab-c94e947c4018
VITE_AZURE_TENANT_ID=8f3313f1-9097-4b77-b87f-3fa8f097e0dc
VITE_AZURE_REDIRECT_URI=http://localhost:5174
VITE_API_BASE_URL=http://localhost:8000
```

## Manual Deployment

```powershell
# Deploy infrastructure
cd infra
az deployment group create \
  --resource-group rg-aisecreviewer-dev \
  --template-file main.bicep \
  --parameters parameters/dev.bicepparam

# Build and push backend image
cd ../backend
az acr build --registry craisecreviewerdev --image aisecreviewer-api:latest .

# Get SWA deployment token
az staticwebapp secrets list --name swa-aisecreviewer-dev --query "properties.apiKey" -o tsv
```

---
Generated: 2026-05-28
