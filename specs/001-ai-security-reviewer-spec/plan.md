# Implementation Plan: AI Security Reviewer

**Branch**: `001-before-specify-hook` | **Date**: 2026-05-26 | **Last Updated**: 2026-05-31 | **Spec**: `specs/001-ai-security-reviewer-spec/spec.md`

**Input**: Feature specification from `/specs/001-ai-security-reviewer-spec/spec.md`

## Summary

Build an Azure-managed, multi-agent security review platform that analyzes GitHub
repositories, pasted source code, and ownership-verified target URLs across ASVS,
SAST, and optional DAST perspectives. Each perspective supports three depth levels
(quick, standard, detailed) with measurably different scope and execution
characteristics, giving users flexibility to balance speed, thoroughness, and cost.

The implementation uses React + TypeScript on Azure Static Web Apps, FastAPI on
Azure Container Apps, Azure OpenAI Service (GPT-4o) for LLM-based analysis,
Semgrep on Azure Functions for static analysis, OWASP ZAP on Azure Container
Instance for dynamic analysis, Azure Cosmos DB for history data, Blob Storage
for export artifacts, and Bicep + GitHub Actions for reproducible deployment.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, React 18, Vite 5+
- Backend: Python 3.11+, FastAPI
- Infrastructure: Bicep (latest stable)

**Primary Dependencies**:
- Frontend: React Router, MSAL browser/client packages, Tailwind CSS, SSE client logic
- Backend: FastAPI, Uvicorn, Pydantic v2, Azure SDKs (Identity, Key Vault Secrets,
  Cosmos, Blob, App Insights/OpenTelemetry), httpx
- Backend NEW: dnspython (DNS TXT verification), beautifulsoup4 (HTML meta parsing),
  python-owasp-zap-v2.4 (ZAP API client)
- AI/Tools:
  - Azure OpenAI Service (GPT-4o) for ASVS analysis and report synthesis
  - Semgrep (Azure Function) for SAST analysis
  - OWASP ZAP (Container Instance) for DAST analysis

**Storage**:
- Azure Cosmos DB (NoSQL):
  - ReviewSession/Finding/Agent run history
  - DepthConfiguration registry
  - OwnershipVerificationRecord (with 24h TTL)
- Azure Blob Storage: Markdown/PDF/JSON report artifacts

**Testing**:
- Frontend: Vitest + React Testing Library + Playwright smoke
- Backend: pytest + httpx + contract tests + integration tests
- Security/Quality: Semgrep ruleset validation + API schema validation
- NEW: Depth × Perspective combination integration tests (9 patterns)

**Target Platform**:
- Azure Static Web Apps (frontend)
- Azure Container Apps (backend API + orchestration)
- Azure Functions (Semgrep execution)
- Azure Container Instance (OWASP ZAP for DAST)
- Region: Japan East

**Project Type**:
- Web application (frontend + backend + managed cloud services)

**Performance Goals**:
- Initial report for standard GitHub review <= 10 minutes (P95)
- Progress stream update interval <= 5 seconds (normal conditions)
- Baseline DAST <= 10 minutes, Full DAST <= 30 minutes
- Depth-specific targets:
  - Quick depth: ~30s-2min completion
  - Standard depth: ~2-15min completion
  - Detailed depth: ~10min-1hour completion

**Constraints**:
- Cost target <= 50 JPY per review average (standard depth)
- Hackathon operation window 2026-06-02 to 2026-06-18 with near-continuous uptime
- Strict Entra ID auth and Key Vault secret flow
- No credentials/customer data/non-public BI source in repository
- DAST scanning requires verified URL ownership (legal compliance)

**Scale/Scope**:
- Around 10 concurrent active users
- 8 primary screens + export/rereview modal flows + URL ownership wizard
- 4 cooperating agents (SpecCompliance/SAST/DAST/Report synthesis)
- 9 (perspective × depth) combinations with distinct behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-design gate status:
- PASS: Azure managed-first architecture choices documented
- PASS: Bicep coverage for all target resources defined
- PASS: Key Vault-only secret flow + Managed Identity plan defined
- PASS: Entra ID auth flow boundaries defined
- PASS: Input validation and AI payload sanitization strategy defined
- PASS: DAST ownership verification mechanism defined
- PASS: Multi-agent role separation and evidence mapping defined
- PASS: 3-minute judge UX and progress streaming commitments preserved
- PASS: Spec-kit phase ordering and commit checkpoints maintained
- PASS: MIT public repo and commit hygiene constraints maintained
- PASS: Depth differentiation strategy documented and testable

