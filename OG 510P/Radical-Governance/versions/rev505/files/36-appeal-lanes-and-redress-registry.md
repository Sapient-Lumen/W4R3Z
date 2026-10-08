# Appeal Lanes & Redress Registry (ALR) (Make Remedies Discoverable and Comparable)

**Stack relation:** use `283-justice-and-redress-stack-routing-guide.md` for the canonical route across the justice/redress cluster. This memo is the lane-discovery and receipting layer; `08` sets remedy floors; `195` handles escalation/ODR routing; `76` handles patterned-harm remediation.

**Purpose:** make remedies **discoverable and navigable without prior knowledge** (where to file, by when, what it can do) with assisted intake and no‑clock‑reset routing.
**Person served:** a person harmed by a decision who needs to find and use the correct appeal lane without being bounced, timed out, or clock‑reset.

**From-below:** This tells you where to go, what you’re owed, and how long it should take when a decision harms you.

**EXP pointer:** EXP-06 (Complexity), EXP-02 (Waiting), EXP-05 (Fear) — see `98-persons-path-and-accessibility-invariants.md`.

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Join constraints:** identifiers/joins using this artifact MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)

**Authority:** each `AL-*` lane MUST disclose whether it can issue binding relief or only recommendations; receipts MUST point to at least one enforceable lane or log a narrow exception. (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** lanes must offer protected intake paths and monitor post-filing adverse-action uplift; treat retaliation as an incident (`83`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** each `AL-*` lane MUST disclose evidentiary standards + what the person must show vs what the state must produce; prefer least-burdensome proof and “once-only” retrieval of state-held facts; adverse outcomes cite `RC-*` (`44`, `47`, `52`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)


Remedy fails in practice when people cannot answer three questions quickly: **(1) where do I file, (2) by when, and (3) what can this forum actually do?**
This memo defines a compact *registry interface* so remedies remain legible across scopes, contractors, and mandate transfers.

**Anchor set:** effective remedy and reason-giving baselines (see [BIB-EU-CHARTER-A47], [BIB-ICCPR], [BIB-UN-REMEDY-60147]) and administrative justice / good administration constraints (see [BIB-COE-GOODADMIN-2007], [BIB-VENICE-ROL-2025], [BIB-VENICE-OMB-2019]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Person-facing invariants and accessibility: `98-persons-path-and-accessibility-invariants.md`.
- Core remedy commitments: `08-...`.
- Systemic redress intake + pattern remediation: `76-...`.
- Records + publication integrity for decisions, deadlines, and outcomes: `31-...`, `53-...`.
- Interop join keys (DRR/ALR links): `70-...`.

## Named tensions (design must surface these)
- Speed vs due process (urgent relief vs fair hearing).
- Confidentiality/safety vs precedent/public learning (and deterrence).
- Individual filing convenience vs collective/pattern accountability.
- Low burden access vs evidentiary rigor and anti-abuse safeguards.

---
## A. Core object: the Appeal Lane (`AL`)

An **Appeal Lane** is a stable identifier for a specific contestation path (informal complaint → internal review → ombuds → tribunal/court).
A lane must be *discoverable, accessible, time-bounded, and linked to enforceable remedies*.

**Rule:** if a decision can be enforced against someone, its Decision Receipt/Record (`DRR`) MUST cite at least one `AL-*` lane that can provide **effective relief** (or a narrow, logged exception).

**Person-facing invariants (ALR-level):**
- **No wrong door:** filings MUST be accepted or routed without loss of deadlines, preserving a single tracking number.
- **Guided navigation:** lanes (or the issuing unit at the point of the adverse decision) SHOULD provide an assisted intake/navigator path that routes a person to the correct lane without requiring prior legal knowledge; availability and how-to-access MUST be disclosed in `HOW-TO-FILE`/assistance fields.
- **Representation duty:** the register MUST disclose who can file on behalf of someone (guardian/advocate/authorized representative) and how conflicts are handled; high‑stakes domains SHOULD provide an independent advocate intake path (`98-persons-path-and-accessibility-invariants.md`). (See `101-claude-rev142-normative-requirements.md` (NR-12, NR-13).)
- **Fear is a defect:** lanes SHOULD provide safe reporting/anti‑retaliation pathways (see `83-whistleblowing-and-protected-disclosures.md`).
- **Anonymous / confidential intake:** lanes SHOULD support anonymous filing where possible, and MUST disclose identity requirements and retaliation safeguards.
- **Retaliation monitoring:** lane owners MUST publish aggregate post‑filing adverse‑action uplift (enforcement actions, benefit reviews, adverse decisions) for filers vs matched non‑filers; treat sustained uplifts as an incident signal and route to oversight. (See `03-metrics-and-evidence.md` [LRR-14] and `04-threat-models.md` [TM-29].) (See `101-claude-rev142-normative-requirements.md` (NR-08).)
- **No digital/AI-only gate:** lane `HOW-TO-FILE` MUST include at least one staffed/non‑digital path and SHOULD support assisted/oral filing where literacy or disability makes written forms a barrier (see `98-persons-path-and-accessibility-invariants.md`).
- **Time is a barrier (subsistence reality):** lanes SHOULD minimize time-costs to file (async/after‑hours options, local/remote intake, fewer trips) and MUST disclose expected steps/time burdens; high‑stakes lanes SHOULD provide fee waivers and practical assistance so “can’t take a day off” doesn’t become “can’t contest.”
- **Collective harms:** lanes MUST support collective filing as a first‑class mode for shared harms (representative complaints, community/organization filing, or class mechanisms), and MUST disclose support/constraints in `COLLECTIVE-FILING`. If collective filing is not available, the register MUST point to an equivalent‑power substitute and record the gap as design debt (representative complaint, watchdog standing, class action, or pattern‑based redress via `76-...`). (See `101-claude-rev142-normative-requirements.md` (NR-12).)
- **Delay is denial:** lanes MUST publish a no‑response rule (deemed denial/grant, auto‑escalation, or interim protection).

(Design test: `98-persons-path-and-accessibility-invariants.md`.)

### Lane types (portable taxonomy; keep small)

Use the portable `AL-*` lane codes defined in `70-interoperability.md` (“Appeal lanes”), plus `AL-COMP` for competence disputes.
`LANE-TYPE` SHOULD be one of:

- `AL-FRONT` (informal fix / service recovery)
- `AL-LEG` (legibility complaint: missing receipt/log / required record)
- `AL-ADM` (administrative review)
- `AL-OMB` (ombudsman / inspectorate complaint channel)
- `AL-TRI` (specialized administrative tribunal)
- `AL-CRT` (courts / judicial review)
- `AL-ADR` (alternative dispute resolution; voluntary; rights-safe)
- `AL-INT` (supranational / international remedy)
- `AL-COMP` (competence/jurisdiction disputes)

**Design rule:** “easy first, enforceable last” is ideal — but an enforceable lane MUST exist for rights-affecting decisions.

**Indifference boundary:** a lane MUST accept filings where the outcome is “correct” under current rules but predictably harmful or structurally unfair; lane resolution MUST emit a route-to-change artifact (pattern intake / rule review) so the harm can’t be dismissed as “no appeal.” (See `76-systemic-redress-and-pattern-remediation.md`; `101-claude-rev142-normative-requirements.md` (NR-11).)

---

## B. The Redress Registry (`ALR`) (minimum public register)

Every scope that issues enforceable decisions MUST publish a versioned **Redress Registry** mapping `AL-*` lanes to their operating constraints.

### Minimum fields (one screen per lane)
| Field | Meaning |
|---|---|
| `LANE-ID` | stable lane identifier (join-key) |
| `LANE-TYPE` | one of the small type set above |
| `COVERAGE` | which units / decision classes this lane applies to (by `UNIT` and/or decision class tags) |
| `FORUM` | body responsible + contact channel(s) |
| `HOW-TO-FILE` | online + offline channels; accessibility commitments |
| `DEADLINES` | filing window(s) and stop-the-clock rules |
| `NO-RESPONSE-RULE` | what happens if the forum misses its deadline (auto-escalate, interim protection, deemed decision) |
| `REMEDIES` | what relief is available (stay, reversal, compensation, correction, discipline referral, etc.) |
| `AUTHORITY` | whether this lane can issue **binding relief** vs **recommend-only/advisory** outcomes (and how recommendations become enforceable) |
| `INTERIM-PROTECTION` | when stays/urgent review apply (especially for high-stakes harms) |
| `COSTS` | fees (if any), waivers, and representation/navigation assistance support |
| `REPRESENTATION` | who may file (self/rep); default rep rules; independent advocate/ombuds path; conflict‑of‑interest handling |
| `COLLECTIVE-FILING` | whether collective filing is supported; mode/rules; substitute mechanism if not |
| `INDEPENDENCE` | internal vs external; appointment/budget notes or pointer to oversight charter |
| `LINKS` | related Rule IDs (`RULE-*`) and any metrics / outcome publications |

**Authority clarity:** lanes MUST say whether outcomes are **binding** or **recommend-only/advisory** so people don’t waste time in powerless forums. (See `101-claude-rev142-normative-requirements.md` (NR-09).)

### Change discipline (avoid “appeal mazes”)
- Lane definitions MUST be **versioned**; changes MUST publish a crosswalk (old `AL-*` → new `AL-*`) and effective date.
- The default stack for a decision SHOULD list **≤3 lanes** in order, unless legally required otherwise.
- A lane that is *mandatory before escalation* MUST guarantee a response deadline; otherwise it becomes procedural exhaustion.

**Interface rule:** if mandates move (`DRR-TYPE: SCOPE`) or competence changes (`DRR-TYPE: COMPETENCE`), publish a **remedy continuity plan** that crosswalks affected decisions to the new lanes.

---

## C. Special requirement: urgent protection for high-stakes harm

Some decisions create irreversible or compounding harms (detention/custody, eviction, deportation, license suspension, loss of essential services, safety enforcement).

**Rule:** for high-stakes decision classes, the registry MUST define at least one lane with:
- a **fast intake** channel (incl. offline),
- authority to grant **interim protection** (stay/suspension or equivalent),
- a reasoned written outcome with `AO-*` codes (see `70-interoperability.md` and `08-remedy-and-grievance.md`).

---

## D. No-response is a defect (deadline semantics)

Delay is a common way to defeat rights without overt denial (“slow denial”). The ALR MUST make deadline failure *legible and actionable*.

**Rule:** each lane MUST publish a `NO-RESPONSE-RULE` describing what happens if the forum misses its deadline. Missed-deadline events SHOULD produce a review-result `DRR` with `AO-NORESP` (even if auto-generated) so delay can be measured and escalated.

**Default design (recommended):**
- **Legibility complaints (`AL-LEG`):** missed deadline triggers auto-escalation to `AL-OMB` (and interim protection for high-stakes harms).
- **Protective lanes (custody, eviction, essential service cutoffs):** missed deadline triggers **interim protection** (stay/continuity) until a reasoned outcome is issued.
- **Entitlements and basic benefits:** missed deadline triggers **auto-escalation** to the next lane and (where feasible) an interim grant/continuation.
- **Permits with public-harm risk:** do **not** treat silence as consent; missed deadline triggers an interim order requiring action + escalation/oversight.

## E. Publishing outcomes (so the system can learn)

Contestability is also an epistemic tool: it surfaces error patterns and capture.

**Minimum publication (aggregate; privacy-safe):**
- volumes by lane and decision class,
- time-to-first-action and time-to-final-outcome,
- outcome codes (`AO-*`) and reversal/modification rates,
- backlog indicators,
- accessibility signals (language/disability/offline usage).

Tie these to **LRR-8..10** (see `03-metrics-and-evidence.md`) and link lanes to Decision IDs (`DRR`) so audits can sample.

---

## F. Skeleton: `AL` lane record (publishable)

**Version semantics (canonical):** treat this register as **append‑only** and queryable **as‑of** a date. Publish revisions with monotonic `REV`, `PUBLISHED-AT`, and (when behavior changes) `EFFECTIVE-*` timestamps—see `70-interoperability.md` §“Version semantics & ‘as‑of’ queries”.

```yaml
LANE-ID: AL-____
LANE-TYPE: AL-____ # one of: AL-FRONT|AL-LEG|AL-ADM|AL-OMB|AL-TRI|AL-CRT|AL-ADR|AL-INT|AL-COMP
COVERAGE:
 UNITS: [UNIT-____, ...] # or references to competence-ledger entries
 DECISION-CLASSES: [permit, benefit, sanction, FOI-appeal, transfer-dispute, ...]
FORUM:
 NAME: ...
 UNIT: UNIT-____
 CONTACT: {online: URL, phone: ..., in_person: ...}
HOW-TO-FILE:
 CHANNELS: [online, in_person, phone, mail]
 ACCESSIBILITY: {languages: [...], disability: ..., offline: ...}
REPRESENTATION:
 CAN-FILE: [self, guardian, advocate, authorized_rep]
 CONFLICT-HANDLING: ...
 INDEPENDENT-ADVOCATE-CHANNEL: {required_for_high_stakes: Y/N, contact: ...}
DEADLINES:
 FILE-WITHIN: P__D # ISO 8601 duration preferred
 STOP-THE-CLOCK: (Y/N + conditions)
NO-RESPONSE-RULE:
 ON-MISSED-DEADLINE: (auto_escalate | interim_protection | deemed_denial | deemed_grant)
 ESCALATE-TO: [AL-____, ...] # if auto_escalate
AUTHORITY: BINDING|RECOMMEND|ADVISORY
COLLECTIVE-FILING:
- `SUPPORTED`: `YES/NO` (default expectation: `YES` for rights-affecting lanes).
- If `YES`: allowed filer types (individual group, org, union, community body), representation rules, opt‑in/out (if applicable), evidentiary bundling rules, and how relief is issued to the group.
- If `NO`: the substitute collective mechanism (watchdog standing / representative complaint / class action / pattern‑intake via `76-...`) + why collective filing is infeasible + who can trigger systemic review.

---

## Where this plugs in
- Decision receipts/records: `DRR` MUST cite `AL-*` (see `31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md`).
- Automation: ADS registers MUST list lanes so human review is real (see `06-digital-and-algorithmic-governance.md`).
- Oversight: ombuds/audit findings (`OFR`) SHOULD cite lanes where systemic harms route (see `32-...`).
- Transfers & compacts: disputes MUST have defined lanes (see `35-transfer-register-and-conditionality.md`, `19-compacts-and-cooperative-governance.md`).
