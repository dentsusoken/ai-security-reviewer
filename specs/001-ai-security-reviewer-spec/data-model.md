# Data Model: AI Security Reviewer

## 1. Cosmos DB Design

### Database
- Name: `ai-security-reviewer`

### Containers
1. `reviewSessions`
- Purpose: review lifecycle and high-level metadata
- Partition key: `/userId`
- Key fields:
  - `id` (reviewSessionId)
  - `userId`
  - `inputType` (`github` | `code` | `url`)
  - `targetRef` (repo/url/file metadata)
  - `branch`
  - `perspectives` (`ASVS`, `SAST`, `DAST`)
  - `depth` (`quick` | `standard` | `detailed`)
  - `status` (`queued` | `running` | `completed` | `failed` | `canceled`)
  - `startedAt`, `completedAt`
  - `durationMs`
  - `scoreSummary`
  - `costEstimateJpy`

2. `findings`
- Purpose: normalized finding records
- Partition key: `/reviewSessionId`
- Key fields:
  - `id` (findingId)
  - `reviewSessionId`
  - `severity` (`critical` | `high` | `medium` | `low`)
  - `title`
  - `description`
  - `filePath`, `lineStart`, `lineEnd`
  - `evidence` (tool output refs, snippets, retrieval IDs)
  - `asvsRequirementIds` (array)
  - `cweIds` (array)
  - `agentSource`
  - `confidence`
  - `resolutionState` (`open` | `resolved`) [session scope for MVP]
  - `references` (URLs)

3. `agentRuns`
- Purpose: per-agent execution telemetry
- Partition key: `/reviewSessionId`
- Key fields:
  - `id`
  - `reviewSessionId`
  - `agentName` (`SpecComplianceAgent` | `SastAnalysisAgent` | `ReportSynthesizerAgent`)
  - `state` (`waiting` | `running` | `completed` | `failed`)
  - `progressPercent`
  - `currentActivity`
  - `startedAt`, `endedAt`
  - `tokenUsage`

4. `ownershipVerifications`
- Purpose: DAST ownership challenge tracking
- Partition key: `/targetHost`
- Key fields:
  - `id`
  - `targetHost`
  - `method` (`html-meta` | `dns-txt`)
  - `challengeToken`
  - `status` (`pending` | `verified` | `expired` | `failed`)
  - `verifiedAt`
  - `expiresAt`
  - `verifiedByUserId`

5. `exportJobs`
- Purpose: export lifecycle and artifact links
- Partition key: `/reviewSessionId`
- Key fields:
  - `id`
  - `reviewSessionId`
  - `format` (`markdown` | `pdf` | `json`)
  - `selectedSections` (array)
  - `status` (`queued` | `running` | `completed` | `failed`)
  - `blobPath`
  - `createdAt`, `completedAt`

## 2. Partition Key Strategy

### Decisions
- `reviewSessions` by `userId` for user-centric listing and dashboard queries
- Child containers by `reviewSessionId` for localized read/write patterns
- `ownershipVerifications` by `targetHost` to prevent duplicate challenge storms

### Trade-offs
- Cross-user admin analytics require cross-partition queries (acceptable for hackathon scale)
- Hot partition risk reduced by low expected concurrency (~10 users)

## 3. Blob Storage Layout

Container: `review-reports`
- Path pattern:
  - `/{userId}/{reviewSessionId}/summary.md`
  - `/{userId}/{reviewSessionId}/report.pdf`
  - `/{userId}/{reviewSessionId}/report.json`
- Metadata tags:
  - `reviewSessionId`, `userId`, `format`, `createdAt`, `classification=internal-demo`

## 4. Schema Examples

### reviewSessions example
```json
{
  "id": "rs_20260526_001",
  "userId": "entra:abc123",
  "inputType": "github",
  "targetRef": { "repoUrl": "https://github.com/example/my-bi-tool" },
  "branch": "main",
  "perspectives": ["ASVS", "SAST"],
  "depth": "standard",
  "status": "running",
  "startedAt": "2026-05-26T09:10:00Z",
  "scoreSummary": { "overall": 62, "critical": 2, "high": 5, "medium": 12, "low": 8 },
  "costEstimateJpy": 37.4
}
```

### findings example
```json
{
  "id": "f_0001",
  "reviewSessionId": "rs_20260526_001",
  "severity": "critical",
  "title": "Potential SQL Injection",
  "filePath": "src/api/users.js",
  "lineStart": 42,
  "lineEnd": 43,
  "asvsRequirementIds": ["V5.3.4"],
  "cweIds": ["CWE-89"],
  "agentSource": "SastAnalysisAgent",
  "confidence": 0.91,
  "resolutionState": "open",
  "evidence": {
    "tool": "semgrep",
    "ruleId": "javascript.lang.security.audit.sql-injection",
    "snippetRef": "blob://reports/rs_20260526_001/snippets/f_0001.txt"
  }
}
```

## 5. Data Retention and Governance

- Retain review metadata and findings for hackathon demo period plus buffer (configurable)
- Apply TTL for transient execution logs where appropriate
- Ensure no credentials, customer data, or non-public third-party source code are stored
- Store only sanitized snippets required for evidence and remediation context