Post-design gate re-check:
- PASS: research.md resolves unknowns and alternatives
- PASS: data-model.md includes evidence mapping entities + DepthConfiguration
- PASS: contracts/api.openapi.yaml captures auth, validation, streaming, error model,
  and new ownership/depth endpoints
- PASS: quickstart.md includes secure runtime and deployment flow

## Review Engine Architecture

### Perspective Agents Overview

| Agent | Method | Tool/Service | Output |
|-------|--------|--------------|--------|
| **SpecComplianceAgent** | LLM-based ASVS check | Azure OpenAI GPT-4o | Findings with ASVS/CWE mapping |
| **SastAnalysisAgent** | Static code analysis | Semgrep (Azure Function) | Findings with rule IDs and CWE |
| **DastAnalysisAgent** | Dynamic web testing | OWASP ZAP (Container Instance) | Findings from attack results |
| **ReportSynthesizerAgent** | Multi-agent merge | Azure OpenAI GPT-4o | Unified deduplicated report |

### Depth Configuration

**Location**: `backend/app/core/depth_config.py`

**Pattern**: Single source of truth for (perspective × depth) settings

**Structure**:
```python
@dataclass
class DepthConfig:
    max_files: int            # For ASVS/SAST
    max_urls: int | None      # For DAST only
    ruleset: str | list[str]  # Semgrep rules or ASVS categories
    use_llm_filter: bool      # SAST FP filtering
    scan_mode: str | None     # DAST: passive/baseline/full
    prompt_style: str         # concise/detailed/expert
    estimated_time_sec: int
    estimated_cost_jpy: int

DEPTH_CONFIGS = {
    (Perspective.ASVS, ReviewDepth.QUICK): DepthConfig(...),
    (Perspective.ASVS, ReviewDepth.STANDARD): DepthConfig(...),
    (Perspective.ASVS, ReviewDepth.DETAILED): DepthConfig(...),
    (Perspective.SAST, ReviewDepth.QUICK): DepthConfig(...),
    (Perspective.SAST, ReviewDepth.STANDARD): DepthConfig(...),
    (Perspective.SAST, ReviewDepth.DETAILED): DepthConfig(...),
    (Perspective.DAST, ReviewDepth.QUICK): DepthConfig(...),
    (Perspective.DAST, ReviewDepth.STANDARD): DepthConfig(...),
    (Perspective.DAST, ReviewDepth.DETAILED): DepthConfig(...),
}
```

### Language Detection Architecture

**Location**: `backend/app/services/language_detector.py` (existing, enhanced)

**Capabilities**:
- 15+ programming languages with security relevance tiers
- Priority-based file filtering for large repositories
- Multi-strategy detection: extension → shebang → pattern analysis

**Integration Points**:
- `SpecComplianceAgent`: File prioritization before LLM analysis
- `SastAnalysisAgent`: Language hint for Semgrep ruleset selection
- Code paste flow: Auto-detection when language="auto"

**API**: `LanguageDetector.detect_for_code_input(filename, content, explicit_language)`

### URL Ownership Verification Architecture

**Module**: `backend/app/services/url_ownership_service.py`

**Token Format**: `aisec-verify-<32-cryptographically-random-chars>`

**Storage**: Cosmos DB collection `ownership_verifications` with TTL (24 hours)

**Verification Methods**:

| Method | Implementation | Library | Timeout |
|--------|---------------|---------|---------|
| HTML meta | HTTP GET + parse `<meta name="ai-sec-reviewer-verification">` | beautifulsoup4 | 30s |
| DNS TXT | Query `_aisecreviewer.<domain>` TXT record | dnspython | 60s |

**Flow**:
```
1. POST /api/ownership/request
   → Generate token, store in Cosmos with 24h TTL
   → Return token + instructions
2. User adds meta tag or DNS record
3. POST /api/ownership/verify {method, url, token}
   → Fetch target / Query DNS
   → Compare with stored token
   → Mark verified or reject
4. Verified record allows DAST scan within 24h
```

**Rate Limiting**: Max 10 verification attempts per IP per hour.

### DAST Implementation Architecture

**ZAP Deployment**:
- Azure Container Instance (on-demand provisioning)
- Image: `owasp/zap2docker-stable`
- API authentication: `-config api.key=<random>`
- Network: Outbound HTTP/HTTPS to internet allowed

**Client**: `backend/app/services/zap_client.py`
- Library: `python-owasp-zap-v2.4`
- Methods: `spider()`, `passive_scan()`, `active_scan()`, `get_alerts()`

**Scan Profiles by Depth**:

