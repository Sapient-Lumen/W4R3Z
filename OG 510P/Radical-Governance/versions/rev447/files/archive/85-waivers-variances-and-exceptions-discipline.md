# Waivers, Variances & Exceptions Discipline (Make rule departures auditable)

**Purpose:** govern exceptions so waivers don’t become an unreviewable shadow system for the well-connected.

**Person served:** A person whose outcome turns on an exception (or denial of one) who needs exceptions governed so mercy isn’t favoritism and refusal isn’t hidden cruelty.

**From-below:** This makes rule departures trackable so exceptions don’t become secret loopholes for the powerful.
**EXP pointer:** counters `EXP-07` (Indifference) by giving “mercy” a supervised, auditable path instead of hidden discretion (`98-persons-path-and-accessibility-invariants.md`).

Governance often fails through *exception laundering*: a regime looks rule‑bound on paper, but outcomes are driven by discretionary **waivers, variances, exemptions, overrides, and “special cases.”**  
This memo defines a minimal, reusable discipline so departures are **time‑bounded, contestable, and reviewable** — without adding a new ID family.

**Scope:** non‑emergency rule departures (permits/variances, procurement exemptions, service standard exceptions, control overrides, compliance extensions).  
**Not this:** emergency declarations/measures (use the `EMR-*` interface in `45-...` and `23-...`).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** disclosure and controls can be weaponized or ignored; design for safety and incentives. (`99-protective-legibility-and-adoption-dynamics.md`)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Rules/instruments registry and versioning: `39-...`.
- Emergency measures register: `45-...`.
- Sunsetting/deprecation discipline: `74-...`.
- Publication integrity + records for waivers: `53-...`, `31-...`.

## Named tensions (design must surface these)
- Flexibility for hardship vs equal treatment and predictability.
- Exceptions as safety valves vs exceptions as capture/entrenchment tools.
- Speed of granting vs review/oversight quality.
- Transparency of waivers vs retaliation/privacy risks.

---
**Note:** regulatory sandboxes/pilots are structured exceptions with extra learning + exit discipline; see `86-regulatory-experimentation-and-sandboxes.md`.

## Mercy / equitable relief (why exceptions exist at all)
Exceptions are not only corruption vectors. They are also where a rule‑bound system makes space for **humane judgment** (hard cases, exceptional hardship, humanitarian relief).

**Design stance:** treat mercy as *lawful and supervised*, not informal and hidden. (See `101-claude-rev142-normative-requirements.md` (NR-16).)
- **Accountability without mercy** becomes bureaucratic cruelty.
- **Mercy without accountability** becomes arbitrary power.

This memo’s discipline is meant to keep discretion **real** (people can get relief) while keeping it **contestable** (favoritism can be detected and challenged). See also `66-justice-and-administrative-justice-governance.md` and `82-service-standards-and-minimum-service-guarantees.md`.

## A. Core rule (receipt over payload)
If an authority grants an exception that changes someone’s rights, obligations, eligibility, or the government’s obligations, it MUST emit a typed **Decision Receipt**:

- `DRR-TYPE: EXCEPTION` — the joinable spine for the waiver/variance/override.
- If the underlying detail cannot be public, still publish the **receipt** and follow `77-sensitive-information-and-secrecy-governance.md`.

**Design intent:** exceptions become *auditable objects* that can be counted, challenged, reviewed, and sunset — rather than informal “one‑offs.”

---

## B. Minimum fields for `DRR-TYPE: EXCEPTION`
A waiver/variance/override receipt MUST include:

1) **What changed**
- governed object(s): `RULE-*` (as‑of) and/or `STD-*` version, `SRV-*` (service), `CON-*` (procurement/contract), `ADS-*` (automation), or other pinned object IDs
- the specific obligation/threshold that is being departed from (cite the clause/field where feasible)

2) **Who authorized it**
- issuing **Unit ID** + `SIGNATORY-ROLE`
- if delegated/acting authority applies: cite the delegation receipt (`DRR-TYPE: DELEGATION`) (see `78-...`)

3) **Why (portable + contestable)**
- plain‑language rationale + `RC-*` reason code(s)
- legal basis pointer (the “can we do this at all?” rule)

4) **Bounds (make it reversible)**
- **time bound** (expiry date) and renewal standard (default: expire unless renewed) (`IOP-27/28`)
- scope bounds (who/where/volume/cap) + non‑transferability where relevant
- compensating controls / mitigations (what prevents abuse)

5) **Verification + remedy**
- how compliance/impact will be checked (link verification schedule or evidence release `REL-*` when relevant; see `81-...`)
- contestation lane(s) `AL-*` (including third‑party standing where the exception harms others)
- if the exception is high‑impact: open or pre‑commit an `AC-*` assurance case hook (`73-...`)

---

## C. The Exception Log (keep it small, keep it public)
Units that grant exceptions at material volume SHOULD publish a periodic **Exception Log** as a `REL-*` release:

- one row per active exception receipt (`DRR-*`) with: object type, category, issued‑at, expiry, and status (active/expired/renewed/revoked)
- method note (coverage thresholds, protected layer policy, revision log)

**Rule:** if you can’t publish the details, you still publish *existence + category + review date* (see `77-...`).

---

## D. Renewal, revocation, and “variance creep” controls
- **Renewal requires a new receipt** (do not extend silently). Cite the prior `DRR-*` and the renewal standard.
- **Revocation** emits a `DRR-*` that cites the exception and states the transition rule (avoid orphaned cases).
- **Variance creep triggers:** if exception volume/rate exceeds a stated threshold, open a scoped systemic `OFR-*` case (`LEGIBILITY-GAP` or `RULE-FIT`) and treat it as evidence the base rule/service/standard needs redesign (`IOP-28`, `76-...`).

---

## E. Common exception classes (portable categories)
Local systems may define finer categories, but SHOULD map to a small portable set:

- `EXC-HARDSHIP` (individual hardship / accessibility accommodation)
- `EXC-TRANSITION` (phase‑in, migration, deprecation bridge)
- `EXC-PILOT` (time‑boxed experiment with explicit evaluation)
- `EXC-PROCUREMENT` (competition exception / urgent sole‑source)
- `EXC-COMPLIANCE` (deadline/requirement extension with verification plan)
- `EXC-CONTROL-OVERRIDE` (temporary override of a control baseline; must route to internal assurance, `84-...`)
- `EXC-SECURITY` (narrow security exception; publish receipt and review date)

---

## F. Where this plugs in (do not duplicate)
- **Rule inventory / rulebook:** `25-...`, `39-...` SHOULD record whether a regime has waiver mechanisms and point to the exception log.
- **Permissioning / approvals:** variances and discretionary approvals MUST be `DRR-TYPE: EXCEPTION` and join to `RULE-*` and `AL-*` (`29-...`).
- **Procurement:** competition exemptions and urgent awards MUST have a joinable exception receipt that cites `CON-*` and the legal basis (`38-...`, `22-...`). Anchors: [BIB-US-FAR-SUBPART-6-3]; [BIB-EU-DIR-2014-24-OJ]; [BIB-UK-PCR2015-REG32].
- **Service delivery:** accommodations and channel exceptions that affect access or timeliness MUST emit receipts and appear in the exception log (`82-...`, `47-...`).
- **Internal controls:** control overrides are exceptions; material exceptions route into follow‑through (`OFR-*`) (`84-...`).
