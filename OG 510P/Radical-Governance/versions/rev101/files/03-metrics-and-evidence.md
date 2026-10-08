# Metrics & Evidence (Minimal Measurement Loops)

Governance systems fail when they can’t *see* reality or can’t *update* based on it. This memo defines a small, reusable measurement discipline.

## A. Measurement rules (to avoid fake precision)
- Indicators MUST be tied to a **decision loop** (what will change if the number moves?).
- Prefer **triangulation**: administrative data + independent audits + surveys + external indices.
- Use **leading** (early warning) and **lagging** (outcome) indicators.
- Every dashboard MUST list: definition, method, owner, update cadence, and known biases.
- Where feasible, indicators SHOULD reference a **Release ID** (dataset/series) with a public method note + revision log (prevents “silent updates”). See `26-epistemic-infrastructure-and-public-knowledge.md`.
- For major programs/policies, predicted effects SHOULD be recorded as joinable **claim IDs** (`CLM-*`) and linked to evaluation commitments under stable `PROG-*` IDs so decisions can be audited and updated. See `37-claims-evidence-and-update-discipline.md` and `28-program-register-and-evaluation-commitments.md`.


## A2) Anti-Goodhart / anti-gaming (make measurement robust to strategy)
Any metric that matters will be targeted. Treat **gaming** as a first-class failure mode of measurement systems.

Minimal defenses:
- **Use portfolios, not single KPIs:** track 2–4 indicators per goal (mix leading + lagging + quality + equity) so “optimize one” can’t hide harm.
- **Pin definitions + publish revisions:** every indicator SHOULD reference a `REL-*` release with a method note and revision log (prevents stealth redefinition).
- **Separate *measurement* from *delivery* where feasible:** independent audit/survey sampling reduces self-report bias.
- **Add canaries:** a small set of hard-to-fake sentinel measures (complaints, appeals, “no-response” rates, random spot checks).
- **Randomize oversight:** sampling audits and mystery-shopper style tests for high-volume services and enforcement interactions (joined to `SRV-*` / `ENF-*`).
- **Pre-register targets:** when targets change, publish the delta and keep the old series visible; “success” claims MUST cite both.

Design note: this is the measurement analogue of adversarial security—**assume strategic adaptation** and make it legible.

## B. The “4-loop” evidence system
1) **Observe:** publish baseline measures and uncertainty.  
2) **Decide:** record decision rationale, predicted effects, and the `PROG-*` ID (so evidence and revisions can attach).  
3) **Act:** implement with audit trails (money, procurement, discretion).  
4) **Review:** pre-committed evaluation window; publish results; revise or sunset.

## C. Minimal cross-scope indicator families (choose a small subset per scope)

### 0) Canonical metric packs (v1; prevent indicator drift)

These are **stable IDs** for a small set of reusable indicators. Memos SHOULD reference the IDs (e.g., `[IPM-2]`) and avoid inventing new names unless truly necessary.

**Selection rule:** pick **≤10 total** per scope. Default mix: 2–4 from **LRR**, 2–4 from **IPM**, 1–3 from **CAD**, plus 0–2 from **SAC/DAG/ECO/REG** as the scope requires.

#### Pack LRR — Legitimacy, rights, remedy (≤9)
- **[LRR-1] Participation breadth:** turnout/engagement + demographic reach for major decisions.
- **[LRR-2] Trust/fairness:** perceived fairness and legitimacy (survey; disaggregated).
- **[LRR-11] Participation integrity:** for major `ENG-*` processes, publish (a) % submissions deduped/clustered, (b) % verified (where relevant), (c) share of “undisclosed sponsor” mass campaigns (if any), and (d) time-to-official-response coverage. Treat “comment volume” as untrusted unless accompanied by a provenance summary (`REL-*`).
- **[LRR-3] Petition/complaint throughput:** intake volume + resolution time (median + 90p) for high-volume channels.
- **[LRR-4] Time-to-remedy:** median + 90p time from harm/decision → enforceable remedy (include outcome categories where possible).
- **[LRR-5] Case timelines/backlog:** priority case categories; backlog and median time-to-disposition.
- **[LRR-6] Compliance with binding decisions:** share of judgments/orders complied with on time (and noncompliance reasons).
- **[LRR-7] Identity & access coverage (where relevant):** coverage + issuance/renewal time for legal ID/CRVS; disaggregated.
- **[LRR-8] Decision transparency coverage:** share of rights-affecting decisions with published reasons + `RC-*` reason codes + `AL-*` appeal lanes (and ALR publication coverage) + disclosure compliance.
- **[LRR-9] Accessibility of remedy:** language/disability/offline access coverage for core grievance channels.
- **[LRR-10] Contestation outcomes:** appeal/challenge rates and outcomes (`AO-*`) by lane (`AL-*`) and reason (`RC-*`), incl. time-to-first-action and time-to-final-outcome, and the `AO-NORESP` share (missed-deadline defect rate).

