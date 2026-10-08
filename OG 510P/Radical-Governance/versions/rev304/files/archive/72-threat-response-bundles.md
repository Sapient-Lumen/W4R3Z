# Threat → Response Bundles (How to “buy down risk” without bloating institutions)

**Purpose:** provide reusable control bundles that map concrete threats to minimal counter‑artifacts implementers can ship.

**Person served:** A community harmed by known governance failure modes that recur in practice, who needs implementable bundles that stop abuse even when capacity is limited.

**From-below:** This helps teams choose small, effective safeguards that reduce real harm, not compliance theater or paper shields.
**EXP pointer:** counters `EXP-06` (Complexity) by packaging controls into deployable bundles with explicit capacity floors (`98-persons-path-and-accessibility-invariants.md`).

This memo turns `04-threat-models.md` into **small, reusable response bundles**: if you name the top threats for a unit/program, you can pick the minimum controls + public artifacts that make failure **legible, contestable, and correctable**.

**Use:** when drafting a new authority, compact, program, or enforcement regime, pick the top 3 `TM-*` and attach the matching bundles as non-negotiable requirements in the `DRR` and in the competence ledger entry (see `34-competence-ledger-and-mandate-registry.md` and `71-interface-obligations-by-scope.md`).

Design rule: prefer controls that (a) create **joinable artifacts**, (b) make noncompliance visible, and (c) route recurring failures into **follow‑through** (`32-oversight-institutions-and-follow-through.md`).

**Capacity check:** Each bundle SHOULD name its lowest‑infrastructure variant (paper/low‑bandwidth/offline) and the staffing/budget assumptions required to keep the control real; if it can’t be met, route to Phase −1 (`80-implementation-roadmap.md`) / degraded‑mode planning (`23-emergency-governance-and-exceptions.md`) rather than shipping theater. (See `101-claude-rev142-normative-requirements.md` (NR-13).)

---
## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Threat catalog: `04-threat-models.md`.
- Design toolkit mitigation knobs: `02-design-toolkit.md`.
- Follow-through (no paper controls): `32-oversight-institutions-and-follow-through.md` + `55-oversight-findings-and-response-register.md`.
- Receipts/records + remedy lanes (make failures contestable): `31-...` + `08-...` + `36-...`.
- Person’s path invariants (controls must be usable by the governed, not just logged): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- Control surface vs operational burden (avoid paperwork theatre).
- Standardized bundles vs local adaptation (don’t launder reality).
- Deterrence vs chilling/retaliation (protect reporters and complainants).

## A) Bundle format (keep it tiny)

Each bundle names:
- **Threats covered** (`TM-*`)
- **Minimum controls** (toolkit modules)
- **Must‑emit artifacts** (join-keys)
- **Backstop / escalation** (who forces closure)

---

## B) The minimal bundles (start with these 15)

### B1) Capture resistance (political / vendor / faction capture)
**Threats:** [TM-1] [TM-15]  
**Minimum controls:** `ACC-1/2/4/5/6`, `OPEN-1/2/10`, `LAW-3`, procurement discipline (`22-public-integrity-and-procurement.md`).  
**Must‑emit artifacts:** `REL-*` (spend + contracts), `CON-*`/OCDS where applicable, conflict disclosures as joinable releases, appointments logs, and closure records for oversight findings (`OFR-*`).  
**Backstop:** independent oversight with follow-through; if oversight is blocked, trigger a statutory/public escalation lane (`32-...`, `08-remedy-and-grievance.md`).

### B2) Fraud & leakage control (procurement + transfers)
**Threats:** [TM-2] [TM-17]  
**Minimum controls:** `ACC-2/3/6`, `CAP-2`, `OPEN-10`, sanctions discipline with due process (`05-...`, `66-justice-...`).  
**Must‑emit artifacts:** contract + payment joins (`REL-*`, OCDS), transfer registers with method notes (`REL-*`), enforcement events (`ENF-*`), audit trails and reconciliation checks.  
**Backstop:** time-boxed recoveries + public exception logs; recurring patterns route to special audits (`32-...`).

### B3) Coercion containment (public safety without abuse)
**Threats:** [TM-3] [TM-4] [TM-12]  
**Minimum controls:** `SAFE-1/2/3/4`, `LAW-1/2/3`, independent investigatory capacity (`05-public-safety-and-coercion.md`).  
**Must‑emit artifacts:** use-of-power logs as joinable releases (`REL-*`), incident dockets (`DRR-*` for rights-impacting acts), complaint + outcome codes (`AL-*`, `AO-*`).  
**Backstop:** independent investigation and protected reporting channels; automatic review triggers for specified harm thresholds.

