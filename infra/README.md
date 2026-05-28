# Infrastructure - Azure Deployment

## 概要

AI Security Reviewer を Azure にデプロイするためのインフラストラクチャ設定です。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure                                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────────────────┐  │
│  │  Static Web Apps │         │    Container Apps            │  │
│  │  (Frontend)      │ ──────► │    (Backend API)             │  │
│  │  Free SKU        │         │    - FastAPI                 │  │
│  │  React + Vite    │         │    - Python 3.11             │  │
│  └──────────────────┘         └──────────────────────────────┘  │
│                                          │                       │
│                               ┌──────────┴──────────┐           │
│                               │  Container Registry │           │
│                               │  Basic SKU          │           │
│                               └─────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## リソース一覧

| リソース | 名前 | SKU | リージョン |
|---------|------|-----|-----------|
| Resource Group | rg-aisecreviewer-dev | - | Japan East |
| Container Registry | craisecreviewer | Basic | Japan East |
| Container Apps Env | cae-aisecreviewer-dev | Consumption | Japan East |
| Container Apps | ca-aisecreviewer-api-dev | - | Japan East |
| Static Web Apps | swa-aisecreviewer-dev | Free | East Asia |

## デプロイ手順

### 前提条件

- Azure CLI がインストールされていること
- Azure サブスクリプションで Contributor 以上の権限があること
- Node.js 18+ がインストールされていること
- Docker がインストールされていること（ローカルビルドの場合）

### 1. Azure にログイン

```powershell
az login
az account set --subscription <subscription-id>
```

### 2. 自動デプロイ（推奨）

```powershell
cd infra
.\deploy-azure.ps1
```

### 3. 手動デプロイ

#### リソースグループ作成
```powershell
az group create --name rg-aisecreviewer-dev --location japaneast
```

#### Container Registry 作成
```powershell
az acr create --resource-group rg-aisecreviewer-dev --name craisecreviewer --sku Basic --admin-enabled true
```

#### Docker イメージビルド＆プッシュ
```powershell
cd backend
az acr build --registry craisecreviewer --image aisecreviewer-api:latest .
```

#### Container Apps Environment 作成
```powershell
az containerapp env create --name cae-aisecreviewer-dev --resource-group rg-aisecreviewer-dev --location japaneast
```

#### Container Apps デプロイ
```powershell
$ACR_PASSWORD = az acr credential show --name craisecreviewer --query "passwords[0].value" -o tsv

az containerapp create `
    --name ca-aisecreviewer-api-dev `
    --resource-group rg-aisecreviewer-dev `
    --environment cae-aisecreviewer-dev `
    --image craisecreviewer.azurecr.io/aisecreviewer-api:latest `
    --target-port 8000 `
    --ingress external `
    --registry-server craisecreviewer.azurecr.io `
    --registry-username craisecreviewer `
    --registry-password $ACR_PASSWORD `
    --cpu 0.5 --memory 1.0Gi `
    --min-replicas 1 --max-replicas 3
```

#### フロントエンドビルド
```powershell
cd frontend
# .env.production を更新（VITE_API_BASE_URL=<backend-url>）
npm run build
```

#### Static Web Apps デプロイ
```powershell
az staticwebapp create --name swa-aisecreviewer-dev --resource-group rg-aisecreviewer-dev --location eastasia --sku Free

# デプロイトークン取得
$TOKEN = az staticwebapp secrets list --name swa-aisecreviewer-dev --resource-group rg-aisecreviewer-dev --query "properties.apiKey" -o tsv

# SWA CLI でデプロイ
npx @azure/static-web-apps-cli deploy ./dist --deployment-token $TOKEN --env production
```

## クリーンアップ

すべてのリソースを削除：
```powershell
az group delete --name rg-aisecreviewer-dev --yes --no-wait
```

## コスト見積もり

| リソース | 月額目安 |
|---------|---------|
| Static Web Apps (Free) | ¥0 |
| Container Apps (Consumption) | ~¥500-2,000 |
| Container Registry (Basic) | ~¥600 |
| **合計** | **~¥1,100-2,600/月** |

※ 使用量により変動します
