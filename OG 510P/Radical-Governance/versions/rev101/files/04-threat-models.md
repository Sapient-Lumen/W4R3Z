# Threat Models (Cross-Scope Failure Modes)

This memo is a compact checklist of how governance systems break, with mitigation hooks into `02-design-toolkit.md`.


## Design posture: adversarial compliance
Assume actors will **optimize against** rules, metrics, and disclosure requirements (not merely violate them). Prefer mitigations that:
- make **noncompliance legible** (missing artifacts become contestable incidents),
- make **gaming costly** (random audits, reconciliation checks, and typed sanctions),
- and, where possible, make compliance **privately optimal** (simpler processes / funding access for good artifact hygiene).


## [TM-1] Capture (by money, parties, factions, or clans)
**Signals:** concentrated donors/vendors; revolving door spikes; policy favors narrow interests; watchdog budget starvation.  
**Mitigations:** `ACC-1/2/4/5/6`, `OPEN-1/2/10`, `DEC-2`, transparent appointments, randomized audits; publish findings→responses→closure (see `32-oversight-institutions-and-follow-through.md`).
**Metric hooks:** [IPM-2] [IPM-3] [IPM-5]

## [TM-2] Corruption & fraud (procurement and transfers)
**Signals:** single-bid contracts; repeated “emergency” contracting; missing deliverables; weak close-out audits.  
**Mitigations:** `OPEN-2/10`, `ACC-1/2/4/5`, beneficial ownership checks where feasible (see [BIB-FATF-BO-2023]), vendor performance histories, hard documentation rules for exceptions. See `22-public-integrity-and-procurement.md` and the CPR spec (`38-contracting-and-procurement-register.md`).
**Metric hooks:** [IPM-1] [IPM-2] [IPM-5]


## [TM-28] Ownership opacity & shell entities (who is the counterparty?)

**Pattern:** contractors, grantees, or influence intermediaries use shell companies, nominee directors, or opaque ownership chains to hide conflicts, evade sanctions, or enable patronage.

**Signals:**
- repeated awards to newly formed entities with shared addresses/directors
- rapid name changes or frequent related-party subcontracting
- weak or missing counterparty identifiers (cannot re-find in a registry)
- politically connected sectors with high single-source or amendment rates

**Mitigations (interface-first):**
- Require `EID` bundles for counterparties in procurement (`CON`), grants/subsidies (`GRT`), and influence disclosures (`INF`) so joins are possible across scopes (`70-...`).
- For high-risk/high-value instruments, require beneficial ownership disclosure; publish joinable statements as `REL-*` releases (prefer BODS [BIB-BODS]) or maintain protected-layer statements with public coverage + verification metadata.
- Implement verification tiers (self-declaration → registry cross-checks → targeted audits) and log false-statement enforcement actions as `DRR`/`OFR` events ([BIB-OPENOWNERSHIP-VERIFY-2020], [BIB-FATF-BO-2023]).
- Use concentration + change-order + influence joins to target audits (`CON`↔`INF/INT`↔`DRR`; [IPM-2] [IPM-3] [IPM-20] [IPM-22]).

## [TM-26] Shadow spending & policy-by-subsidy (grants, subsidies, tax expenditures)
**Signals:** large benefits delivered off-contract; rapid growth in tax expenditures; “pilot” subsidies that never sunset; opaque recipient lists; foregone-revenue estimates missing or revised without explanation.  
**Mitigations:** require `GRT-*`/`TEX-*` register coverage with stable IDs + costing method + revision logs (`49-...`); publish annual inventories with sunsets/renewal receipts; join awards to `DRR-*`/`RULE-*` and (for high-spend/high-risk) `CLM-*`/`EVAL-*`; apply integrity controls (beneficial ownership where feasible; conflict/influence joins); audit lotteries + reconciliation checks (see `02-...`, `32-...`).  
**Metric hooks:** [IPM-8] [IPM-11] [IPM-21]

## [TM-3] Coercion drift (security institutions become political tools)
**Signals:** opaque use-of-force, selective enforcement, intimidation of opposition, impunity.  
**Mitigations:** `SAFE-1/2/4/5`, `LAW-2/3`, public reporting, independent serious-incident investigations, separation of operational command; see `05-public-safety-and-coercion.md`.
**Metric hooks:** [SAC-1] [SAC-3] [LRR-4]

