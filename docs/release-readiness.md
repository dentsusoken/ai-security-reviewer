# リリース準備チェックリスト

## 認証 & セキュリティ
- [x] MSAL redirect フロー実装
- [x] JWT ミドルウェア（backend）
- [x] 入力ガードミドルウェア
- [x] CORS設定
- [x] Azure Entra ID SPA プラットフォーム登録

## バックエンド API
- [x] レビュー作成 (GitHub / Code)
- [x] SSE 進捗ストリーミング
- [x] 結果取得 & Finding一覧
- [x] 再実行 (rerun) エンドポイント
- [x] デモモード（モックデータ）
- [x] ASVS SpecComplianceAgent
- [x] SAST SastAnalysisAgent + Semgrep統合
- [x] Finding取り込みパイプライン
- [x] Cosmos DB リポジトリ層

## フロントエンド
- [x] ランディングページ
- [x] 新規レビューページ（GitHub / Code / URL入力）
- [x] パースペクティブ選択 (ASVS / SAST / DAST)
- [x] 進捗ページ（SSE連携）
- [x] 結果ページ & Finding詳細
- [x] ダッシュボード
- [x] 履歴ページ
- [x] 再レビューモーダル
- [x] Excel エクスポート
- [x] ダーク/ライトテーマ切替

## インフラ (IaC)
- [x] Azure Container Apps (backend)
- [x] Azure Static Web Apps (frontend)
- [x] Cosmos DB
- [x] Key Vault
- [x] Azure OpenAI
- [x] Application Insights
- [x] AI Search Bicep モジュール
- [x] AI Foundry Agent Bicep モジュール
- [x] deploy-azure.ps1 デプロイスクリプト

## テスト
- [x] API 統合テスト (pytest)
- [x] E2E テスト (Playwright)
- [ ] ユニットテスト拡充（必要に応じて）

## 未完了（P3 / 将来対応）
- [ ] ZAP 動的スキャン (T062-T065) - URL所有確認 + ZAPクライアント
- [ ] Playwright テスト実行 & CI統合
- [ ] 負荷テスト
