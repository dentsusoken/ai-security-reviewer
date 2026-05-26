<!--
Sync Impact Report
Version change: template-draft -> 1.0.0
Modified principles:
- template principle 1 -> I. Azure-Native Managed-First Technical Foundation
- template principle 2 -> II. Secure-by-Default Service and Data Protection
- template principle 3 -> III. Judge-Centric Demo UX
- template principle 4 -> IV. Evidence-Backed Multi-Agent Intelligence
- template principle 5 -> V. Spec-Driven Delivery Discipline
Added sections:
- Delivery Constraints and Scope Boundaries
- Execution and Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
- ✅ .specify/templates/tasks-template.md
- ⚠ pending .specify/templates/commands/*.md (directory not present in this repository)
Follow-up TODOs:
- None
-->
# AI Security Reviewer Constitution

## Core Principles

### I. Azure-Native Managed-First Technical Foundation
All production-facing components MUST prioritize Azure managed services to minimize
operations overhead and delivery risk for the hackathon timeline. The system MUST use
Azure AI Agent Service as the center of the agentic architecture, MUST define all cloud
resources with Bicep, and MUST keep all secrets in Azure Key Vault only.
Rationale: managed services and reproducible IaC maximize delivery speed and lower
misconfiguration risk under tight deadlines.

### II. Secure-by-Default Service and Data Protection
The platform MUST be secure by default in every environment. Authentication MUST be
Microsoft Entra ID for all human access, user-provided input MUST be validated before
processing, and all prompts or tool inputs sent to AI components MUST be sanitized.
Any DAST target URL MUST pass explicit ownership verification before scanning starts.
Rationale: a security-review product loses credibility if the product itself is unsafe.

### III. Judge-Centric Demo UX
Every feature slice MUST support a demo where judges can understand the value within
3 minutes. Long-running review operations MUST stream progress and intermediate
results to the UI, and all user-facing screens MUST support both dark and light themes.
Rationale: rapid comprehension and visible progress are essential for hackathon impact.

### IV. Evidence-Backed Multi-Agent Intelligence
Security analysis MUST be executed by collaborating agents with explicit role
separation; a single monolithic prompt is prohibited for core review logic. Every
finding MUST include machine-readable evidence and an explicit normative reference,
such as ASVS requirement mapping. LLM responses MUST be treated as untrusted until
cross-checked against tool execution outputs and retrieved evidence.
Rationale: verifiable, grounded findings are required for trustworthy security review.

### V. Spec-Driven Delivery Discipline
All work MUST follow Spec-Driven Development through the sequence
specification -> implementation plan -> tasks -> implementation. Each phase MUST
produce committed artifacts in Git before the next phase begins, with traceability from
requirements to code changes.
Rationale: strict phase gates preserve quality, auditability, and team alignment.

## Delivery Constraints and Scope Boundaries

- The primary target is a hackathon submission due 2026-06-01; trade-offs MUST favor
	demonstrable end-to-end value over broad feature expansion.
- The demo baseline MUST support 8 screens, dark and light themes, three review
	perspectives (ASVS, SAST, DAST), and three cooperating AI agents.
- Existing BI tooling in React/JavaScript MAY be used as demonstration input, but
	integration boundaries MUST be documented in feature specifications.

## Execution and Quality Gates

- A plan passes Constitution Check only when it defines: Azure managed service choices,
	Bicep coverage, Key Vault secret flow, Entra ID auth flow, input sanitization,
	DAST ownership verification, and evidence mapping for findings.
- A specification is complete only when measurable UX outcomes include
	3-minute judge comprehension and streaming progress behavior.
- A task list is complete only when it includes explicit tasks for security controls,
	evidence pipeline implementation, and phase-level Git commits.
- Pull requests MUST include a constitution compliance statement and identify any
	approved exceptions.

## Governance

This constitution is authoritative for architecture, security, UX, AI behavior, and
delivery process decisions in this repository.

Amendment process:
1. Propose changes in a dedicated constitution update.
2. Document rationale, impacted principles, and template propagation changes.
3. Obtain explicit maintainer approval before merge.

Versioning policy:
- MAJOR: incompatible redefinition or removal of a principle or governance rule.
- MINOR: new principle or materially expanded mandatory guidance.
- PATCH: clarifications, wording improvements, and non-semantic refinements.

Compliance review expectations:
- Every plan, spec, tasks document, and pull request MUST be checked against this
	constitution.
- Non-compliance MUST be resolved before merge or tracked as an explicit,
	time-bounded exception.

**Version**: 1.0.0 | **Ratified**: 2026-05-26 | **Last Amended**: 2026-05-26
