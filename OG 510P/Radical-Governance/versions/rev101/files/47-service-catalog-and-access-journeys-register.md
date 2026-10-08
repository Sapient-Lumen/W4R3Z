# Service Catalog & Access Journeys Register (Make Service Power Legible)

Most people experience “government” as **services**: getting an ID, applying for benefits, registering a business, requesting repairs, obtaining a permit, contesting a bill. When the service journey is opaque, **administrative burden** becomes a hidden policy instrument (and a corruption, exclusion, and surveillance surface). See: [BIB-RSF-ADMINBURDEN-2018].

This memo defines a minimal **Service Catalog & Access Journeys Register** keyed by stable `SRV-*` IDs. It does **not** store personal case data; it makes the *rules, steps, and accountability* of services legible.

**Anchor set (service design/delivery):** [BIB-OECD-GPP-SERVICE-2022], [BIB-UK-SERVICESTANDARD], [BIB-US-21C-IDEA-2018].

---

## A. Object: `SRV-*` (a public service definition)

A `SRV-*` entry is the canonical public definition of a service workflow:
- what the service is for (outcomes),
- who can access it (eligibility),
- what the state promises (time, channels, fees),
- what decisions occur (and when a `DRR` receipt is issued),
- how harms are corrected (appeal lanes),
- and what systems/contracting/data/automation are involved.

**Rule:** If a program exists (`PROG-*`), services are its *front door(s)*. A `PROG` can have multiple `SRV`s.

---

## B. Minimal public schema (one screen)

| Field | Meaning |
|---|---|
| Service ID | stable `SRV-*` (join-key) |
| Title + short description | plain-language “what it does” |
| Owning unit | Unit ID (competence ledger) + accountable officer role |
| Program link | `PROG-*` (if applicable) |
| Legal basis | `RULE-*` list (**with versions/as-of**) and any `CMP-*` authority |
| Eligibility & gates | plain-language summary + linked `IDN-*` (if identity/credential proofing gates access) |
| Inputs & evidence | required documents/attestations; “once-only” reuse sources if allowed |
| Channels | online/phone/in-person/mail; accessibility + language support |
| Fees & exemptions | amounts + waiver logic; payment channels |
| Decision points | when a rights-/resource-affecting decision occurs and a `DRR` receipt MUST be issued |
| Automation disclosure | if material, cite `ADS-*` / `MOD-*` (and human review option) |
| Time commitments | statutory deadlines and published median/90p processing times |
| Remedy / redress | `AL-*` lane(s) + urgent protection rules + correction deadlines |
| Data use | `DPR-*` entries relevant to the service; retention note |
| Procurement links | if delivery is vendor-supported, cite `CON-*` (and key subcontracting when published) |
| Funding / transfers | if service funding is conditional or cross-scope, cite `TRF-*` |
| Essentiality / continuity | `ESS-0` (non-essential) or `ESS-1` (essential): if `ESS-1`, define a **continuity floor** (minimum service mode) + backstop Unit/funding path so the service can’t be quietly collapsed via fiscal distress or transfer enforcement (continuity planning anchors: [BIB-FEMA-CGC-2024]; [BIB-ISO-22301-2019]) |
| Emergency mode(s) | pre-defined emergency adaptations (if any); when activated, cite `EMR-*` (and any temporary continuity-floor modification) |
| Change log | what changed and why; effective window |

**Publication note:** keep the public `SRV` page stable; older versions remain accessible via an “as-of” view (align with PRR `RULE` versioning).

---

## C. Interface rules (how `SRV` joins to the rest of the system)

1) **Decision receipts MUST cite service context**
- Any rights-/resource-affecting decision *within a service* MUST issue a `DRR` receipt that cites:
  - `SRV-*` (service context),
  - `RULE-*` basis (versions/as-of),
  - `AL-*` lane(s),
  - `IDN-*` when identity/credential gates were material,
  - `ADS-*`/`MOD-*` when automation materially influenced the outcome.
(See `31-...`, `08-...`, `70-...`, `44-...`, `42-...`.)

