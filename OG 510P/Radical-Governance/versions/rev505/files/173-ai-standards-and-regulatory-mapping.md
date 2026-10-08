# 173 — AI Standards & Regulatory Mapping (joinable compliance without checkbox theater)

**Stack relation:** use `301-digital-governance-data-interoperability-and-algorithmic-assurance-routing-guide.md` for the canonical route across the digital-governance / data / interoperability / algorithmic-assurance family. This memo is the law / standards / conformance mapping neighbor; `152` is the ex ante impact-assessment front door; `146` is runtime assurance and AI-ops discipline; `42` / `191` are the registry and audit substrates.

**Purpose:** help public institutions (and their vendors) align **law**, **standards**, and **operational controls** so AI governance is *auditable*, *contestable*, and resistant to “paper compliance.”

**Person served:** anyone affected by an automated / AI‑assisted decision who needs: (1) a clear decision owner, (2) a meaningful appeal path, and (3) evidence that the system was safe *in their case*.

**Use with:** `146-ai-assurance-and-public-sector-ai-ops.md` (runtime ops), `152-algorithmic-impact-assessment-and-public-ai-governance.md` (AIA as a joinable artifact), `162-procurement-as-governance-lever-and-guardrails.md` (contract leverage), `115-information-integrity-and-record-interfaces.md` (records).

---

## The problem this memo solves

Most systems fail at the seam between:
- **Regulatory duties** (what must be true)
- **Standards** (how to organize management + controls)
- **Operational reality** (what actually happens at runtime)

Result: *silent model swaps*, vendor opacity, unscoped copilots, and “risk assessments” that never touch the live system.

This memo gives a **mapping layer**: a small set of join‑keys that let you trace from **law/standard → control → evidence → incident learning**.

---

## Minimum join‑keys (non‑negotiable)

Every governed AI/algorithmic system MUST have:
1. **System ID + version lineage** (what is it; what changed; when; why) — no silent swap.
2. **Purpose & decision boundary** (what decisions it can influence; what it MUST NOT do).
3. **Risk tier + justification** (with scope test + citations).
4. **Impact profile** (who can be harmed; severity; distribution).
5. **Controls map** (controls → tests → monitoring → owners).
6. **Evidence bundle** (model/data cards, evals, red‑team results, incident history).
7. **Appeals & human override protocol** (including time budgets).
8. **Procurement bindings** (audit rights, logging, escrow/portability, remedies).

These join‑keys are the spine connecting: **AIA** (`152`) + **AI Ops Registry** (`146`) + **contract rails** (`162`).

---

## Mapping: EU AI Act ↔ ISO/IEC 42001 ↔ NIST AI RMF ↔ Archive artifacts

| Governance requirement (plain language) | EU AI Act (law) | ISO/IEC 42001 (AIMS) | NIST AI RMF (voluntary) | Archive artifact(s) |
|---|---|---|---|---|
| Know what AI you run; classify risk; keep docs | Risk-based obligations for AI systems | Management system + documented processes | “Govern” function; RM context | `146`, `152`, `115` |
| Prevent unsafe / biased outcomes via testing + monitoring | High-risk style obligations (risk mgmt, data, logging, human oversight) | Risk assessment + lifecycle management | “Map/Measure/Manage” + metrics | `152`, `37-claims-evidence-and-update-discipline.md`, `104` |
| Keep logs and make decisions contestable | Traceability / record obligations | Documentation & operational controls | Measurement + governance | `115`, `172-administrative-justice-complaints-ombuds-mesh.md` |
| Assign accountable owners (no “vendor did it”) | Provider/deployer responsibilities | Roles, responsibilities, accountability | Governance | `09`, `113`, `162` |
| Run sandboxes / controlled deployments | AI sandboxes (implementation tool) | Continual improvement + controlled change | Risk management lifecycle | `171-constitutional-maintenance-and-amendment-ops.md` (change control patterns), `146` |

**Important:** the archive’s stance is *person-facing*: the “compliance” output is not a PDF — it’s a **joinable evidence graph** that an affected person (or advocate) can query and contest.

---

## Implementation pattern: “Compliance as a running system”

1. **AIA first** (`152`) — publish a minimal, queryable impact assessment with scope boundaries.
2. **Register + operate** (`146`) — monitoring, incident response, model swap discipline.
3. **Bind contracts** (`162`) — audit rights, logging requirements, portability, remedies.
4. **Emit records** (`115`) — decision notices + explanation interface + retention guarantees.
5. **Close the loop** (`104`) — incidents update controls; controls update procurement; procurement updates scope.

---

## Anti-patterns (ban list)

- **Checkbox assessments** with no linkage to runtime monitoring.
- **Vendor-only evaluation** with no independent test harness or audit rights.
- **Non-joinable artifacts** (PDFs without IDs, versions, or machine-readable keys).
- **“Human-in-the-loop” theater** (no override authority, time, or training).

---

## Citations

- EU AI Act overview (official EU portal): [BIB-EC-AIACT-HUB-2026]
- ISO/IEC 42001 AIMS standard: [BIB-ISO-42001-2023]
- NIST AI RMF 1.0 (PDF): [BIB-NIST-AIRMF]