#### Pack IPM — Integrity & public money (≤18)
- **[IPM-1] Open publication coverage:** share of spend/awards published with stable IDs (timeliness + completeness).
- **[IPM-2] Procurement competitiveness:** single-bid share (by value) + mean/median bids per tender.
- **[IPM-3] Vendor concentration:** top-10 share (or HHI) for key categories; trigger threshold review.
- **[IPM-4] Integrity disclosures & protections:** COI/asset declaration compliance; whistleblower retaliation incidence.
- **[IPM-5] Audit closure:** % audit findings/recommendations closed within 12/24 months.
- **[IPM-6] Budget credibility:** variance between approved budgets and execution (aggregate + priority programs).
- **[IPM-7] Consolidation coverage & timeliness:** % of public spend/liabilities in consolidated statements + time-to-publish audited accounts (incl. authorities/SOEs).
- **[IPM-8] Fiscal risk statement completeness:** guarantees/PPPs/SOEs/disasters/tax expenditures (existence + rubric score).
- **[IPM-21] Tax expenditure & subsidy transparency:** share of material `TEX-*`/`GRT-*` instruments in a public register with cost ranges, method notes, and review/sunset status (see `49-...`).
- **[IPM-22] Entity identity & beneficial ownership coverage:** share of major counterparties (contractors, grantees, lobby entities) with stable `EID` bundles; share of high-risk spend with joinable BO statement references and verification status.
- **[IPM-9] Debt + contingent liabilities:** trend + stress test of explicit and implicit exposures (off-book where material).
- **[IPM-10] Transfers predictability & legibility (multi-level):** share of transfers published with `TRF` IDs + formula/conditions; variance + timeliness; withholding/clawback events logged with reasons **and** (when service delivery is affected) the impacted `SRV-*` (flagging any `ESS-1` services) + whether the continuity backstop was triggered.
- **[IPM-11] Evidence coverage:** share of high-spend / rights-affecting programs with `PROG` + ≥1 `CLM` + ≥1 `EVAL` commitment.
- **[IPM-12] Evidence follow-through:** share of completed `EVAL` reports that have a published response (`DRR` or `PROG` revision) within an agreed window.
- **[IPM-13] Procurement openness & change-order share:** non-open share + change-order share (anti-capture/delivery signal).
- **[IPM-14] Dark enforcement metric:** enforcement without clear Rule basis / receipts (rule-of-law signal).
- **[IPM-15] Participation integrity & follow-through:** major decisions with `ENG` + timely `DRR` response.
- **[IPM-16] No-silent-algorithms compliance:** rights-affecting automated decisions cite `ADS-*`/`MOD-*`.
- **[IPM-17] Logged coercion coverage:** coercive contacts logged with `ENF-*` + receipt/serious-incident linkage completeness.
- **[IPM-18] Identity gate integrity:** coverage of legal ID/credential access, denial disparities for identity-gated services, and time-to-correction/fallback availability (tie to `IDN-*`).



