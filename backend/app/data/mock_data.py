"""Mock data for development and testing.

Data values match the mockup HTML for consistency.
"""

from datetime import datetime, timedelta, timezone

# Demo review session IDs
DEMO_REVIEW_ID = "rs_demo_001"
DEMO_REVIEW_ID_2 = "rs_demo_002"
DEMO_REVIEW_ID_3 = "rs_demo_003"

# Demo timestamps
NOW = datetime.now(timezone.utc)

# ============================================================
# Review Sessions
# ============================================================

MOCK_REVIEWS = {
    DEMO_REVIEW_ID: {
        "id": DEMO_REVIEW_ID,
        "status": "completed",
        "inputType": "github",
        "repoUrl": "https://github.com/example/my-bi-tool",
        "branch": "main",
        "perspectives": ["asvs", "sast"],
        "depth": "standard",
        "startedAt": (NOW - timedelta(hours=1)).isoformat(),
        "completedAt": (NOW - timedelta(hours=1) + timedelta(minutes=5, seconds=12)).isoformat(),
        "durationMs": 312000,  # 5分12秒
        "scoreSummary": {
            "overall": 62,
            "critical": 2,
            "high": 5,
            "medium": 12,
            "low": 8,
        },
        "perspectiveScores": [
            {"category": "V1 アーキテクチャ", "percentage": 85},
            {"category": "V2 認証", "percentage": 45},
            {"category": "V3 セッション管理", "percentage": 90},
            {"category": "V4 アクセス制御", "percentage": 60},
            {"category": "V5 入力検証・エンコーディング", "percentage": 30},
            {"category": "V6 暗号化", "percentage": 75},
            {"category": "V7 エラー処理", "percentage": 55},
            {"category": "V8 データ保護", "percentage": 80},
            {"category": "V9 通信", "percentage": 92},
            {"category": "V10 悪性コード", "percentage": 88},
            {"category": "V11 ビジネスロジック", "percentage": 70},
            {"category": "V12 ファイル", "percentage": 65},
            {"category": "V13 API", "percentage": 50},
            {"category": "V14 設定", "percentage": 82},
        ],
    },
    DEMO_REVIEW_ID_2: {
        "id": DEMO_REVIEW_ID_2,
        "status": "completed",
        "inputType": "github",
        "repoUrl": "https://github.com/example/my-bi-tool",
        "branch": "main",
        "perspectives": ["asvs", "sast", "dast"],
        "depth": "detailed",
        "startedAt": (NOW - timedelta(hours=2)).isoformat(),
        "completedAt": (NOW - timedelta(hours=2) + timedelta(minutes=4, seconds=58)).isoformat(),
        "durationMs": 298000,  # 4分58秒
        "scoreSummary": {
            "overall": 45,
            "critical": 4,
            "high": 8,
            "medium": 15,
            "low": 6,
        },
        "perspectiveScores": [
            {"category": "V1 アーキテクチャ", "percentage": 60},
            {"category": "V2 認証", "percentage": 35},
            {"category": "V3 セッション管理", "percentage": 55},
            {"category": "V4 アクセス制御", "percentage": 40},
            {"category": "V5 入力検証・エンコーディング", "percentage": 25},
        ],
    },
    DEMO_REVIEW_ID_3: {
        "id": DEMO_REVIEW_ID_3,
        "status": "completed",
        "inputType": "github",
        "repoUrl": "https://github.com/example/sample-api",
        "branch": "develop",
        "perspectives": ["asvs", "sast"],
        "depth": "standard",
        "startedAt": (NOW - timedelta(hours=3)).isoformat(),
        "completedAt": (NOW - timedelta(hours=3) + timedelta(minutes=6, seconds=30)).isoformat(),
        "durationMs": 390000,  # 6分30秒
        "scoreSummary": {
            "overall": 78,
            "critical": 0,
            "high": 3,
            "medium": 8,
            "low": 5,
        },
        "perspectiveScores": [
            {"category": "V1 アーキテクチャ", "percentage": 90},
            {"category": "V2 認証", "percentage": 75},
            {"category": "V3 セッション管理", "percentage": 85},
            {"category": "V4 アクセス制御", "percentage": 70},
            {"category": "V5 入力検証・エンコーディング", "percentage": 65},
        ],
    },
}

# ============================================================
# Findings
# ============================================================

