# Implementation Plan: AI Security Reviewer

**Branch**: `001-before-specify-hook` | **Date**: 2026-05-26 | **Spec**: `specs/001-ai-security-reviewer-spec/spec.md`

**Input**: Feature specification from `/specs/001-ai-security-reviewer-spec/spec.md`

## Summary

Build an Azure-managed, multi-agent security review platform that analyzes GitHub
repositories, pasted source code, and ownership-verified target URLs across ASVS,
SAST, and optional DAST perspectives. The implementation uses React + TypeScript on
Azure Static Web Apps, FastAPI on Azure Container Apps, Azure AI Agent Service with
three specialist agents, Azure AI Search for ASVS RAG, Cosmos DB for history data,
Blob Storage for export artifacts, and Bicep + GitHub Actions for reproducible
deployment.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, React 18, Vite 5+
- Backend: Python 3.11+, FastAPI
- Infrastructure: Bicep (latest stable)

**Primary Dependencies**:
- Frontend: React Router, MSAL browser/client packages, Tailwind CSS, SSE client logic
- Backend: FastAPI, Uvicorn, Pydantic v2, Azure SDKs (Identity, Key Vault Secrets,
  Cosmos, Blob, App Insights/OpenTelemetry), httpx
- AI/Tools: Azure AI Agent Service (GPT-4o), Azure AI Search, Semgrep executor,
  ZAP Baseline runner

**Storage**:
- Azure Cosmos DB (NoSQL): ReviewSession/Finding/Agent run history
- Azure Blob Storage: Markdown/PDF/JSON report artifacts

**Testing**:
- Frontend: Vitest + React Testing Library + Playwright smoke
- Backend: pytest + httpx + contract tests + integration tests
- Security/Quality: Semgrep ruleset validation + API schema validation

**Target Platform**:
- Azure Static Web Apps (frontend)
- Azure Container Apps (backend API + orchestration)
- Azure Functions (Semgrep execution)
- Azure Container Apps Jobs (ZAP Baseline)
- Region: Japan East

**Project Type**:
- Web application (frontend + backend + managed cloud services)

**Performance Goals**:
- Initial report for standard GitHub review <= 10 minutes (P95)
- Progress stream update interval <= 5 seconds (normal conditions)
- Baseline DAST <= 10 minutes, Full DAST <= 30 minutes

**Constraints**:
- Cost target <= 50 JPY per review average
- Hackathon operation window 2026-06-02 to 2026-06-18 with near-continuous uptime
- Strict Entra ID auth and Key Vault secret flow
- No credentials/customer data/non-public BI source in repository

**Scale/Scope**:
- Around 10 concurrent active users
- 8 primary screens + export/rereview modal flows
- 3 cooperating agents (SpecCompliance/SAST/Report synthesis)

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

Post-design gate re-check:
- PASS: research.md resolves unknowns and alternatives
- PASS: data-model.md includes evidence mapping entities
- PASS: contracts/api.openapi.yaml captures auth, validation, streaming, and error model
- PASS: quickstart.md includes secure runtime and deployment flow

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
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── reviews/
│   │   ├── findings/
│   │   ├── history/
│   │   └── agents/
│   ├── services/
│   └── styles/
└── tests/

backend/
├── app/
│   ├── api/
│   ├── domain/
│   ├── agents/
│   ├── services/
│   ├── repositories/
│   ├── integrations/
│   └── security/
└── tests/

infra/
├── main.bicep
├── modules/
│   ├── staticwebapp.bicep
│   ├── containerapp.bicep
│   ├── containerapps-job-zap.bicep
│   ├── functions-semgrep.bicep
│   ├── cosmosdb.bicep
│   ├── storage.bicep
│   ├── keyvault.bicep
│   ├── appinsights.bicep
│   ├── aifoundry-agent.bicep
│   └── aisearch.bicep
└── parameters/
    └── dev.bicepparam

.github/
└── workflows/
    ├── ci.yml
    └── deploy-dev.yml
```

**Structure Decision**: Web application split into `frontend`, `backend`, and `infra`
to align with Azure managed deployment boundaries, independent CI jobs, and clearer
security isolation.

## Complexity Tracking

No constitution violations requiring exception.