### [IPM-13] Procurement openness & change-order share (anti-capture signal)
- **Non-open share:** value awarded via single-source/limited/emergency methods ÷ total awarded value (report by unit and category).
- **Single-bid share:** value of single-bid awards ÷ total awarded value.
- **Change-order share:** value added via amendments/change orders ÷ original awarded value (and % of contracts with ≥1 major amendment).
- **Close-out coverage:** share of contracts with documented completion/close-out review.

**Artifact hooks:** `CON` (prefer OCID), `DRR` for award/amendments, `AL-*` lanes for bid protest/sanctions. See CPR (`38-...`) and [BIB-OCDS].

#### Pack MCL — Mandate clarity & boundary health (≤5)
These measure whether people can reliably find *who is responsible* and whether cross-scope systems are legible.
- **[MCL-1] Competence ledger coverage:** % of public spend and liabilities covered by units with published ledger entries (incl. functional authorities).
- **[MCL-2] Ledger freshness:** median days since last review/update; count/share of stale entries.
- **[MCL-3] Mandate overlap & orphans:** number of reported issues with unclear/overlapping owner (incl. formal competence disputes); median time to assign a responsible Unit ID; median time to a competence ruling when disputed (if a lane like `AL-COMP` exists).
- **[MCL-4] Scope-change auditability:** % of mandate/boundary changes with published `DRR-TYPE: SCOPE` linked to the updated ledger entry.
- **[MCL-5] “Wrong door” rate:** share of service requests/grievances redirected because the initial authority was not responsible (trend and hotspots).

See: `34-competence-ledger-and-mandate-registry.md`, `70-interoperability.md`, `31-records-foi-and-government-memory.md`.

#### Pack CAD — Capability & delivery (≤8)
- **[CAD-1] Reliability/uptime:** outage frequency/duration for top critical services.
- **[CAD-2] Response/queue times + access friction:** median + 90p for top service requests, including processing time-to-decision and user-facing burden indicators (abandonment, rework/missing-doc loops), keyed by `SRV-*` where possible.
- **[CAD-3] Equity of access:** dispersion of service coverage/outcomes across neighborhoods/municipalities.
- **[CAD-4] Critical vacancy rate:** vacancy rate + time-to-fill for critical roles.
- **[CAD-5] Churn in critical roles:** turnover/attrition rate in key functions.
- **[CAD-6] Capex delivery slippage:** cost/schedule variance on top projects.
- **[CAD-7] Maintenance backlog:** asset condition / backlog ratio for key assets (key by `AST-*` where possible; see `48-asset-and-infrastructure-register.md`).
- **[CAD-8] Training completion (critical skills):** procurement/digital/frontline management completion rates for covered roles.

#### Pack SAC — Safety & coercion (≤7)
- **[SAC-1] Serious use-of-force incidents:** per encounter + injury severity; de-escalation compliance where measurable.
- **[SAC-2] Deaths in custody:** deaths in custody/detention; classification and public notice timeliness.
- **[SAC-3] Time-to-independent-review:** serious incidents assigned to independent review/investigation within defined SLA.
- **[SAC-4] Detention inspection coverage:** inspection coverage + critical findings closure rate.
- **[SAC-5] Mutual aid activations logged:** activations logged and reconciled (MASIP / MAAL compliance where applicable).
- **[SAC-6] Serious harm/victimization:** scope-appropriate serious harm rate (and trend).
- **[SAC-7] Perceived safety + trust:** survey-based perceived safety and trust in safety institutions.

#### Pack DAG — Digital & algorithmic governance (≤6)
- **[DAG-1] ADS register coverage:** % of rights-affecting systems listed and current.
- **[DAG-2] High-risk IA + audit completion:** % high-risk systems with completed IA and independent audit.
- **[DAG-3] ADS appeal outcomes:** appeal timeliness + overturn rate (with `RC-*` reason codes and `AL-*` lanes).
- **[DAG-4] ADS incident rate + response:** outages/undeclared updates/disparate impact signals + response time.
- **[DAG-5] Official data provenance:** publication with methods/provenance + correction latency.
- **[DAG-6] DPR coverage (personal data):** % high-risk processing activities listed and current in the DPR + on-time access/correction outcomes (tie to TM‑15).