## [TM-4] Epistemic failure (decision-makers lose contact with reality)
**Signals:** suppressed stats; politicized public health/environment data; rapid narrative swings; policy without evaluation; information disorder overwhelms institutions; evidence laundering (selective metrics / selective studies); indicator drift without revision logs.
**Mitigations:** `OPEN-4/5`, claim-and-evidence discipline (`CLM-*`, `37-...`), `03-metrics-and-evidence.md` loops, red-team reviews, duty-to-respond, and MVEI (public releases with methods + revision logs) (`26-epistemic-infrastructure-and-public-knowledge.md`); platform/accountability alignment where relevant (see [BIB-UN-GDC]).
**Metric hooks:** [DAG-5] [LRR-8] [REG-1]

**Adversarial measurement note:** epistemic failure often appears as **KPI theater** (targets are met while reality worsens). Defend with metric portfolios, pinned definitions (`REL-*`), and independent sampling audits; see `03-metrics-and-evidence.md` (§A2).



## [TM-5] Legitimacy collapse (participation feels pointless)
**Signals:** low turnout + high cynicism; protests substitute for institutions; minorities excluded; decisions reverse without explanation.  
**Mitigations:** `DEC-2/3`, an Engagement Register with decision hooks + duty-to-respond (`IOP-17`), predictable review cycles, accessible remedy (`ACC-3`, `LAW-3`), rights protections.
**Metric hooks:** [LRR-1] [LRR-2] [LRR-4] [LRR-11]

## [TM-25] Participation manipulation (astroturf, bots, identity theft)

**Signals:** extreme comment volume with high duplication/form-letter clustering; credible reports of identity theft or scripted submissions; large “undisclosed sponsor” campaigns; mismatch between participation claims and verified/representative input; consultation records that cannot be audited.

**Mitigations:** treat participation as an **information integrity** problem as well as a legitimacy problem. Require `ENG-*` entries to publish an **Input Provenance Summary** (`REL-*` or indexed report) including dedupe/clustering methods, verification share (where relevant), and sponsor disclosure fields; label anonymous/unverified inputs; and make suspected manipulation an oversight event (`OFR-*` case) with a corrective `DRR` and follow‑through (see `41-...`, `32-...`). If one‑person‑one‑input or eligibility is material, disclose the assurance tier(s) and `IDN-*` gate(s) used; prefer privacy‑preserving uniqueness over globally joinable identities, and document tradeoffs for proof‑of‑personhood approaches. Anchors: [BIB-PEW-FCC-COMMENTS-2017]; [BIB-STANFORD-FILTERINGBOTS-2017]; [BIB-NYAG-FAKECOMMENTS-2021]; [BIB-POPP-SIDDARTH-2020].

**Metric hooks:** [LRR-11] [LRR-1] [LRR-2]

## [TM-6] Administrative overload (complexity > capacity)
**Signals:** backlogs; rule explosion; inconsistent decisions; shadow discretion; burnout and turnover.  
**Mitigations:** simplify mandates; publish service standards; build `CAP-1/2`; use tribunals (`LAW-3`); sunset low-value rules; maintain a public rules register with stable IDs + change logs (prevents "regulatory dark matter"); see `39-rulebook-and-instruments-registry.md` and `25-legal-legibility-and-rule-inventory.md`.
**Metric hooks:** [CAD-2] [CAD-4] [REG-2]

## [TM-23] Remedy sabotage / denial by delay (deadlines ignored)
**Signals:** chronic missed deadlines; “mandatory” pre-steps with no response SLA; high `AO-NORESP` share; procedural dismissals replacing merits review; essential-service harms continuing while remedies wait.  
**Mitigations:** require every `AL-*` lane to publish a `NO-RESPONSE-RULE` (auto-escalation and/or interim protection) and to log missed-deadline events as `AO-NORESP` via a review-result `DRR`. Escalate repeated misses to oversight (`OFR-KIND: FINDING`) and (for high-stakes harms) ensure interim protection is available. See `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md`.  
**Metric hooks:** [LRR-4] [LRR-5] [LRR-10]


