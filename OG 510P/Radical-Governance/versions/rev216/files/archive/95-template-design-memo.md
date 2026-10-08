# Template: Design Memo

**Purpose:** provide a standard, from‑below design memo template that keeps mechanisms tied to lived harms and agency.

**Scope:**  
**Problem class:** (collective action / distribution / externalities / violence / information)  
**Primary advantage:**  
**Primary risk:** (choose `TM-*` from `04-threat-models.md`)
**Baseline + decision loop (GATE-0):** (pick ≤10 metric IDs + name the decision hook / review cadence)

### Optional front matter (for scope designs)
If this memo is primarily a **scope design** (new unit, tier, or major scope transfer), prepend a **one-screen scope card** (see “Scope card schema” in `14-scope-ladder.md`).

**Person served (one sentence):** name the concrete person or community most affected (especially low-literacy/low-trust/time‑poor people) and what they need from this design.

**Moral stake (one sentence):** state what power owes the person/community here (the obligation this mechanism makes enforceable), in plain language.

**Experiences addressed (98 §A):** list the 1–3 primary `EXP-*` experiences this design is meant to reduce (e.g., `EXP-01` opacity, `EXP-04` error).

**Mechanism justification (one sentence):** for any new register/join-key/interface, complete: “This exists because without it, the person cannot **see / challenge / correct** a specific exercise of power.” If you can’t, don’t add it—refactor instead.

## Kernel anchors (do not repeat)
- Person-facing path + accessibility floors: `98-persons-path-and-accessibility-invariants.md`.
- Receipts/records and comprehension test: `31-records-foi-and-government-memory.md`.
- Remedy lanes and safe contestation (incl. representation/collective filing): `08-remedy-and-grievance.md` + `36-appeal-lanes-and-redress-registry.md`.
- Interface obligations and join-key map: `71-interface-obligations-by-scope.md` + `70-interoperability.md`.
- Protective legibility / adoption dynamics (transparency ≠ safety): `99-protective-legibility-and-adoption-dynamics.md` (and secrecy where relevant: `77-sensitive-information-and-secrecy-governance.md`).

## Named tensions (design must surface these)
Pick 3–6 that actually apply and write them down (don’t smuggle tradeoffs):
- Speed/throughput vs due process and correctness.
- Legibility/joinability vs privacy/safety/retaliation.
- Standardization vs plural functional equivalents.
- Accountability vs cruelty (avoid punishing the vulnerable to discipline institutions).

## 0) Framing (GATE-0)
- What happens if we do nothing?
- What discretion expands (if any), and what trace artifacts will constrain it (`DRR`, `RULE`, registers)?
- Top 3 `TM-*` threats + smallest countermeasure each.
- If this expands high-discretion power (coercion/emergency/ADS/critical infrastructure), attach or reference an `AC-*` assurance case (see `73-...` and `IOP-26`).
- If this creates/changes a high-impact `RULE-*` or `PROG-*`, set the review clock and publish a one-screen review packet now (metrics + distributional check + remedy health + renewal standard) (see `74-...` and `IOP-28`).
- If this is a live pilot/sandbox (rule-relief for testing), pre-commit stop conditions + exit artifacts (see `86-regulatory-experimentation-and-sandboxes.md`).
- **Person’s Path check:** name the concrete person(s) most affected (low literacy, low trust, limited time/digital access) and confirm the interface works for them: **comprehension‑tested receipts**, **no‑wrong‑door** routing, **safe remedy** (incl. representation) and an offline channel where needed (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `47-...`).




### Optional: scope assignment record (for boundary/mandate/authority changes)
If this memo **creates, transfers, or materially expands** a mandate (new authority, delegation via compact, boundary change), treat it as a scope decision and produce a `DRR` tagged `DRR-TYPE: SCOPE` (see `IOP-10` in `02-design-toolkit.md`) that records:
- local-knowledge / spillover / scale / rights-risk / enforceability tests,
- funding alignment (who pays/bears residual risk),
- competence-ledger change (old → new entry/version + effective date),
- remedy continuity plan (appeals during/after transition),
- review/sunset trigger.




### Optional: testable claims (for major proposals)
If this memo proposes a major program/policy (high spend, rights-affecting, or high-discretion), create or reference ≥1 `CLM-*` claim ID describing predicted effects, key metric IDs, baseline (`REL` where possible), harms/guardrails, and a review trigger. Link evaluation commitments (`EVAL-*`) as available. See `37-claims-evidence-and-update-discipline.md` and `28-program-register-and-evaluation-commitments.md`.
### Optional: assurance case (for high-discretion power)
If this memo authorizes or materially expands high-discretion power (coercion, emergency authority, high-stakes ADS, critical infrastructure operations, cross-boundary regimes with weak exit), publish or reference an `AC-*` assurance case summary that names top claims, threats (`TM-*`), evidence docket pointers, monitoring thresholds, stop/review triggers, and remedy lanes (`AL-*`). See `73-assurance-case-and-governance-safety-case.md` and `IOP-26`.

