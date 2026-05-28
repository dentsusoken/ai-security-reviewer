# Entra ID (Azure AD) Setup Guide

本ドキュメントでは、AI Security Reviewer のEntra ID認証設定手順を説明します。

## 前提条件

- Azure サブスクリプションへのアクセス
- Entra ID (Azure AD) テナントの管理者権限
- Azure CLI がインストール済み

## 1. アプリ登録の作成

### Azure Portal での手順

1. [Azure Portal](https://portal.azure.com) にサインイン
2. **Microsoft Entra ID** > **アプリの登録** > **新規登録**
3. 以下の設定で登録:

| 項目 | 値 |
|------|-----|
| 名前 | `AI Security Reviewer` |
| サポートされているアカウントの種類 | この組織ディレクトリのみに含まれるアカウント |
| リダイレクト URI (種類) | シングルページ アプリケーション (SPA) |
| リダイレクト URI (URL) | `http://localhost:5173` (開発用) |

### Azure CLI での手順

```bash
# ログイン
az login

# アプリ登録の作成
az ad app create \
  --display-name "AI Security Reviewer" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "http://localhost:5173" \
  --enable-access-token-issuance true \
  --enable-id-token-issuance true
```

## 2. 追加のリダイレクト URI 設定

本番環境用のリダイレクト URI を追加:

1. **認証** > **プラットフォームの追加** > **シングルページ アプリケーション**
2. 以下の URI を追加:
   - `https://<your-static-web-app>.azurestaticapps.net` (Azure SWA)
   - `http://localhost:3000` (代替開発ポート)

## 3. API スコープの公開

バックエンド API にアクセスするためのスコープを設定:

1. **API の公開** > **アプリケーション ID URI の設定**
   - 形式: `api://<client-id>`

2. **スコープの追加**:

| スコープ名 | 表示名 | 説明 | 同意 |
|-----------|--------|------|------|
| `access_as_user` | Access as user | API へのアクセス | 管理者とユーザー |

## 4. 必要な環境変数

### フロントエンド (.env)

```env
VITE_AZURE_CLIENT_ID=<アプリケーション (クライアント) ID>
VITE_AZURE_TENANT_ID=<ディレクトリ (テナント) ID>
VITE_AZURE_REDIRECT_URI=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

### バックエンド (.env)

```env
AZURE_CLIENT_ID=<アプリケーション (クライアント) ID>
AZURE_TENANT_ID=<ディレクトリ (テナント) ID>
AUTH_DISABLED=false
```

## 5. トークン検証の設定

バックエンドでは以下の検証を実施:

- **発行者 (iss)**: `https://login.microsoftonline.com/<tenant-id>/v2.0`
- **対象者 (aud)**: `<client-id>` または `api://<client-id>`
- **署名**: Microsoft の公開キーで検証

## 6. 開発モード

開発時は `AUTH_DISABLED=true` を設定することで、認証をスキップできます:

```env
AUTH_DISABLED=true
```

この場合、すべてのリクエストは以下のモックユーザーとして処理されます:
- User ID: `dev-user-001`
- Email: `dev@example.com`
- Name: 開発ユーザー

## 7. トラブルシューティング

### CORS エラー

バックエンドの `CORS_ORIGINS` にフロントエンドの URL が含まれていることを確認:

```python
cors_origins = [
    "http://localhost:5173",
    "https://your-app.azurestaticapps.net",
]
```

### トークン取得エラー

1. リダイレクト URI が正確に一致しているか確認
2. アプリ登録で「暗黙のフロー」が有効か確認
3. ブラウザのコンソールでエラー詳細を確認

### 401 Unauthorized

1. トークンの有効期限を確認
2. `aud` クレームが正しいか確認
3. バックエンドログで詳細なエラーを確認

## 8. セキュリティベストプラクティス

1. **本番環境では認証を無効にしない**
2. **クライアントシークレットをフロントエンドに含めない** (SPAはパブリッククライアント)
3. **最小権限の原則を適用**
4. **定期的にアプリ登録の設定を監査**

## 参考リンク

- [Microsoft identity platform documentation](https://docs.microsoft.com/azure/active-directory/develop/)
- [MSAL.js documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [Azure Static Web Apps authentication](https://docs.microsoft.com/azure/static-web-apps/authentication-authorization)