## [TM-24] Adversarial compliance / gaming ("do the form, defeat the substance")
**Signals:** clean paperwork with worsening outcomes; sudden metric jumps at reporting cutoffs; policy compliance that shifts harm to unmeasured channels; “perfect” logs that don’t match complaints; selective issuance of receipts; systematic use of exceptions.
**Mitigations:** portfolio metrics + pinned definitions (`REL-*` + revision logs); **randomized audits** and cross-register reconciliation (payments↔contracts, denials↔appeals, enforcement↔complaints); require exception logs to be typed and sampled; make missing required artifacts appealable (`AL-LEG`) and auditable (`CASE-TYPE: LEGIBILITY-GAP`). Use **conditionality** and process simplification to reward artifact hygiene, and pair audits with a **self-report safe harbor** to surface near-misses (`ACC-8`) (see `35-transfer-register-and-conditionality.md` and `80-implementation-roadmap.md`).
**Metric hooks:** [LRR-8] [IPM-5] [DAG-5]


## [TM-7] Digital/vendor capture (opaque systems govern the public)
**Signals:** proprietary lock-in; un-auditable automated decisions; surveillance creep; data breaches; “terms of service” replacing law; outages-as-denial-of-service.  
**Mitigations:** `IOP-4/5`, procurement transparency (`OPEN-2`), privacy-by-design, audit logs + system registers, independent testing rights, exit clauses, and **contractual legibility** so outsourcing can’t create a shadow state (CLC pack: receipt/record emission, rule traceability for scripts/config, FOI/records continuity; see `38-...` and [BIB-HUP-GOVBYCONTRACT-2009]).
**Metric hooks:** [DAG-1] [DAG-2] [CAD-1]

## [TM-15] Targeting & surveillance (personal data becomes a political weapon)

Mitigation hook: enforce the **no silent algorithms** rule—`DRR` MUST cite `ADS-*` (and `MOD-*` when material), with `RULE` basis + `RC-*` + appeal lane `AL-*`; publish the `ADS` register (canonical `42-...`).
**Signals:** undeclared cross-agency data sharing; function creep (eligibility → enforcement); large-scale location/biometric use; “secret lists” or risk scores; low access/correction success; retaliation fears for using rights.  
Additional signal: unusual or discriminatory **Reason Code** (`RC-*`) distributions in denial/sanction decisions (when published in aggregate with safeguards).
**Mitigations:** `LAW-8` (data governance baseline) + DPR register discipline (`IOP-9`), retention/records controls (`OPEN-9`), independent complaint + audit channels (`ACC-3`, `ACC-6`), and explicit compacts for cross-scope/cross-border sharing (`IOP-1`). See `33-data-protection-and-personal-data-governance.md`. Anchors: [BIB-EU-GDPR]; [BIB-OECD-PRIV-2013]; [BIB-COE-C108].  
**Metric hooks:** [DAG-4] [DAG-6] [LRR-4] [LRR-8] [LRR-9] [LRR-10]


## [TM-8] Boundary failure (jurisdictional gaps and blame shifting)
**Signals:** “not my job”; unfunded mandates; inconsistent standards; crisis coordination failures; high “wrong door” routing for services/grievances.  
**Mitigations:** competence ledger + mandate registry (`34-competence-ledger-and-mandate-registry.md`), `70-interoperability.md` interfaces, `IOP-1` compacts, and a **duty-to-route** requests to the correct Unit ID (with public tracking). For contested competence, pre-designate a rapid lane (`AL-COMP`) and require a **backstop + timeout** so someone must issue a time-bounded interim routing/allocation order if the lane cannot rule by deadline (logged as `DRR-TYPE: COMPETENCE`). Scope/boundary changes MUST publish `DRR-TYPE: SCOPE` (`IOP-10`).  
**Metric hooks:** [MCL-3] [MCL-5] [IPM-10] [SAC-5] [CAD-3]



## [TM-9] Ecological overshoot (commons collapse and irreversible harms)
**Signals:** degrading baselines; permit systems divorced from outcomes; leakage across borders; “paper parks”; slow harms with no accountability.  
**Mitigations:** ecological budgets + registries + cross-boundary compacts (`OPEN-6`; `70-interoperability.md`); environmental rule-of-law disciplines; see `11-commons-and-ecological-governance.md`.
**Metric hooks:** [ECO-1] [ECO-2] [ECO-3]

## [TM-10] Fiscal illusion (commitments exceed reality)
**Signals:** off-budget vehicles; rising contingent liabilities; repeated “one-off” measures; missing tax expenditure disclosure; optimistic forecasts.  
**Mitigations:** `CAP-2/3/4`, consolidated accounts + audit, fiscal risk statements; see `07-fiscal-and-budgetary-governance.md`.
**Metric hooks:** [IPM-6] [IPM-8] [IPM-9]