MOCK_FINDINGS = {
    "f1": {
        "id": "f1",
        "reviewSessionId": DEMO_REVIEW_ID,
        "severity": "critical",
        "title": "SQLインジェクションの可能性",
        "description": "ユーザー入力を直接SQL文字列に連結しているため、攻撃者が任意のSQLを実行できる状態です。",
        "filePath": "src/api/users.js",
        "lineStart": 42,
        "lineEnd": 46,
        "detectedCode": """40 app.get('/users/:id', (req, res) => {
41   const id = req.params.id;
42   const query = `SELECT * FROM users
43     WHERE id = ${id}`;  // ⚠ 危険
44   db.query(query, (err, rows) => {
45     res.json(rows);
46   });
47 });""",
        "fixSuggestion": """40 app.get('/users/:id', (req, res) => {
41   const id = req.params.id;
42   const query = 'SELECT * FROM users WHERE id = ?';
43   db.query(query, [id], (err, rows) => {
44     res.json(rows);
45   });
46 });""",
        "aiExplanation": "ユーザー入力を直接SQL文字列に連結しているため、攻撃者が任意のSQLを実行できる状態です。パラメータ化クエリで防止できます。",
        "agentSource": "SastAnalysisAgent",
        "asvsRequirementIds": ["V5.3.4"],
        "cweIds": ["CWE-89"],
        "resolutionState": "open",
        "references": [
            {
                "title": "OWASP: SQL Injection Prevention Cheat Sheet",
                "url": "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
            },
            {
                "title": "OWASP ASVS V5.3.4 詳細",
                "url": "https://owasp.org/www-project-application-security-verification-standard/",
            },
        ],
    },
    "f2": {
        "id": "f2",
        "reviewSessionId": DEMO_REVIEW_ID,
        "severity": "critical",
        "title": "ハードコードされた認証情報",
        "description": "データベース接続情報がソースコードにハードコードされています。",
        "filePath": "src/config/db.js",
        "lineStart": 8,
        "lineEnd": 12,
        "detectedCode": """8 const dbConfig = {
9   host: 'localhost',
10   user: 'admin',
11   password: 'password123',  // ⚠ 危険
12   database: 'myapp'
13 };""",
        "fixSuggestion": """8 const dbConfig = {
9   host: process.env.DB_HOST,
10   user: process.env.DB_USER,
11   password: process.env.DB_PASSWORD,
12   database: process.env.DB_NAME
13 };""",
        "aiExplanation": "認証情報をソースコードに直接記載すると、リポジトリ漏洩時にシステムが侵害されます。環境変数やシークレット管理サービスを使用してください。",
        "agentSource": "SastAnalysisAgent",
        "asvsRequirementIds": ["V2.10.4"],
        "cweIds": ["CWE-798"],
        "resolutionState": "open",
        "references": [
            {
                "title": "OWASP: Password Storage Cheat Sheet",
                "url": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html",
            },
        ],
    },
    "f3": {
        "id": "f3",
        "reviewSessionId": DEMO_REVIEW_ID,
        "severity": "high",
        "title": "CSRF対策が未実装",
        "description": "状態変更を伴うAPIエンドポイントにCSRFトークン検証がありません。",
        "filePath": "src/api/index.js",
        "lineStart": None,
        "lineEnd": None,
        "detectedCode": """app.post('/api/users', (req, res) => {
  // No CSRF token validation
  createUser(req.body);
  res.json({ success: true });
});""",
        "fixSuggestion": """import csrf from 'csurf';
const csrfProtection = csrf({ cookie: true });

app.post('/api/users', csrfProtection, (req, res) => {
  createUser(req.body);
  res.json({ success: true });
});""",
        "aiExplanation": "CSRFトークンなしで状態変更APIを公開すると、悪意のあるサイトからユーザーを騙してリクエストを送信される可能性があります。",
        "agentSource": "SpecComplianceAgent",
        "asvsRequirementIds": ["V4.2.2"],
        "cweIds": ["CWE-352"],
        "resolutionState": "open",
        "references": [
            {
                "title": "OWASP: CSRF Prevention Cheat Sheet",
                "url": "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
            },
        ],
    },
    "f4": {
        "id": "f4",
        "reviewSessionId": DEMO_REVIEW_ID,
        "severity": "high",
        "title": "XSSの可能性（出力エスケープ漏れ）",
        "description": "ユーザー入力をHTMLに直接埋め込んでおり、XSS攻撃に脆弱です。",
        "filePath": "src/components/Dashboard.jsx",
        "lineStart": 115,
        "lineEnd": 117,
        "detectedCode": """115 <div
116   dangerouslySetInnerHTML={{ __html: userComment }}
117 />""",
        "fixSuggestion": """115 import DOMPurify from 'dompurify';
116 <div
117   dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userComment) }}
118 />""",
        "aiExplanation": "dangerouslySetInnerHTMLを使用する際は、必ずサニタイズ処理を行ってください。DOMPurifyなどのライブラリを使用することを推奨します。",
        "agentSource": "SastAnalysisAgent",
        "asvsRequirementIds": ["V5.3.3"],
        "cweIds": ["CWE-79"],
        "resolutionState": "open",
        "references": [
            {
                "title": "OWASP: XSS Prevention Cheat Sheet",
                "url": "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
            },
        ],
    },
    "f5": {
        "id": "f5",
        "reviewSessionId": DEMO_REVIEW_ID,
        "severity": "medium",
        "title": "不適切なエラーハンドリング",
        "description": "エラーメッセージにスタックトレースが含まれており、内部情報が漏洩する可能性があります。",
        "filePath": "src/api/middleware.js",
        "lineStart": 23,
        "lineEnd": 26,
        "detectedCode": """23 app.use((err, req, res, next) => {
24   console.error(err.stack);
25   res.status(500).json({ error: err.stack });  // ⚠ 情報漏洩
26 });""",
        "fixSuggestion": """23 app.use((err, req, res, next) => {
24   console.error(err.stack);
25   res.status(500).json({
26     error: 'Internal Server Error',
27     requestId: req.id
28   });
29 });""",
        "aiExplanation": "スタックトレースには内部実装の詳細が含まれており、攻撃者に有用な情報を与えてしまいます。本番環境では一般的なエラーメッセージのみを返してください。",
        "agentSource": "SpecComplianceAgent",
        "asvsRequirementIds": ["V7.4.1"],
        "cweIds": ["CWE-209"],
        "resolutionState": "open",
        "references": [
            {
                "title": "OWASP: Error Handling Cheat Sheet",
                "url": "https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html",
            },
        ],
    },
}

