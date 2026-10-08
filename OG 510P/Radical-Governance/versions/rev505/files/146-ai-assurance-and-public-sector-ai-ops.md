# AI Assurance & Public-Sector AI Ops (from registry → running system)

**Stack relation:** use `301-digital-governance-data-interoperability-and-algorithmic-assurance-routing-guide.md` for the canonical route across the digital-governance / data / interoperability / algorithmic-assurance family. This memo is the runtime assurance / AI-ops specialization; `152` is the ex ante impact-assessment front door; `42` is the ADS / model-inventory substrate; `191` is the public registry / audit-rails specialization; `173` is the standards / legal-mapping neighbor.

**Problem:** Many governments can *inventory* algorithmic tools but still fail at *operational accountability* (quiet model swaps, unseen drift, “automation creep,” vendor opacity, unbounded copilots, and incident learning that never closes).

**Design goal:** Treat AI as **governance infrastructure** with an *assurance pipeline* that is (a) joinable to decisions, (b) renewable at change points, and (c) audit/incident-ready by default.

**Cross-links:** Algorithmic Impact Assessment + public AI governance (`152`), Model/ADS inventory (`42`), records/receipts (`31`), rule change control (`118`), audits (`130`), evaluation (`133`), safety cases (`73`, `139`), procurement integrity (`110`), data governance (`127`), interoperability (`128`), legitimacy protocols (`106`).

**See also:** `173-ai-standards-and-regulatory-mapping.md` (law/standards ↔ ops mapping)

---

## 1) Minimal artifacts (small set; high leverage)

### A. **AI Service Card** (`AIS-*`) — one page, public by default
A service-level view for an AI-mediated capability (including copilots used by staff when they affect outcomes).

**Must include:**
- **Purpose & mandate** (links to `MC-*` if applicable).
- **Decision surface**: what decisions or recommendations it can influence.
- **Model lineage**: pointer(s) to `MOD-*` / `ADS-*` in the registry (`42`).
- **Data boundary**: what data classes it uses and any prohibited joins (`127`).
- **Human role**: when humans must review/override; disallowed delegations (“no rubber stamp”).
- **Contestability**: the appeal lane / ombuds path (`36`, `08`) and how to request explanation.
- **Monitoring**: key harms to watch (bias, error asymmetry, privacy leakage, safety).

**Notes:** This is the “interface object” used by policy, legal, engineers, auditors, and the public.

### B. **Assurance Case Card** (`AICC-*`) — a compact claim → evidence map
This is a safety/assurance case *adapted* for AI-mediated public services:
- **Top claims** (bounded): e.g., “Model X is fit-for-purpose for task Y under constraints Z.”
- **Evidence pointers**: evaluation reports (`EFR-*`), red-team findings, audits (`AFR-*`), incident learning (`IRR-*`).
- **Assurance receipt**: a time-bounded `SACR-*` style receipt at go-live + after material change (`139`).

Anchor the assurance format to risk management baselines like **NIST AI RMF** and (where used) management-system controls like **ISO/IEC 42001**. ([BIB-NIST-AIRMF], [BIB-ISO-42001-2023])

### C. **Material Change Receipt** (`AICR-*`) — “no silent model swap”
Any material change must produce a joinable receipt:
- Model/version swap, data source swap, threshold change, prompt/policy change, fine-tune, retraining, vendor change.
- Links to: rule change receipt (`RCR-*` if rule impacts), test results, updated AICC, and updated `AIS-*`.

### D. **AI Incident Receipt** (`AIIR-*`) — reversible-by-default learning loop
When the system harms or degrades:
- incident classification + scope + affected groups
- immediate protections / rollback trigger
- notifications to oversight (audit/inspector) and to affected people where feasible
- post-incident learning committed to `LR-*` and evaluation (`133`)

---

## 2) Procurement + vendor boundary (make opacity expensive)

**Rule:** if a vendor can’t support the join surfaces, the system is not “deployable in government.”

Add (or require via policy) procurement clauses consistent with `110`:
- **Right to audit** (incl. subcontractors), model cards / eval reports disclosure.
- **Change-control obligations** (vendor must issue `AICR-*`-compatible change notices).
- **Logging + export**: event logs and decision-support logs exportable in open formats.
- **Contestability support**: vendor must support explanations, correction workflow, and appeals evidence packages.
- **Termination & portability**: government can migrate with continuity (avoid vendor lock-in).

When a jurisdiction has a legal framework (e.g., EU AI Act) treat those requirements as part of the *minimum deployable* baseline rather than “extra compliance.” ([BIB-EU-AIACT])

---

## 3) Transparency: inventory is necessary but not sufficient

- The **ATRS** (UK) is a useful template for public disclosure about algorithmic tools, but the critical move is: connect disclosure → operational receipts (`AIS/AICC/AICR/AIIR`). ([BIB-UK-ATRS])
- If the law requires public disclosure, measure compliance as an integrity metric (missing records are governance incidents). (ATRS hub/mandate discussions provide a cautionary story about registers being underfilled.) ([BIB-UK-ATRS])

---

## 4) Copilots and “assistive AI” (the hidden surface)

Many high-stakes harms arrive via *staff-facing* AI:
- drafting notices, translating evidence, triaging queues, recommending sanctions, suggesting interview questions.

**Policy:** treat staff copilots as decision-support systems when they can influence outcomes.

Operational requirements:
- **AIS** must cover copilots used in workflows.
- Logs must show *when* staff used AI assistance for a given case (joinable to `DRR-*` when feasible).
- Prohibit automation of “reason giving”: decisions must remain reasoned and contestable (`31`, `106`).

---

## 5) Deployment tiers (avoid one-size-fits-all)

**Tier 0 — non-impacting tools:** informational copilots with no case impact (still data-bound).

**Tier 1 — advisory:** recommendations to staff; requires AIS + minimal AICC.

**Tier 2 — high-impact support:** triage, eligibility scoring, enforcement targeting; requires AIS + AICC + incident receipts + audit-ready logging.

**Tier 3 — safety-critical / rights-critical:** health, custody, critical infrastructure, asylum, sanctions; requires full safety-case discipline (`139`) + independent audit cadence (`130`) + evaluation triggers (`133`).

---

## 6) Failure modes checklist (use in design reviews)

- **Quiet swaps:** model changed without public receipt (`AICR-*`).
- **Automation creep:** tool starts influencing decisions beyond stated purpose.
- **Evidence laundering:** AI outputs treated as “objective” without provenance.
- **Appeal dead-ends:** no pathway to challenge AI-affected decisions.
- **Drift blindness:** monitoring exists but has no circuit breaker.
- **Vendor opacity:** no logs, no export, no audit rights.

---

## 7) Hooks to add elsewhere

- Add an `AIS-*` pointer field to `42-automated-decision-systems-and-model-registry.md` so each model/system entry links to its service surface.
- Add a procurement “AI deployability checklist” row to `110-budget-procurement-integrity.md`.