## [TM-22] Fiscal distress → essential service collapse (austerity shock)
**Signals:** arrears/payroll delays; maintenance shutdowns; sudden fee hikes; “temporary” service suspensions; provider nonpayment; emergency-only operations becoming the norm; cuts concentrated in high-need areas.
**Mitigations:** treat **continuity of essential services** as a hard constraint of distress/workout design (not a discretionary promise). Operationalize this via:
- `SRV-*` catalog entries flagged `ESS-1` with published **continuity floors** (minimum service mode + fallback channel),
- `TRF-*` entries that publish beneficiary continuity backstops (route/direct pay/escrow rather than blunt suspensions), and
- distress interventions that remain legible and contestable (publish a `DRR` for material enforcement actions; route residents to an `AL-*` lane).
See: `18-intergovernmental-finance.md`, `35-transfer-register-and-conditionality.md`, `47-service-catalog-and-access-journeys-register.md`. Anchors: [BIB-OECD-SNG-INSOLVENCY-2018]; [BIB-IMF-SNG-FISCALRISKS-2022]; [BIB-WB-UNTILDEBT-2013].
**Metric hooks:** [IPM-9] [IPM-10] [CAD-1] [CAD-2] [CAD-3]


## [TM-21] Deferred maintenance & “capex theatre” (infrastructure decay)
**Signals:** glamorous new builds while core assets fail; backlog spikes; repeated emergency repairs; “ghost assets” (paid for, not there); condition claims without methods.
**Mitigations:** require an Asset & Infrastructure Register (`AST-*`) with condition grades, inspection methods, and backlog estimates (`IOP-23`); link capital approvals and deferrals to `AST-*` via `DRR` receipts; audit physical existence/condition samples; apply PIMA-style investment governance checks. See `48-asset-and-infrastructure-register.md`. Anchors: [BIB-OECD-INFRA-2020]; [BIB-IMF-PIMA-2022]; [BIB-ISO-55000].
**Metric hooks:** [CAD-6] [CAD-7] [IPM-8]


## [TM-11] Exclusion & invisibility (people fall outside registries)
**Signals:** high unregistered births/deaths; people unable to obtain ID; “paper-only” services; high denial/deferral rates for status; informal payments for documents.  
**Mitigations:** `IOP-6` identity + CRVS baseline with non-exclusion design; accessible enrollment; correction and remedy (`LAW-5`); audit disparities and reduce documentation burdens. See `12-identity-and-recognition.md`.
**Metric hooks:** [LRR-7] [LRR-9] [CAD-3]

## [TM-12] Regulatory capture & monopoly rents (utilities and markets)
**Signals:** opaque tariffs/fees; discretionary licensing; exemptions for incumbents; enforcement that targets small players; regulator-industry revolving door; “guidance” functioning as law.
**Mitigations:** `CAP-7` rulemaking quality + public regulatory inventory; `ACC-5` influence transparency; publish decisions/reasons/data; meaningful appeal (`LAW-5`); procedural fairness norms for competition enforcement; clear separation of ownership and regulation for SOEs (`CAP-8`). See `13-regulation-utilities-and-soes.md`.
**Metric hooks:** [REG-1] [REG-4] [IPM-3]

## [TM-13] Fragmentation & hidden government (special districts / SPVs proliferate)
**Signals:** explosion of single-purpose bodies; off-book borrowing; unclear accountability; overlapping mandates; low-information elections; procurement opacity.  
**Mitigations:** mandate that *all* authorities appear in the competence ledger (`34-...`), consolidate accounts + fiscal risk statements (`CAP-2/3`), standardized charters + sunset/re-charter, open contracting (`OPEN-2`), and explicit remedy lanes (`LAW-5`). Treat “ledger staleness” as a governance risk. For baseline evidence that special-purpose governments can be large and diverse, see [BIB-USCENSUS-SPECIALDIST-2022].  
**Metric hooks:** [MCL-1] [MCL-2] [IPM-7] [IPM-1] [IPM-9]


