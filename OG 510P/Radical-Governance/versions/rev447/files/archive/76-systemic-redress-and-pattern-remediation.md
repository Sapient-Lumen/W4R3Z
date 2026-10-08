# Systemic Redress & Pattern Remediation (When Individual Complaints Are Not Enough)

**Stack relation:** use `283-justice-and-redress-stack-routing-guide.md` for the canonical route across the justice/redress cluster. This memo is the patterned-harm and structural-correction layer; `08` covers individual remedy principles; `36` covers lane discovery; `195` covers escalation and dispute routing.

**Purpose:** turn recurring harms into structural fixes by detecting patterns and routing them to enforceable change.

**Person served:** People harmed by a recurring pattern who need collective remedy and rule change, not endless individual appeals. (See `101-claude-rev142-normative-requirements.md` (NR-12).)

**From-below:** This shows how repeated harms become system fixes, so you don’t have to fight the same battle case by case.
**EXP pointer:** counters `EXP-07` (Indifference) by making pattern-level harm routable to rule change, not endless individual appeals (`98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** pattern cases are owned by an accountable actor (ombuds/audit/regulator) with power to compel correction or route to binding rule/policy change (`55`, `32`, `41`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect sources and communities surfacing patterns; prefer aggregate/public releases with safe channels (`83`, `77`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** pattern claims MUST not force individuals to carry impossible burdens; agencies must produce relevant state-held evidence and publish standards for action; adverse outcomes cite `RC-*` + `AL-*` (`44`, `03`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


Individual grievance and appeal lanes can correct *single* wrongs, but many governance failures are **patterned**:
recurring illegal denials, “no response” by delay, discriminatory enforcement, or systemic design bugs in a service/ADS.
This memo defines a **minimal protocol** for detecting and correcting patterned harm without inventing a new sovereign tier.

**Anchor set:** effective remedy and non-judicial grievance effectiveness criteria (see [BIB-UN-REMEDY-60147], [BIB-UNGP-BHR-2011]) and administrative justice / ombuds standards (see [BIB-VENICE-OMB-2019], [BIB-OECD-OMBUDS-OPEN-GOV-2018]).

**Canonical homes:** individual remedy design (`08-remedy-and-grievance.md`), remedy discoverability (`36-appeal-lanes-and-redress-registry.md`), follow‑through (`55-oversight-findings-and-response-register.md`).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Decision receipts (person-facing) default to `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields).
- Appeals lane registry + collective filing fields: `36-...`.
- Remedy commitments and person-facing safety: `08-...`, `98-persons-path-and-accessibility-invariants.md`.
- Oversight findings + binding hooks: `32-...`, `55-...`.
- Evidence/metrics discipline (pattern detection that can be audited): `03-...`.

## Named tensions (design must surface these)
- False positives (overreach) vs under-detection (letting patterns persist).
- Transparency/public learning vs retaliation and stigma risks.
- Speed of remediation vs careful causal attribution (don’t “fix” the wrong thing).
- Local discretion to respond vs systemic uniformity of rights floors.

---
## A. Design goal
Turn repeated harms into a **publicly trackable correction loop**:
1) detect a pattern,
2) open a scoped case with deadlines,
3) produce and verify corrective action,
4) close with evidence (and keep monitoring).

**Rule:** if the system can enforce decisions, it must also provide a *credible* path to correct systemic error.

**Boundary:** systemic redress corrects patterned illegality and implementation/design defects; it does not substitute for political change when rules work *as written* but still produce harmful outcomes. In those cases, the obligation is to make the pattern legible with joinable evidence (receipts/releases) and route it to the rule/policy change stack (`41-...`, `88-...`, `28-...`).

---

## B. What counts as “systemic” (trigger conditions)

A unit SHOULD treat harms as systemic when any of the following are true (set thresholds per domain, publish them):
- **Volume spike:** complaints/appeals per 1k decisions jump above baseline.
- **Delay failure:** `AO-NORESP` exceeds a stated ceiling in any `AL-*` lane.
- **Disparity signal:** material outcome gaps across protected/at‑risk groups (after reasonable controls).
- **Repeat offenders:** the same office/vendor/system generates repeated overturned/modified decisions (`AO-REVERSE/AO-MOD`).
- **Safety/rights incident:** coercion/custody/emergency/benefits cutoff causes credible severe harm.
- **Design bug:** a known defective rule, form, workflow, or model version keeps producing predictable wrongs.
- **Correct‑but‑harmful outcomes (adequacy):** rules are applied correctly but the outcome is still materially harmful at scale; treat this as systemic and route to rule/policy change (not endless individual appeals). (See `101-claude-rev142-normative-requirements.md` (NR-11).)

