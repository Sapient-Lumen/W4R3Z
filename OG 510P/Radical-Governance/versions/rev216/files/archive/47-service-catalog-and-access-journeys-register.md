# Service Catalog & Access Journeys Register (Make Service Power Legible)

**Purpose:** make services legible from below (steps, proofs, waits, reasons, remedies) so administrative burden can’t be used as hidden policy.

Most people experience “government” as **services**: getting an ID, applying for benefits, registering a business, requesting repairs, obtaining a permit, contesting a bill. When the service journey is opaque, **administrative burden** becomes a hidden policy instrument (and a corruption, exclusion, and surveillance surface). See: [BIB-RSF-ADMINBURDEN-2018].

This memo defines a minimal **Service Catalog & Access Journeys Register** keyed by stable `SRV-*` IDs. It does **not** store personal case data; it makes the *rules, steps, and accountability* of services legible.

**Anchor set (service design/delivery):** [BIB-OECD-GPP-SERVICE-2022], [BIB-UK-SERVICESTANDARD], [BIB-US-21C-IDEA-2018].

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Person-facing channel and non-reading floors: `98-persons-path-and-accessibility-invariants.md`.
- Service standards / MSG floors: `82-...`.
- Records/receipts (what/why/next-step, deadlines): `31-...`.
- Interop join keys for service journey artifacts: `70-...`.

## Named tensions (design must surface these)
- Simplicity/usability vs completeness (overwhelming catalogs become hidden denial).
- Proof burdens/fraud prevention vs exclusion and time/subsistence reality.
- Standardized journeys vs local adaptation and plural institutions.
- Digital convenience vs coercive exclusion (no app/AI-only front doors).

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
| Channels | online/phone/in-person/mail; accessibility + language support; **no app/AI-only front door** and an assisted/non‑digital equivalent MUST exist (`98-persons-path-and-accessibility-invariants.md`) |
| Fees & exemptions | amounts + waiver logic; payment channels |
| Decision points | when a rights-/resource-affecting decision occurs and a `DRR` receipt MUST be issued |
| Automation disclosure | if material, cite `ADS-*` / `MOD-*` (and human review option) |
| Time commitments | statutory deadlines and published time promises: **acknowledgement / first substantive contact / decision**, plus median/90p and tail-wait shares |
| Service standard & guarantees | pointer to the published standard (SS) and the current performance dashboard `REL-*`; for `ESS-1`, include MSG floor (see `82-...`) |
| Remedy / redress | `AL-*` lane(s) + urgent protection rules + correction deadlines |
| Data use | `DPR-*` entries relevant to the service; retention note |
| Procurement links | if delivery is vendor-supported, cite `CON-*` (and key subcontracting when published) |
| Funding / transfers | if service funding is conditional or cross-scope, cite `TRF-*` |
| Essentiality / continuity | `ESS-0` (non-essential) or `ESS-1` (essential): if `ESS-1`, define a **continuity floor** (minimum service mode) + backstop Unit/funding path so the service can’t be quietly collapsed via fiscal distress or transfer enforcement (continuity planning anchors: [BIB-FEMA-CGC-2024]; [BIB-ISO-22301-2019]) |
| Emergency mode(s) | pre-defined emergency adaptations (if any); when activated, cite `EMR-*` (and any temporary continuity-floor modification) |
| Change log | what changed and why; effective window |

**Accessibility invariant:** a service definition is incomplete unless a person without reliable internet, strong literacy, or dominant-language fluency can still complete the journey with assistance. Treat missing channels/assistance as a **service defect**, not “user error” (see `98-persons-path-and-accessibility-invariants.md`).
**Publication note:** keep the public `SRV` page stable; older versions remain accessible via an “as-of” view (align with PRR `RULE` versioning).


**Degraded-mode channels (low infrastructure):** “Channels” can include community radio, printed notices, public bulletin boards, and traveling/mobile service desks/ombuds, as long as they satisfy the person-facing invariants in `98-persons-path-and-accessibility-invariants.md`.

---

### B1) Proof burden inventory (publish the burden)
A service becomes a hidden exclusion tool when people cannot predict what proof is required.
- Each `SRV-*` SHOULD publish a compact **proof burden inventory**: required claims/documents, acceptable alternatives, where to obtain them, typical turnaround time, fees (if any), and an estimated **interaction/time/cost** burden for a typical applicant.
- Where fraud controls require stricter proof, the `SRV-*` entry MUST state the rule basis and the least-burdensome acceptable alternatives.

### B2) Once-only principle (don’t make people re-prove what the state already knows)
- Where lawful and safe, services MUST follow a **once-only** principle: if a fact is already held by the state, repeatedly demanding it from the person is a design defect and requires explicit justification.
- If repeated proof is required (time lapse, changed circumstances, adversarial context), the service MUST say why and provide a low-burden path.


### B3a) Time promises (ack vs contact vs decision)
A service can be “responsive” while still leaving people in limbo. `SRV-*` entries SHOULD decompose time obligations into **acknowledgement**, **first substantive contact**, and **final decision** (align with `82-service-standards-and-minimum-service-guarantees.md`). For `ESS-1` services, missed time promises MUST trigger the defined consequence (escalation / interim protection / deemed outcome) rather than silence (`08-...`, `36-...`, `98-persons-path-and-accessibility-invariants.md`).
Where feasible, `SRV-*` entries SHOULD also publish **typical** and **P90** cycle times for the three clocks (ack/contact/decision), and MUST provide a **non‑portal** way for the person to receive status updates (e.g., phone/in‑person/paper) so “waiting” is not an information black hole (EXP‑02; see `98-persons-path-and-accessibility-invariants.md`).


### B3) Navigation duty (no wrong door)
- `SRV-*` entries MUST list the **front-door** channels (online/offline) and the fallback escalation path.
- **No wrong door intake (hard):** any public‑facing contact point that can receive a request MUST either accept it or route it to the correct owner **without restarting the clock**, preserving a tracking number (see `08-...`, ALR `36-...`, and `98-persons-path-and-accessibility-invariants.md`).


### B3b) Representation duty (people who cannot self‑advocate)
Some affected parties cannot reliably file or contest on their own (children; people under custody/control; severe cognitive disability; incapacitation).
- `SRV-*` entries for rights‑affecting services that touch these groups MUST disclose **representative filing** options (who may file; proof of standing; conflict‑of‑interest handling).
- For high‑stakes services, the `SRV-*` entry SHOULD provide an **independent advocate / ombuds intake path** and name it on notices/receipts (see `08-...`, `36-...`, `98-persons-path-and-accessibility-invariants.md`).
- When the guardian/household decision‑maker may be adverse to the affected party, the service MUST offer a **safe, non‑guardian route** to contest or report.


### B4) Residual category handling (don’t erase edge cases)
Category systems always have edges; the people at the edges are often the most harmed.
- Each `SRV-*` MUST state what happens when a person does **not** fit the published eligibility categories (or cannot safely supply the “default” proof). Silent exclusion is not allowed: outcomes MUST still emit a `DRR-*` with reasons + a discoverable `AL-*` lane.
- For genuine “no-fit” cases, the service SHOULD provide an escalation path to authorized human adjudication (often via the relevant `IDN-*` gate’s residual path in `44-...`) and publish a periodic **category review** trigger when mismatch/deflection rates rise (see `98-persons-path-and-accessibility-invariants.md`).

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
- **Once-only disclosure in denials (recommended):** if a denial is driven by “missing documentation,” the `DRR` SHOULD state whether the missing item is plausibly **state‑obtainable** under once‑only / inter‑agency retrieval rules, and offer assisted retrieval or explain why repeated proof is required.


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