| Depth    | ZAP Operations                           | Risk Level |
|----------|------------------------------------------|------------|
| quick    | Spider + Passive scan only               | Safe       |
| standard | Spider + Passive + Light active baseline | Moderate   |
| detailed | Spider + Full active scan all attack vectors | High   |

**Pre-scan Validation**:
- Ownership token still valid (< 24h)
- Target URL still reachable
- User explicit confirmation for production-like URLs (detailed depth)

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-security-reviewer-spec/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   ├── pages/
│   │   └── OwnershipVerificationPage.tsx  (NEW)
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── reviews/
│   │   │   ├── DepthSelector.tsx          (NEW: with estimates)
│   │   │   ├── PerspectiveSelector.tsx    (NEW: validity check)
│   │   │   └── UrlOwnershipWizard.tsx     (NEW)
│   │   ├── findings/
│   │   ├── history/
│   │   └── agents/
│   ├── services/
│   └── styles/
└── tests/

backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── reviews.py
│   │   │   ├── findings.py
│   │   │   ├── history.py
│   │   │   ├── exports.py
│   │   │   ├── ownership.py               (NEW)
│   │   │   └── auth.py
│   │   └── schemas/
│   ├── core/
│   │   └── depth_config.py                (NEW)
│   ├── domain/
│   ├── agents/
│   │   ├── spec_compliance_agent.py       (depth-aware)
│   │   ├── sast_analysis_agent.py         (REINSTATE)
│   │   ├── dast_analysis_agent.py         (NEW)
│   │   └── report_synthesizer_agent.py
│   ├── services/
│   │   ├── openai_service.py              (depth-aware prompts)
│   │   ├── github_service.py
│   │   ├── language_detector.py           (existing, enhanced)
│   │   ├── semgrep_client.py              (REINSTATE)
│   │   ├── zap_client.py                  (NEW)
│   │   ├── url_ownership_service.py       (NEW)
│   │   ├── finding_ingestion_service.py   (REINSTATE)
│   │   └── excel_export_service.py
│   ├── repositories/
│   ├── integrations/
│   └── security/
└── tests/
    ├── test_depth_config.py               (NEW)
    ├── test_language_detector.py          (NEW)
    ├── test_url_ownership.py              (NEW)
    ├── test_sast_agent.py                 (NEW)
    └── test_dast_agent.py                 (NEW)

infra/
├── main.bicep
├── modules/
│   ├── staticwebapp.bicep
│   ├── containerapp.bicep
│   ├── containerapps-job-zap.bicep        (replaced by ZAP container)
│   ├── zap-container-instance.bicep       (NEW)
│   ├── functions-semgrep.bicep
│   ├── cosmosdb.bicep
│   ├── storage.bicep
│   ├── keyvault.bicep
│   ├── appinsights.bicep
│   └── openai-account.bicep               (NEW: Azure OpenAI)
└── parameters/
    └── dev.bicepparam

tools/
└── semgrep-function/                      (existing Azure Function for Semgrep)

.github/
└── workflows/
    ├── ci.yml
    └── deploy-dev.yml
