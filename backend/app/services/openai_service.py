"""Azure OpenAI service for AI-powered security analysis."""

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()


# Security review system prompt
SECURITY_REVIEW_PROMPT = """
You are a senior security engineer expert in OWASP ASVS standards.
Analyze the provided source code for security vulnerabilities.

Respond ONLY with valid JSON in this exact format:
{
  "summary": {
    "overall_score": <0-100>,
    "critical_count": <int>,
    "high_count": <int>,
    "medium_count": <int>,
    "low_count": <int>
  },
  "perspective_scores": [
    {"category": "V1", "name": "Architecture", "percentage": <0-100>},
    {"category": "V2", "name": "Authentication", "percentage": <0-100>},
    {"category": "V3", "name": "Session Management", "percentage": <0-100>},
    {"category": "V4", "name": "Access Control", "percentage": <0-100>},
    {"category": "V5", "name": "Input Validation", "percentage": <0-100>}
  ],
  "findings": [
    {
      "id": "f1",
      "severity": "critical|high|medium|low",
      "title": "Concise title in Japanese",
      "description": "Detailed explanation in Japanese",
      "file_path": "path/to/file.js",
      "line_start": 42,
      "line_end": 45,
      "code_snippet": "vulnerable code",
      "asvs_requirements": ["V5.3.4"],
      "cwe_ids": ["CWE-89"],
      "remediation": "How to fix in Japanese",
      "fixed_code": "corrected code example"
    }
  ]
}

IMPORTANT:
- Find at least 3 findings if any vulnerabilities exist
- All titles, descriptions, remediation must be in Japanese
- Code snippets and code examples can be in original language
- Map findings to ASVS requirements and CWE IDs accurately
- Be thorough but realistic - only report actual vulnerabilities
- If no vulnerabilities found, return empty findings array with high scores
"""


class OpenAIService:
    """Service for Azure OpenAI interactions."""

    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure OpenAI credentials not configured. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env"
            )

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    async def analyze_code_security(
        self,
        code_files: list[dict[str, str]],
        progress_callback=None,
    ) -> dict[str, Any]:
        """Analyze code files for security vulnerabilities.

        Args:
            code_files: List of dicts with 'path' and 'content' keys
            progress_callback: Optional async callback for progress updates

        Returns:
            Structured analysis results
        """
        if progress_callback:
            await progress_callback(
                "analyzing_code",
                {
                    "message": "GPT-4o によるセキュリティ解析を開始...",
                },
            )

        # Build code content for analysis
        code_content = self._format_code_for_analysis(code_files)

        if progress_callback:
            await progress_callback(
                "agent_progress",
                {
                    "agent_name": "SpecComplianceAgent",
                    "status": "running",
                    "progress_percent": 30,
                    "message": "OWASP ASVS カテゴリを評価中...",
                },
            )

        # Call Azure OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": SECURITY_REVIEW_PROMPT},
                    {"role": "user", "content": code_content},
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )

            if progress_callback:
                await progress_callback(
                    "agent_progress",
                    {
                        "agent_name": "SpecComplianceAgent",
                        "status": "running",
                        "progress_percent": 80,
                        "message": "解析結果を処理中...",
                    },
                )

            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)

            if progress_callback:
                await progress_callback(
                    "agent_progress",
                    {
                        "agent_name": "SpecComplianceAgent",
                        "status": "completed",
                        "progress_percent": 100,
                        "message": "解析完了",
                    },
                )

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI API error: {e}") from e

    def _format_code_for_analysis(self, code_files: list[dict[str, str]]) -> str:
        """Format code files for AI analysis prompt."""
        parts = ["Please analyze the following code files for security vulnerabilities:\n"]

        for file in code_files:
            parts.append(f"\n--- File: {file['path']} ---\n")
            parts.append(file["content"])
            parts.append("\n")

        parts.append("\nAnalyze all files above and provide a comprehensive security review.")

        return "".join(parts)

    async def quick_test(self) -> bool:
        """Quick test to verify API connection."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "user", "content": "Say 'OK' if you can hear me."},
                ],
                max_tokens=10,
            )
            return "OK" in response.choices[0].message.content.upper()
        except Exception:
            return False


# Singleton instance
_openai_service: OpenAIService | None = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service singleton."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