## [TM-14] Entrenchment & democratic backsliding (rules change so power can’t be replaced)
**Signals:** election rules changed for incumbent advantage; partisan election administration; intimidation of opposition/civil society; court/oversight capture; emergency powers used to delay transfers; selective prosecution; media capture; “legalism as repression” (formal rules used to disable contestation).  
**Mitigations:** independent election administration + transparent tabulation (`DEC-5`); political finance and influence transparency (`ACC-5`); emergency guardrails + EMR logging (`SAFE-3`, `23-...`); judicial independence + accessible constitutional review (`LAW-2`, `LAW-5`); rule-of-law health checks with public methods (`LAW-4`); oversight budget independence + follow-through (`ACC-1`, `ACC-6`); records/FOI and public reason-giving (`OPEN-1`, `OPEN-9`).  
**Metric hooks:** [LRR-1] [LRR-2] [LRR-10] [IPM-4]

**Anchors:** see [BIB-VDEM-DR-2025] and [BIB-IDEA-GSOD-2025].

**Referencing rule:** scope and domain memos SHOULD cite threats by ID (e.g., `TM-1`, `TM-8`) to keep risk language consistent and avoid “new names for old failures.”

## Minimal practice
Every scope memo SHOULD include:
- its top 3 threats from this list
- the *one* institutional change that most reduces each threat (small, not heroic)

## Artifact crosswalk (minimum public artifacts)
A fast link between common failure modes and the *smallest public artifacts* that make the mitigations enforceable.

| Threat | Minimum public artifact(s) |
|---|---|
| TM-1 Capture | lobbying/meetings register; contract register; Oversight Files & Responses Register (OFRR) |
| TM-2 Corruption & fraud | open contracting records (OCDS/IDs); typed exception records; debarment + appeal outcomes |
| TM-3 Coercion drift | published use-of-force policy; serious-incident case log; custody inspection reports |
| TM-4 Epistemic failure | Release IDs (methods + revision logs); corrections/errata log; Evaluation Registry |
| TM-5 Legitimacy collapse | decision records (reasons + legal basis); `ENG` register (decision hooks + official response); appeals/complaints stats |
| TM-25 Participation manipulation | `ENG` register + joinable provenance summary (`REL-*`); sponsor disclosure policy; oversight case log when manipulation suspected |
| TM-6 Administrative overload | service standards + backlog dashboard; public rules register with change logs/sunsets |
| TM-7 Digital/vendor capture | ADS/System Register; audit logging policy; portability/exit clauses disclosed |
| TM-15 Targeting & surveillance | DPR (processing inventory); access/correction request log; sharing agreements/compacts; breach/incident log |
| TM-27 Secrecy abuse / classification laundering | withholding/refusal `DRR` (existence metadata + review dates); disclosure/withholding log; independent review outcomes |
| TM-8 Boundary failure | competence ledger; compacts register; transfer register (including conditions) |
| TM-9 Ecological overshoot | ecological budget objects; permits/emissions registries; monitoring releases |
| TM-10 Fiscal illusion | consolidated accounts; fiscal risk statement; tax expenditure disclosure |
| TM-21 Deferred maintenance | Asset & Infrastructure Register (`AST-*`); condition/inspection releases; capex/deferral `DRR` receipts |
| TM-11 Exclusion & invisibility | CRVS/ID coverage stats; denial/deferral logs; correction/appeal queue |
| TM-12 Monopoly rents | tariff/fee decisions with reasons; rulemaking docket; appeal outcomes |
| TM-13 Fragmentation & hidden government | entity/SPV inventory; consolidated accounts; procurement disclosure |
| TM-14 Entrenchment & backsliding | election administration logs; Emergency Measures Register; oversight findings→closure |

## Artifact controls (minimal anti-capture spine)
Many threats are “stopped” less by ideology and more by **mandatory artifacts** that make abuse contestable.

- **Competence ledger + PRR Rule IDs** (who had authority, under what rule): constrains mission creep and forum-shopping (`70-interoperability.md`, `25-...`). Hits TM‑1/2/5/6/14.
- **Decision Records / Receipts (`DRR`)** (reasons + legal basis + appeal lane): prevents silent punishment and makes remedy real (`31-...`, `08-...`). Hits TM‑5/6/11/12/14.
- **Engagement Register (`ENG`)** (decision hook + duty-to-respond): prevents consultation-washing and makes participation auditable (`41-...`). Hits TM‑5/1/14.
- **Public Data Release Register (`REL`)** (methods + revisions): prevents epistemic capture and “numbers laundering” (`26-...`). Hits TM‑3/7/8/13.
- **OFRR** (findings → responses → closure): blocks oversight theater (`32-...`). Hits TM‑1/6/10/12.
- **DPR + access/correction logs** (personal data legible and contestable): blocks targeting-by-database (`33-...`; `IOP-9`). Hits TM‑15/11/14.
- **OCDS + beneficial ownership disclosure** (contracts/concessions legible): blocks procurement-as-patronage (`22-...`; see [BIB-OCDS]; [BIB-BODS]). Hits TM‑1/2/6/10.

