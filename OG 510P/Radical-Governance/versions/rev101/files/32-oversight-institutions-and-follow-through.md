# Oversight Institutions & Follow‑Through (Audit, Ombuds, Integrity)

“Checks and balances” fail in practice when oversight is **starved**, **captured**, or **non-binding** (findings disappear into political fog). This memo defines a compact *oversight stack* and a *follow‑through loop* that works across scopes.

**Anchor set (start here):**
- See: [BIB-INTOSAI-P10]; [BIB-INTOSAI-P1]; [BIB-VENICE-OMB-2019]; [BIB-UN-PARIS-PRINC-48134].
---

## A. Treat oversight as a closed loop (not a “watchdog” slogan)
**Goal:** convert findings into verified fixes.

**Minimum loop**
1) **Discover** (audit/investigation/complaints)
2) **Publish** (redacted where necessary)
3) **Respond** (duty‑to‑respond with an action plan)
4) **Remediate** (implementation with deadlines)
5) **Verify & close** (independent verification; closure criteria)

**Rule:** if a body can publish findings, the governed entity MUST have a **time‑bound duty to respond** and the public MUST be able to see whether issues were closed.

---


### OFRR lifecycle states (make “follow-through” auditable)
Use a small state machine so findings don’t disappear into narrative.

| State | Meaning | Who can set it | Minimum evidence |
|---|---|---|---|
| `OPEN` | file opened; response clock starts when a response is required | oversight body | record + scope + legal basis |
| `RESPONDED` | duty-to-respond satisfied | responsible unit | action plan + owners + dates |
| `IN-REMEDIATION` | fixes in progress | responsible unit | work log + budget/contract links |
| `VERIFICATION` | independent check underway | oversight body / verifier | test plan + data sources |
| `CLOSED-VERIFIED` | fix verified and durable | oversight body | verification note + residual risk |
| `REOPENED` | recurrence or failed fix | oversight body | trigger evidence + new plan |

**Interface rule:** OFRR entries SHOULD link to `RULE` (legal basis), `PROG` (program), `CON` (contracts), and `REL` (data releases) where applicable (see `70-interoperability.md`).

### OFR kinds (case vs. finding)
The same join-key (`OFR-*`) must cover both *event-linked oversight cases* and *standalone findings*, without proliferating ID families.

- **`OFR-KIND: CASE`** — an open file for an incident/investigation/pattern inquiry. A case MAY contain multiple findings over time, but the **case ID stays stable** so timelines and responses remain joinable.
- **`OFR-KIND: FINDING`** — a standalone published finding (e.g., an audit report) that still needs a duty-to-respond, action plan, and closure verification.

**Rule (serious incidents):** serious incidents SHOULD open an `OFR-*` with `OFR-KIND: CASE` (and `CASE-TYPE: SERIOUS-INCIDENT`) within 24 hours (see `24-mutual-aid-and-serious-incident-protocol.md`).

## B. Minimum Viable Oversight Stack (MVOS)
Rather than proliferating agencies, define a small stack by *function*.

### Core (should exist at municipal+; national MUST)
1) **External audit (SAI / audit office)**
- mandate: financial + compliance + (optionally) performance/value-for-money
- outputs: audited accounts; thematic audits; recommendation tracking

2) **Ombuds / complaints reviewer (low-cost remedy)**
- mandate: maladministration, service failures, procedural justice
- outputs: case resolutions + systemic “pattern reports”

3) **Integrity investigation / inspector general function**
- mandate: corruption, serious misconduct, conflicts, procurement fraud
- outputs: investigations + referrals + systemic risk findings

### Optional add-ons (scope-dependent)
- **NHRI (rights monitoring)** — typically national; may be regional in federations.
- **Independent election administration** — where elections occur.
- **Independent fiscal institution** — for forecasting/costing discipline.
- **Data protection / competition / sector regulators** — where market power or sensitive data are central.

