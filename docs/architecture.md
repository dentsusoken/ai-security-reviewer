# アーキテクチャ図

> **アプリ名**: AI Security Reviewer
> **アプリ概要**: GitHubリポジトリのソースコードをAIエージェントが自動でセキュリティレビューし、OWASP ASVS準拠のレポートを生成するWebサービス
> **ハッカソン名**: Microsoft AI Hackathon 2026

## システム構成

```mermaid
flowchart LR
    subgraph User["👤 User"]
        U[🧑‍💻 開発者]
    end

    subgraph Azure["☁️ Azure Subscription"]
        subgraph Frontend["🌐 Frontend Layer"]
            SWA[🌍 Azure Static Web Apps<br/>React + TypeScript + Vite]
        end

        subgraph Backend["⚙️ Backend / API Layer"]
            CAE[📦 Container Apps Environment]
            CA[🐳 Azure Container Apps<br/>FastAPI + Python 3.11]
            ACR[🗄️ Azure Container Registry]
        end

        subgraph AI["🤖 AI Services Layer"]
            AOAI[🧠 Azure OpenAI Service<br/>GPT-4o]
            AGENT[🔍 SpecComplianceAgent<br/>OWASP ASVS解析]
        end

        subgraph Data["💾 Data Layer"]
            GITHUB[🐙 GitHub API<br/>リポジトリ取得]
            MEMORY[💿 In-Memory Store<br/>レビュー状態管理]
        end

        subgraph Security["🔐 Security & Identity"]
            ENTRA[🔑 Microsoft Entra ID<br/>MSAL認証]
        end

        subgraph Monitoring["📊 Monitoring & Ops"]
            LOG[📈 Log Analytics<br/>Workspace]
        end
    end

    U -->|①ログイン| ENTRA
    ENTRA -->|トークン発行| SWA
    U -->|②レビュー依頼| SWA
    SWA -->|③API呼出| CA
    CA -->|④コード取得| GITHUB
    CA -->|⑤セキュリティ解析| AGENT
    AGENT -->|AI推論| AOAI
    CA -->|⑥状態保存| MEMORY
    CA -->|⑦SSE進捗通知| SWA
    SWA -->|⑧結果表示| U
    ACR -->|イメージ配信| CA
    CA -->|ログ送信| LOG

    classDef frontend fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    classDef backend fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    classDef ai fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px
    classDef data fill:#FFF3E0,stroke:#F57C00,stroke-width:2px
    classDef security fill:#FFEBEE,stroke:#C62828,stroke-width:2px
    classDef monitoring fill:#FFFDE7,stroke:#F9A825,stroke-width:2px

    class SWA frontend
    class CA,CAE,ACR backend
    class AOAI,AGENT ai
    class GITHUB,MEMORY data
    class ENTRA security
    class LOG monitoring
```

## 各コンポーネントの役割

| サービス | 役割 |
|----------|------|
| 🌍 Azure Static Web Apps | React SPAのホスティング。グローバルCDN配信、自動HTTPS |
| 🐳 Azure Container Apps | FastAPI バックエンドのサーバーレスコンテナ実行。オートスケール対応 |
| 🗄️ Azure Container Registry | Dockerイメージの格納・配信。ACR Buildでクラウドビルド |
| 🧠 Azure OpenAI Service | GPT-4oモデルによるコードセキュリティ解析・脆弱性検出 |
| 🔍 SpecComplianceAgent | OWASP ASVS基準に基づくセキュリティ評価を実行するAIエージェント |
| 🐙 GitHub API | 指定リポジトリからソースコードを取得 |
| 💿 In-Memory Store | レビューセッションの状態・進捗・結果を一時保存（MVP用） |
| 🔑 Microsoft Entra ID | OAuth2/OIDCによるユーザー認証。MSAL.jsでSPA連携 |
| 📈 Log Analytics Workspace | Container Appsのログ収集・監視 |

## 技術スタック詳細

### フロントエンド
| 技術 | バージョン | 用途 |
|------|-----------|------|
| React | 19.x | UIフレームワーク |
| TypeScript | 6.x | 型安全なJavaScript |
| Vite | 8.x | 高速ビルドツール |
| Tailwind CSS | 3.x | ユーティリティファーストCSS |
| MSAL React | 5.x | Azure AD認証ライブラリ |
| React Router | 7.x | SPAルーティング |

### バックエンド
| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11 | 実行環境 |
| FastAPI | latest | REST API フレームワーク |
| Uvicorn | latest | ASGIサーバー |
| Azure OpenAI SDK | 1.x | GPT-4o API連携 |
| SSE-Starlette | latest | Server-Sent Events |
| OpenPyXL | 3.x | Excelレポート生成 |

## データフロー

1. **ユーザー認証**: 開発者がMicrosoft Entra IDでログイン、MSALがアクセストークンを取得
2. **レビュー依頼**: フロントエンドからGitHubリポジトリURLを指定してレビューをリクエスト
3. **コード取得**: バックエンドがGitHub APIを使用してリポジトリのソースコードを取得
4. **AI解析**: SpecComplianceAgentがAzure OpenAI (GPT-4o)を使用してOWASP ASVS基準でセキュリティ解析を実行
5. **進捗通知**: 解析の進捗状況をSSE (Server-Sent Events)でリアルタイムにフロントエンドへ配信
6. **結果表示**: 脆弱性の検出結果、重要度分類、修正提案をダッシュボードに表示
7. **レポート出力**: Excel形式でのレビュー結果エクスポートが可能

## デプロイ構成

| リソース | 名前 | リージョン | SKU |
|----------|------|-----------|-----|
| Resource Group | rg-aisecreviewer-dev | Japan East | - |
| Static Web Apps | swa-aisecreviewer-dev | East Asia | Free |
| Container Apps | ca-aisecreviewer-api-dev | Japan East | Consumption |
| Container Registry | craisecreviewer | Japan East | Basic |
| OpenAI Service | oai-aisecreviewer-dev | Japan East | S0 |
| Log Analytics | workspace-* | Japan East | - |

## 将来の拡張予定

```mermaid
flowchart LR
    subgraph Planned["🔮 計画中のサービス"]
        COSMOS[🗃️ Cosmos DB<br/>レビュー履歴永続化]
        BLOB[📁 Blob Storage<br/>レポート保存]
        KV[🔒 Key Vault<br/>シークレット管理]
        SEARCH[🔎 AI Search<br/>ASVS RAG検索]
        SEMGREP[🛡️ Azure Functions<br/>Semgrep SAST]
        ZAP[⚡ Container Apps Jobs<br/>ZAP DAST]
    end

    style Planned fill:#F5F5F5,stroke:#9E9E9E,stroke-dasharray: 5 5
```

| 計画サービス | 目的 |
|-------------|------|
| Azure Cosmos DB | レビュー履歴・指摘事項の永続化 |
| Azure Blob Storage | PDF/Excelレポートの保存 |
| Azure Key Vault | APIキー・シークレットの安全な管理 |
| Azure AI Search | ASVS要件のRAG検索 |
| Azure Functions | Semgrep静的解析の実行 |
| Container Apps Jobs | ZAP動的スキャンの実行 |