**Publication rule:** triggers and thresholds MUST be published (and versioned) so pattern recognition is not discretionary.

---

## C. The minimal systemic redress pipeline (SRP)

### C1) Open a case (use `OFR-*`, do not invent a new registry)
When systemic triggers fire, open an **Oversight Finding / Case**:
- Cases MAY be opened from **collective filings** (community/organization complaints) when individual harms are small but the pattern is large (see ALR `36-...`, person-facing invariants in `08-...`).
- `OFR-KIND: SYSTEMIC` (or a local mapping) with scope + affected decision classes + suspected causes.
- Link the **join graph**: sample Decision Receipts (`DRR-*`), Rule IDs (`RULE-*` as‑of), releases/metrics (`REL-*`), and the relevant remedy lanes (`AL-*`).

### C2) Provide interim protection (when stakes are high)
For high-stakes decisions (custody, eviction, benefits cutoff, immigration removal, emergency restrictions):
- publish an interim protection rule in the lane record (`NO-RESPONSE-RULE` and stay/hold conditions),
- and ensure the SRP cannot proceed without a protective backstop.

### C3) Corrective action plan (CAP) with testable commitments
A systemic case MUST produce a short plan (pointer bundle, not annexes) that includes:
- the hypothesized failure mode(s),
- the fix (rule change, workflow change, staffing, vendor control, model rollback, training),
- a verification method and date,
- a remediation pathway for already-harmed people (retroactive correction where feasible).

### C4) Verify and close (closure is evidence‑based)
Close the `OFR-*` case only when:
- the fix is deployed and measured,
- remedy lanes are updated/cross-walked (no orphaned cases),
- and “lookback” sampling shows the pattern is no longer present (or is bounded and understood).

**Closure emits:** an `OFR-*` closure record plus a joinable receipt (`DRR-*`) if rules/powers changed (`RULE/PROG/AC/EMR/ADS`).

---

## D. Minimal artifacts (keep them joinable)
Systemic redress should be legible using existing IDs:

- **Case tracking:** `OFR-*` (case open → required actions → deadlines → closure evidence).
- **Decision sampling:** `DRR-*` (original decisions) and review-result `DRR-*` with `AO-*` outcomes.
- **Rules-as-of:** `RULE-*` cited in decisions (and amended via the rule register).
- **Remedy lanes:** `AL-*` lanes recorded in ALR; lane records MUST disclose `COLLECTIVE-FILING` support/constraints and point to a substitute mechanism when collective filing is not available (`36-...`, `08-...`).
- **Evidence pointers:** `REL-*` releases (metrics, audit samples) + `EVAL-*` where applicable.
- **If high-discretion:** the relevant `AC-*` MUST link to systemic redress triggers and backstops (see `73-...`).

---

## E. Minimal metrics (avoid vanity)
Track only what drives correction:
- **Pattern detection:** complaint/appeal rate per 1k decisions; `AO-NORESP` share by lane (`AL-*`).
- **Correction speed:** time-to-first-action and time-to-closure for systemic `OFR-*`.
- **Effectiveness:** recurrence rate post-fix; disparity deltas after remediation.
- **Remedy completeness:** share of affected population receiving retroactive correction (where applicable).

(See `03-metrics-and-evidence.md` for LRR and contestation metrics.)

---

## F. Common failure modes (and how to block them)
- **“We fixed it” without evidence:** require `REL-*` / sampling proof before closing `OFR-*`.
- **Blame shifting across mandates:** use `AL-COMP` competence lanes + compacts (`19-...`) and mandate logs (`34-...`).
- **Retaliation and chilling:** whistleblower protections + publish retaliation incidents as oversight cases.
- **Vendor shield:** contracts (`CON-*`) must bind to evidence/trace obligations and allow audits/rollback.

---

## G. Interfaces across scopes
Systemic harms often cross boundaries (vendor platforms, metro services, cross-border regimes). The SRP SHOULD:
- name the **owning unit** and any **dependent units**,
- specify what is local-fixable vs escalated,
- and publish the escalation path and deadlines (who can force closure).