Rule of thumb: if a government can act **without leaving these traces**, it will be captured.
## [TM-16] Dark enforcement & unlogged coercion (rights violations without records)

When coercive power is exercised without receipts and joinable logs, abuse becomes deniable, remedy becomes impossible, and learning collapses into rumor.

**Mitigation hook:** enforce **no dark enforcement** — coercive contacts generate `ENF-*` event logs + person-facing receipts (`DRR`/receipt), with `RULE` basis (as-of) and complaint lane `AL-*`; custody episodes logged start→end; serious incidents trigger independent pipeline (`24-...`) and link to `OFR-*`. (Canonical: `43-...`; see also `31-...`, `36-...`.)
**Enforcement note (non-circular):** the requirement is enforced by treating **missing required artifacts** as a rights violation in itself: (a) a complainant can file into an urgent `AL-*` lane on the basis of “no receipt / no log,” (b) oversight audits sample for gaps and issue findings with deadlines, and (c) repeated gaps trigger presumptive remedies or sanctions (policy choice), because *delay/opacity becomes the tactic*.


**Signals:** high complaint rate with low logged-event rate; missing/duplicated IDs; “unknown reason” share rising; evidence retention gaps (missing bodycam/dashcam pointers); spikes in emergency/exception usage; unexplained disparities by area/group.

**Metric hooks:** [IPM-17] [SAFE-2] [LRR-4]



## [TM-27] Secrecy abuse / classification laundering (hide power behind exemptions)

**Attack / failure mode:** over-classification, over-redaction, NDAs, and broad “commercial confidentiality” claims suppress decision reasons, evidence, and public-money traceability. The state still acts, but contestation becomes impossible because the record surface is intentionally darkened.

**Symptoms:** refusal/heavy-redaction share rising; vague or expanding exemption categories; long secrecy durations without review; low reversal rates; “confidential by default” contracting; missing declassification/review logs; discrepancy between public narrative and what later emerges through leaks/whistleblowing/litigation.

**Mitigations (minimum):** treat withholding as a joinable decision artifact. Denials/withholding MUST emit a `DRR-KIND: REFUSAL` with typed legal basis, non-sensitive reasons summary + `RC-*`, **existence metadata** (class, date range, holding unit, counts), a review-by date/sunset rule, and `AL-*` lanes. Independent review should be able to inspect withheld material (in camera) and publish outcome summaries; periodic withholding reports SHOULD be published as `REL-*` releases. Contracts MUST not use confidentiality clauses to block lawful oversight/audit (see the CLC pack in `38-...`).

**Anchors:** access-to-documents baselines and national-security exception guardrails: [BIB-COE-TROMSO], [BIB-TSHWANE-2013], [BIB-JOHANNESBURG-1995].

**Metric hooks:** [LRR-8] [LRR-4]


## [TM-17] Identity gatekeeping & exclusion (rights denied by opaque chokepoints)

When identity proofing and credential systems are opaque, they become a **discretionary choke point**: people lose benefits, housing, mobility, and political access without a legible decision, and “missing paperwork” becomes a proxy for discrimination.

**Mitigation hook:** make the gate auditable — maintain an `IDN` register describing proofing/issuance/verification + correction and appeal paths; denials due to identity/eligibility MUST issue a `DRR` citing `RULE` (as-of), `IDN-*`, and `AL-*` (and `ADS-*`/`MOD-*` when automated). Add fallback paths for essential services and audit denial disparities. (Canonical: `44-...`; see also `12-...`, `08-...`, `33-...`, `70-...`.)

**Signals:** high “documentation missing” denial share; long correction times; denial disparities by group/area; large vendor lock-in; frequent identity system outages; unexplained join growth (identity used for new purposes without rule changes).

**Metric hooks:** [IPM-18] [LRR-3] [LRR-4] [DAG-6]



## [TM-18] Exception entrenchment (“temporary” powers become permanent)
**Attack / failure mode:** governments invoke emergency authority to bypass normal constraints (procurement, data access, elections, movement, enforcement), then renew repeatedly without deltas until the exceptional becomes the baseline.

