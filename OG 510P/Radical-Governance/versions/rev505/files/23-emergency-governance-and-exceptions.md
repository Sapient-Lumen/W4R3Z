# Emergency Governance & Exceptions (States of Emergency, Escape Clauses, Crisis Powers)

**Stack relation:** use `286-emergency-powers-stack-and-exit-governance-guide.md` for the canonical route across the emergency / exception cluster. This memo is the broad system frame; `112` is the generic exception-control kernel; `165` is the canonical emergency-powers rails layer; `186` is the narrower declaration / renewal / sunset companion; `234` is the public-health operating specialization.

**Purpose:** enable crisis response without permanent exception—time-bounded, logged, reviewable, and reversible.
**Person served:** a person living under emergency powers who needs exceptions to be bounded, documented, and reversible—while remedy and records remain available.

**From-below:** This keeps crises from becoming blank checks by forcing time limits, receipts, and review while harm is still preventable.
**EXP pointer:** counters `EXP-02` (Waiting) and `EXP-05` (Fear) in emergencies by requiring receipted coercion + reachable review even in degraded modes (`98-persons-path-and-accessibility-invariants.md`).
**Material floor (one sentence):** emergency protocols assume degraded infrastructure; publishability, receipting, and remedy/record continuity MUST have a lowest‑infrastructure variant (radio/posters/paper + staffed intake). (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-05).)

Emergencies are when legitimacy and the rule of law are *most needed*—and when systems most often break.
This memo defines a compact **Emergency & Exceptions Protocol** so governments can act fast **without normalizing exceptional powers**.

**Anchor set (start here):**
- ICCPR Article 4 (derogations; strict necessity, non‑discrimination): [BIB-ICCPR].
- UN HRC General Comment No. 29 (states of emergency; legality + reporting discipline): [BIB-HRC-GC29].
- Siracusa Principles (limitation/derogation interpretive constraints): [BIB-SIRACUSA].
- Venice Commission (2020) *Interim Report on the measures taken in the EU Member States as a result of the COVID‑19 crisis…*: [BIB-VENICE-COVID-EMERGENCY-2020].
- ECtHR Guide on Article 15 (derogation notice + strict necessity): [BIB-ECHR-A15-GUIDE-2025].
- Venice Commission compilation on states of emergency (benchmarks): [BIB-VENICE-SOE-COMPILATION-2020].
- Council of Europe Treaty Office note on Article 15 notice/registration procedure: [BIB-COE-A15-NOTIF-PROC].
- FEMA Continuity Guidance Circular (2018; 2024 update) (continuity of essential functions/services): [BIB-FEMA-CGC-2024].

**Canonical EMR spec:** `45-emergency-measures-register.md`.

**Public health + biosecurity response spine:** see `57-public-health-and-biosecurity-governance.md` (surveillance releases + trigger rubrics + contestable measures).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Emergency measures must still emit **receipts + reasons + sunsets**: `45-emergency-measures-register.md`, `31-records-foi-and-government-memory.md`.
- Person’s path under crisis (waiting harm, proof burdens, safe remedy, non-digital access): `98-persons-path-and-accessibility-invariants.md`, `82-service-standards-and-minimum-service-guarantees.md`, `47-service-catalog-and-access-journeys-register.md`.
- Coercion controls do not pause in emergencies: `05-public-safety-and-coercion.md`, `43-enforcement-and-custody-event-register.md`.
- Oversight follow-through (after-action closure must bind): `32-oversight-institutions-and-follow-through.md`.
- Community continuity under exception: `24-mutual-aid-and-serious-incident-protocol.md`, `10-micro-local.md` (don’t treat mutual aid as volunteer slack; fund and protect it).

## Named tensions (design must surface these)
- **Speed vs contestability:** fast action is necessary; unreviewable action becomes normalization of exception.
- **Transparency vs panic/retaliation:** publish what people need; protect vulnerable reporters and operators.
- **Central command vs local legitimacy:** crisis coordination must not erase local realities and harm patterns.
- **Governance vs violence:** when emergency powers collapse into indiscriminate force, the archive becomes a record of failure; keep coercive actions receipted and reviewable. (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-16).)

**See also:** `165-emergency-powers-derogation-sunsets-rails.md` (derogation standards + sunset rails).

---

## 0) Collapse boundary (name the limit)
Some crises are not “exceptions within law” but a breakdown into coercion without accountability (war, civil conflict, mass repression). The archive’s interfaces can reduce drift and document abuse, but they cannot substitute for the basic political conditions of lawful governance (independent oversight, enforceable remedy, and non‑arbitrary use of force). Emergency design SHOULD explicitly plan for degraded modes (paper receipts, independent witness/recordkeeping, minimum service floors) rather than assuming normal infrastructure. (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-16).)