#### Pack ECO — Ecology & commons (≤6)
- **[ECO-1] Monitoring coverage + lag:** air/water/emissions monitoring coverage + publication lag.
- **[ECO-2] Trajectory vs budgets/targets:** progress vs explicit ecological budget/targets (e.g., emissions trajectory).
- **[ECO-3] Enforcement closure:** inspection coverage + violation closure rate.
- **[ECO-4] Restoration completion:** restoration/no-net-loss completion where relevant.
- **[ECO-5] Leakage/arbitrage:** outsourced harms / regulatory arbitrage signals where measurable.
- **[ECO-6] Participation + justice:** access-to-info/participation/remedy coverage for ecological decisions.

#### Pack REG — Regulatory governance (≤5)
- **[REG-1] Rulemaking openness:** % major rules with draft + comment + published response log.
- **[REG-2] Review discipline:** % major rules with sunset/review clause; % reviews completed on time.
- **[REG-3] Regulatory appeal timeliness:** time-to-remedy for regulated parties and affected users (median + 90p).
- **[REG-4] Utility performance & affordability:** reliability/outage + affordability burden (lowest-income quintile) where measurable.
- **[REG-5] SOE disclosure & support transparency:** audited financials publication + state support/guarantee disclosure.

---



### 1) Metric recipes (decision-loop oriented)

The packs above are the *parts bin*. These “recipes” show **how to choose ≤10 metrics** that actually connect to a decision loop (and avoid duplicating long indicator lists).

**Recipe rule:** if you can’t name what will change when the number moves, delete the metric.

| Decision loop | Default metric IDs (starting kit) | Why this is usually enough |
|---|---|---|
| Legitimacy + remedy (high-volume) | `[LRR-1] [LRR-3] [LRR-4] [LRR-6] [LRR-8] [LRR-11]` | measures contestation, throughput, and whether remedies are real (not theatre) |
| Public money + procurement integrity | `[IPM-1] [IPM-2] [IPM-3] [IPM-5] [IPM-7]` | detects capture, non-competition, and “off-book” drift; ties to audit closure |
| Service delivery (frontline) | `[CAD-1] [CAD-2] [CAD-3] [CAD-6] [CAD-7]` | reliability + queues + equity + delivery slippage + maintenance debt |
| Coercion / custody governance | `[SAC-1] [SAC-2] [SAC-3] [SAC-4] [SAC-7]` + `[LRR-4]` | makes harm + independent review visible; adds time-to-remedy for affected people |
| Digital / ADS in rights-affecting decisions | `[DAG-1] [DAG-2] [DAG-3] [DAG-4]` + `[LRR-4]` | coverage + audit + appeal outcomes + incident signals; anchors to remedy |
| Personal data & surveillance risk (TM‑15) | `[DAG-6] [LRR-3] [LRR-4]` (+ `[DAG-4]` when ADS is involved) | makes “data power” visible: processing inventory coverage + request throughput + enforceable correction |
| Ecology / commons budgets | `[ECO-1] [ECO-2] [ECO-3] [ECO-6]` | monitoring + trajectory + enforcement closure + participation/remedy coverage |
| Regulatory governance (permits, tariffs, inspections) | `[REG-1] [REG-2] [REG-3]` + `[LRR-4]` | makes rulemaking legible, forces review discipline, and tracks appeal timeliness |
| Multi-level finance dependence | `[IPM-10]` + one outcome pack (usually `CAD` or `LRR`) | transfer predictability is the boundary-failure early warning for devolved mandates |

**If you can only track five:** `[LRR-4] [IPM-5] [IPM-7] [CAD-2] [CAD-3]`. Don’t measure “threats” directly—measure the failure signals (see `04-threat-models.md`) and link them to decisions.

## Optional external benchmarks (use sparingly)
External indices can be useful as **context** or as a backstop for “are we drifting?”—but they should not replace the local decision-loop metrics above. If you use them, **pin the version/date** and treat them as *inputs*, not targets.