2) **No “procedural denial” without reasons**
- Denials for missing steps/documents MUST:
  - cite the exact requirement (`RULE-*` or documented `SRV` requirement),
  - name an accessible correction path and deadline (`AL-*` or correction lane),
  - and provide a *lowest-burden* alternative when permitted (attestation, assisted submission).

3) **Channel parity**
- If a digital channel exists, a safe alternative channel MUST exist for:
  - disability accommodations, language access, connectivity constraints, safety concerns.
Channel closures are a `DRR` decision citing the updated `SRV` and evidence for the change.

4) **Vendor/digital systems cannot be a black box**
- If a vendor-operated platform is used, the relevant `CON-*` MUST be linked.
- For rights-affecting or `ESS-1` services, vendor contracts SHOULD carry the **CLC pack** (receipt/record emission, audit access, portability/exit, FOI/records continuity) so outsourcing cannot defeat notice, remedy, or oversight (see `38-...`).
- If the platform implements rules, the legally controlling text remains the `RULE-*` (PRR); “rules as code” is derivative and subordinate.

5) **Essential services have continuity floors**
- `SRV` entries SHOULD carry an **essentiality flag** (`ESS-0`/`ESS-1`).
- If `ESS-1`, the `SRV` MUST publish a **continuity floor** (minimum service mode + fallback channel) and name a **backstop Unit** + funding path (typically a ring‑fenced or direct-pay `TRF-*`) so the service can’t be quietly collapsed via fiscal distress or transfer enforcement.
- Any action (including a transfer holdback/clawback) that would push an `ESS-1` service below its floor MUST trigger a logged corrective action and remain contestable via an `AL-*` lane. If emergency authority is part of the trigger or remedy, cite `EMR-*`.

---

## D. Burden budgets (make friction measurable)

A service SHOULD publish a small “burden budget”:
- step count (forms/screens) and required interactions,
- required documents/verification events,
- median time-to-complete (user time) and median time-to-decision (state time),
- abandonment and rework rates (missing-doc loops; duplicate submissions),
- denial share attributable to process defects (missing docs, unclear eligibility, channel failures).


**Anti-sludge / anti-dark-pattern constraint:** service interfaces MUST NOT use manipulative UX to change outcomes (e.g., hiding eligibility, burying opt-outs, confusing defaults, or infinite “missing document” loops). If the service relies on UX friction as a policy lever, it MUST be stated as such in the legal basis (`RULE-*`) and remain contestable via remedy lanes.
(Useful framing: “dark commercial patterns” [BIB-OECD-DARKPATTERNS-2022].)


**Metric hook:** fold into delivery metrics (CAD-2) and equity checks (CAD-3), keyed by `SRV-*`.

---

## E. Failure modes (what this prevents)

- **Procedural cruelty:** friction is used to shrink access without formally changing law. (See [BIB-RSF-ADMINBURDEN-2018].)
- **Hostile UX / dark patterns:** interfaces are tuned to reduce uptake or push people into unsafe defaults while claiming “access exists.” (Measure via burden budgets; treat as a remedy/oversight issue.)
- **“No wrong door” failures:** people bounce between offices because ownership/steps are unclear.
- **Hidden automation:** systems deny/triage without disclosure or remedy (`ADS-*` missing).
- **Stealth surveillance via eligibility gates:** identity systems expand beyond purpose (`IDN-*` missing or drifting).
- **Contract capture:** delivery platforms shape access; change-orders reshape incentives (`CON-*` not joinable).

---

## F. Where it plugs in
- PRR and legal legibility: `39-...`, `25-...`
- Decision receipts and records: `31-...`
- Remedy: `08-...`, ALR `36-...`
- Identity and eligibility gates: `44-...`
- Automated decision systems: `42-...`, `06-...`
- Procurement: `38-...`
- Implementation roadmap: `80-...`
- Multi-level finance/conditionality: `18-...`, `35-...` (essentiality/continuity floors and anti-hostage enforcement)