## Preparedness baseline (build the legitimacy infrastructure *before* crisis)
Emergency design fails when the “rules of exception” are invented mid‑event. Minimum preparedness:
- **Prebuilt registers:** EMR (`45-...`) and the core join‑keys (`DRR`, `RULE`, `AL-*`, `REL`) must exist in peacetime (even if sparse).
- **Pre‑committed thresholds:** define a small set of trigger conditions (public health, disaster, security) and what procedural upgrades they activate (notice, renewal votes, review, continuity checks). For climate/disaster-risk baselines + trigger rubrics as auditable infrastructure, see `63-climate-adaptation-and-disaster-risk-governance.md`.
- **Receipt discipline under stress:** emergency actions still issue receipts (`DRR`) and log exceptions; “urgent” is not a waiver for illegibility.
- **After‑action duty:** every emergency declaration and renewal schedules an after‑action review with publication by deadline (logged; missed deadlines become `AO-NORESP`).

This does not prevent abuse by itself, but it ensures crises cannot be used as a pretext to operate entirely off-ledger.

## A. Core concept: “exceptions are typed and logged”
An **exception** is any deviation from baseline constraints:
- rights limits beyond ordinary law,
- accelerated/waived procedures (procurement, permitting, inspections),
- extraordinary data access/sharing,
- extraordinary fiscal actions (escape clause, emergency appropriations, debt/guarantees),
- extraordinary coercive powers (curfew, detention, movement restrictions).

**Classification rule (rights mode):** each measure MUST state whether it is (a) an ordinary **limitation** under existing law, (b) an emergency-accelerated **limitation** (still within ordinary limits), or (c) a **derogation** under a treaty/constitutional derogation clause. If (c), the EMR MUST record the required **depositary notifications** and the exact provisions derogated (see [BIB-ICCPR], [BIB-HRC-GC29], [BIB-ECHR-A15-GUIDE-2025], [BIB-COE-A15-NOTIF-PROC], [BIB-VENICE-SOE-COMPILATION-2020]).

**Rule:** *If it isn’t typed and logged, it didn’t happen (officially).*
Exceptions MUST be legible to auditors, courts, and the public.

---

## B. Minimum Viable Emergency Governance (MVEG)

- **Assurance case (where stakes are high):** recurring or high-impact emergency/exception regimes SHOULD have an `AC-*` case (claims, controls, monitoring thresholds, stop/review triggers; see `73-assurance-case-and-governance-safety-case.md`).

### MVEG-1 Declare narrowly (typed, bounded, time-limited)
A formal emergency declaration MUST specify:
- **Hazard type** (e.g., flood, epidemic, cyber incident, riot) and *trigger evidence*,
- **Geographic coverage** (map or service-area reference),
- **Powers invoked** (enumerated; no “blank cheque” clauses),
- **Rights affected** and the proportionality rationale (**rights mode**: limitation vs derogation; if derogating, list provisions derogated and required depositary notifications),
- **Start / end time** (short default), and **renewal conditions**.

**Default:** use ordinary limitation powers first; use derogations/state-of-emergency only when ordinary law is insufficient.

**Cross-border interface note:** where global notification/coordination obligations exist (e.g., pandemics under the IHR), the EMR entry SHOULD include references to the relevant global instruments and any required notifications (see [BIB-WHO-IHR-TEXT-2025]).

### MVEG-2 Renewal is a decision, not an autopilot
- MUST: renewal requires an affirmative vote (or equivalent multi-party approval) on a fixed cadence.
- MUST: each renewal republishes (a) what changed, (b) what powers remain necessary, (c) what will end next.
- SHOULD: require a higher threshold after N renewals (anti-normalization).

### MVEG-3 Independent review stays on
- MUST: courts/tribunals remain open for emergency-related harms (remote if needed).
- MUST: rapid review lane for high-impact restrictions (movement, assembly, detention, property seizure).
- SHOULD: ombuds/inspection bodies have guaranteed access (incl. detention facilities).

(See: `08-remedy-and-grievance.md`.)

### MVEG-4 Emergency measures register (public)
Publish a public **Emergency Measures Register** (EMR) with stable IDs, containing:
- declaration + renewals,
- each exceptional measure (what power; who authorized; scope; duration),
- links to: procurement exceptions, data exceptions, fiscal actions, coercive actions,
- after-action review link (when complete).

This prevents “hidden emergency government.”