**Design rule:** new oversight bodies SHOULD only be created if they cover a distinct failure mode *and* can be made independent *and* the follow‑through loop is in place.

---

## C. Independence protections (portable)
Independence is not a vibe; it is *appointment + tenure + budget + access*.

**MUST (all core oversight bodies)**
- **Appointment transparency:** published criteria; public shortlist; conflict disclosures.
- **Removal for cause only:** narrow grounds; recorded reasons; reviewable.
- **Budget protection:** formula or multi-year floor; cannot be retaliatorily cut mid‑investigation.
- **Access to records:** statutory right of timely access (including contractors, where public funds or delegated authority is involved).
- **Publication default:** publish findings with narrow, typed redactions.

**SHOULD**
- **Plural appointment pathway:** e.g., mixed supermajority + independent panel to reduce single‑party capture.
- **Cooling-off and revolving door limits** for oversight leadership.

Anchors for these protections appear in INTOSAI‑P 1/10 (audit independence) and the Venice Principles (ombuds independence and mandate).

## C2. Oversight ecosystem (press, civil society, and complainant support)
Institutional oversight works better when the *public oversight ecosystem* is not starved or chilled.

**MUST**
- keep FOI/RTI **fees low/capped**, publish deadlines, and make denials typed + appealable (see `31-...` and [BIB-COE-TROMSO]).
- protect whistleblowers and provide safe reporting channels (see [BIB-EU-WHISTLE-2019]).
- protect complainants against retaliation (including in service/benefit systems) and make retaliation itself contestable (log as a case where feasible).

**SHOULD**
- provide basic **navigation help** (ombuds/legal aid) for complex remedy lanes so rights exist in practice.
- enable accredited researchers/auditors to access protected data in secure settings for replication and disparity testing (privacy‑preserving; purpose‑limited).
- publish “evidence packs” for major public decisions so third parties can contest reasons and detect omissions.


---

## D. Follow‑through protocol (stop “audit theatre”)
### 1) Duty to respond
- MUST: every published finding requires a **written response** within a fixed window (e.g., 60–120 days) stating:
  - accept / partial / reject (with reasons)
  - actions, deadlines, owners
  - required resources (if any)

### 2) Public tracking
- MUST: publish status and closure criteria; “implemented” claims require evidence.
- SHOULD: legislative hearing or council session for high-severity findings.

### 3) Escalation ladder
- SHOULD: repeated noncompliance triggers:
  1) mandatory public hearing
  2) budget holdback on the affected program (bounded)
  3) referral to prosecutor / tribunal / court (as appropriate)

**Rule:** escalation MUST be typed and linked to the legal basis (`RULE-*` IDs where available).

---

## D2. Legibility-gap audits (treat absence as a signal)
Artifact discipline is only enforceable if *missing artifacts* create an auditable trail.

**Pattern:** open a typed oversight case when statistical or administrative signals suggest “dark government”:
- complaints/surveys show high coercive contact, but `ENF-*`/`DRR-*` logs are low;
- significant spending occurs without matching `CON-*` records;
- denial volumes rise without corresponding receipts or reason codes.

**OFRR practice:** create `OFR-KIND: CASE` with `CASE-TYPE: LEGIBILITY-GAP`, publish the detection method (at a high level), require a remediation plan with deadlines, and verify closure via sampling.

This makes “nothing happened” contestable: absence becomes a joinable object in the same follow-through loop as other findings.


**Detection tactics (keep cheap):**
- **Randomized sampling** (“mystery shopper” service requests; spot-check receipts vs. outcomes).
- **Reconciliation checks** (payments↔contracts↔deliverables; denials↔appeals; enforcement contacts↔complaints).
- **Whistleblower intake + safe disclosure** (with optional *bounded* integrity bounties for verified high-impact omissions, where lawful).
- **Synthetic test cases** for ADS-driven processes (submit controlled inputs to validate reason codes, deadlines, and recourse behavior).
- **Self-report + safe harbor:** maintain a channel where units/vendors can file correction receipts for artifact failures (missing logs, wrong bases, data errors) and earn reduced sanctions for fast correction—while repeat self-reports trigger deeper audits (`ACC-8`).

