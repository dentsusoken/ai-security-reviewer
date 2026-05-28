# Research: AI Security Reviewer

## 1. Architecture Overview

### Decision
Adopt a managed Azure-first architecture with separated frontend/backend/tool runners:
- Frontend: React + TypeScript + Vite on Azure Static Web Apps
- Backend API/Orchestrator: FastAPI on Azure Container Apps
- AI: Azure AI Agent Service (GPT-4o) + Azure AI Search for ASVS RAG
- SAST: Semgrep on Azure Functions
- DAST: ZAP Baseline on Azure Container Apps Jobs
- Data: Cosmos DB + Blob Storage
- Security/Identity: Entra ID + Key Vault + Managed Identity
- Observability: Application Insights
- IaC/Delivery: Bicep + GitHub Actions

### Rationale
- Maximizes managed service usage (constitution principle I)
- Supports low-ops hackathon delivery timeline
- Enables independent scaling and fault isolation per processing lane
- Preserves evidence-backed AI workflow with explicit tool outputs

### Alternatives Considered
- Single monolith VM deployment: rejected due to higher ops burden
- Kubernetes (AKS): rejected due to operational complexity for hackathon
- Local file storage for history: rejected due to poor durability/queryability

## 2. Technology Selection and Alternatives

### Frontend
- Decision: React + TypeScript + Vite + Tailwind
- Why: Fast development, type safety, mockup parity, simple SWA deployment
- Alternative: Next.js
- Rejected because: unnecessary SSR complexity for this workload

### Backend
- Decision: FastAPI + Python 3.11+
- Why: excellent async support, OpenAPI-first APIs, Python AI ecosystem fit
- Alternative: Node.js/Express
- Rejected because: weaker alignment with Semgrep/ZAP orchestration and Python AI tooling

### Agent Runtime
- Decision: Azure AI Agent Service + 3 specialist agents
- Why: role separation, traceability, managed model operations, clear orchestration
- Alternative: single prompt chain
- Rejected because: violates constitution multi-agent principle and weak explainability

### Storage
- Decision: Cosmos DB NoSQL + Blob Storage
- Why: JSON-native data, partition scalability, low-latency retrieval, artifact durability
- Alternative: PostgreSQL + file shares
- Rejected because: higher schema migration overhead and less natural document model

### Tool Execution
- Decision: Semgrep in Functions, ZAP in Container Apps Jobs
- Why: burst execution model, cost control, isolation from API runtime
- Alternative: run tools in backend container
- Rejected because: noisy-neighbor risk and runtime instability

## 3. Communication and Data Flow

### Decision
- Browser -> API via HTTPS REST
- Browser <- API via SSE for progress streaming
- API -> Agent Service for orchestrated AI analysis
- API -> Functions (Semgrep) and CA Jobs (ZAP) for tool execution
- API -> Cosmos/Blob for persistence and exports

### Rationale
- SSE is simpler than WebSocket for one-way progress feeds
- Keeps control plane in API while delegating heavy tasks to worker services

### Alternatives Considered
- WebSocket only: rejected due to unnecessary bidirectional complexity
- Polling progress endpoint: rejected due to delayed UX and increased request load

## 4. Security Flow Decisions

### Decision
- Entra ID OIDC for user auth
- Backend validates bearer tokens and enforces route authorization
- Managed Identity for service-to-service auth
- Key Vault as sole secret source (PAT, API keys)
- Input sanitization at ingress and before LLM/tool invocation
- DAST ownership verification via HTML meta or DNS TXT challenge

### Rationale
- Meets constitution principle II and quality gates
- Reduces secret leakage and privilege sprawl

### Alternatives Considered
- Static env secrets only: rejected due to rotation/audit limitations
- DAST opt-in checkbox without ownership proof: rejected as unsafe

## 5. Cost Strategy (Target <= 50 JPY/Review)

### Decision
- Default to standard depth with bounded model token budget
- Reuse cached repo metadata and ASVS retrieval results where safe
- Run Semgrep/ZAP only for selected perspectives
- Use Blob retention policy and report compression
- Cap Full DAST availability for admin/explicit confirmation only

### Rationale
- Cost is dominated by model tokens + scanning jobs; bounded execution and selective runs keep average low

### Alternatives Considered
- Always run all perspectives/depth: rejected due to cost and latency blow-up

## 6. Observability Strategy

### Decision
- Structured logs with correlation IDs across API/agents/workers
- Trace review lifecycle spans in Application Insights
- Emit metrics for latency, failures, token usage, scan durations, and per-review cost estimate

### Rationale
- Needed for rapid issue isolation during judging window

### Alternatives Considered
- Basic logs only: rejected due to insufficient troubleshooting fidelity

## 7. Risks and Mitigations

### Decision
- Model hallucination risk: enforce evidence cross-check and confidence tags
- Scan misuse risk: hard-gate ownership verification and target validation
- Cost spikes: token budgets, scan depth controls, throttling
- Service throttling: queue + retry with backoff and workload shedding
- Secret leakage: commit scanning + Key Vault-only runtime fetch

### Rationale
- Directly addresses constitution quality gates and hackathon reliability target

### Alternatives Considered
- Manual ops playbook only: rejected due to slower mitigation during live demo
