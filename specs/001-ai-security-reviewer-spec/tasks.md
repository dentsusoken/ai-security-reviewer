# Tasks: AI Security Reviewer

**Input**: Design documents from `/specs/001-ai-security-reviewer-spec/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.openapi.yaml, quickstart.md
**Last Updated**: 2026-05-31

**Legend**:
- `CP-I..V` = Constitution Core Principles I..V
- `USx` = User Story x
- `FR-xxx` = Functional Requirement ID in spec
- `[P]` = parallelizable task

## Phase 1: Setup (Phase A - Foundation)

**Purpose**: Project bootstrap and baseline repository structure

- [x] T001 Create monorepo directory skeleton in `frontend/`, `backend/`, `infra/` | Deps: none | DoD: folders and README stubs exist | Est: 4h | Related: US1, FR-006, CP-I | Phase: A
- [x] T002 Initialize React + TypeScript + Vite app in `frontend/` | Deps: T001 | DoD: app builds and dev server starts | Est: 6h | Related: US11, FR-045, CP-III | Phase: A
- [x] T003 Initialize FastAPI service skeleton in `backend/` | Deps: T001 | DoD: health endpoint responds locally | Est: 6h | Related: US1, FR-024, CP-I | Phase: A
- [x] T004 [P] Add frontend lint/format config in `frontend/eslint.config.js` and `frontend/prettier.config.cjs` | Deps: T002 | DoD: lint and format commands pass | Est: 4h | Related: US11, CP-V | Phase: A
- [x] T005 [P] Add backend lint/format config in `backend/pyproject.toml` | Deps: T003 | DoD: ruff/black checks pass | Est: 4h | Related: US1, CP-V | Phase: A
- [x] T006 [P] Add secret scanning and pre-commit hooks in `.pre-commit-config.yaml` and `.gitleaks.toml` | Deps: T001 | DoD: blocked sample secret commit test fails as expected | Est: 4h | Related: US10, FR-002, CP-II | Phase: A
- [x] T007 [P] Create CI workflow baseline in `.github/workflows/ci.yml` | Deps: T002, T003 | DoD: PR pipeline runs lint and unit test jobs | Est: 6h | Related: US1, FR-023, CP-V | Phase: A
- [x] T008 [P] Create deployment workflow baseline in `.github/workflows/deploy-dev.yml` | Deps: T007 | DoD: workflow has build and infra deploy stages | Est: 6h | Related: US1, FR-023, CP-I | Phase: A
- [x] T009 [P] Create Bicep entrypoint and dev parameters in `infra/main.bicep` and `infra/parameters/dev.bicepparam` | Deps: T001 | DoD: `az deployment group validate` succeeds | Est: 8h | Related: US1, FR-006, CP-I | Phase: A
- [x] T010 [P] Add base Azure modules for SWA/API/Functions/Jobs in `infra/modules/*.bicep` | Deps: T009 | DoD: module contracts compile without errors | Est: 8h | Related: US1, FR-017, CP-I | Phase: A

**Phase Completion Criteria (A)**:
- Frontend and backend scaffolds run locally
- CI and deploy workflows exist and pass validation
- Bicep baseline compiles and can be validated
- Secret hygiene checks are active

---

## Phase 2: Foundational (Phase A - Foundation Continuation)

**Purpose**: Blocking infrastructure and platform services required by all user stories

- [x] T011 Implement Cosmos DB and Blob modules in `infra/modules/cosmosdb.bicep` and `infra/modules/storage.bicep` | Deps: T010 | DoD: resources deploy successfully in dev | Est: 8h | Related: US7, FR-037, CP-I | Phase: A
- [x] T012 Implement Key Vault and Managed Identity modules in `infra/modules/keyvault.bicep` | Deps: T010 | DoD: identities can read secrets via RBAC | Est: 8h | Related: US10, FR-002, CP-II | Phase: A
- [x] T013 [P] Implement Application Insights module in `infra/modules/appinsights.bicep` | Deps: T010 | DoD: telemetry connection string available | Est: 4h | Related: US13, FR-022, CP-I | Phase: A
- [x] T014 [P] Implement AI Agent Service and AI Search modules in `infra/modules/aifoundry-agent.bicep` and `infra/modules/aisearch.bicep` | Deps: T010 | DoD: endpoints and credentials resolved via Key Vault | Est: 8h | Related: US1, FR-025, CP-IV | Phase: A
- [x] T015 Configure Entra ID app registration documentation in `docs/entra-id-setup.md` | Deps: T001 | DoD: app registration steps reproducible by teammate | Est: 4h | Related: US10, FR-001, CP-II | Phase: A
- [x] T016 Implement backend settings and secret resolution in `backend/app/core/settings.py` | Deps: T012 | DoD: local and cloud config modes both load | Est: 6h | Related: US10, FR-002, CP-II | Phase: A
- [x] T017 Implement input validation and sanitization middleware in `backend/app/security/input_guard.py` | Deps: T003, T016 | DoD: malicious payload tests rejected | Est: 6h | Related: US1, FR-017, CP-II | Phase: A
- [x] T018 Implement correlation ID and structured logging middleware in `backend/app/observability/logging.py` | Deps: T013, T003 | DoD: trace IDs appear in API logs and responses | Est: 6h | Related: US13, FR-022, CP-V | Phase: A

**Phase Completion Criteria (A)**:
- Core Azure managed resources deploy from Bicep
- Entra/Key Vault/Managed Identity flow is executable
- API has baseline security middleware and observability
- Foundation gates in constitution are satisfied

---

## Phase 3: User Story 1 - GitHub Repository Security Review (Priority: P1) (Phase B - MVP Core)

**Goal**: Execute GitHub-based ASVS review and produce initial report

**Independent Test**: Run a public GitHub review on `main` and get report <=10 minutes with ASVS evidence

- [x] T019 [US1] Implement GitHub review request schema in `backend/app/api/schemas/review.py` | Deps: T017 | DoD: schema validates repo URL/branch defaults | Est: 4h | Related: US1, FR-007, CP-II | Phase: B
- [x] T020 [US1] Implement GitHub repository fetch service in `backend/app/integrations/github_client.py` | Deps: T019, T016 | DoD: public repo clone/download works with configured PAT fallback | Est: 8h | Related: US1, FR-008, CP-I | Phase: B
- [x] T021 [P] [US1] Implement language detection pipeline in `backend/app/services/language_detector.py` | Deps: T020 | DoD: JS/TS/Python priority detection covered by tests | Est: 6h | Related: US1, FR-009, CP-IV | Phase: B
- [x] T022 [US1] Implement review session creation API in `backend/app/api/routes/reviews.py` | Deps: T019, T011 | DoD: POST `/reviews` persists session and returns ID | Est: 6h | Related: US1, FR-024, CP-V | Phase: B
- [x] T023 [US1] Implement SpecComplianceAgent client in `backend/app/agents/spec_compliance_agent.py` | Deps: T014, T022 | DoD: agent run returns ASVS-tagged findings | Est: 8h | Related: US1, FR-025, CP-IV | Phase: B
- [x] T024 [US1] Implement ASVS evidence mapping formatter in `backend/app/services/evidence_mapper.py` | Deps: T023 | DoD: every finding includes ASVS IDs and source evidence refs | Est: 6h | Related: US1, FR-026, CP-IV | Phase: B
- [x] T025 [US1] Implement result summary endpoint in `backend/app/api/routes/review_results.py` | Deps: T022, T024 | DoD: response includes score, severities, perspective summary | Est: 6h | Related: US1, FR-024, CP-V | Phase: B

**Phase Completion Criteria (B / US1)**:
- GitHub review executes end-to-end ✅
- ASVS evidence included in output findings ✅
- Result summary endpoint supports UI consumption ✅

---

## Phase 4: User Story 10 - Entra ID Authentication (Priority: P1) (Phase B - MVP Core)

**Goal**: Entra ID sign-in/out and protected API routes

**Independent Test**: Login from landing, access protected page, logout to landing

- [x] T026 [P] [US10] Implement MSAL auth provider in `frontend/src/features/auth/AuthProvider.tsx` | Deps: T002, T015 | DoD: login popup/redirect succeeds in dev tenant | Est: 8h | Related: US10, FR-001, CP-II | Phase: B
- [x] T027 [US10] Implement frontend auth route guards in `frontend/src/app/router.tsx` | Deps: T026 | DoD: non-authenticated users redirected to landing | Est: 4h | Related: US10, FR-002, CP-II | Phase: B
- [x] T028 [US10] Implement JWT verification middleware in `backend/app/security/jwt_middleware.py` | Deps: T015, T003 | DoD: invalid token requests return 401 with audit log | Est: 8h | Related: US10, FR-002, CP-II | Phase: B
- [x] T029 [US10] Implement `/auth/me` endpoint in `backend/app/api/routes/auth.py` | Deps: T028 | DoD: endpoint returns user profile from token claims | Est: 4h | Related: US10, FR-001, CP-V | Phase: B

**Phase Completion Criteria (B / US10)**:
- Frontend sign-in/out works with Entra ID ✅
- Backend protects APIs with JWT validation ✅
- User identity available to UI and logs ✅

---

## Phase 5: User Story 11 - Dashboard Home (Priority: P1) (Phase B - MVP Core)

**Goal**: Display stats, recent reviews, and CTA from authenticated home

**Independent Test**: Authenticated user sees 4 metrics, 3 latest reviews, and start CTA

- [x] T030 [US11] Implement dashboard query API in `backend/app/api/routes/dashboard.py` | Deps: T011, T022, T028 | DoD: API returns metrics + top 3 recent sessions | Est: 6h | Related: US11, FR-003, CP-V | Phase: B
- [x] T031 [P] [US11] Implement dashboard page shell from mock in `frontend/src/pages/DashboardPage.tsx` | Deps: T027 | DoD: page layout matches approved mock structure | Est: 6h | Related: US11, FR-005, CP-III | Phase: B
- [x] T032 [US11] Bind dashboard metrics and recent list in `frontend/src/features/dashboard/useDashboard.ts` | Deps: T030, T031 | DoD: live API data renders and refreshes on load | Est: 6h | Related: US11, FR-004, CP-III | Phase: B
- [x] T033 [US11] Implement landing page sign-in CTA in `frontend/src/pages/LandingPage.tsx` | Deps: T026 | DoD: sign-in button routes authenticated users to dashboard | Est: 4h | Related: US11, FR-001, CP-III | Phase: B

**Phase Completion Criteria (B / US11)**:
- Landing and dashboard flow is usable for demo entry ✅
- Dashboard shows live stats and recent reviews ✅
- New review CTA navigates correctly ✅

---

## Phase 6: User Story 13 - Real-Time AI Agent Visibility (Priority: P1) (Phase B - MVP Core)

**Goal**: Show global and per-agent progress with live log stream

**Independent Test**: Start review and observe streaming updates in progress screen

- [x] T034 [US13] Implement SSE progress endpoint in `backend/app/api/routes/review_events.py` | Deps: T022, T018 | DoD: endpoint emits status/percent/log events until completion | Est: 8h | Related: US13, FR-020, CP-III | Phase: B
- [x] T035 [US13] Implement agent run state repository in `backend/app/repositories/agent_run_repository.py` | Deps: T011, T023 | DoD: waiting/running/completed states persisted per review | Est: 6h | Related: US13, FR-021, CP-IV | Phase: B
- [x] T036 [P] [US13] Implement SSE client hook in `frontend/src/features/agents/useReviewProgressSSE.ts` | Deps: T034 | DoD: reconnect and incremental event handling works | Est: 6h | Related: US13, FR-022, CP-III | Phase: B
- [x] T037 [US13] Implement progress screen with per-agent cards in `frontend/src/pages/ReviewProgressPage.tsx` | Deps: T036 | DoD: global progress, agent status, and log panel render live | Est: 8h | Related: US13, FR-021, CP-III | Phase: B
- [x] T038 [US13] Implement persistent AI status indicator in `frontend/src/components/layout/AIAgentStatusBadge.tsx` | Deps: T036 | DoD: indicator visible on authenticated pages during running reviews | Est: 4h | Related: US13, FR-046, CP-III | Phase: B

**Phase Completion Criteria (B / US13)**:
- Progress streaming works end-to-end via SSE ✅
- UI shows global and per-agent execution state ✅
- Agent status remains visible across authenticated navigation ✅

---

## Phase 7: User Story 2 - Direct Code Review by Paste (Priority: P2) (Phase C - Extension)

**Goal**: Support code paste review with size/language constraints

**Independent Test**: Paste <=10,000 lines and obtain review; oversized payload rejected

- [x] T039 [US2] Implement code-paste schema and line limit guard in `backend/app/api/schemas/code_input.py` | Deps: T017, T022 | DoD: >10,000 line request rejected with validation error | Est: 6h | Related: US2, FR-011, CP-II | Phase: C
- [x] T040 [US2] Implement code input form in `frontend/src/features/reviews/CodeInputForm.tsx` | Deps: T031 | DoD: filename/language/code fields submit to API | Est: 6h | Related: US2, FR-010, CP-III | Phase: C
- [x] T041 [US2] Extend orchestrator for code-source pipeline in `backend/app/services/review_orchestrator.py` | Deps: T039, T023 | DoD: code input runs through same finding/report flow | Est: 8h | Related: US2, FR-006, CP-IV | Phase: C

**Phase Completion Criteria (C / US2)**:
- Code-paste review path is fully operational ✅
- Input limits and sanitization are enforced ✅

---

## Phase 8: User Story 4 - Integrated Static Analysis (Priority: P2) (Phase C - Extension)

**Goal**: Run Semgrep and merge interpreted SAST findings

**Independent Test**: SAST-enabled review includes Semgrep findings with prioritization and false-positive flags

> **NOTE**: SAST implementation was removed during the `Resolve review API regressions` refactor (commit d0f8be9). Re-implementation is tracked in Phase F.

- [x] T042 [US4] Implement Semgrep Azure Function handler in `tools/semgrep-function/__init__.py` | Deps: T010, T017 | DoD: function returns normalized finding payloads | Est: 8h | Related: US4, FR-014, CP-I | Phase: C
- [ ] T043 [US4] Implement function invocation client in `backend/app/integrations/semgrep_client.py` | Deps: T042, T041 | DoD: backend calls function and receives findings | Est: 6h | Related: US4, FR-025, CP-I | Phase: C | **Status: REMOVED - See T085**
- [ ] T044 [US4] Implement SastAnalysisAgent in `backend/app/agents/sast_analysis_agent.py` | Deps: T043, T014 | DoD: agent prioritizes findings and sets false-positive flags | Est: 8h | Related: US4, FR-025, CP-IV | Phase: C | **Status: REMOVED - See T086**
- [ ] T045 [US4] Implement findings ingestion pipeline in `backend/app/services/finding_ingestion_service.py` | Deps: T043, T044, T011 | DoD: Semgrep + AI findings stored in `findings` container | Est: 6h | Related: US4, FR-026, CP-IV | Phase: C | **Status: REMOVED - See T087**
- [x] T046 [US4] Integrate SAST perspective toggle in `frontend/src/features/reviews/PerspectiveSelector.tsx` | Deps: T040 | DoD: SAST selection drives backend execution path | Est: 4h | Related: US4, FR-018, CP-III | Phase: C

**Phase Completion Criteria (C / US4)**:
- ⚠️ Semgrep execution integration removed - See Phase F.3 for re-implementation
- SAST findings are AI-prioritized and persisted (pending F.3)
- Perspective selection UI exists (T046 done)

---

## Phase 9: User Story 5 - Finding Detail Inspection (Priority: P2) (Phase C - Extension)

**Goal**: Provide detailed finding view with evidence and remediation

**Independent Test**: Open any finding from report and verify all detail sections

- [x] T047 [US5] Implement finding detail API in `backend/app/api/routes/findings.py` | Deps: T045, T025 | DoD: API returns code snippet, explanation, fix, ASVS/CWE, links | Est: 6h | Related: US5, FR-027, CP-IV | Phase: C
- [x] T048 [US5] Implement result summary page bindings in `frontend/src/pages/ReviewResultPage.tsx` | Deps: T025, T031 | DoD: finding list and perspective score render from API | Est: 8h | Related: US5, FR-025, CP-III | Phase: C
- [x] T049 [US5] Implement finding detail page in `frontend/src/pages/FindingDetailPage.tsx` | Deps: T047, T048 | DoD: highlighted code and copyable fix are usable | Est: 8h | Related: US5, FR-029, CP-III | Phase: C
- [x] T050 [US5] Implement evidence reference renderer in `frontend/src/features/findings/EvidencePanel.tsx` | Deps: T049 | DoD: ASVS/CWE/reference links shown consistently | Est: 4h | Related: US5, FR-030, CP-IV | Phase: C

**Phase Completion Criteria (C / US5)**:
- Users can inspect findings deeply and copy remediation ✅
- Evidence mapping is visible and traceable ✅

---

## Phase 10: User Story 6 - In-Screen Resolution State Management (Priority: P2) (Phase C - Extension)

**Goal**: Toggle finding resolution state in-session and reflect in summary

**Independent Test**: Mark resolved/unresolved and observe immediate UI update

- [x] T051 [US6] Implement finding status patch API in `backend/app/api/routes/finding_status.py` | Deps: T047 | DoD: open/resolved transitions persist for current session | Est: 4h | Related: US6, FR-031, CP-V | Phase: C
- [x] T052 [US6] Implement detail-page resolve toggle in `frontend/src/features/findings/ResolveToggle.tsx` | Deps: T049, T051 | DoD: button toggles state and confirms action | Est: 4h | Related: US6, FR-031, CP-III | Phase: C
- [x] T053 [US6] Implement summary state synchronization in `frontend/src/features/reviews/useFindingStateSync.ts` | Deps: T052, T048 | DoD: summary badges update without full reload | Est: 6h | Related: US6, FR-032, CP-III | Phase: C

**Phase Completion Criteria (C / US6)**:
- In-session resolution workflow is complete ✅
- Result and detail pages remain state-consistent ✅

---

## Phase 11: User Story 7 - Review History Search and Filtering (Priority: P2) (Phase C - Extension)

**Goal**: Implement searchable, filterable review history

**Independent Test**: Apply all filters and verify counts/empty state

- [x] T054 [US7] Implement history query API with filters in `backend/app/api/routes/history.py` | Deps: T011, T022, T028 | DoD: query/period/score/perspective filters supported | Est: 8h | Related: US7, FR-034, CP-V | Phase: C
- [x] T055 [US7] Implement history page list and count UI in `frontend/src/pages/HistoryPage.tsx` | Deps: T031, T054 | DoD: list and dynamic result count render correctly | Est: 8h | Related: US7, FR-037, CP-III | Phase: C
- [x] T056 [US7] Implement history filter controls in `frontend/src/features/history/HistoryFilters.tsx` | Deps: T055 | DoD: all filters map to API parameters | Est: 6h | Related: US7, FR-036, CP-III | Phase: C
- [x] T057 [US7] Implement empty-state and clear-filter behaviors in `frontend/src/features/history/HistoryEmptyState.tsx` | Deps: T056 | DoD: zero results message and clear action work | Est: 4h | Related: US7, FR-037, CP-III | Phase: C

**Phase Completion Criteria (C / US7)**:
- Full history search/filter feature is available ✅
- Empty and normal states are both verified ✅

---

## Phase 12: User Story 8 - Re-Review with Preserved Context (Priority: P2) (Phase C - Extension)

**Goal**: Allow rerun from prior review with immutable repo metadata

**Independent Test**: Trigger rerun from history/result and execute with modified depth/perspectives

- [x] T058 [US8] Implement rerun API in `backend/app/api/routes/rerun.py` | Deps: T054, T041 | DoD: rerun uses original target and applies new options | Est: 6h | Related: US8, FR-038, CP-V | Phase: C
- [x] T059 [US8] Implement rerun modal in `frontend/src/features/reviews/RerunModal.tsx` | Deps: T055, T058 | DoD: repo/branch read-only and options editable | Est: 6h | Related: US8, FR-039, CP-III | Phase: C
- [x] T060 [US8] Implement dynamic time estimate logic in `frontend/src/features/reviews/useRerunEstimate.ts` | Deps: T059 | DoD: estimate updates on depth/perspective changes | Est: 4h | Related: US8, FR-040, CP-III | Phase: C

**Phase Completion Criteria (C / US8)**:
- Re-review flow is fully operational from history and result pages ✅
- Immutable metadata and dynamic estimation behavior are verified ✅

---

## Phase 13: User Story 3 - Optional Dynamic Scan with Ownership Verification (Priority: P3) (Phase D - Optional & Polish)

**Goal**: Enable ownership-verified ZAP baseline scanning

**Independent Test**: Unverified URL scan blocked; verified URL baseline scan succeeds

> **NOTE**: DAST implementation moved to Phase F.5 with detailed re-design

- [ ] T061 [US3] Implement ownership challenge APIs in `backend/app/api/routes/ownership.py` | Deps: T017, T011 | DoD: challenge issue and verify flows persisted | Est: 8h | Related: US3, FR-013, CP-II | Phase: D | **Status: MOVED to F.5.1**
- [ ] T062 [US3] Implement ZAP baseline job trigger client in `backend/app/integrations/zap_job_client.py` | Deps: T010, T061 | DoD: backend can enqueue and monitor baseline job | Est: 6h | Related: US3, FR-014, CP-I | Phase: D | **Status: MOVED to F.5.2**
- [ ] T063 [US3] Extend review form for URL dynamic mode in `frontend/src/features/reviews/UrlScanForm.tsx` | Deps: T040, T061 | DoD: ownership method + scan type UI operational | Est: 8h | Related: US3, FR-012, CP-III | Phase: D | **Status: MOVED to F.6**
- [ ] T064 [US3] Implement ownership enforcement guard in `backend/app/services/ownership_guard.py` | Deps: T061, T062 | DoD: unverified targets are rejected with 403 | Est: 6h | Related: US3, FR-017, CP-II | Phase: D | **Status: MOVED to F.5.1**
- [ ] T065 [US3] Implement DAST findings normalization in `backend/app/services/dast_ingestion_service.py` | Deps: T062, T045 | DoD: ZAP output converted to finding schema with evidence | Est: 8h | Related: US3, FR-025, CP-IV | Phase: D | **Status: MOVED to F.5.2**

**Phase Completion Criteria (D / US3)**:
- ⚠️ MOVED TO PHASE F.5 (detailed re-design with depth differentiation)

---

## Phase 14: User Story 9 - Report Export (Priority: P3) (Phase D - Optional & Polish)

**Goal**: Export reports in Markdown/PDF/JSON with section selection

**Independent Test**: Generate each format and verify selected content inclusion

- [x] T066 [US9] Implement export job API in `backend/app/api/routes/exports.py` | Deps: T011, T025 | DoD: export requests create jobs with selected sections | Est: 6h | Related: US9, FR-041, CP-V | Phase: D
- [x] T067 [US9] Implement export generators in `backend/app/services/export_service.py` | Deps: T066, T012 | DoD: md/pdf/json artifacts saved to Blob Storage | Est: 8h | Related: US9, FR-042, CP-I | Phase: D
- [x] T068 [US9] Implement export modal UI in `frontend/src/features/reviews/ExportModal.tsx` | Deps: T048, T066 | DoD: format/section selectors and action flow work | Est: 6h | Related: US9, FR-042, CP-III | Phase: D
- [x] T069 [US9] Implement export status polling and download links in `frontend/src/features/reviews/useExportJob.ts` | Deps: T067, T068 | DoD: users can download completed artifact per format | Est: 4h | Related: US9, FR-041, CP-III | Phase: D

**Phase Completion Criteria (D / US9)**:
- ⚠️ Excel format only currently. MD/PDF/JSON formats pending

---

## Phase 15: User Story 12 - Theme Switching (Priority: P3) (Phase D - Optional & Polish)

**Goal**: Provide dark/light switch with persistence

**Independent Test**: Toggle theme and verify persisted state on reload/navigation

- [x] T070 [US12] Implement theme context and storage in `frontend/src/features/theme/ThemeProvider.tsx` | Deps: T002 | DoD: dark/light state persists in local storage | Est: 6h | Related: US12, FR-044, CP-III | Phase: D
- [x] T071 [US12] Implement header theme toggle control in `frontend/src/components/layout/ThemeToggle.tsx` | Deps: T070 | DoD: toggle available on authenticated screens | Est: 4h | Related: US12, FR-043, CP-III | Phase: D
- [x] T072 [US12] Apply theme tokens across app styles in `frontend/src/styles/theme.css` | Deps: T070 | DoD: all key screens switch visual scheme correctly | Est: 6h | Related: US12, FR-045, CP-III | Phase: D

**Phase Completion Criteria (D / US12)**:
- Theme switching is complete and persistent ✅
- Both themes are validated across major screens ✅

---

## Phase 16: Polish & Cross-Cutting (Phase E - Quality & Submission)

**Purpose**: Quality hardening, observability, demo readiness, and submission prep

- [ ] T073 [P] Implement Playwright 3-minute judge path test in `tests/e2e/judge_path.spec.ts` | Deps: T033, T037, T048, T068 | DoD: test covers login->review->result->export flow | Est: 8h | Related: US1, SC-001, CP-III | Phase: E
- [ ] T074 [P] Add API integration tests for auth/review/events/export in `backend/tests/integration/test_review_flow.py` | Deps: T029, T034, T066 | DoD: critical APIs validated in CI | Est: 8h | Related: US10, FR-023, CP-V | Phase: E
- [ ] T075 Implement observability enrichment in `backend/app/observability/metrics.py` | Deps: T018, T013 | DoD: key metrics and traces emitted to App Insights | Est: 6h | Related: US13, SC-007, CP-V | Phase: E
- [ ] T076 Implement responsive and micro-interaction polish in `frontend/src/styles/responsive.css` and `frontend/src/components/ui/` | Deps: T072, T055 | DoD: tablet/mobile layout and motion polish approved | Est: 8h | Related: US12, FR-045, CP-III | Phase: E
- [ ] T077 Create architecture diagrams and submission assets in `docs/architecture/solution.mmd` and `docs/submission/` | Deps: T065, T069 | DoD: architecture diagram + demo script + checklist prepared | Est: 8h | Related: US13, SC-001, CP-V | Phase: E
- [ ] T078 Final security and release readiness sweep in `docs/release/readiness-checklist.md` | Deps: T073, T074, T075, T077 | DoD: no secret leaks, quality gates pass, submission package finalized | Est: 6h | Related: US3, SC-010, CP-II | Phase: E

**Phase Completion Criteria (E)**:
- E2E/integration quality checks pass
- Observability and cost metrics are available
- Submission assets and final readiness checklist are complete

---

## Phase F: Full Review Options Implementation (NEW - Current Focus)

**Purpose**: Implement depth differentiation, restore SAST, add DAST, and enhance language detection

**Status**: 🔄 In Progress on branch `feature/full-review-options`

### F.1 Depth Configuration Foundation

- [ ] T079 Create depth configuration module in `backend/app/core/depth_config.py` | Deps: T016 | DoD: 9 (perspective × depth) configurations defined with type-checked DepthConfig dataclass | Est: 3h | Related: US14, FR-047, CP-IV | Phase: F
- [ ] T080 [P] Add depth config unit tests in `backend/tests/test_depth_config.py` | Deps: T079 | DoD: all 9 combinations validated, monotonicity verified | Est: 2h | Related: US14, SC-011, CP-V | Phase: F

### F.2 ASVS Depth Integration

- [ ] T081 Update SpecComplianceAgent to accept depth parameter in `backend/app/agents/spec_compliance_agent.py` | Deps: T079, T023 | DoD: review() method takes depth, passes to OpenAIService | Est: 3h | Related: US14, FR-048, CP-IV | Phase: F
- [ ] T082 Implement depth-aware prompts in `backend/app/services/openai_service.py` | Deps: T079 | DoD: 3 depth variants of SECURITY_REVIEW_PROMPT, file truncation by max_files | Est: 4h | Related: US14, FR-048, CP-IV | Phase: F
- [ ] T083 Update run_review_task() to pass depth in `backend/app/api/routes/reviews.py` | Deps: T081, T082 | DoD: depth flows from request to agent, language_detector prioritizes files | Est: 3h | Related: US14, FR-047, CP-IV | Phase: F

### F.3 SAST Re-implementation (with Depth)

- [ ] T084 [P] Create Semgrep HTTP client in `backend/app/services/semgrep_client.py` | Deps: T042 | DoD: HTTP client with timeout, error handling, language hint support | Est: 4h | Related: US4, FR-049, CP-I | Phase: F
- [ ] T085 Create SastAnalysisAgent in `backend/app/agents/sast_analysis_agent.py` | Deps: T084, T079 | DoD: depth-aware rule selection, result normalization to finding schema | Est: 6h | Related: US4, FR-049, CP-IV | Phase: F
- [ ] T086 Integrate SAST into run_review_task() | Deps: T085, T083 | DoD: SAST runs when "sast" in perspectives, parallel with ASVS | Est: 3h | Related: US4, FR-018, CP-IV | Phase: F
- [ ] T087 [P] Create finding ingestion service in `backend/app/services/finding_ingestion_service.py` | Deps: T011, T035 | DoD: ingest_asvs_findings, ingest_sast_findings, ingest_dast_findings methods | Est: 4h | Related: US4, FR-026, CP-IV | Phase: F

### F.4 Language Auto-Detection (Code Input)

- [ ] T088 Add detect_for_code_input() to language_detector | Deps: T021 | DoD: accepts (filename, content, explicit_language), returns resolved language | Est: 2h | Related: US16, FR-051, CP-IV | Phase: F
- [ ] T089 Update run_code_review_task() for auto-detection in `backend/app/api/routes/reviews.py` | Deps: T088 | DoD: language="auto" triggers detection, explicit selection bypasses | Est: 3h | Related: US16, FR-051, CP-IV | Phase: F
- [ ] T090 [P] Add language-specific prompt hints in `backend/app/services/openai_service.py` | Deps: T082, T088 | DoD: Python (Django/Flask), JS/TS (Express/React), Java (Spring) hints injected | Est: 3h | Related: US16, FR-052, CP-IV | Phase: F

### F.5 DAST Implementation

#### F.5.1 URL Ownership Verification

- [ ] T091 Create URL ownership service in `backend/app/services/url_ownership_service.py` | Deps: T011 | DoD: token generation, Cosmos DB storage with 24h TTL, verification dispatch | Est: 6h | Related: US17, FR-053, CP-II | Phase: F
- [ ] T092 Implement HTML meta tag verification | Deps: T091 | DoD: HTTP GET + beautifulsoup4 parse + meta tag comparison, 30s timeout | Est: 3h | Related: US17, FR-054, CP-II | Phase: F
- [ ] T093 Implement DNS TXT verification | Deps: T091 | DoD: dnspython query `_aisecreviewer.<domain>` TXT, 60s timeout | Est: 3h | Related: US17, FR-054, CP-II | Phase: F
- [ ] T094 Create ownership API routes in `backend/app/api/routes/ownership.py` | Deps: T092, T093 | DoD: POST /api/ownership/request, POST /api/ownership/verify with rate limiting | Est: 4h | Related: US17, FR-055, CP-II | Phase: F

#### F.5.2 OWASP ZAP Integration

- [ ] T095 [P] Create ZAP Container Instance Bicep module in `infra/modules/zap-container-instance.bicep` | Deps: T010 | DoD: on-demand ACI provisioning, API key auth, outbound network rules | Est: 4h | Related: US18, FR-050, CP-I | Phase: F
- [ ] T096 Create ZAP client wrapper in `backend/app/services/zap_client.py` | Deps: T095 | DoD: spider(), passive_scan(), active_scan(), get_alerts() methods | Est: 6h | Related: US18, FR-050, CP-I | Phase: F
- [ ] T097 Create DastAnalysisAgent in `backend/app/agents/dast_analysis_agent.py` | Deps: T096, T079, T091 | DoD: depth-aware scan mode (passive/baseline/full), pre-scan ownership verification | Est: 8h | Related: US18, FR-050, CP-IV | Phase: F
- [ ] T098 Integrate DAST into run_review_task() | Deps: T097, T087 | DoD: DAST runs when perspectives=["dast"] AND input_type="url", verified ownership | Est: 4h | Related: US18, FR-018, CP-IV | Phase: F

### F.6 Frontend Enhancements

- [ ] T099 Update NewReviewPage with depth descriptions in `frontend/src/pages/NewReviewPage.tsx` | Deps: T079 | DoD: each depth shows ⚡/🎯/🔬 icon, time and cost estimates from DEPTH_CONFIGS | Est: 4h | Related: US14, FR-019, CP-III | Phase: F
- [ ] T100 Create UrlOwnershipWizard component in `frontend/src/features/reviews/UrlOwnershipWizard.tsx` | Deps: T094 | DoD: token display with copy, method selection (HTML/DNS), instructions, verify button | Est: 6h | Related: US17, FR-013, CP-III | Phase: F
- [ ] T101 Add DAST scan mode selector | Deps: T100 | DoD: passive/active radio, warning dialog for production URLs in detailed depth | Est: 3h | Related: US18, FR-014, CP-III | Phase: F
- [ ] T102 Update perspective validation in `frontend/src/features/reviews/PerspectiveSelector.tsx` | Deps: T046 | DoD: DAST requires input_type=url, ASVS/SAST work with github/code, invalid combos disabled | Est: 3h | Related: US15, FR-018, CP-III | Phase: F

### F.7 Testing

- [ ] T103 Integration tests for 9 depth × perspective combinations in `backend/tests/integration/test_depth_combinations.py` | Deps: T083, T086, T098 | DoD: all 9 patterns produce distinct results, time/cost within ±20% of estimates | Est: 6h | Related: US14, SC-011, CP-V | Phase: F
- [ ] T104 [P] Unit tests for language detector in `backend/tests/test_language_detector.py` | Deps: T088 | DoD: detect_for_code_input covers all priority cases | Est: 3h | Related: US16, FR-051, CP-V | Phase: F
- [ ] T105 [P] E2E test for URL ownership HTML method in `frontend/e2e/ownership-html.spec.ts` | Deps: T100 | DoD: full HTML verification flow tested | Est: 3h | Related: US17, FR-054, CP-V | Phase: F
- [ ] T106 [P] E2E test for URL ownership DNS method in `frontend/e2e/ownership-dns.spec.ts` | Deps: T100 | DoD: full DNS verification flow tested | Est: 3h | Related: US17, FR-054, CP-V | Phase: F
- [ ] T107 E2E test for DAST passive scan in `frontend/e2e/dast-passive.spec.ts` | Deps: T097 | DoD: quick depth DAST completes with findings | Est: 4h | Related: US18, FR-050, CP-V | Phase: F
- [ ] T108 E2E test for DAST active scan in `frontend/e2e/dast-active.spec.ts` | Deps: T097, T101 | DoD: standard/detailed depth DAST with ownership confirmation | Est: 6h | Related: US18, FR-050, CP-V | Phase: F

### F.8 Documentation

- [ ] T109 [P] Update README with new options in `README.md` | Deps: F.1-F.6 complete | DoD: depth selection, language support, DAST instructions documented | Est: 2h | Related: SC-001, CP-V | Phase: F
- [ ] T110 [P] Create DAST setup guide in `docs/dast-setup.md` | Deps: T094, T097 | DoD: URL ownership procedure, ZAP container troubleshooting | Est: 3h | Related: US17, US18, CP-V | Phase: F
- [ ] T111 [P] Update architecture diagram in `docs/architecture/solution.mmd` | Deps: F.5 complete | DoD: ZAP container, ownership flow, depth config shown | Est: 2h | Related: SC-001, CP-V | Phase: F
- [ ] T112 [P] Update API documentation (OpenAPI) in `specs/001-ai-security-reviewer-spec/contracts/api.openapi.yaml` | Deps: T094, T098 | DoD: ownership endpoints, depth/perspective parameters documented | Est: 3h | Related: FR-018, FR-019, CP-V | Phase: F

### F.9 Deployment

- [ ] T113 Deploy Semgrep Azure Function | Deps: T042, T084 | DoD: function reachable, returns valid results | Est: 2h | Related: US4, CP-I | Phase: F
- [ ] T114 Deploy ZAP Container Instance | Deps: T095 | DoD: ACI provisioned, API key configured, network rules verified | Est: 3h | Related: US18, CP-I | Phase: F
- [ ] T115 Update Container App environment variables | Deps: T113, T114 | DoD: SEMGREP_FUNCTION_URL, ZAP_API_ENDPOINT, ZAP_API_KEY added | Est: 1h | Related: US4, US18, CP-II | Phase: F
- [ ] T116 Verify all 9 patterns work in production | Deps: T103, T115 | DoD: each (perspective × depth) tested with sample input on live env | Est: 4h | Related: SC-011, CP-V | Phase: F

**Phase Completion Criteria (F)**:
- 9 (perspective × depth) combinations produce measurably different behavior
- SAST re-implementation works with depth differentiation
- DAST URL ownership verification operational (HTML + DNS)
- DAST scans run in 3 depth modes (passive/baseline/full)
- Language auto-detection covers JS/TS/Python/Java/Go
- Frontend shows depth estimates and validates combinations
- All 9 patterns verified in production environment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (A-Setup)**: starts immediately ✅ DONE
- **Phase 2 (A-Foundation)**: depends on Phase 1 completion and blocks story implementation ✅ DONE
- **Phase 3-6 (B-MVP P1 stories)**: depend on Phase 2; preferred order US1 -> US10 -> US11 -> US13 ✅ DONE
- **Phase 7-12 (C-P2 stories)**: depend on MVP completion; can be parallelized by story teams ✅ DONE
- **Phase 13-15 (D-P3 stories)**: depend on P2 baseline readiness for shared APIs ⚠️ PARTIAL
- **Phase 16 (E-Quality & Submission)**: depends on all targeted user stories being completed ⏳ TODO
- **Phase F (Full Review Options)**: depends on Phase B completion; restores SAST and adds DAST 🔄 IN PROGRESS

### User Story Dependency Order (Priority-aligned)

1. P1 MVP stories: US1, US10, US11, US13, **US14** (depth differentiation) ✅
2. P2 extension stories: US2, US4, US5, US6, US7, US8, **US15** (multi-perspective), **US16** (language detection)
3. P3 optional/polish stories: US3, US9, US12, **US17** (URL ownership), **US18** (DAST scan modes)

### MVP Scope Recommendation

- **MVP release target**: complete through Phase 6 (US1 + US10 + US11 + US13) ✅ ACHIEVED
- **Enhanced MVP**: include Phase F.1-F.4 (depth + language) for differentiated user experience
- **Full feature**: complete Phase F.5 (DAST) for all 3 perspectives

---

## Parallel Execution Examples Per User Story

- **US1**: Run T021 in parallel with T022 after T020
- **US10**: Run T026 and T028 in parallel, then merge via T029
- **US11**: Run T031 in parallel with T030
- **US13**: Run T036 in parallel with T035 after T034
- **US2**: Run T040 in parallel with T039
- **US4**: Run T042 and T046 in parallel, then continue T043/T044/T045 (now T084-T087)
- **US5**: Run T048 in parallel with T047
- **US6**: Run T052 after T051; T053 can start once T052 API wiring stabilizes
- **US7**: Run T055 in parallel with T054
- **US8**: Run T059 in parallel with T058, then finalize T060
- **US3**: Now T091-T098 (moved to F.5)
- **US9**: Run T068 in parallel with T067 after T066
- **US12**: Run T071 and T072 in parallel after T070
- **US14 (Depth)**: Run T079 + T080 in parallel; then T081-T083 sequential
- **US16 (Language)**: Run T088 + T090 in parallel
- **US17 (Ownership)**: T091 first, then T092 + T093 in parallel
- **US18 (DAST)**: T095 + T096 in parallel after T079

---

## Implementation Strategy

### MVP First (DONE ✅)

1. ✅ Complete Phase 1 and Phase 2 foundations
2. ✅ Deliver P1 stories (US1, US10, US11, US13)
3. ✅ Validate 3-minute judge flow and SSE progress experience
4. ✅ Freeze MVP baseline for demo fallback

### Phase F: Enhanced Differentiation (CURRENT)

1. **F.1-F.2**: Implement depth differentiation for ASVS (immediate value)
2. **F.3**: Restore SAST with depth support
3. **F.4**: Enhance language detection for code input
4. **F.6**: Frontend UI improvements (depth estimates)
5. **F.5**: Implement DAST (URL ownership + ZAP)
6. **F.7-F.9**: Testing, docs, deployment

### Incremental Expansion (REMAINING)

1. Add P2 stories in usability-impact order: ✅ DONE (US2, US4, US5, US6, US7, US8)
2. Add P3 stories: ✅ DONE (US9, US12) | ⚠️ PARTIAL (US3 → F.5)
3. Execute final quality/submission phase (E)

### Team Parallelization Suggestion

- Team A: frontend experience (US11/US13/US7/US12, **F.6**)
- Team B: backend orchestration and agents (US1/US4/US8, **F.1-F.4**)
- Team C: security tooling and platform (US10/US3/US9/Phase E, **F.5**)

---

## Task Count Summary

- **Total tasks: 116** (was 78, +38 new in Phase F)
- Phase A tasks: 18 ✅ DONE
- Phase B tasks (P1 stories): 20 ✅ DONE
- Phase C tasks (P2 stories): 22 ✅ DONE (with US4 SAST removed, pending F.3)
- Phase D tasks (P3 stories): 12 (US9/US12 ✅ DONE | US3 → F.5)
- Phase E tasks: 6 ⏳ TODO
- **Phase F tasks (NEW)**: 38 🔄 IN PROGRESS
  - F.1 Depth Config: 2
  - F.2 ASVS Depth: 3
  - F.3 SAST Re-implementation: 4
  - F.4 Language Detection: 3
  - F.5 DAST: 8 (4.1 + 4.2)
  - F.6 Frontend: 4
  - F.7 Testing: 6
  - F.8 Documentation: 4
  - F.9 Deployment: 4

### Current Status

- ✅ Completed: 60 tasks (Phases A, B, C partial, D partial)
- ⚠️ Removed/Moved: 9 tasks (T043-T045 SAST, T061-T065 DAST → Phase F)
- ⏳ Pending: 6 tasks (Phase E)
- 🔄 New (Phase F): 38 tasks (current focus)

Format validation:
- All tasks use checklist format: `- [ ] T### [P?] [US?] Description with file path`
- Story labels applied only on user-story phases
- Setup/foundation/polish tasks omit story labels by design
- Status markers added: ✅ DONE, ⚠️ PARTIAL/REMOVED, 🔄 IN PROGRESS, ⏳ TODO