**Empirical note (why randomization matters):** randomized audits/monitoring have shown deterrence and leakage-reduction effects in field settings, and public disclosure of audit findings can change political incentives by informing voters (see [BIB-OLKEN-2007]; [BIB-FERRAZFINAN-2008]).


**Assurance practice (make control failures predictable):**
- publish a lightweight **registry conformance report** (quarterly/annual): % decisions with `DRR`, % denials with `RC-*` + `AL-*`, % deadlines met (and `AO-NORESP` logs where not), % services with published burden budgets, % core registers with “as-of” access.
- run periodic **adversarial drills** (“governance red‑teaming”): attempt to execute a rights-affecting action *without* producing the required artifacts, or to sabotage remedy by delay, and measure detection + escalation time.
- treat “artifact integrity” as part of assurance: checksum manifests + mirrors for core registers (see `31-...`).




## D3. Participation‑integrity cases (stop consultation capture)

Where public consultation is online (or high‑volume), it is vulnerable to **bot floods, identity theft, and organized astroturf** that manufacture the appearance of consent. Treat this as a governance integrity issue, not a PR dispute.

**Pattern:** open an `OFR-*` with `OFR-KIND: CASE` and `CASE-TYPE: PARTICIPATION-INTEGRITY` when there is credible evidence of manipulation *or* when an `ENG-*` process fails to publish a required provenance summary.

**Minimum case outputs**
- a public **provenance summary** (join to the `ENG-*` entry; usually a `REL-*` release) describing dedupe/clustering and any verification sampling;
- a typed remediation plan (platform controls, sponsor disclosure enforcement, re‑run or re‑weighting policy);
- a corrective `DRR` for any material decision that relied on manipulated inputs (or a recorded justification for why not).

Anchors: [BIB-PEW-FCC-COMMENTS-2017]; [BIB-STANFORD-FILTERINGBOTS-2017]; [BIB-NYAG-FAKECOMMENTS-2021]. Canonical participation register: `41-...`.



## E. Oversight Files & Responses Register (OFRR)
To prevent oversight from disappearing into PDFs, maintain a small public register conforming to `IOP-9`.

**Minimum:** a machine-readable feed + human view.

### OFRR — minimum fields
- **OFR ID** (stable)
- **OFR kind** (`CASE` / `FINDING`)
- **Issuing body** (Unit ID; appears in competence ledger)
- **Case/finding type** (audit / ombuds pattern / investigation / evaluation / inspection / serious incident / other)
- **Subject unit(s)** (Unit IDs)
- **Trigger joins** (for `CASE`: linked `ENF-*` / `DRR-*` / `EMR-*` / `CMP-*` as applicable)
- **Linked objects** (`RULE-*` IDs, `PROG-*` IDs, `CON-*` IDs, `PAR-*` IDs, `EMR-*` IDs, etc.)
- **Severity** (small ordinal scale)
- **Publication date** + redaction basis (if any)
- **Response due date** + link to response
- **Action plan** (owners + deadlines)
- **Status** (see lifecycle states)
- **Closure verification** (who verified + date)

**Recordkeeping:** preserve underlying decision records and evidence links (see `31-records-foi-and-government-memory.md`).

---

## F. Minimal metrics (portable)
Prefer metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- audit/oversight **closure rate** within 12/24 months [IPM-5]
- median time from finding → published response (new; can be added as a local derivative of [IPM-5])
- repeat findings rate (same issue reappears within 24 months)
- ombuds case resolution time and systemic pattern rate [LRR-4]
- substantiated misconduct/corruption cases with outcomes (bounded, privacy-preserving) [IPM-4]