- **V-Dem** (indices + Democracy Reports): see [BIB-VDEM-DATA] and [BIB-VDEM-DR-2025].
- **International IDEA** Global State of Democracy 2025 + tracker: see [BIB-IDEA-GSOD-2025].
- **World Justice Project** Rule of Law Index / overview: see [BIB-WJP-ROL].
- **Electoral Integrity Project** (GEIR 2024 + PEI dataset): see [BIB-EIP-GEIR-2024].



Method note: whenever a metric is published, prefer referencing a **Release ID** (dataset/series) with a method note + revision log (see `26-epistemic-infrastructure-and-public-knowledge.md`) to prevent “silent revisions.”

---

## D. Standard external “anchors” (use sparingly)
These are not “truth,” but useful comparative baselines:
- UN Fundamental Principles of Official Statistics (UNFPOS): see [BIB-UNFPOS].
- OECD Recommendation on Good Statistical Practice (OECD/LEGAL/0417): see [BIB-OECD-GSP].
- Worldwide Governance Indicators (WGI): see [BIB-WB-WGI]  
- Global Indicators of Regulatory Governance (GIRG): see [BIB-WB-GIRG].
- World Justice Project Rule of Law factors: see [BIB-WJP-ROL].
- SDG 16 (peace, justice, strong institutions): see [BIB-UN-SDG16]  
- Open Contracting Data Standard: see [BIB-OCDS].

## E. Falsification & stop conditions (anti-rationalization)
A reform SHOULD pause or reverse when any of these persist:
- watchdog independence declines (budget or appointment capture)
- discretionary power grows without audit trails (money, permits, enforcement)
- “exception regime” expands (emergency powers normalize without sunsets)
- measurement becomes less transparent (methods withheld, indicators cherry-picked)

### [IPM-14] Rulebook legibility & update discipline (anti-“dark enforcement”)
- **PRR SLA compliance:** share of new/changed enforceable rules entered in PRR within the SLA window (report by `UNIT`).
- **Citable enforcement share:** share of enforcement/eligibility `DRR`s that cite `RULE` IDs **and versions/as-of**.
- **Unregistered enforcement incidents:** count of cases where a decision cites no resolvable `RULE` (or cites “policy” without PRR entry).
- **Guidance creep:** count/value of `GLAW` items still enforced after a set aging threshold (e.g., >180 days) without conversion/repeal.


### [IPM-15] Participation integrity & follow-through (anti-consultation-washing)
- **Decision-hook coverage:** share of major decisions (high spend/rights/long-horizon) that cite an `ENG-*` when participation was promised or material.
- **Duty-to-respond compliance:** share of `ENG-*` processes with an official response `DRR` published by the deadline (report by unit/method class).
- **Representativeness/inclusion disclosure:** for processes with recruited participants, share that publish sampling/stratification parameters and inclusion supports (at least in aggregate; protect participant safety).
- **Participation-to-impact trace:** fraction of recommendations whose disposition is recorded (accepted/partial/rejected/deferred) with reasons (portable reason codes when feasible).
- **Process complaint rate:** complaints per `ENG-*` (with outcomes), to detect manipulation or exclusion.

(Implementation note: these metrics assume an Engagement Register keyed by `ENG` IDs; see `41-...` and `IOP-17`.)


**[IPM-16] Automated decision transparency & contestability**
- Share of rights-/resource-affecting decisions that cite `ADS-*` (and `MOD-*` when material) in `DRR`.
- Share of `ADS-*` entries with a live `AL-*` appeal lane + published `RC-*` reason code taxonomy.
- Change-control signal: count of material `ADS/MOD` changes without updated public register entry.


**[IPM-17] Logged coercion coverage (no dark enforcement)**
- **Event coverage:** share of coercive contacts with an `ENF-*` record (report by event type + unit).
- **Receipt coverage:** share of `ENF` events with a linked person-facing receipt (`DRR` / receipt ID), or a typed exception.
- **Receipt verifiability:** share of issued receipts that pass possession‑based verification (and the mismatch rate: receipts presented by subjects that have no corresponding `ENF/DRR` record).
- **Rule coverage:** share of `ENF` events citing `RULE-*` basis (**as-of**) (and `DRR-*` when warrant/order exists).
- **Serious-incident completeness:** share of serious incidents with `ENF-*` → independent pipeline → `OFR-*` case opened (`OFR-KIND: CASE`) → findings/responses + closure within window.
(Implementation note: assumes an Enforcement & Custody Event Register keyed by `ENF` IDs; see `43-...` and `IOP-18`.)


