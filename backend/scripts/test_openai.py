#!/usr/bin/env python3
"""
Azure OpenAI Service 動作確認スクリプト

使用方法:
    cd backend
    python scripts/test_openai.py
"""

import os
import sys
from pathlib import Path

# backend ディレクトリを Python パスに追加
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from openai import AzureOpenAI

# .env ファイルを読み込み
load_dotenv(backend_dir / ".env")


def main():
    """GPT-4o との接続テスト"""

    # 環境変数を取得
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    # 設定値の確認
    print("=" * 50)
    print("Azure OpenAI 接続テスト")
    print("=" * 50)
    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment_name}")
    print(f"API Version: {api_version}")
    print("=" * 50)

    if not endpoint or not api_key:
        print("❌ エラー: AZURE_OPENAI_ENDPOINT または AZURE_OPENAI_API_KEY が設定されていません")
        print("backend/.env ファイルを確認してください")
        sys.exit(1)

    # Azure OpenAI クライアントを初期化
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )

    # テストメッセージを送信
    print("\n📤 テストメッセージを送信: 'Hello'")
    print("-" * 50)

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=100,
            temperature=0.7,
        )

        # 応答を表示
        message = response.choices[0].message.content
        print(f"📥 GPT-4o からの応答:\n{message}")
        print("-" * 50)
        print(f"✅ 接続テスト成功!")
        print(f"   モデル: {response.model}")
        print(f"   使用トークン: {response.usage.total_tokens}")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
