# Quickstart: AI Security Reviewer (Dev)

## 1. Prerequisites

- Azure subscription with permission to create resources in Japan East
- GitHub repository with Actions enabled
- Python 3.11+ and Node.js 20+
- Azure CLI and Bicep installed
- Semgrep runtime dependency available for Function app build

## 2. Provision Infrastructure (Bicep)

1. Login and select subscription.
2. Deploy `infra/main.bicep` with `infra/parameters/dev.bicepparam`.
3. Confirm creation of:
   - Static Web App
   - Container App (API)
   - Container Apps Job (ZAP)
   - Function App (Semgrep)
   - Cosmos DB account/database/containers
   - Blob Storage account/container
   - Key Vault
   - Application Insights
   - Azure AI Agent Service and AI Search resources

## 3. Configure Identity and Secrets

1. Enable system-assigned managed identities for backend, function, and job resources.
2. Assign least-privilege RBAC:
   - Key Vault secrets user
   - Cosmos DB data contributor (only where required)
   - Blob data contributor (export path)
3. Store secrets in Key Vault (PAT, model/API references).
4. Configure backend/function to resolve secrets via Key Vault references.

## 4. Backend Setup (FastAPI)

1. Create virtual environment and install dependencies.
2. Configure local `.env` with non-secret dev placeholders and Key Vault endpoints.
3. Run API locally with Uvicorn.
4. Verify:
   - `/auth/me`
   - `/reviews` creation
   - SSE stream endpoint `/reviews/{id}/events`

## 5. Frontend Setup (React + Vite)

1. Install dependencies and run `vite` dev server.
2. Configure MSAL for Entra ID login flow.
3. Point API base URL to backend endpoint.
4. Validate full UI flow with mock or live API.

## 6. Tool Integration Validation

- Semgrep path: API -> Function -> findings ingest
- ZAP path: API -> ownership verification -> CA Job trigger
- AI path: API -> Agent Service -> evidence synthesis

## 7. CI/CD (GitHub Actions)

- `ci.yml`: lint, tests, contract checks, build
- `deploy-dev.yml`: Bicep deploy + app deploy to dev environment
- Add branch protection and secret scanning checks

## 8. Observability Checklist

- Correlation ID generated at review creation and propagated
- App Insights traces across API, function, and jobs
- Custom metrics:
  - review_duration_ms
  - sse_event_lag_ms
  - agent_failures_total
  - cost_estimate_jpy

## 9. Cost Guardrails

- Default depth: standard
- Perspective-based execution (no unnecessary tool runs)
- Token budget and timeout limits per agent
- DAST baseline-by-default

## 10. Demo Readiness Validation

- Judge path test under 3 minutes:
  - Login -> New Review -> Progress -> Result -> Finding Detail -> Export
- Validate dark/light theme persistence
- Validate no sensitive data in logs, exports, or repository
