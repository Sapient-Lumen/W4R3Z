# Appeal Lanes & Redress Registry (ALR) (Make Remedies Discoverable and Comparable)

Remedy fails in practice when people cannot answer three questions quickly: **(1) where do I file, (2) by when, and (3) what can this forum actually do?**  
This memo defines a compact *registry interface* so remedies remain legible across scopes, contractors, and mandate transfers.

**Anchor set:** effective remedy and reason-giving baselines (see [BIB-EU-CHARTER-A47], [BIB-ICCPR], [BIB-UN-REMEDY-60147]) and administrative justice / good administration constraints (see [BIB-COE-GOODADMIN-2007], [BIB-VENICE-ROL-2025], [BIB-VENICE-OMB-2019]).

---

## A. Core object: the Appeal Lane (`AL`)

An **Appeal Lane** is a stable identifier for a specific contestation path (informal complaint → internal review → ombuds → tribunal/court).  
A lane must be *discoverable, accessible, time-bounded, and linked to enforceable remedies*.

**Rule:** if a decision can be enforced against someone, its Decision Receipt/Record (`DRR`) MUST cite at least one `AL-*` lane that can provide **effective relief** (or a narrow, logged exception).

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
| `INTERIM-PROTECTION` | when stays/urgent review apply (especially for high-stakes harms) |
| `COSTS` | fees (if any), waivers, and representation support |
| `INDEPENDENCE` | internal vs external; appointment/budget notes or pointer to oversight charter |
| `LINKS` | related Rule IDs (`RULE-*`) and any metrics / outcome publications |

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

```yaml
LANE-ID: AL-____
LANE-TYPE: AL-____   # one of: AL-FRONT|AL-LEG|AL-ADM|AL-OMB|AL-TRI|AL-CRT|AL-ADR|AL-INT|AL-COMP
COVERAGE:
  UNITS: [UNIT-____, ...]          # or references to competence-ledger entries
  DECISION-CLASSES: [permit, benefit, sanction, FOI-appeal, transfer-dispute, ...]
FORUM:
  NAME: ...
  UNIT: UNIT-____
  CONTACT: {online: URL, phone: ..., in_person: ...}
HOW-TO-FILE:
  CHANNELS: [online, in_person, phone, mail]
  ACCESSIBILITY: {languages: [...], disability: ..., offline: ...}
DEADLINES:
  FILE-WITHIN: P__D                # ISO 8601 duration preferred
  STOP-THE-CLOCK: (Y/N + conditions)
NO-RESPONSE-RULE:
  ON-MISSED-DEADLINE: (auto_escalate | interim_protection | deemed_denial | deemed_grant)
  ESCALATE-TO: [AL-____, ...]      # if auto_escalate
REMEDIES: [stay, reversal, correction, compensation, referral, ...]
INTERIM-PROTECTION:
  AVAILABLE: Y/N
  TRIGGERS: [custody, eviction, essential_service_cutoff, ...]
COSTS:
  FEES: (none | amount)
  WAIVERS: (Y/N + rule)
  ASSISTANCE: (legal_aid | navigator | none)
INDEPENDENCE: (internal | external | mixed)   # plus pointer to charter/oversight
LEGAL-BASIS: [RULE-____, ...]
METRICS: {publish: Y/N, link: ...}
REVISION:
  VERSION: v__
  EFFECTIVE-DATE: YYYY-MM-DD
  CROSSWALK: (if replacing another lane)
```

---

## Where this plugs in
- Decision receipts/records: `DRR` MUST cite `AL-*` (see `31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md`).
- Automation: ADS registers MUST list lanes so human review is real (see `06-digital-and-algorithmic-governance.md`).
- Oversight: ombuds/audit findings (`OFR`) SHOULD cite lanes where systemic harms route (see `32-...`).
- Transfers & compacts: disputes MUST have defined lanes (see `35-transfer-register-and-conditionality.md`, `19-compacts-and-cooperative-governance.md`).

