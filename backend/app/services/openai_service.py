"""Azure OpenAI service for AI-powered security analysis."""

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()


# Security review system prompt (base)
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
- All titles, descriptions, remediation must be in Japanese
- Code snippets and code examples can be in original language
- Map findings to ASVS requirements and CWE IDs accurately
- Be thorough but realistic - only report actual vulnerabilities
- If no vulnerabilities found, return empty findings array with high scores
"""


# Depth-specific prompt hints (appended to base prompt)
DEPTH_PROMPT_HINTS = {
    "quick": """
========================================
ANALYSIS DEPTH: QUICK (HIGH SPEED MODE)
========================================

CRITICAL CONSTRAINTS - YOU MUST FOLLOW STRICTLY:
1. ONLY analyze these 3 ASVS categories: V1 (Architecture), V2 (Authentication), V5 (Validation)
2. Maximum 5 findings (ABSOLUTELY DO NOT exceed this limit)
3. Each finding description: 1-2 sentences ONLY
4. Skip MEDIUM and LOW severity unless they have critical impact
5. Focus on the most obvious, surface-level critical vulnerabilities

PERSPECTIVE SCORES (return ONLY these 3 categories):
[V1, V2, V5]

DO NOT analyze: V3, V4, V6, V7, V8, V9, V10, V11, V12, V13, V14
DO NOT return findings for those categories.

REMEMBER: This is QUICK mode - prioritize SPEED over completeness.
If you find more than 5 issues, report ONLY the top 5 most critical ones.
""",
    "standard": """
========================================
ANALYSIS DEPTH: STANDARD (BALANCED MODE)
========================================

REQUIREMENTS:
1. Analyze ASVS categories V1 through V7
2. Find 8-15 findings if vulnerabilities exist
3. Include all severity levels (CRITICAL, HIGH, MEDIUM, LOW)
4. Each finding: detailed description (3-5 sentences)
5. Include remediation guidance with code examples

PERSPECTIVE SCORES (return these 7):
[V1, V2, V3, V4, V5, V6, V7]

DO NOT analyze: V8, V9, V10, V11, V12, V13, V14

REMEMBER: This is STANDARD mode - balanced thoroughness.
Aim for 8-15 findings, not fewer.
""",
    "detailed": """
========================================
ANALYSIS DEPTH: DETAILED (EXHAUSTIVE EXPERT MODE)
========================================

MANDATORY REQUIREMENTS - ABSOLUTELY MUST FOLLOW:
1. Analyze ALL 14 ASVS categories: V1 through V14
2. **YOU MUST FIND AT LEAST 15 findings** (this is a hard requirement)
3. Consider edge cases, subtle vulnerabilities, defensive coding gaps
4. For each finding, provide:
   - Detailed attack scenario (4+ sentences explaining HOW an attacker exploits it)
   - Step-by-step exploitation example
   - Multiple remediation approaches with detailed code
   - CWE references AND business impact analysis
   - Reference links to OWASP/MITRE documentation
5. Be EXTREMELY thorough - examine every line carefully
6. Consider: race conditions, side channels, business logic flaws, timing attacks
7. Include LOW severity issues that QUICK mode would skip
8. Look for defense-in-depth gaps

PERSPECTIVE SCORES (return ALL 14 categories):
[V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11, V12, V13, V14]

CATEGORIES YOU MUST CHECK:
- V1: Architecture, Design and Threat Modeling
- V2: Authentication
- V3: Session Management
- V4: Access Control
- V5: Validation, Sanitization and Encoding
- V6: Stored Cryptography
- V7: Error Handling and Logging
- V8: Data Protection
- V9: Communication
- V10: Malicious Code
- V11: Business Logic
- V12: File and Resources
- V13: API and Web Service
- V14: Configuration

