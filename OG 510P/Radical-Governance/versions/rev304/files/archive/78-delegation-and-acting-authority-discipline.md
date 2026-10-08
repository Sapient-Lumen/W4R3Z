# Delegation & Acting Authority Discipline (Make authority chains auditable)

**Purpose:** limit delegation/acting authority so temporary discretion doesn’t become permanent, untracked power.

**Person served:** A person affected by an action taken “on behalf of” someone else who needs to know who had authority, for how long, and how to challenge it.

**From-below:** This makes authority chains visible so you can tell who actually decided, whether they were allowed to, and where to appeal.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-04` (Error) by making authority chains auditable so invalid signatories and shadow delegation can be contested (see `98-persons-path-and-accessibility-invariants.md`).

**Authority:** delegated/acting authority must be time‑bounded and reviewable; invalid delegation is contestable (and voidable where law allows) via a binding lane (`31`, `36`, `66`). (See `101-claude-rev142-normative-requirements.md` (NR-09).)
**Retaliation safety:** safe channels for staff/public to report authority laundering or coerced signatures; protect reporters and log retaliation signals (`83`, `77`, `03`). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)


A governance system fails **in practice** when affected people cannot answer:

- **Who had authority to do this?** (Unit mandate)
- **Who was allowed to sign?** (role authority)
- **Was the signer acting or delegated?** (time‑bounded delegation chain)
- **If the work was outsourced or automated, what constrained discretion?** (contract + system joins)

Without these answers, institutions drift into **authority laundering** ("nobody is responsible") and **shadow government** (decisions made by contractors, informal power brokers, or unreviewable automation).

This memo adds a minimal discipline that keeps delegation reversible, contestable, and joinable — *without* introducing a new ID family. Delegations are recorded as typed `DRR-*` receipts and linked through the competence ledger.

See also: `34-competence-ledger-and-mandate-registry.md`, `31-records-foi-and-government-memory.md`, `38-contracting-and-procurement-register.md` (CLC pack), `06-digital-and-algorithmic-governance.md`, and `77-sensitive-information-and-secrecy-governance.md`.

## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Competence/mandate map (who can act): `34-...`.
- Records/publication integrity for delegations and acting orders: `31-...`, `53-...`.
- Emergency measures register interactions: `45-...`.
- Adoption dynamics (delegation as a discretion shift): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Continuity of service vs abuse of acting authority.
- Flexibility for emergencies vs normalizing exception governance.
- Clear accountability vs distributed decision-making realities.
- Rapid delegation vs review/ratification by legitimate bodies.

---
## A. Minimal success condition
For any rights‑ or resource‑affecting decision, a reviewer can reconstruct (from public artifacts):

1) **Unit authority:** the issuing Unit ID’s mandate and legal basis (competence ledger).
2) **Role authority:** the signing **role** is authorized for that decision class (authority schedule).
3) **Delegation chain (if any):** any acting/delegated authority is time‑bounded and recorded as a `DRR-TYPE: DELEGATION` receipt.
4) **Constraint joins:** when discretion is exercised via vendors or automation, the decision cites the governing `CON-*` / `ADS-*` (and, when relevant, `DPR-*` and `STD-*`).

---

## B. Required artifacts (smallest enforceable set)

### B1) Authority Schedule (role‑level signatory matrix)
Each Unit ID entry SHOULD include a pointer to a published **Authority Schedule** (roles, not persons).

**Form:** a versioned `REL-*` release that can be diffed (“as‑of” access; no silent edits).

**Minimum fields**
- `UNIT` — Unit ID
- `ROLE` — signatory role label (not a person)
- `DECISION-CLASS` — bounded category list (permit, grant, sanction, procurement award, emergency declaration, etc.)
- `LIMITS` — explicit ceilings (money, duration, scope, coercion ceiling if applicable)
- `RULE-BASIS` — `RULE-*` references (as‑of) for the authority
- `DELEGABLE` — yes/no + constraints
- `REVIEW` — review date (joins to sunset discipline)

**Why it matters:** it makes “who can sign what” auditable, comparable, and revocable.

### B2) Delegation / acting authority receipts (`DRR-TYPE: DELEGATION`)
Any delegation, subdelegation, acting appointment, revocation, or emergency override MUST emit a joinable `DRR-*` tagged `DRR-TYPE: DELEGATION`.

**Minimum fields (one screen)**
- `DRR-ID`, `DATE`, `UNIT` (issuer)
- `DELEGATOR-ROLE` → `DELEGATEE-ROLE` (roles, not persons)
- `SCOPE` (decision classes + explicit exclusions)
- `LIMITS` (money/time/territory/conditions)
- `START` / `END` (default: time‑bounded)
- `RULE-BASIS` (as‑of) + any relevant `CMP-*` (cross‑unit)
- `REASON` + portable `RC-*` where applicable
- `REVOCATION` (how to revoke; who can revoke)
- `AL-*` lane for delegation disputes (standing must exist)
- **Joins:** `INT-*` (if delegation arises from recusal/COI), `CON-*` (if delegation is to a contractor‑operated workflow), `ADS-*` (if delegation relies on automation)

### B3) Decision receipts cite authority and delegation
All rights‑ or resource‑affecting `DRR-*` SHOULD include:
- `SIGNATORY-ROLE` (role label)
- `AUTHORITY-SCHEDULE` pointer (or implied via Unit entry)
- `AUTH-DRR` pointer when acting/delegated authority applies (the relevant `DRR-TYPE: DELEGATION`)

**Rule:** no “unsigned” discretionary government.

---

## C. Outsourcing and automation cannot expand authority

### C1) Vendor-operated decision workflows (subdelegation)
When a contractor executes or materially shapes a decision workflow:
- the governing contract MUST be joinable (`CON-*`) and carry the **CLC pack** so receipts/logs/remedy cannot be evaded by outsourcing.
- delegation MUST be explicit: a `DRR-TYPE: DELEGATION` defines what the contractor may do, what they may not do, and where human sign‑off is required.
- the person‑facing decision receipt remains a `DRR-*` issued under the Unit’s authority (the vendor cannot become the de facto public authority).

### C2) Automated decision systems (ADS)
If an automated system materially influences or makes a consequential decision:
- cite the relevant `ADS-*` (and `MOD-*` where material) and the `RULE-*` criteria as-of.
- delegate only what is contestable: human review + `AL-*` lanes must exist; “no appeal because the model did it” is invalid.
- authority limits apply to the *system*: an ADS cannot exceed the role authority or delegation limits.

---

## D. Interface cases (where delegation laundering often hides)

### D1) Cross-unit delegation and mutual aid
Cross‑jurisdiction work should be governed by compacts (`CMP-*`) **and** operational delegation receipts:
- compact defines the standing arrangement (scope, metrics, dispute path, exit).
- each activation that changes user outcomes emits a `DRR` that cites `CMP-*` and (where a local signer is acting under another unit’s authority) the `DRR-TYPE: DELEGATION`.

### D2) Emergency delegation
Emergency delegations must cite the relevant `EMR-*` episode and remain time‑bounded, with explicit reversion rules (see `45-...` and `74-...`).

### D3) Sensitive delegation details
If publishing delegation details would create operational risk, publish the **receipt** with withholding discipline (existence metadata + review date + independent review access). See `77-sensitive-information-and-secrecy-governance.md`.

---

## E. Failure modes (and minimum mitigations)

- **Shadow signatories:** decisions signed by “acting” officials without published authority → require `SIGNATORY-ROLE` + `AUTH-DRR` when acting.
- **Recusal laundering:** conflicts handled informally → recusals emit `DRR-TYPE: INTEGRITY` and any replacement authority emits `DRR-TYPE: DELEGATION` linked to `INT-*`.
- **Vendor authority creep:** contractors become de facto decision-makers → constrain via explicit delegation + CLC pack + receipts remain `DRR-*` under Unit authority.
- **Emergency permanence:** “temporary” delegations never expire → hard end dates; missed reviews are incidents (`OFR-*` `LEGIBILITY-GAP`).

---

## F. Minimal metrics (audit signals)
- **Delegation coverage:** share of high-impact decision classes with a published authority schedule.
- **Acting authority share:** share of `DRR-*` with `AUTH-DRR` pointers (trend + outliers).
- **Delegation staleness:** delegations past end date or past review date.
- **Authority-chain defects:** audit sample rate of `DRR-*` missing `SIGNATORY-ROLE` or missing valid authority basis.

---

## G. Anchors (why this is not bespoke)
- “Good administration” and effective remedy principles support reasoned, attributable, reviewable administrative action: see [BIB-COE-GOODADMIN-2007] and [BIB-EU-CHARTER-A41], [BIB-EU-CHARTER-A47].
- Integrity systems rely on role clarity, accountability chains, and conflict management: see [BIB-OECD-PI].
- For one operationalized example of delegation limits and delegated authority letters in public finance, see UK HM Treasury Managing Public Money guidance: [BIB-UK-MPM-2025] (and related approvals process guidance [BIB-UK-TREASURY-APPROVALS-2024]).