### MVEG-5 Procurement and fiscal actions get *stricter* ex post
- MUST: emergency procurement uses a dedicated exception type; publish vendor, value, justification, delivery status; trigger an ex-post audit.
- MUST: emergency appropriations/guarantees/debt are logged with beneficiaries, ceilings, and end dates; consolidate off-book entities.
- SHOULD: pre-approved framework contracts and surge rosters reduce sole-source reliance.

(See: `22-public-integrity-and-procurement.md`, `07-fiscal-and-budgetary-governance.md`, `18-intergovernmental-finance.md`.)

### MVEG-6 Emergency data powers are time-bounded and logged
- MUST: emergency access/sharing requires: purpose, legal basis, minimization, retention limit, audit log, and deletion/rollback plan.
- MUST: publish a public summary in the EMR (without compromising operational security).
- SHOULD: split “public health/relief operations” data use from “law enforcement” data use with hard firewalls.

(See: `06-digital-and-algorithmic-governance.md`.)

### MVEG-10 Essential service continuity is a hard constraint (no “quiet collapse”)
- SHOULD: any emergency measure that changes or interrupts a service workflow cites impacted `SRV-*` entries (and whether any are `ESS-1`).
- MUST: if a measure risks pushing an `ESS-1` service below its published **continuity floor**, the EMR entry includes a beneficiary-protecting backstop plan (typically a `TRF-*` continuity routing/escrow/direct-pay design) **or** logs a temporary floor modification as a typed measure with an explicit end date and urgent-protection `AL-*` lane.
- SHOULD: where possible, predefine “emergency mode(s)” in the service catalog so the EMR can cite a known fallback rather than invent ad hoc rules.
- MUST: after-action review reports any `ESS-1` floor breaches and corrective actions.

Anchors: disaster-risk governance emphasis on resilience/“build back better” [BIB-UNDRR-SENDAI-2015]; continuity guidance for essential services during outbreaks [BIB-WHO-EHS-2020].

### MVEG-7 Elections and power-transfers are protected (anti-entrenchment; TM-14)
- MUST: emergency powers cannot be used to entrench incumbents.
- MUST: election date changes require: independent election authority concurrence + cross-party supermajority + a clear rescheduling bound.
- SHOULD: publish a short **election-integrity notice** for any emergency-era changes to election operations (what changed, why, who approved, how contestation/audit will work).
- See: `56-elections-and-electoral-administration.md` (MVEIS: auditability + dispute lanes).
- SHOULD: sunset any emergency speech/assembly restrictions automatically unless renewed with heightened scrutiny.

### MVEG-8 Mutual aid and compacts are pre-authorized
- SHOULD: pre-negotiate mutual aid compacts with:
 - standardized reporting,
 - rights baselines,
 - cost-sharing rules,
 - cross-jurisdiction command clarity,
 - dispute resolution and exit/continuity clauses.

(See: `19-compacts-and-cooperative-governance.md`, `70-interoperability.md`.)

### MVEG-9 After-action review is mandatory
Within a fixed window after termination:
- MUST: publish an **After-Action Review**: what worked, what failed, rights impacts, spend/outcomes, corrective actions, and deprecations.
- SHOULD: run a public hearing (or citizens’ panel) for high-salience events.

---

## C. Emergency Measures Register (EMR)
See the canonical register spec: `45-emergency-measures-register.md`.

---

## D. Common failure modes (and the antidotes)
- **Normalization:** renewals become routine → *raise renewal threshold over time + publish delta each renewal.*
- **Blank-cheque clauses:** “whatever is necessary” → *enumerate powers; prohibit open-ended delegations.*
- **Secrecy by default:** emergency treated as classified → *publish EMR summaries; classify narrowly* (see `77-sensitive-information-and-secrecy-governance.md`).
- **Exceptional procurement capture:** repeated sole-source → *framework contracts + ex-post audit + delivery verification.*
- **Data creep:** surveillance persists → *retention caps + deletion proofs + audit logs.*
- **Rights scapegoating:** targeted restrictions → *non-discrimination checks + rapid remedy lane.*
- **Off-book finance:** SPVs/guarantees hidden → *consolidate accounts + publish liabilities.*
- **Entrenchment via emergency:** crisis powers used to delay transfers, suppress contestation, or harden rules → *MVEG-7 discipline + EMR transparency + independent review stays on.*

---

## E. “Ideal” extensions (only when capacity exists)
- A standing **resilience unit** (scenario planning, drills, surge staffing, logistics).
- Trigger-based stabilizers (automatic relief and unemployment support) to reduce discretionary emergency spending.
- Cross-scope incident command templates (with rights baselines baked in).
