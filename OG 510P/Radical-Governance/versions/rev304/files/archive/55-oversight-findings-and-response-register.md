# Oversight Findings & Response Register (OFRR) (Make Follow‑Through Auditable)

**Purpose:** ensure oversight findings lead to tracked commitments and consequences, not reports that vanish into inboxes.
**Person served:** a complainant or affected community who needs oversight findings to produce tracked commitments and verifiable follow‑through.

**From-below:** This lets you track whether oversight findings were acted on, so institutions can’t promise reform and then stall.

**EXP pointer:** counters `EXP-07` (Indifference) and `EXP-02` (Waiting) by making follow-through time-bounded, verifiable, and visible to complainants (see `98-persons-path-and-accessibility-invariants.md`).
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)

**Authority:** oversight bodies open `OFR-*` and issue findings; affected units owe timed responses and verification, and at least one lever must bind (`32-...`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect complainants/staff via protected intake + redaction; publish aggregated outcomes and retaliation signals (`83`, `77`, `03`). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)


Oversight fails when findings disappear into narrative: reports are published, but **responses, remediation, and verification** are not legible.
The **OFRR** is the smallest joinable artifact that turns oversight into a **closed loop** across scopes.

**Anchor set:** follow‑up/reporting expectations in INTOSAI performance audit principles and standards (see [BIB-ISSAI-300-2019], [BIB-ISSAI-3000-2019]) and ombuds duty‑to‑respond baselines (see [BIB-VENICE-OMB-2019]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Oversight institutions + binding hooks: `32-...`.
- Publication integrity + as-of access for findings: `53-...`.
- Records custody + FOI: `31-...`.
- Remedy/systemic redress joins: `36-...`, `76-...`.
- Person-facing visibility of follow-through (track a case from complaint to closure): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- Public accountability vs retaliation risk to complainants/staff.
- Naming and sanctions vs due process / defamation risk.
- Speed of response vs thorough investigation (and capture).
- Independence vs embedment (outsider audit vs operational learning).

---
## A. Core object: an Oversight File (`OFR-*`)
`OFR-*` is the join-key for **both**:
- a live oversight **case** (investigation / serious incident / pattern inquiry), and
- a published oversight **finding** (audit report / ombuds systemic report / integrity finding) that still requires follow‑through.

### OFR kinds
- `OFR-KIND: CASE` — an open file with a timeline and (optionally) multiple findings over time.
- `OFR-KIND: FINDING` — a standalone published finding that still triggers response + remediation + verification.

**Rule (serious incidents):** serious incidents SHOULD open an `OFR-*` with `OFR-KIND: CASE` within 24 hours (see `24-mutual-aid-and-serious-incident-protocol.md`).

---

## B. Minimum public schema (stable; machine-readable + human view)

### OFR object — minimum fields
- `OFR-ID` (stable)
- `OFR-KIND` (`CASE` / `FINDING`)
- `ISSUING-BODY` (Unit ID; appears in competence ledger)
- `TITLE` (plain language)
- `SCOPE` (scope level(s) affected; may cite `DRR-TYPE: SCOPE` where relevant)
- `BASIS` (legal/mandate basis; cite `RULE-*` as-of)
- `FINDING-TYPE` (optional: `ACTION` / `OMISSION` / `MIXED`; use `OMISSION` for failure-to-act / failure-to-provide-mandated-service cases)
- `SUBJECT-UNITS` (Unit ID(s) being reviewed)
- `SUBJECT-EIDS` (optional; vendors/grantees/lobby entities via `EID` bundle)
- `RELATED` (0+ join links: `DRR-*`, `REL-*`, `PROG-*`, `TRF-*`, `CON-*`, `EMR-*`, `ENF-*`, `SRV-*`, `CMP-*`)
- `PUBLICATION` (link to public report/notice release via `REL-*` or stable report ID; include redaction basis if applicable)
- `STATUS` (state machine below)
- `DEADLINES` (response due date; remediation milestone dates)
- `ACTION-PLAN` (pointer to the responsible unit’s plan; MAY be a `REL-*` release)
- `VERIFICATION` (who verifies; method; evidence pointers; MAY be a `REL-*`)
- `RESIDUAL-RISK` (short note; what remains and why)
- `UPDATED-AT` (timestamp)
- `HISTORY` (change log pointer; MUST be non-silent—see `53-...`)

**Coverage rule:** any finding with recommendations that materially affect rights, safety, or money MUST be in the OFRR.

---

## C. Lifecycle states (small state machine)

| State | Meaning | Who can set it | Minimum evidence |
|---|---|---|---|
| `OPEN` | file opened; response clock starts when required | oversight body | record + scope + basis |
| `RESPONDED` | duty‑to‑respond satisfied | responsible unit | action plan + owners + dates |
| `IN-REMEDIATION` | fixes in progress | responsible unit | work log + budget/contract links |
| `VERIFICATION` | independent check underway | oversight body / verifier | test plan + data sources |
| `CLOSED-VERIFIED` | fix verified and durable | oversight body | verification note + residual risk |
| `REOPENED` | recurrence or failed fix | oversight body | trigger evidence + new plan |

**Interface rule:** OFRR entries SHOULD link to `RULE` (basis), `REL` (evidence/data), and `AL-*` (appeal/protection lanes) where applicable (see `70-interoperability.md`, `36-...`, `51-...`).

---

## D. Duty-to-respond and escalation (portable constraints)
- A published `FINDING` MUST trigger a **time‑bound duty to respond** by the responsible unit.
- The OFRR MUST make non-response legible (missed deadlines are visible).
- **Deterministic escalation:** each scope SHOULD publish a simple rule for what happens on missed response deadlines (e.g., automatic hearing scheduling, conditionality review, bounded holdback, or referral). Where possible, use the OFRR state + deadline breach as a **non‑discretionary trigger** so “ignored findings” become auditable events, not politics-as-usual.
- Where enforcement is weak, compacts/transfers MAY use OFRR states as a **non‑discretionary trigger** for escalation (e.g., automatic review, conditionality review) (see `19-...`, `35-...`).

---

## E. Integrity (no silent rewrites)
For “constitutional” feeds (competence ledger, PRR, EMR, OFRR, core enforcement logs), use tamper‑evident publication discipline:
- publish change logs and “as‑of” snapshots,
- prefer signed bundles for releases,
- optionally publish manifests into an append‑only transparency log (see `53-publication-integrity-and-tamper-evident-logs.md`).

---

## F. Sampling and verification selection (make “follow-through” credible)
Many oversight bodies can’t fully verify every claim of remediation. The OFRR SHOULD therefore publish how it selects what to check.

- **Rule:** closures (`CLOSED-VERIFIED`) SHOULD be supported by a published verification method (test plan + evidence pointers).
- **Sampling policy:** publish a coarse `REL-*` sampling policy for verification (risk + random component), and log selections so “audit shopping” and bias are harder (see `81-verification-inspection-and-compliance-ladders.md`).
- **Random re-open checks:** reserve a small random share of “closed” files for delayed re-checks (e.g., 6–18 months) to detect recurrence and superficial fixes (tie to `76-...`).

Metric hook: `[IPM-25]` in `03-metrics-and-evidence.md`.