# Pre-Commit Hooks Setup Guide

この document では、プロジェクトの pre-commit フレームワークをセットアップし、コード品質と セキュリティを保証する方法を説明します。

## 概要

AI Security Reviewer プロジェクトは自動化されたコミット前チェック（pre-commit hooks）を使用して、以下を実施しています：

1. **Secret Detection**: AWS キーやパスワードなどの機密情報をコミットから防止
2. **Code Quality**: ESLint (Frontend) / Ruff (Backend) での構文と style チェック
3. **File Integrity**: 末尾の EOF、trailing whitespace、YAML/JSON 構文の修正

## インストール手順

### 1. Pre-commit Framework のインストール

```bash
# Python を使用してインストール
pip install pre-commit

# または pipenv を使用している場合
pipenv install --dev pre-commit
```

### 2. Git Hooks の登録

リポジトリルートで以下を実行：

```bash
pre-commit install
```

出力例：
```
pre-commit installed at .git/hooks/pre-commit
```

## 使用方法

### 通常のコミット操作（自動実行）

```bash
git add .
git commit -m "feat: add new feature"
```

コミット時に自動的に全フックが実行されます。全てのチェックに合格すればコミットが成功します。

### 全ファイルに対してフックを手動実行

```bash
pre-commit run --all-files
```

## フック詳細

### 1. Detect Secrets (Custom)
- **目的**: AWS キー、パスワード、API キーなどの機密情報を検出
- **検出パターン**:
  - AWS Access Keys: `AKIA*` で始まる文字列
  - パスワード フィールド: `password=...`
  - API キー: `api_key=...`
  - 秘密キー: `secret=...`, `PRIVATE KEY`
- **動作**: 機密情報が検出された場合、コミットがブロックされます
- **例外**: `.git/`, `node_modules/`, `.venv/`, `docs/mockup/` ディレクトリは除外

### 2. End-of-File-Fixer
- **目的**: ファイルが空白行で終わっているか確認し、修正
- **動作**: 自動的にファイルを修正

### 3. Trim-Trailing-Whitespace
- **目的**: 行末の空白を削除
- **動作**: 自動的にファイルを修正

### 4. Check-YAML
- **目的**: YAML ファイルの構文チェック
- **動作**: 構文エラーの場合コミットをブロック

### 5. Check-JSON
- **目的**: JSON ファイルの構文チェック
- **例外**: `tsconfig.json` ファイルは除外（コメント許可）
- **動作**: 構文エラーの場合コミットをブロック

### 6. Check-Added-Large-Files
- **目的**: 5MB 以上のファイルのコミットをブロック
- **動作**: 大きいバイナリやログファイルの誤コミットを防止

### 7. Ruff (Backend)
- **目的**: Python コードの linting（Backend のみ）
- **対象**: `backend/*.py` ファイル
- **動作**: linting エラーでコミットをブロック

## トラブルシューティング

### フックの実行をスキップしたい場合

```bash
# 注意: セキュリティリスク。やむを得ない場合のみ使用
git commit --no-verify -m "commit message"
```

### 特定のフックだけ実行したい場合

```bash
pre-commit run detect-secrets --all-files
pre-commit run ruff --all-files
```

### フックのセットアップをやり直したい場合

```bash
# Hooks の再登録
pre-commit uninstall
pre-commit install
```

## Constitution との連携

このセットアップは **Constitution v1.1.0** の以下要件を実装しています：

- **Requirement**: "認証情報・顧客データ・非公開ソースのコミット禁止"
  - 実装: Detect Secrets hook による自動機密情報検出と commit ブロック
  - 効果: AWS キー、API キー、パスワードなどの誤りコミットを防止

## テスト例

### 秘密情報検出のテスト

1. ダミーシークレットを含むファイルを作成：
```bash
echo 'AWS_KEY=AKIAIOSFODNN7EXAMPLE' > test_secret.txt
```

2. コミットを試みる：
```bash
git add test_secret.txt
git commit -m "test"
```

3. 期待結果：
```
[WARNING] Secret detected in test_secret.txt: AWS Access Key ID
[ERROR] Commit blocked: Potential secrets detected
```

4. ファイルを削除してリセット：
```bash
rm test_secret.txt
git reset HEAD
```

## 参考資料

- [Pre-commit Framework Documentation](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [ESLint Documentation](https://eslint.org/)
- [Project Constitution](../../specs/001-ai-security-reviewer-spec/plan.md)