### B4) Emergency discipline (EMR: “temporary” powers that don’t become permanent)
**Threats:** [TM-5] [TM-6]  
**Minimum controls:** emergency rule-of-law constraints (`23-emergency-governance-and-exceptions.md`), hard sunsets/review (`IOP-27/28`), records discipline (`31-...`), and follow-through (`32-...`).  
**Must‑emit artifacts:** Emergency Measures Register entries (`EMR-*`) with legal basis, scope, sunset/review trigger, and after‑action evaluation plan; underlying objects still logged (`CON-*`, `DPR-*`, `ENF-*`, `TRF-*`, etc.); emergency procurement/finance disclosures as `REL-*` releases with revision logs; post‑mortems routed to `OFR-*` when material.  
**Backstop:** automatic legislative/judicial review windows; “no EMR, no exceptional authority” enforcement.

### B5) Epistemic robustness (data, models, and measurement gaming)
**Threats:** [TM-7] [TM-8] [TM-21]  
**Minimum controls:** `IOP-4`, `OPEN-6`, evaluation commitments (`28-...`), anti‑Goodhart rules (`03-metrics-and-evidence.md`).  
**Must‑emit artifacts:** versioned releases (`REL-*`) + method notes, claim IDs (`CLM-*`) tied to `PROG-*`, model registers where applicable (`06-digital-and-algorithmic-governance.md`).  
**Backstop:** independent replication/audit capacity; decision hooks that force update or rollback when indicators fail.

### B6) Inclusion floor (avoid exclusion + legibility traps)
**Threats:** [TM-9] [TM-10]  
**Minimum controls:** `OPEN-2/3/4`, `CAP-4`, administrative burden controls (`64-...`, [BIB-RSF-ADMINBURDEN-2018]).  
**Must‑emit artifacts:** service standard checklists, accessibility exceptions logs, benefit/eligibility rule inventories (`RULE-*`), complaint lanes with response timeouts.  
**Backstop:** ombuds + administrative tribunal; “continuity of benefits/services” constraints during disputes.

### B7) Fragmentation control (boundary failures and coordination gaps)
**Threats:** [TM-11] [TM-18]  
**Minimum controls:** compact discipline (`19-...`), functional authority discipline (`15-...`), scope-test dockets (`54-...`).  
**Must‑emit artifacts:** `CMP-*` compact records, competence-ledger links, interop minimums (`70-...`), and dispute/exit clauses that preserve remedy continuity.  
**Backstop:** escalation to a higher scope with equalization/continuity powers (`18-intergovernmental-finance.md`).

### B8) Intergenerational + systemic risk discipline (slow disasters)
**Threats:** [TM-13] [TM-14] [TM-20]  
**Minimum controls:** long-horizon budgeting + risk registers (`07-...`, `59-...`), independent scientific advisory interface (`26-...`), pre-committed triggers and finance rules.  
**Must‑emit artifacts:** risk registers as releases (`REL-*`), scenario methods, trigger dockets (`DRR-*`), and ex post accountability reports with closure tracking.  
**Backstop:** statutory trigger commitments + independent verification + ring-fenced finance where needed (`60-global.md`, `65-energy-and-decarbonization-governance.md`).

---

### B9) Remedy health & systemic redress (pattern correction loop)
**Threats:** [TM-23] [TM-5]  
**Minimum controls:** `LAW-5`, `ACC-3`, `OPEN-1` (publication), `IOP-27/28` (review clocks), and follow-through (`32-...`).  
**Must‑emit artifacts:** `ALR` lane records with `NO-RESPONSE-RULE`; review-result `DRR` with `AO-*` outcomes; publish remedy health metrics (LRR-8..10); when triggers fire, open a systemic `OFR-*` case that links sampled `DRR-*`, governing `RULE-*` as‑of, and corrective actions.  
**Backstop:** independent oversight forces deadlines/closure; courts/tribunals set enforceable standards; missed review dates become governance incidents (`OFR`).

(Protocol: `76-systemic-redress-and-pattern-remediation.md`.)

### B10) Secrecy exception discipline (anti–classification laundering)
**Threats:** [TM-27] [TM-16]  
**Minimum controls:** `LAW-3`, `OPEN-2`, records/FOI discipline (`31-...`), publication integrity exceptions (`53-...`).  
**Must‑emit artifacts:** withholding/classification `DRR-*` receipts with portable reason categories (`RC-SECU`/`RC-PRIV`/`RC-COMM`/`RC-INV`), a public withholding log (existence metadata + review dates), and appeal/independent review lane records (`AL-*`).  
**Backstop:** independent reviewer with protective access to unredacted records; patterned misuse escalates to systemic `OFR-*` (see `76-...`).  
**Canonical spec:** `77-sensitive-information-and-secrecy-governance.md`.

### B11) Influence & COI discipline (anti-influence laundering)
**Threats:** [TM-19] [TM-16]  
**Minimum controls:** `ACC-5`, `OPEN-10`, `IOP-32`, and procurement integrity (`22-public-integrity-and-procurement.md`) with joinable influence/interest registers (`46-...`).  
**Must‑emit artifacts:** `INF-*` interaction disclosures, `INT-*` status and management actions, `DRR-TYPE: INTEGRITY` receipts for recusals/cooling-off/waivers, and high-risk `DRR-*` decisions that cite `INF-*` or `INF: NONE DECLARED` (plus an `AL-*` lane for ethics disputes).  
**Backstop:** independent ethics/oversight function forces compliance; chronic low disclosure/overdue status triggers a scoped `OFR-*` case and targeted audits; blocking triggers statutory escalation (`32-...`, `55-...`).