```

**Structure Decision**: Web application split into `frontend`, `backend`, `infra`, and
`tools` to align with Azure managed deployment boundaries, independent CI jobs, and
clearer security isolation. The `tools/` directory hosts standalone services like the
Semgrep Azure Function.

## Implementation Phases

### Phase A: Foundation (Existing)
- Authentication (Entra ID via MSAL)
- Basic CRUD APIs
- Dashboard, History, basic Review flows
- ASVS analysis via Azure OpenAI

### Phase B: Depth Differentiation (Current Focus)
- F.1: Depth Configuration module
- F.2: ASVS depth integration
- F.3: SAST reinstatement (file recreation) with depth
- F.4: Language auto-detection for code input
- F.6: Frontend depth UI enhancements

### Phase C: DAST Implementation
- F.5.1: URL ownership verification
  - Token generation and storage
  - HTML meta tag verification
  - DNS TXT record verification
- F.5.2: OWASP ZAP integration
  - Azure Container Instance provisioning
  - ZAP client wrapper
  - DastAnalysisAgent with depth-aware scan modes

### Phase D: Polish & Production
- F.7: Integration tests for 9 patterns
- F.8: Documentation updates
- F.9: Production deployment verification

## Key Technical Decisions

### Why Azure OpenAI for LLM (not Azure AI Agent Service)?

**Decision**: Use Azure OpenAI Service directly with GPT-4o.

**Rationale**:
- Direct SDK access provides better control over prompts and parameters
- Lower cost than Agent Service for simple LLM calls
- Sufficient for our orchestration needs (we handle agent state internally)
- Existing working implementation already in place

**Trade-off**: We lose some Agent Service features (built-in memory, function calling
auto-routing), but our use case doesn't require them.

### Why Semgrep on Azure Function (not as library)?

**Decision**: Run Semgrep as separate Azure Function service.

**Rationale**:
- Semgrep has heavy dependencies (Python + OCaml + various rules)
- Isolated execution avoids backend container bloat
- Independent scaling for SAST workload spikes
- Easier to update Semgrep version without rebuilding main backend

**Trade-off**: Adds HTTP latency (~100-500ms), but acceptable for analysis tasks.

### Why OWASP ZAP on Container Instance (not Container Apps Jobs)?

**Decision**: Use Azure Container Instance for ZAP.

**Rationale**:
- Container Instance supports long-running processes (DAST can take 1 hour)
- Per-second billing (~$0.005/hour) is cost-effective
- Simpler API for on-demand provisioning
- No need for Container Apps scaling features

**Trade-off**: Less integration with Container Apps environment, but adequate
for batch-style DAST workloads.

### Why dnspython for DNS verification (not Azure DNS SDK)?

**Decision**: Use `dnspython` library for DNS TXT queries.

**Rationale**:
- We query external DNS, not manage Azure DNS zones
- `dnspython` is the de facto standard for DNS operations in Python
- Lightweight, well-maintained, no Azure dependency

### Depth Configuration: Code vs Database?

**Decision**: Define `DEPTH_CONFIGS` in code (`depth_config.py`), not database.

**Rationale**:
- Depth settings are application logic, not user data
- Code-based allows type-checking and IDE support
- Version-controlled with rest of codebase
- No DB query overhead on every review

**Trade-off**: Configuration changes require deployment. Acceptable since changes
should be rare and reviewed.

## Risk Mitigation

### Risk 1: DAST Cost Explosion
**Scenario**: Detailed DAST scan running for 1 hour at scale.

**Mitigation**:
- Max URLs cap per depth (5/30/200)
- Per-IP rate limit on scan initiation
- Cost monitoring with Azure Cost Management alerts
- Auto-shutdown of idle ZAP container after 5 minutes

### Risk 2: URL Ownership Bypass
**Scenario**: User scans someone else's site by tricking verification.

**Mitigation**:
- Token format prevents prediction (cryptographic random)
- Token expiry (24h) limits window
- Re-verification check at scan start (not just at request time)
- Rate limiting on verification attempts (10/hour/IP)

### Risk 3: LLM Cost Overrun (Detailed ASVS)
**Scenario**: Detailed ASVS with 100 files exceeds 150 JPY estimate.

**Mitigation**:
- Token counter before LLM call, abort if estimate exceeds limit
- Use GPT-4o-mini for non-critical depth variants if needed
- Cost monitoring per review with hard cap at 500 JPY

### Risk 4: SAST/Semgrep Function Latency
**Scenario**: Semgrep Function cold start adds 5-10s latency.

**Mitigation**:
- Use Premium plan for warm instances during demo
- Pre-warm function 5 minutes before scheduled demos
- Cache Semgrep results for identical code (Cosmos DB)

## Cost Estimates

### Per-Review Cost (Standard Depth)

| Perspective | Service | Cost (JPY) |
|-------------|---------|-----------|
| ASVS | Azure OpenAI (GPT-4o, ~10K tokens) | ~30 |
| SAST | Semgrep Function (execution) | ~5 |
| DAST | ZAP Container (15min) | ~10 |
| Storage | Cosmos + Blob | ~1 |
| **Total** | (Standard, 1 perspective) | **~30-50** |

### Per-Review Cost (Detailed Depth)

| Perspective | Service | Cost (JPY) |
|-------------|---------|-----------|
| ASVS | Azure OpenAI (~80K tokens) | ~150 |
| SAST | Semgrep + LLM filter | ~80 |
| DAST | ZAP Container (1 hour) | ~500 |
| Storage | Cosmos + Blob | ~5 |
| **Total** | (Detailed, all 3 perspectives) | **~700** |

### Monthly Operating Cost (10 reviews/day, mixed depths)

- Azure OpenAI: ~10,000 JPY/month
- Container Apps: ~5,000 JPY/month
- Container Instance (ZAP, on-demand): ~3,000 JPY/month
- Functions (Semgrep): ~2,000 JPY/month
- Cosmos DB + Blob: ~2,000 JPY/month
- **Estimated Total**: ~22,000 JPY/month

## Complexity Tracking

No constitution violations requiring exception.

**Justified complexity**:
- DAST requires separate compute (Container Instance) due to long-running nature
- Semgrep separated to Function for dependency isolation
- These choices align with Azure managed-first principle (CP-I)