## 1) What this level must own (and nothing else)
- 3–7 bullets

## 2) Minimum Viable Government (MVG)
- institutions that MUST exist for basic legitimacy + capability (reference toolkit modules)

## 3) Ideal institutional stack (bounded)
- 3–6 components, each with:
  - mandate
  - selection/appointment
  - accountability hooks

## 4) Interfaces (how it plugs into the rest)
- upward/downward protocols (cite `70-interoperability.md`)
- interface obligations: ensure required artifacts are emitted for this scope (see `71-interface-obligations-by-scope.md`).
- legal legibility: cite rule authority with stable Rule IDs where possible; point to the public rules register (`25-legal-legibility-and-rule-inventory.md`).
- epistemic legibility: where metrics are cited, prefer referencing a Release ID (dataset/series) with methods + revision logs (`26-epistemic-infrastructure-and-public-knowledge.md`).
- policy learning: for major programs/policies, cite stable `PROG-*` IDs and `EVAL-*` IDs (decision hooks) where applicable (`28-program-register-and-evaluation-commitments.md`).
- standards legibility: if a technical standard is required/incorporated/procurement-required, reference a stable `STD-*` ID and point to the Public Standards Register (`27-standards-and-technical-governance.md`).
- records legibility: rights-/resource-affecting decisions produce a retrievable **Decision Record/Receipt** with a stable Decision ID (`DRR`), reasons, legal basis (Rule IDs where possible), and appeal lane (`AL-*`; see ALR `36-...`) (`31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md`).
- personal data legibility: if personal data processing or sharing is central, reference `DPR-*` IDs (processing inventory) and the enforceable access/correction/remedy path (`LAW-8`; see `33-data-protection-and-personal-data-governance.md`).
- oversight legibility: major audits/investigations/pattern reports use stable Finding IDs and are tracked to closure via an Oversight Files & Responses Register (OFRR) (`ACC-6`; see `32-oversight-institutions-and-follow-through.md`).
- permissioning legibility: if permits/licences/approvals are central, reference Permit IDs and point to a public Permit/Approval Register (PAR) (`LAW-7`; see `29-permissioning-and-approvals.md`).
- register discipline: any new public register MUST assign stable IDs, publish a change log, and provide a machine-readable feed (see `IOP-9` and `70-interoperability.md`).

## 5) Success metrics
- pick **≤10** measures, preferably by referencing **metric IDs** from `03-metrics-and-evidence.md` (packs like `[LRR-4]`, `[IPM-2]`).

## 6) Failure modes + countermeasures
- map to `TM-*` threats (`04-threat-models.md`) and toolkit modules

## 7) Sources / anchors (keep tight)
- List the minimum `[BIB-*]` keys used (from `90-bibliography.md`).
- If you must add an inline URL, treat it as provisional; if it shows up in **2+ memos**, promote it to a `[BIB-*]` key in `90-bibliography.md` and replace inline URLs with `see [BIB-…]`.

## Design checks (do not ship without)
- [ ] Appears in the competence ledger (or explicitly has **no** decision authority).
- [ ] Produces a Decision Record/Receipt (`DRR`) for rights-/resource-affecting decisions (reasons + legal basis) and names the remedy path (stop/review/enforce).

- [ ] **Receipts are usable:** any person-facing receipt/notice passes the **comprehension test** (What? Why? What now/by when?) and includes navigation details (what to submit, cost/fee disclosure where applicable, assistance availability) (`98-persons-path-and-accessibility-invariants.md`, `31-...`).
- [ ] **Remedy is safe to use:** confidentiality/anonymous options where feasible; anti‑retaliation pathway; representation/collective filing options for low-capacity or high-risk contexts (`08-...`, `36-...`, `83-...`, `98-persons-path-and-accessibility-invariants.md`).
- [ ] **Delay/proof burdens are governed:** service time promises distinguish ack/first contact/final decision and publish tail waits; publish proof burden inventory + once‑only checks for missing-doc denials (`47-...`, `82-...`).
- [ ] **Protective legibility check:** name the enforcement/countervailing-power preconditions (standing, funding, independent oversight) and avoid registry weaponization (minimize centralization; secrecy/withholding receipts where needed) (`99-protective-legibility-and-adoption-dynamics.md`, `77-...`, `33-...`).

- [ ] If this memo creates/transfers mandates or creates a new authority/compact: produces a `DRR-TYPE: SCOPE` record and links the competence-ledger diff (see `IOP-10`).
- [ ] Names ≤10 metrics + the decision hook that uses them.
- [ ] Names top 3 `TM-*` threats and the smallest countermeasure for each.
- [ ] Defines interfaces: registers/IDs and escalation across scopes.
- [ ] Includes a sunset/review cadence for high-stakes powers and exceptions (and, where relevant, a deprecation/decommission plan; see `74-sunsetting-and-deprecation-discipline.md`).