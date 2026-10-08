# Reason Codes Registry (`RC-*`)

**Purpose:** keep stated reasons human-usable and comparable so denials and sanctions can be contested and pattern‑audited.
**Person served:** a person receiving a denial or sanction who needs a plain, comparable reason that routes to the right remedy.

**From-below:** This gives a shared vocabulary of reasons so decisions don’t hide behind vague labels you can’t meaningfully contest.
**EXP pointer:** counters `EXP-01` (Opacity) by making reasons portable and pattern-auditable across systems (`98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** identifiers/joins using this artifact MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)
**Material floor (one sentence):** `RC-*` codes and their plain-language explanations MUST be printable, translatable, and usable offline (e.g., on paper receipts), not only via portals. (See `101-claude-rev142-normative-requirements.md` (NR-13).)

`RC-*` codes make **reasons portable** across scopes and systems. They are not “bureaucratic jargon”; they are a compact interface so:
- people can understand *why* something happened (paired with plain language),
- remedies can route correctly (some reasons imply urgency or interim protection),
- oversight can detect patterns (procedural denial, discrimination, capture),
- and different agencies don’t invent incompatible reason taxonomies.

This file defines a small **Reason Codes Registry (RCR)**. Reason codes are used inside:
- `DRR-*` decision records and one-screen decision receipts (`08-...`, `31-...`),
- automated decision systems disclosures (`42-...`),
- enforcement and custody events (`43-...`),
- FOI/refusal records (`31-...`).

**Anchors:** good administration and effective remedy principles ([BIB-COE-GOODADMIN-2007], [BIB-EU-CHARTER-A41], [BIB-EU-CHARTER-A47]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Rules/instruments registry (what rules authorize reasons): `39-...`.
- Decision receipts + records discipline: `31-...`.
- Appeals/redress lanes (how reasons route to remedy): `36-...`, `08-...`.
- Person’s path comprehension/access invariants (reasons must be usable): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- Specificity for accountability vs gaming/strategic compliance.
- Stable categories vs evolving reality (update without breaking audits).
- Universal code set vs domain nuance / functional equivalents.
- Honest uncertainty vs forced certainty (don’t manufacture precision).

---
## A) How to use reason codes (rules)

Reason codes are also used to make **omission** legible: when deadlines are missed or a unit fails to issue an acknowledgement/decision, the resulting `AO-NORESP` outcome SHOULD carry an `RC-PROC-*` reason describing the procedural failure (See `101-claude-rev142-normative-requirements.md` (NR-02).).
- **Always pair `RC-*` with plain language.** Codes alone are never sufficient notice.
- **Keep the set small and stable.** Add only when analytics/remedy routing needs it; never “rename” codes—deprecate with a mapped successor.
- **Residual category rule:** avoid “Other/Unknown” as a terminal reason. If a residual code is used, the notice MUST include a plain-language explanation and the system MUST treat high residual usage as a taxonomy defect that triggers review/expansion.
- **Make codes cross-walkable.** If a sector needs sub-codes, keep them under a stable parent.
- **Reason ≠ evidence.** Evidence is referenced via record pointers or `REL-*` release IDs (`51-...`).

---

## B) Minimum schema (for each code)
| Field | Meaning |
|---|---|
| `RC-*` | stable reason code |
| Title | short name |
| Plain language | one-sentence explanation |
| Applies to | decision classes (permit/benefit/enforcement/FOI/procurement/etc.) |
| Typical legal basis | common `RULE-*` instrument types (statute/regulation/policy) |
| Evidence commonly required | what must be cited (records / `REL-*` / verification steps) |
| Remedy notes | default `AL-*` lane(s), urgency/interim protection flags where relevant |
| Abuse signals | patterns that suggest misuse (e.g., “missing info” used to hide bias) |
| Status | active / deprecated (with successor mapping) |

---

## C) Starter set (minimal, extensible)

### C1) Procedural & jurisdiction (`RC-PROC-*`)
- `RC-PROC-001` **Missing required information** — required fields/documents were not provided by the deadline; the receipt MUST list what is missing, the resubmission deadline, acceptable alternatives and where/how to obtain them, and whether the state could have obtained the item itself (with consent) under a once-only policy (see `31-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
- `RC-PROC-002` **Unable to verify information** — provided info could not be verified to the required assurance level (cite `IDN-*` / verification step).
- `RC-PROC-003` **Late / outside time limit** — request or appeal filed outside a statutory/posted deadline.
- `RC-PROC-004` **Not within jurisdiction/competence** — the issuing unit lacks authority (must cite competence ledger entry).
- `RC-PROC-005` **Duplicate / already decided** — materially identical matter already decided; cite prior `DRR-*`.
- `RC-PROC-006` **Applicant withdrew** — requester withdrew or cancelled.
- `RC-PROC-007` **Fee/cost not paid** — lawful fee not paid (must cite fee rule + waiver options).
- `RC-PROC-008` **No acknowledgement / tracking number issued** — intake not receipted; the absence of a receipt is itself a defect (trigger remedy routing).
- `RC-PROC-009` **Decision deadline missed (constructive denial)** — decision not issued by the posted/statutory deadline; treat delay as denial (`AO-NORESP`) and route to the relevant `AL-*` lane.
- `RC-PROC-010` **Mandated service unavailable / intake paused** — service exists in the catalog but intake/processing is suspended or effectively unavailable; MUST cite the published suspension notice (or open a legibility-gap appeal / oversight finding if none exists).

### C1a) Scope assignment & mandate transfers (`RC-SCOPE-*`)
Use these when issuing `DRR-TYPE: SCOPE` (mandate assignment/transfer/boundary adjustment) so scope choices are comparable across time and jurisdictions (see `54-subsidiarity-and-scope-assignment-test.md`).

- `RC-SCOPE-001` **Material spillovers** — costs/benefits fall outside the boundary; escalation or compact needed.
- `RC-SCOPE-002` **Scale / fixed-cost advantage** — economies of scale/capex/rare expertise justify higher-scope or functional authority.
- `RC-SCOPE-003` **Coordination failure** — fragmented action predictably fails (race-to-the-bottom/free riding).
- `RC-SCOPE-004` **Rights/integrity protection** — higher-scope baseline/oversight needed to prevent rights failure or capture.
- `RC-SCOPE-005` **Capacity floor not met** — unit cannot reliably execute; transfer or conditional capacity-building required.
- `RC-SCOPE-006` **Uniformity/common-market requirement** — portability/interoperability requires consistent rules or standards.

### C1b) Constitutional / charter change integrity (`RC-CONST-*`)
Use these for integrity-gating decisions on constitutional/charter/treaty change (typically `DRR-TYPE: INTEGRITY`; see `58-constitutional-change-and-amendment-discipline.md`).

- `RC-CONST-001` **Single-subject / anti-logrolling** — proposal violates (or is conditioned to satisfy) the jurisdiction’s single-subject rule.
- `RC-CONST-002` **Clarity / neutrality of question/summary** — wording is misleading/compound or requires correction before ratification.
- `RC-CONST-003` **Insufficient publication / cooling-off** — required publication window not met (proposal/voter info pack not available long enough).
- `RC-CONST-004` **Rights-floor / remedy integrity safeguard** — change affects remedy/oversight/equality protections; heightened safeguards required or proposal blocked.
- `RC-CONST-005` **Emergency-window restriction** — constitutional/charter change restricted while emergency powers are active unless heightened safeguards are satisfied.

### C2) Eligibility & access (`RC-ELIG-*`)
- `RC-ELIG-001` **Not eligible (criteria unmet)** — one or more eligibility criteria not met (cite criteria + which failed).
- `RC-ELIG-002` **Income/means test** — means test threshold not met (cite method + `REL-*` baseline used if applicable).
- `RC-ELIG-003` **Residency/connection requirement** — residency/connection criteria not met (include alternative jurisdiction path if any).
- `RC-ELIG-004` **Identity/credential requirement** — required credential not met (cite `IDN-*` + appeal options; avoid over-collection).
- `RC-ELIG-005` **Capacity/quotas exhausted** — limited slots/funds are exhausted (must cite allocation rule + next review date).

### C3) Risk, safety, and public interest (`RC-RISK-*`)
- `RC-RISK-001` **Immediate safety risk** — credible imminent risk requiring restriction/interim action (flag interim protection lane).
- `RC-RISK-002` **Material fraud risk** — evidence indicates fraud risk above threshold (cite indicators; allow rebuttal).
- `RC-RISK-003` **Noncompliance history** — history triggers enhanced scrutiny/sanction ladder (cite prior `DRR-*`/`ENF-*`).
- `RC-RISK-004` **Public interest balancing** — lawful balancing test leads to restriction/condition (must cite balancing rule and factors).

### C3a) Public health & biosecurity (`RC-PH-*`)
- `RC-PH-001` **Transmission suppression measure** — a measure is applied to reduce spread based on published triggers (cite `REL-*` baseline + `RULE-*`).
- `RC-PH-002` **Scarce resource allocation** — allocation/triage decision under published scarcity policy (cite allocation `RULE-*` + allow urgent review where high harm risk).
- `RC-PH-003` **Public health data use (lawful basis + minimization)** — sensitive data used for outbreak control under a cited lawful basis with safeguards and retention limits.
- `RC-PH-004` **Guidance correction / withdrawal** — official guidance is materially corrected/retracted; must link old/new `REL-*` (or issue correction `DRR`).

### C3b) Critical infrastructure & cyber resilience (`RC-CY-*`)
Use these for cyber/IT/OT decisions that affect service continuity, disclosure, or risk acceptance (typically `DRR-TYPE: INCIDENT` or integrity approvals; see `59-critical-infrastructure-and-cyber-resilience-governance.md`).

- `RC-CY-001` **Material cyber incident action** — containment/recovery action taken in response to a material incident (cite incident `DRR-*` + affected `AST-*`/`SRV-*`).
- `RC-CY-002` **Risk acceptance / exception approval (time-bounded)** — a baseline control/patch requirement is deferred with compensating controls and a review/expiry date (cite baseline `REL-*`/`STD-*`).
- `RC-CY-003` **Vulnerability remediation / disclosure** — action taken to remediate or disclose a materially exploitable vulnerability (cite advisory `REL-*` where publishable).
- `RC-CY-004` **Emergency cyber authority invoked** — extraordinary authority used (shutdown, emergency procurement, exceptional data-sharing) (must cite `EMR-*` and publish review/closure expectations).

### C3c) Land-use & housing (`RC-LH-*`)
Use these for land-use planning, zoning, permits, variances, affordability conditions, and displacement mitigation decisions (see `62-land-and-housing-governance.md`).

- `RC-LH-001` **By-right approval** — meets published criteria; issued under as-of `RULE-*`.
- `RC-LH-002` **Capacity constraint (published)** — denial/condition due to a published infrastructure/ecological limit (must cite `REL-*` method + threshold).
- `RC-LH-003` **Variance/exception criteria unmet** — exception request fails the published test; cite the criteria and missing element.
- `RC-LH-004` **Affordability / inclusionary condition applied** — condition imposed under a cited `RULE-*` (publish calculation method).
- `RC-LH-005` **Displacement mitigation required** — approval conditioned on mitigation/relocation plan under a cited rubric.
- `RC-LH-006` **Conflict-of-interest remediation** — decision paused/invalidated due to conflict disclosure failure (cite `INT-*` rule).

### C3d) Climate adaptation / disaster risk reduction (`RC-DRR-*`)
Use these for resilience planning, trigger activations, risk-acceptance exceptions, and managed retreat/reconstruction decisions (see `63-climate-adaptation-and-disaster-risk-governance.md`).

- `RC-DRR-001` **Trigger threshold met** — action taken under a published trigger rubric (must cite `RULE-*` row + `REL-*` inputs).
- `RC-DRR-002` **Trigger threshold not met** — activation request denied because published thresholds were not met (cite the same).
- `RC-DRR-003` **Risk acceptance approved (time-bounded)** — deviation from baseline approved with compensating controls and expiry/review date (cite baseline `REL-*` and mitigation plan).
- `RC-DRR-004` **Risk reduction investment prioritized** — project prioritized under a published risk-reduction rubric (publish scoring summary via `REL-*`).
- `RC-DRR-005` **No-rebuild / retreat decision** — relocation or no-rebuild policy applied under a published rubric with a discoverable remedy lane (`AL-*`).

### C3e) Social protection & benefits (`RC-SP-*`)
Use these for benefit determinations, suspensions, adjustments, and recovery actions (see `64-social-protection-and-benefits-governance.md`). Use alongside `RC-ELIG-*` and `RC-PROC-*`.

- `RC-SP-001` **Benefit granted (criteria met)** — eligibility and amount verified under as‑of `RULE-*` (cite method/inputs).
- `RC-SP-002` **Benefit suspended/terminated (recertification failure)** — required recertification or contact step missed; MUST include reactivation path and appeal lane.
- `RC-SP-003` **Benefit adjusted (reported change)** — amount changed due to a documented change in circumstances under a published rule; include effective date and backpay/recoup method.
- `RC-SP-004` **Overpayment recovery / clawback** — recovery initiated under a published method; MUST include dispute/waiver path where the law allows.

### C3f) Energy transition / decarbonization (`RC-ET-*`)

Use these for core mitigation decisions and justifications. Pair with plain language and cite the controlling target/standard.

- **RC-ET-001** Target/budget trigger met (action required) — decision implements a rule-triggered mitigation action.
- **RC-ET-002** Target/budget trigger not met (corrective action) — decision escalates instruments due to under-performance.
- **RC-ET-003** Reliability risk acceptance (time‑bounded) — decision accepts reliability risk or curtailment/load‑shedding rule with explicit sunset and oversight.
- **RC-ET-004** Lock‑in risk accepted with mitigations — long‑lived asset approved with documented mitigations (retrofit path, decommission plan).
- **RC-ET-005** Affordability/distribution protection applied — tariff or instrument includes protective design (rebates, lifeline rates, targeted support).
- **RC-ET-006** Offset/removal claim rejected — proposed offset/removal fails quality controls (additionality, durability, double‑counting).

### C3g) Migration & mobility (`RC-MIG-*`)
Use these for migration status determinations, work authorization conditions, detention/custody authorizations, and return/removal orders (see `67-migration-and-mobility-governance.md`). Use alongside `RC-PROC-*`, `RC-ELIG-*`, and (where coercion applies) `RC-ENF-*`.

- `RC-MIG-001` **Protection/status granted** — criteria met under as‑of `RULE-*` (cite key elements).
- `RC-MIG-002` **Status denied (criteria unmet)** — eligibility criteria not met (cite which element failed + evidence basis).
- `RC-MIG-003` **Inadmissible / barred** — statutory bar applies (cite the bar rule; name remedy lane and any waiver pathway).
- `RC-MIG-004` **Condition/work authorization decision** — authorization granted/denied/limited under a published rubric (cite rule + effective dates).
- `RC-MIG-005` **Detention/custody authorized or extended (time‑bounded)** — deprivation of liberty authorized/extended with review date and lane.
- `RC-MIG-006` **Return/removal order issued** — order issued under cited authority; MUST include remedy lane and documented safeguard checks.

### C3h) Education & skills (`RC-EDU-*`)
Use these for enrollment/placement/discipline/accommodation and credential decisions (see `68-education-and-skills-governance.md`). Use alongside `RC-PROC-*` and `RC-ELIG-*`.

- `RC-EDU-001` **Enrollment denied (capacity / catchment rule)** — denial/waitlist under a published placement rule; MUST include next steps and appeal lane.
- `RC-EDU-002` **Enrollment denied (documentation / residency proof)** — denial due to missing evidence; MUST state acceptable alternatives and deadline.
- `RC-EDU-003` **Placement / track assignment** — placement into program/track under a published rubric; MUST cite criteria and review lane.
- `RC-EDU-004` **Accommodation/support decision** — support granted/denied/modified under a published framework; MUST include reassessment timeline.
- `RC-EDU-005` **Disciplinary action (suspension/expulsion)** — action taken under a published code; MUST include proportionality test and appeal lane.
- `RC-EDU-006` **Credential awarded/withheld** — credential decision under a published standard; MUST state unmet element(s) and remedy/retest path.

### C4) Enforcement & sanctions (`RC-ENF-*`)

- `RC-ENF-001` **Rule violation established** — violation of a cited `RULE-*` (as-of) is established.
- `RC-ENF-002` **Failure to comply with order** — noncompliance with a prior lawful order (cite order `DRR-*`).
- `RC-ENF-003` **Emergency measure applied** — action taken under an emergency measure (cite `EMR-*` episode if emergency authority is used).

### C5) Procurement / funding integrity (`RC-PROCURE-*`)
- `RC-PROCURE-001` **Non-responsive bid** — bid did not meet mandatory requirements (cite requirement list).
- `RC-PROCURE-002` **Conflict of interest** — disqualifying conflict (cite `INT-*` / disclosure failure).
- `RC-PROCURE-003` **Value-for-money / evaluation result** — evaluation outcome ranks bid below award threshold (publish scoring summary via `REL-*` where allowed).
- `RC-PROCURE-004` **Sanctions / debarment** — vendor ineligible due to debarment/sanctions status (cite registry entry).

### C6) FOI / access-to-information (`RC-FOI-*`)
- `RC-FOI-001` **No record exists / not held** — the unit does not hold the record (must publish existence metadata + search description).
- `RC-FOI-002` **Exemption applies** — lawful exemption invoked (cite exemption + public interest test where required).
- `RC-FOI-003` **Third-party privacy** — disclosure would unlawfully reveal personal data (cite redaction options).
- `RC-FOI-004` **Operational safety / national security** — restriction for safety/security (must include review/declassification date where possible).
- `RC-FOI-005` **Vexatious or abusive request** — only where the law allows; must include higher-level review lane.

### C7) Public communication integrity (`RC-COMM-*`)
- `RC-COMM-001` **Material correction** — prior guidance contained a material error; publish corrected `REL-*` with visible change log.
- `RC-COMM-002` **Retraction** — prior guidance withdrawn as unreliable; publish replacement guidance or explicit “unknown” state.
- `RC-COMM-003` **Update (new evidence/conditions)** — update driven by new data, revised models, or changed conditions (cite `REL-*`).
- `RC-COMM-004` **Clarification (non-binding vs binding)** — clarify whether a statement is advisory or legally binding; link `RULE-*` if binding.

### C8) Justice & administrative justice (`RC-JUS-*`)
These codes are primarily for **procedural dispositions** (routing, admissibility, urgent protection) and *do not replace* plain-language reasons.
- `RC-JUS-001` **Wrong forum / no jurisdiction** — filed in the wrong court/tribunal; MUST name the correct `AL-*` lane if known.
- `RC-JUS-002` **Time-bar / late filing** — deadline missed; MUST cite the rule and any waiver/extension pathway.
- `RC-JUS-003` **Standing / admissibility failure** — applicant lacks standing or claim is inadmissible; MUST cite criteria.
- `RC-JUS-004` **Interim relief decision** — interim protection granted/denied (urgent); MUST state test and evidence basis.

---

## C3i) Labor & work (`RC-LAB-*`)
Use these for labor inspection, wage-and-hour, classification, and organizing/retaliation protections (see `69-labor-and-work-governance.md`). Use alongside `RC-PROC-*` and (where benefits/tax status hinges on work status) `RC-ELIG-*`.

- `RC-LAB-001` **Employment relationship / status determination** — employee/contractor/joint-employer or agency-work determination under a published rubric; MUST cite the rubric and the appeal lane.
- `RC-LAB-002` **Wage underpayment / wage theft finding** — minimum wage/overtime/unpaid wages/illegal deductions; MUST state the calculation method and remedy path.
- `RC-LAB-003` **Working time / scheduling violation** — hours/rest/break/scheduling-rule compliance finding; MUST cite the governing rule and corrective steps.
- `RC-LAB-004` **Workplace safety/health violation** — hazard finding and abatement order under a published standard; MUST include compliance deadline(s).
- `RC-LAB-005` **Retaliation / interference** — adverse action or interference related to complaints/organizing; MUST include interim-protection and escalation paths where lawful.
- `RC-LAB-006` **Collective bargaining / freedom of association issue** — refusal to bargain, anti-union discrimination, or related rights issue; MUST cite basis and remedy lane.

## D) Governance of the registry
- Host `RC-*` in a versioned public register (can be a small table). Every change logs: add/deprecate, mapping, effective date.
- Oversight SHOULD test for “procedural denial abuse” (high `RC-PROC-001/002` rates) and disparate impact signals (see `03-metrics-and-evidence.md`).

See also: `36-appeal-lanes-and-redress-registry.md` (how lanes are discovered), `32-oversight-institutions-and-follow-through.md` (case patterns).