### [IPM-19] Emergency exception density & closure (anti-normalization)
**Why:** emergency powers are a common route to entrenchment and hidden bypasses.

**Signals (minimum):**
- **Days under emergency:** total days with any active `EMR-*` episode (per year).
- **Renewal intensity:** renewal count per episode; share of renewals with published deltas.
- **Emergency spend share:** % of procurement spend linked to `EMR-*` (joins `EMR` ↔ `CON` ↔ budget execution).
- **Sunset explicitness:** % of emergency measures with explicit end dates.
- **Service join coverage:** % of EMR measures that cite impacted `SRV-*` when service workflows are changed/suspended.
- **ESS floor breaches:** count of `ESS-1` continuity-floor breaches during EMR episodes; share with a published backstop/fallback plan (often via `TRF-*`) and closure corrective action.
- **Closure follow-through:** % of episodes with after-action review (`OFR-*`/`EVAL-*`) completed within target window.

**Mechanism:** raise renewal thresholds after N renewals; require closure artifacts to terminate an episode.
(See `45-emergency-measures-register.md`, `23-emergency-governance-and-exceptions.md`.)


### [IPM-20] Influence transparency & recusal compliance (anti-capture)
**Why:** capture often shows up first as *hidden contact*, *unmanaged conflicts*, and *procurement tailoring*.

**Signals (minimum):**
- **Disclosure coverage:** % of high-risk `DRR`s with `INF-*` citations or `INF: NONE DECLARED`.
- **Timeliness:** median days from interaction to `INF` publication (by channel).
- **COI compliance:** % of covered roles with up-to-date `INT` declarations; % overdue.
- **Recusal traceability:** % of recusals/authority changes that produce a joinable `DRR` citing `INT-*`.
- **Procurement joins:** % of above-threshold awards/amendments with recorded cross-check against relevant `INF/INT` (process attestation).

**Mechanism:** raise scrutiny on decision classes with low disclosure coverage; target audit sampling using `INF`↔`DRR`↔`CON` joins.
(See `46-influence-and-interests-register.md` and `22-public-integrity-and-procurement.md`.)

### [IPM-21] Tax expenditure & subsidy transparency (shadow spending signal)
- **Coverage:** % of material tax expenditures and grant/subsidy schemes present as `TEX-*`/`GRT-*` register entries.
- **Costing quality:** share with published method note + cost range (and revision log), and share with distributional notes (where feasible).
- **Governance discipline:** share with sunset/review status and a join to `DRR-*` for material renewals/expansions.

### [IPM-22] Entity identity & beneficial ownership coverage (anti-shell-entity)
**Why:** shell entities and ownership opacity enable procurement/subsidy capture, sanctions evasion, and conflict-of-interest laundering. The goal is not full disclosure of everything; it is a **joinable counterparty identity spine** with verification signals.

**Signals (minimum):**
- **EID coverage:** % of above-threshold `CON-*` and `GRT-*` awards with an `EID` bundle (and % with ≥2 identifiers where feasible).
- **BO join coverage (high-risk only):** % of high-risk spend with a joinable beneficial ownership statement reference (or a public pointer to a protected-layer statement).
- **Verification status:** share of BO disclosures verified (by check tier) and share corrected within a target window; false-statement enforcement events logged.
- **Cross-register coherence:** share of `INF-*` external parties that can be joined to contractor/grantee entities (EID match rate).

**Mechanism:** risk-tier the requirement (high-value, single-source, concessions, repeated awards, politically connected sectors) and use targeted audits; publish *coverage + verification* even when owner identities are protected.
(See `70-interoperability.md` (EID + BO join pattern), `38-...`, `49-...`, `46-...`, and `22-...`.)