### B12) Verification spine (make compliance real)
**Threats:** [TM-4] [TM-14] [TM-19] [TM-23]  
**Minimum controls:** obligation inventory (`RULE-*`/`STD-*`/`CMP-*` as‑of), evidence releases with methods + revision logs (`REL-*`), published verification schedule (coverage + sampling logic), typed findings receipts (`DRR-*`) with `RC-*` reasons + `AL-*` lanes, and follow‑through (`OFR-*`).  
**Must‑emit artifacts:** `REL-*` verification plan/schedule; findings `DRR-TYPE: AUDIT/INSPECTION`; corrective action plans + checkpoints as `REL-*`; systemic cases as `OFR-*`.  
**Backstop:** independent review authority with protected access where needed (`77-...`), and pre‑committed compliance ladder escalation (assist → warn → corrective plan → penalty → suspension/referral).

(See `81-verification-inspection-and-compliance-ladders.md`.)
### B13) Protected disclosures + retaliation controls (make integrity speakable)
**Threats:** [TM-1] [TM-15] [TM-19] [TM-23]  
**Minimum controls:** protected disclosure lane(s) with at least one **independent** channel (`IOP-35`), anti-retaliation rule + interim protections, conflicts test for investigators, and oversight follow-through (`ACC-2/3/6`).  
**Must‑emit artifacts:** disclosure lane entries (`AL-*`), intake/triage receipts (`DRR-TYPE: INTEGRITY-INTAKE`) with `RC-*` reasons, retaliation determinations (`DRR-TYPE: INTEGRITY-RETALIATION`), periodic disclosure/retaliation stats as `REL-*` (method noted), and systemic patterns as `OFR-*`.  
**Backstop:** if the implicated unit controls the process or deadlines are missed, auto-escalate to independent oversight and treat repeated failures as a scoped `OFR-*` audit case; handle confidentiality via withholding receipts (`77-...`).

(See `83-whistleblowing-and-protected-disclosures.md`.)

### B14) Internal control + continuous assurance (execution that withstands audit)
**Threats:** [TM-2] [TM-16] [TM-19]  
**Minimum controls:** separation-of-duties (or compensating controls), control map + testing discipline (`IOP-36`), procurement/payment controls (`38-...`), protected disclosures (`IOP-35`), and follow‑through (`55-...`).  
**Must‑emit artifacts:** `REL-*` control map + test plan + results (methods noted), material exception `OFR-*` cases with closure evidence, and typed authority-change receipts (`DRR-TYPE: DELEGATION/INTEGRITY`) when findings change who can act.  
**Backstop:** internal audit independence (3rd line) plus external oversight if blocked; secrecy handled via `77` (publish receipts even when payload withheld).

(See `84-internal-controls-and-continuous-assurance.md`.)

### B15) Waiver / variance discipline (anti–exception laundering)
**Threats:** [TM-1] [TM-2] [TM-24]  
**Minimum controls:** `IOP-37` (exceptions receipts + logs), `IOP-27/28` (review clocks), verification spine where compliance/impact is material (`IOP-33`), and internal assurance routing for control overrides (`IOP-36`).  
**Must‑emit artifacts:** `DRR-*` receipts tagged `DRR-TYPE: EXCEPTION` (legal basis, bounds, expiry, `RC-*`, `AL-*`), a periodic exception log as `REL-*` (existence metadata + review dates even when details are withheld), and renewal/revocation receipts (no silent extensions). Variance‑creep beyond a published threshold opens a scoped systemic `OFR-*` case.
**Backstop:** independent oversight forces closure; missing exception artifacts are treated as governance incidents (`OFR`), not “informal discretion.”

(See `85-waivers-variances-and-exceptions-discipline.md`.)

## C) Minimal “attachment” language (for DRRs and compacts)

When writing a `DRR` or `CMP` that adopts a bundle, include:
- which bundle(s) apply and why (`TM-*` evidence),
- which artifacts are mandatory, and
- the enforcement/backstop path if artifacts are missing.

This prevents “we adopted good governance principles” from being non-falsifiable.

### B16) Contestability under power asymmetry & omission (make remedy usable, not theoretical)
**Threats:** [TM-33] [TM-30] [TM-23] [TM-29]  
**Minimum controls:** remedy stack + deadlines (`IOP-27/28`), “no wrong door” routing, anti‑retaliation discipline (`83-...`), service standards with time guarantees (`82-...`), and pattern‑based redress (`76-...`).  
**Must‑emit artifacts:** acknowledgement receipts + tracking numbers; person-facing decision receipts (`DRR-*`) with ≥1 `AL-*`; published lane metadata (ALR); queue/time-to-decision performance releases (`REL-*`) keyed by `SRV-*`; and (where safe) aggregate retaliation/complaint signals.  
**Backstop:** independent ombuds/oversight can compel response; missed deadlines or missing receipts are governance incidents and trigger escalation.