# Findings list for the demo review
MOCK_FINDINGS_LIST = [
    {
        "id": f["id"],
        "severity": f["severity"],
        "title": f["title"],
        "filePath": f["filePath"],
        "lineStart": f["lineStart"],
        "asvsRequirementIds": f["asvsRequirementIds"],
        "cweIds": f["cweIds"],
    }
    for f in MOCK_FINDINGS.values()
]

# ============================================================
# Agent States for Progress Simulation
# ============================================================

MOCK_AGENT_STATES = [
    {
        "agentName": "SpecComplianceAgent",
        "status": "completed",
        "progressPercent": 100,
        "currentActivity": "OWASP ASVS 14カテゴリを評価",
        "details": ["🔴 2", "🟠 4", "🟡 8"],
    },
    {
        "agentName": "SastAnalysisAgent",
        "status": "running",
        "progressPercent": 67,
        "currentActivity": "Semgrep 実行中... (245ルール適用)",
        "details": None,
    },
    {
        "agentName": "ReportSynthesizerAgent",
        "status": "waiting",
        "progressPercent": 0,
        "currentActivity": "各エージェント結果の統合とサマリ生成",
        "details": None,
    },
]

# ============================================================
# Live Log Messages for Progress Simulation
# ============================================================

MOCK_LOG_MESSAGES = [
    "[14:26:42] → Semgrep: src/api/users.js を解析中...",
    "[14:26:43] ⚠ 検出: 潜在的SQLインジェクション (line 42)",
    "[14:26:44] 🧠 AI Agent: 該当ASVS要件を AI Search から取得中...",
    "[14:26:45] ✓ ASVS V5.3.4 取得完了",
    "[14:26:46] → Semgrep: src/api/products.js を解析中...",
    "[14:26:48] → Semgrep: src/config/db.js を解析中...",
    "[14:26:49] ⚠ 検出: ハードコードされた認証情報 (line 8)",
    "[14:26:50] 🧠 AI Agent: ASVS V2.10.4 を評価中...",
    "[14:26:52] ✓ SpecComplianceAgent 完了",
    "[14:26:53] → ReportSynthesizerAgent 開始",
    "[14:26:55] 📝 レポート生成中...",
    "[14:26:58] ✓ レビュー完了",
]

# ============================================================
# Dashboard Statistics
# ============================================================

MOCK_DASHBOARD_STATS = {
    "totalReviews": 12,
    "totalFindings": 47,
    "resolvedFindings": 23,
    "averageScore": 72,
}

# ============================================================
# Mutable state for demo (in-memory)
# ============================================================

# Track resolution states for findings
finding_states: dict[str, str] = {f_id: "open" for f_id in MOCK_FINDINGS}