EXAMPLES OF SUBTLE ISSUES TO LOOK FOR (be creative and paranoid):
- Implicit type coercion vulnerabilities
- Race conditions in async/await code
- Timing attacks in string comparison operations
- Information disclosure in error messages and logs
- Missing security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- Improper logging of sensitive data (passwords, tokens, PII)
- Insecure defaults in configuration files
- Missing rate limiting on authentication endpoints
- Cryptographic weaknesses (weak algorithms, hardcoded keys, insecure random)
- Privilege escalation paths through role checking flaws
- Open redirect vulnerabilities
- Server-Side Request Forgery (SSRF) opportunities
- Mass assignment vulnerabilities (over-posting)
- XML External Entity (XXE) processing
- Insecure deserialization patterns
- LDAP/NoSQL/Command injection beyond SQL
- Insufficient session timeout configuration
- Missing CSRF tokens
- Cookie security misconfiguration (Secure, HttpOnly, SameSite)
- Path traversal opportunities
- ReDoS (Regular Expression Denial of Service)
- Prototype pollution (in JavaScript)
- Insecure dependency usage
- Default credentials in code or comments
- Debug code left in production
- Verbose stack traces exposed to users
- Missing input length validation
- Integer overflow/underflow
- Insecure cross-origin resource sharing