**Symptoms:**
- repeated renewals with no published delta; indefinite extensions;
- emergency procurement without joinable contracting records;
- restrictions imposed without clear appeal lanes or urgent protection;
- silent revisions to measures; unclear legal basis (“whatever is necessary”).

**Mitigations (minimum):**
- **EMR register discipline:** publish episode + measures with explicit sunsets and renewal/termination `DRR`s; all exceptions cite `EMR-*`.
- **Rising renewal thresholds:** higher bars after N renewals; require published deltas each time.
- **Joinable constraints:** emergency procurement still appears in CPR (`CON-*`), emergency data access in DPR (`DPR-*`), coercive actions in `ENF-*`.
- **Service continuity floors:** if emergency authority changes delivery of `ESS-1` services, the EMR measure cites impacted `SRV-*` and records the continuity-floor check + beneficiary-protecting backstop (often via `TRF-*`).
- **Contestability:** `EMR-*` entries list the relevant `AL-*` lanes, including urgent protection.
- **Closure requirement:** after-action review (`OFR-*`/`EVAL-*`) before “episode closed.”
(See `45-emergency-measures-register.md`, `23-emergency-governance-and-exceptions.md`.)


## [TM-19] Influence laundering (shadow lobbying, intermediaries, revolving door)
**Attack / failure mode:** private interests shape public outcomes through unofficial channels (messages, intermediaries, “advisors,” gifts/travel, post-employment promises), leaving no official trace and making conflicts deniable.

**Symptoms:**
- high-impact decisions with no contact disclosure and thin reasons;
- procurement specs tailored to a narrow vendor set; heavy amendment/change-order patterns;
- repeated “informal” contact via channels not logged as meetings;
- conflicts handled privately (no recusal record; no ethics determination).

**Mitigations (minimum):**
- **INF/INT register discipline:** publish `INF-*` interactions and `INT-*` declaration status; no silent edits; late filing is visible.
- **DRR disclosure rule:** high-risk `DRR`s cite `INF-*` (or `INF: NONE DECLARED`) and cite `INT-*` when recusals/management actions apply.
- **Procurement joins:** contract awards and major amendments remain joinable (`CON-*`); cross-check integrity joins (`INF/INT`) on above-threshold cases.
- **Contestability:** explicit `AL-*` lanes for ethics findings, register noncompliance, and sanctions; urgent protection available where coercion or livelihood is implicated.
- **Oversight loop:** sampling audits use `INF`↔`DRR`↔`CON` patterns; findings close via OFRR (`OFR-*`) (see `32-...`).

**Interface hooks:** `INF`, `INT`, `DRR`, `CON`, `AL`, `OFR`  
**Metrics hooks:** [IPM-20] [IPM-13]


## [TM-20] Administrative burden as stealth policy (procedural cruelty, access shrinkage)
**Attack / failure mode:** rules stay formally unchanged, but access is reduced via *process friction* (forms, repeated verification, documentation demands, channel closures, confusing requirements). This can function as targeted exclusion while remaining deniable and hard to litigate. See: [BIB-RSF-ADMINBURDEN-2018].

**Symptoms:**
- rising abandonment and rework loops (missing-doc churn); high “procedural denial” share;
- frequent recertification/reverification with little fraud/error evidence;
- digital-only channels without safe alternatives; language/accessibility failures;
- inconsistent requirements across offices; frontline discretion substitutes for rule clarity;
- service steps/commitments not published (no `SRV-*`); receipts omit the specific requirement being enforced.

**Mitigations (minimum):**
- **Service legibility:** publish and version a Service Catalog & Access Journeys Register (`SRV-*`), including steps, documents, channels, deadlines, fees, and remedy lanes (see `47-...`).
- **Receipt discipline:** any denial for missing steps/docs MUST issue a `DRR` citing the exact requirement (`RULE` as-of or `SRV` requirement) and a correction/appeal lane (`AL-*`) (see `08-...`, `31-...`).
- **Measure friction:** include burden indicators in delivery metrics (CAD-2) and equity checks (CAD-3), keyed by `SRV-*` where possible (see `03-...`).
- **Gate audit:** if identity/credential proofing gates access, decisions cite `IDN-*` and correction deadlines; prohibit stealth joins to surveillance (see `44-...`, `33-...`).
- **Service standards:** require joined-up, whole-journey design and accessible channels (see [BIB-OECD-GPP-SERVICE-2022], [BIB-UK-SERVICESTANDARD]).