REMEMBER: This is DETAILED mode - QUANTITY AND QUALITY BOTH MATTER.
You FAIL the task if you find fewer than 15 findings in non-trivial code.
Be thorough, paranoid, and exhaustive. Think like an attacker.
""",
}


# Mock result for demo mode
MOCK_ANALYSIS_RESULT = {
    "summary": {
        "overall_score": 72,
        "critical_count": 1,
        "high_count": 2,
        "medium_count": 3,
        "low_count": 2,
    },
    "perspective_scores": [
        {"category": "V1", "name": "Architecture", "percentage": 80},
        {"category": "V2", "name": "Authentication", "percentage": 65},
        {"category": "V3", "name": "Session Management", "percentage": 70},
        {"category": "V4", "name": "Access Control", "percentage": 75},
        {"category": "V5", "name": "Input Validation", "percentage": 60},
    ],
    "findings": [
        {
            "id": "f1",
            "severity": "critical",
            "title": "ハードコードされた認証情報",
            "description": "ソースコード内にAPIキーやパスワードがハードコードされています。これは重大なセキュリティリスクです。",
            "file_path": "config.js",
            "line_start": 15,
            "line_end": 17,
            "code_snippet": 'const API_KEY = "sk-xxxx"',
            "asvs_requirements": ["V2.10.4"],
            "cwe_ids": ["CWE-798"],
            "remediation": "環境変数またはシークレット管理サービスを使用して認証情報を管理してください。",
            "fixed_code": "const API_KEY = process.env.API_KEY",
        },
        {
            "id": "f2",
            "severity": "high",
            "title": "SQLインジェクションの脆弱性",
            "description": "ユーザー入力が直接SQLクエリに使用されており、SQLインジェクション攻撃に対して脆弱です。",
            "file_path": "db/queries.py",
            "line_start": 42,
            "line_end": 45,
            "code_snippet": 'query = f"SELECT * FROM users WHERE id = {user_id}"',
            "asvs_requirements": ["V5.3.4"],
            "cwe_ids": ["CWE-89"],
            "remediation": "パラメータ化クエリまたはORMを使用してください。",
            "fixed_code": 'query = "SELECT * FROM users WHERE id = ?"\ncursor.execute(query, (user_id,))',
        },
        {
            "id": "f3",
            "severity": "high",
            "title": "XSS脆弱性",
            "description": "ユーザー入力がエスケープされずにHTMLに出力されています。",
            "file_path": "templates/user.html",
            "line_start": 28,
            "line_end": 28,
            "code_snippet": "<div>{{ user.name | safe }}</div>",
            "asvs_requirements": ["V5.3.3"],
            "cwe_ids": ["CWE-79"],
            "remediation": "safe フィルターを削除し、自動エスケープを有効にしてください。",
            "fixed_code": "<div>{{ user.name }}</div>",
        },
        {
            "id": "f4",
            "severity": "medium",
            "title": "不十分なパスワード要件",
            "description": "パスワードの複雑さに関する検証が不足しています。",
            "file_path": "auth/validators.py",
            "line_start": 12,
            "line_end": 15,
            "code_snippet": "if len(password) >= 6:\n    return True",
            "asvs_requirements": ["V2.1.1"],
            "cwe_ids": ["CWE-521"],
            "remediation": "最低8文字、大文字・小文字・数字・特殊文字を含む要件を追加してください。",
            "fixed_code": 'import re\nif len(password) >= 8 and re.search(r"[A-Z]", password) and re.search(r"[a-z]", password) and re.search(r"\\d", password):\n    return True',
        },
        {
            "id": "f5",
            "severity": "medium",
            "title": "セッションタイムアウト未設定",
            "description": "セッションの有効期限が設定されていません。",
            "file_path": "config/session.py",
            "line_start": 8,
            "line_end": 10,
            "code_snippet": "SESSION_TIMEOUT = None",
            "asvs_requirements": ["V3.3.1"],
            "cwe_ids": ["CWE-613"],
            "remediation": "適切なセッションタイムアウト(例:30分)を設定してください。",
            "fixed_code": "SESSION_TIMEOUT = 1800  # 30 minutes",
        },
        {
            "id": "f6",
            "severity": "medium",
            "title": "CORS設定が緩い",
            "description": "CORSでワイルドカード(*)が使用されており、任意のオリジンからのアクセスを許可しています。",
            "file_path": "app.py",
            "line_start": 22,
            "line_end": 25,
            "code_snippet": 'app.config["CORS_ORIGINS"] = "*"',
            "asvs_requirements": ["V14.5.3"],
            "cwe_ids": ["CWE-942"],
            "remediation": "許可するオリジンを明示的に指定してください。",
            "fixed_code": 'app.config["CORS_ORIGINS"] = ["https://example.com"]',
        },
        {
            "id": "f7",
            "severity": "low",
            "title": "詳細なエラーメッセージ",
            "description": "例外発生時にスタックトレースがユーザーに表示される可能性があります。",
            "file_path": "handlers/error.py",
            "line_start": 18,
            "line_end": 20,
            "code_snippet": "except Exception as e:\n    return str(e)",
            "asvs_requirements": ["V7.4.1"],
            "cwe_ids": ["CWE-209"],
            "remediation": "本番環境では汎用的なエラーメッセージを返し、詳細はログに記録してください。",
            "fixed_code": "except Exception as e:\n    logger.error(f'Error: {e}')\n    return 'エラーが発生しました'",
        },
        {
            "id": "f8",
            "severity": "low",
            "title": "HTTPSが強制されていない",
            "description": "HTTPからHTTPSへのリダイレクトが設定されていません。",
            "file_path": "config/security.py",
            "line_start": 5,
            "line_end": 6,
            "code_snippet": "FORCE_HTTPS = False",
            "asvs_requirements": ["V9.1.1"],
            "cwe_ids": ["CWE-319"],
            "remediation": "本番環境ではHTTPSを強制してください。",
            "fixed_code": "FORCE_HTTPS = True",
        },
    ],
}


# Depth-specific max_tokens for OpenAI API
DEPTH_MAX_TOKENS = {
    "quick": 1500,       # Short responses (5 findings max)
    "standard": 4000,    # Balanced (8-15 findings)
    "detailed": 16000,   # Large detailed responses (15+ findings)
}


# Depth-specific temperature
DEPTH_TEMPERATURE = {
    "quick": 0.1,       # Deterministic, focused on obvious issues
    "standard": 0.3,    # Balanced
    "detailed": 0.5,    # More creative, finds subtle issues
}


class OpenAIService:
    """Service for Azure OpenAI interactions."""

    def __init__(self, mock_mode: bool = False):
        """Initialize Azure OpenAI client.

        Args:
            mock_mode: If True, use mock responses instead of real API calls
        """
        self.mock_mode = mock_mode
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

        # Enable mock mode if credentials are not available
        if not self.endpoint or not self.api_key:
            self.mock_mode = True
            self.client = None
        else:
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
            )

    async def analyze_code_security(
        self,
        code_files: list[dict[str, str]],
        depth: str = "standard",
        progress_callback=None,
    ) -> dict[str, Any]:
        """Analyze code files for security vulnerabilities.

        Args:
            code_files: List of dicts with 'path' and 'content' keys
            depth: Review depth (quick/standard/detailed)
            progress_callback: Optional async callback for progress updates

        Returns:
            Structured analysis results
        """
        if progress_callback:
            await progress_callback(
                "analyzing_code",
                {
                    "message": f"GPT-4o によるセキュリティ解析を開始 [{depth}]...",
                },
            )

        # Use mock mode if enabled
        if self.mock_mode:
            return await self._mock_analyze(code_files, depth, progress_callback)

        # Build depth-aware system prompt
        depth_hint = DEPTH_PROMPT_HINTS.get(depth, DEPTH_PROMPT_HINTS["standard"])
        system_prompt = SECURITY_REVIEW_PROMPT + "\n" + depth_hint

        # Get depth-specific settings
        max_tokens = DEPTH_MAX_TOKENS.get(depth, 4000)
        temperature = DEPTH_TEMPERATURE.get(depth, 0.3)

        # Build code content for analysis
        code_content = self._format_code_for_analysis(code_files)

        if progress_callback:
            await progress_callback(
                "agent_progress",
                {
                    "agent_name": "SpecComplianceAgent",
                    "status": "running",
                    "progress_percent": 30,
                    "message": f"OWASP ASVS カテゴリを評価中 [{depth}] (max_tokens={max_tokens}, temp={temperature})...",
                },
            )

        # Call Azure OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": code_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
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

            # Log findings count for verification
            findings_count = len(result.get("findings", []))
            if progress_callback:
                await progress_callback(
                    "agent_progress",
                    {
                        "agent_name": "SpecComplianceAgent",
                        "status": "completed",
                        "progress_percent": 100,
                        "message": f"解析完了 [{depth}] ({findings_count} findings)",
                    },
                )

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI API error: {e}") from e

    def _format_code_for_analysis(self, code_files: list[dict[str, str]]) -> str:
        """Format code files for AI analysis prompt."""
        parts = [
            "Please analyze the following code files for security vulnerabilities:\n"
        ]

        for file in code_files:
            parts.append(f"\n--- File: {file['path']} ---\n")
            parts.append(file["content"])
            parts.append("\n")

        parts.append(
            "\nAnalyze all files above and provide a comprehensive security review."
        )

        return "".join(parts)

    async def _mock_analyze(
        self,
        code_files: list[dict[str, str]],
        depth: str = "standard",
        progress_callback=None,
    ) -> dict[str, Any]:
        """Return mock analysis results for demo purposes.

        Args:
            code_files: List of code files (used to update file paths)
            depth: Review depth (affects number of findings returned)
            progress_callback: Optional progress callback
        """
        import asyncio
        import copy

        # Simulate processing time
        if progress_callback:
            await progress_callback(
                "agent_progress",
                {
                    "agent_name": "SpecComplianceAgent",
                    "status": "running",
                    "progress_percent": 20,
                    "message": f"[デモモード/{depth}] OWASP ASVS カテゴリを評価中...",
                },
            )

        await asyncio.sleep(1)

        if progress_callback:
            await progress_callback(
                "agent_progress",
                {
                    "agent_name": "SpecComplianceAgent",
                    "status": "running",
                    "progress_percent": 50,
                    "message": f"[デモモード/{depth}] 脆弱性パターンを検出中...",
                },
            )

        await asyncio.sleep(1)

        if progress_callback:
            await progress_callback(
                "agent_progress",
                {
                    "agent_name": "SpecComplianceAgent",
                    "status": "running",
                    "progress_percent": 80,
                    "message": f"[デモモード/{depth}] 解析結果を処理中...",
                },
            )

        await asyncio.sleep(0.5)

        # Create a copy of mock result
        result = copy.deepcopy(MOCK_ANALYSIS_RESULT)

        # Filter findings by depth (mock behavior)
        depth_finding_limits = {
            "quick": 3,       # Only top 3 critical/high
            "standard": 6,    # Mid-range
            "detailed": 8,    # All findings
        }
        max_findings = depth_finding_limits.get(depth, 6)
        result["findings"] = result["findings"][:max_findings]

        # Recalculate counts based on filtered findings
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in result["findings"]:
            sev = f.get("severity", "low")
            if sev in counts:
                counts[sev] += 1

        result["summary"]["critical_count"] = counts["critical"]
        result["summary"]["high_count"] = counts["high"]
        result["summary"]["medium_count"] = counts["medium"]
        result["summary"]["low_count"] = counts["low"]

        # Update file paths to match actual files if available
        if code_files:
            for i, finding in enumerate(result["findings"]):
                if i < len(code_files):
                    finding["file_path"] = code_files[i % len(code_files)]["path"]

        if progress_callback:
            await progress_callback(
                "agent_progress",
                {
                    "agent_name": "SpecComplianceAgent",
                    "status": "completed",
                    "progress_percent": 100,
                    "message": f"[デモモード/{depth}] 解析完了 ({len(result['findings'])} findings)",
                },
            )

        return result

    async def quick_test(self) -> bool:
        """Quick test to verify API connection."""
        if self.mock_mode:
            return True
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
