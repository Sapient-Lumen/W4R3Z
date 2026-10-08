# Governance Test Suite (Quick checks that catch illegitimacy early)

**Purpose:** convert political ideals into **tests** you can run on any institution/interface—before deployment, after incidents, and at revision time.

**How to use:** treat each test as a “unit test” for a governance component. If it fails, you need either (a) a redesign, or (b) an explicit, appealable exception with safeguards.

---

## T‑0: Standing & scope

- **T0.1 — Standing clarity:** Can an affected person tell *why they count* (or why they don’t) and how to challenge standing?
- **T0.2 — Scope fit:** Is the decision made at the lowest scope that can handle the externalities? If not, is the cross‑scope delegation explicit?
- **T0.3 — No ping‑pong:** If more than one authority is plausibly responsible, is there a single accountable lane with interim continuity and a bounded binding decider?
- **T0.4 — Failure migration:** If a scope can’t meet the capability/rights floor, is there an explicit escalation + continuity duty + return test?
- **T0.5 — Authority routing is explicit:** For any case type, can the public compute the single-responsible endpoint (SRE), see delegations/compacts/shared-service edges, and find the appeal path as-of a timestamp? (Anchor: `221-jurisdiction-graph-and-authority-routing.md`.)
- **T0.6 — Cross-border no ping‑pong:** for cross‑border matters, the system returns a single cross‑border SRE and issues a Jurisdiction Packet with continuity duty + contest lane (see `230-conflict-of-laws-and-cross-border-dispute-rails.md`).


- **T3.15 — Constitutional change is legible and anti-bundled:** proposed constitutional changes have a public Change Packet (text diff + reasons + rights/checks impact) and are single-subject; high-risk “Harder Path” triggers are enforced (see `206-constitutional-change-and-amendment-rails.md`).
- **T3.16 — Rules have review or expiry discipline:** high-impact rules appear in a public Rule Register with review dates; sunset continuation requires a published continuation report; rollback lanes exist for clear harm/failure (see `207-sunset-review-and-rollback-rails.md`).
- **T3.17 — Material changes have CHG packets + public release notes:** any material change to policy, service access, data requirements, enforcement intensity, or automated decision logic has a Change Packet (authority + delta + monitoring + remedy readiness) and a `REL-*` release note (see `208-change-management-and-release-engineering-for-government.md` and `51-release-registry.md`).
- **T3.18 — No silent swaps (verifiable “as-of” state):** the public can determine the current rule/version “as of now,” see what changed, and obtain a receipt linking to authority and remedy (see `53-publication-integrity-and-tamper-evident-logs.md`, `39-rulebook-and-instruments-registry.md`, and `208-change-management-and-release-engineering-for-government.md`).
- **T3.19 — Lawmaking is diff-first and amendment-legible:** bills and amendments publish diffs, reasons, and a joinable log of submissions→responses→changes; no vote on material text without a final Change Packet + implementation/remedy readiness (see `215-legislative-process-and-drafting-rails.md`).
- **T3.20 — Recognition/refusal is bounded:** cross‑border recognition/enforcement refusals use a bounded list of reasons, are receipted, and include an appeal lane with a public clock (`230`).
- **T3.21 — Seam continuity holds:** rights/status do not lapse while cross‑border coordination proceeds; temporary protection activates on clock breach (`230`, `109`).
- **T3.20 — RIA + ex post review closes the loop:** material rules ship with an impact assessment packet and a review commitment, and negative findings trigger a binding update (renew/modify/sunset) rather than report-only outcomes (see `216-regulatory-impact-assessment-and-ex-post-review-rails.md`, `133-evaluation-and-learning-integrity.md`, `207-sunset-review-and-rollback-rails.md`).


(Links: `70-interoperability.md`, `71-interface-obligations-by-scope.md`, `109-portability-and-cross-jurisdiction-continuity.md`, `114-interjurisdictional-dispute-and-coordination.md`, `14`, `103`.)

---

## T‑1: Visibility & reasons (anti‑mystery governance)

- **T1.1 — Authority receipt exists** (who/why/jurisdiction).
- **T1.2 — Reasons are legible** to a non‑insider (plain language + evidence pointers).
- **T1.3 — Data provenance**: what facts came from where; what is contested; what is unknown.
- **T1.3a — Access to information (ATI/FOI):** Can a person request official documents, receive clocked status updates, obtain partial disclosure by default with exception reasons + sunsets, and appeal to an independent reviewer? (Anchor: `200-freedom-of-information-and-access-to-official-documents-rails.md`.)
- **T1.4 — Rule version replay:** Can you identify the exact rule version that governed the outcome, and reproduce the decision under that version? (Anchor: `118-rulemaking-and-change-control.md`.)
- **T1.5 — Selection replay (if applicable):** Can you reproduce any random selection (panel/audit/lottery) from a Draw Receipt (`DR-*`) and public randomness? (Anchor: `119-selection-and-sortition-integrity.md`.)
- **T1.6 — Influence footprint (if applicable):** For major decisions, can you join the Decision Receipt to an Influence Ledger (contacts/advisors) and verify any recusals/conflict-handling receipts? (Anchor: `120-conflicts-of-interest-and-influence-integrity.md`.)
- **T1.7 — Algorithmic registry (if applicable):** If an algorithmic system influenced the outcome, is it listed in the public registry with owner, version, inputs, monitoring, and an appeal path? (Anchor: `191-algorithmic-systems-registry-and-audit-rails.md`.)
- **T1.7 — Protected disclosure lane:** Can a reporting person file anonymously, receive a receipt, get interim protection, and see clocked status updates without retaliation risk? (Anchor: `121-whistleblowing-and-protected-disclosure.md`.)
- **T1.8 — Future impact trace (if applicable):** For major rule/budget/coercion changes, is there a Future Impact Statement (`FIS-*`) and a Sunset & Review Receipt (`SRR-*`) with a bounded review date and rollback triggers? (Anchor: `122-intergenerational-and-future-protection.md`.)
- **T1.9 — Association & collective remedy:** Can people organize and file collectively without retaliation risk, and do collective submissions produce clocked response receipts and systemic remediation? (Anchor: `123-association-and-collective-power.md`.)
- **T1.10 — Constitutional change receipts (if applicable):** For any foundational change, can you trace `APP-*` → `CCR-*` gates (notice, deliberation, decision, review) and identify the exact active `FVER-*`? (Anchor: `124-constitutional-amendment-and-entrenchment.md`.)
- **T1.11 — Status integrity (identity/membership):** For any eligibility/identity/residency decision, does a `CSR-*` exist with evidence pointers, effective dates, and a reachable contest lane—and does transfer across institutions preserve standing/clocks (non-reset + provisional continuity)? (Anchor: `125-identity-membership-and-civil-status.md`.)
- **T1.11a — Digital identity minimization + portability:** If a digital identity/credential is used, can the person satisfy the requirement via *minimal disclosure* (claim-based proof), switch wallet/provider without losing access, and obtain a denial receipt + fast restoration lane (no silent lockout)? (Anchor: `160-digital-identity-credentials-privacy-utility.md`.)
- **T1.12 — Data access / purpose integrity:** For any person-impacting decision, can you join `DRR-*` → `PDR-*` (what data was used, for what purpose) and (on request) produce a bounded `ALR-*` view of access/share events with safety-aware withholding receipts and a correction lane? (Anchor: `127-data-governance-and-privacy-interfaces.md`.)
- **T1.12a — Federation corridor registry:** Can you enumerate every cross-domain data-sharing corridor (who→who, purpose, legal basis, retention) and show an approval/change receipt for each corridor? (Anchor: `211-privacy-preserving-federation-and-consent-ledgers.md`.)
- **T1.12b — User-visible access ledger:** Can an individual obtain a bounded access ledger (near-real-time) showing who accessed or shared their data, with purpose binding and a contest lane? (Anchor: `211-privacy-preserving-federation-and-consent-ledgers.md`; joins: `127`, `200`.)
- **T1.12c — Credential revocation reliability:** If credentials are used, can revocation propagate rapidly to verifiers, and can denial/restoration be completed within published time-budgets? (Anchor: `210-digital-identity-and-credentialing-rails.md`.)

- **T1.13 — Interoperability conformance & seam continuity:** For any cross-agency exchange, can you point to an Interface Card (`IIC-*`), show an Interface Change Receipt (`ICR-*`) for recent changes, and demonstrate conformance—*without* resetting clocks/evidence during transfer? (Anchor: `128-interoperability-interfaces-and-standards.md`; seam invariants: `109`, `114`.)

- **T1.14 — Epistemic integrity (public sphere):** For high-impact public claims or integrity incidents, can you (a) log the incident with scope/time/sunset, (b) show amplification policy/receipt for any reach changes, (c) issue correction receipts that propagate proportionally to original reach, and (d) provide a safe contest lane for takedown/downrank/label actions? (Anchor: `129-public-sphere-and-epistemic-infrastructure.md`; joins: `112`, `115`, `120`.)

- **T1.15 — Audit trail & follow‑through (if applicable):** Can you trace `APR-*` → `AFR-*` → `MRR-*` and see a live `FTL-*` follow‑through ledger with escalation when deadlines are missed—and are audit scope exclusions receipted and reviewable? (Anchor: `130-audit-and-inspection-integrity.md`.)
- **T1.15a — SAI independence + public accounts loop (if applicable):** Is there an independent SAI with unrestricted access and publish rights, and does a Public Accounts process force time‑bounded executive responses, remediation tickets, and verification (no paper closure)? (Anchor: `231-supreme-audit-institutions-and-public-accounts-rails.md`; joins: `130/226/227`.)
- **T1.16 — Official statistics integrity (if applicable):** For any high-impact public metric, can you identify the `STAT-*` Series Card (definition, method version, release cadence), reproduce revisions via `REV-*`, and show independence safeguards for method/timing (no selective release)? (Anchor: `184-official-statistics-and-census-integrity.md`.)
- **T1.17 — Microdata confidentiality & safe access (if applicable):** If research access to microdata exists, is there an access ladder with `MDA-*` receipts, documented disclosure controls (`SDL-*`), output-check receipts (`OUT-*`), and published time-to-approve metrics—without enforcement spillover? (Anchor: `185-microdata-access-and-disclosure-avoidance-rails.md`.)
- **T1.16 — Sanction proportionality & review (if applicable):** For any enforcement action at penalty-or-stronger levels, does a `CFR-*` exist with rule-version linkage, a proportionality/reversibility check (`PRC-*`), and a reachable contest window—and do debarments/exclusions have bounded durations and reinstatement criteria? (Anchor: `131-compliance-and-sanctions-integrity.md`.)


- **T1.17 — Mandate drift & scope clarity:** For each major body, is there a current one‑page `MC-*` Mandate Card, and does every material delegation (`DLG-*`) or competence shift (`SCR-*`) have a receipted record with contestability—and are overlaps/gaps tracked in an `OGR-*` with a seam owner and continuity defaults? (Anchor: `132-mandates-and-jurisdiction-scope-integrity.md`.)

(Links: `03-metrics-and-evidence.md`, `06-digital-and-algorithmic-governance.md`, `104`, `118-rulemaking-and-change-control.md`, `119-selection-and-sortition-integrity.md`, `120-conflicts-of-interest-and-influence-integrity.md`.).

---

## T‑2: Contestability & remedy (anti‑Kafka)
- **T1.18 — Ex post evaluation & loop closure:** For each material program/rule/budget line, is there at least one current `CLM-*` claim and an `EPR-*` plan, with findings (`EFR-*`/`PIRR-*`) published by deadline, and a binding update (`DUR-*`) when results arrive—especially when results are negative? (Anchor: `133-evaluation-and-learning-integrity.md`; joins: `104/105/118/130`.)
- **T1.19 — Legibility & complexity budgets:** For each person-facing pathway, is there a published complexity budget (steps/time/cost/docs/language), and do budget breaches trigger circuit breakers (interim protection / escalation / deadline-default), with breaches recorded in a public incident ledger? (Anchor: `134-legibility-and-complexity-budgets.md`; joins: `98/108/109/114/115/118/130`.)
- **T1.20 — Revenue integrity & replay:** Are revenue rules versioned and public (TRR-*), and can any assessment/payment/refund be replayed from receipts (TAR/TPR/TRF) with clear clocks and non-retaliation protections? (Anchor: `135-taxation-and-revenue-integrity.md`; joins: `118/131/134/115/127/109`.)
- **T1.21 — Land / housing integrity & displacement continuity (if applicable):** For any permit/zoning/allocation/relocation, do `PCR/CCR-*` cards exist, and can you trace `LDR-*` / `HAR-*` / `DRP-*` with rule-version linkage and bounded clocks—without seam resets during transfer—and do displacement cases carry interim protections when deadlines are missed? (Anchor: `136-land-housing-and-commons-integrity.md`; joins: `108/109/114/118/134/131`.)





**T1.22 — Critical infrastructure / utilities continuity (if applicable):** For any outage, rationing, or safety shutdown, is there a published `USC-*` service card, and do significant events generate joinable `OER-*` receipts with restoration clocks, protections for medically/legally dependent people, and post‑incident audit hooks? If scarcity triggers prioritization, are `PRR-*` receipts issued with rule-version linkage and contest lanes? (Anchor: `137-critical-infrastructure-and-utilities-integrity.md`; joins: `108/112/115/118/130`.)

- **T2.1 — One‑click contest path exists** (or equivalent low‑friction path).
- **T2.2 — Interim protection** triggers when delay is irreversible harm (subsistence/rights/safety).
- **T2.3 — Remedy is real**: can outcomes be changed; are harms compensated; are precedents published?
- **T2.4 — Service promises are published:** each essential service has a short public service card (eligibility, expected times, errors, contestation lanes) (see `189-service-level-governance-and-redress-ops.md`).
- **T2.5 — Grievance pipeline has deadlines:** intake channels, processing rules, complainant updates, and appeal path exist; repeated failures trigger escalation (see `189-service-level-governance-and-redress-ops.md`).
- **T2.6 — Low-conflict resolution lane:** where appropriate, is there a restorative/mediation option with safe refusal, consent receipt, safety & power plan, explicit confidentiality boundary, and a breach ladder that can escalate without bait‑and‑switch? (See `193-restorative-justice-and-conflict-resolution-rails.md`.)
- **T2.7 — No wrong door + transferable case file:** if a dispute crosses agencies/scopes, do routing receipts, non-reset evidence transfer, and enforced escalation clocks prevent ping‑pong—and can the case move between negotiation/mediation/ombuds/tribunal via a standard transfer bundle (ODR‑TX)? (See `195-dispute-resolution-escalation-and-odr-rails.md`.)

(Links: `08-remedy-and-grievance.md`, `105-institutional-circuit-breakers.md`.)

---



**T1.23 — Capital projects are gated and outcomes are checked (if applicable):** For any material capital project / major IT program, is there a versioned public `PC-*` project card, do spend increases require an `SGR-*` stage-gate receipt, are large deltas issued as `CCR-PI-*` change-control receipts, and are benefits checked via `BRR-*` receipts that gate future tranches? (Anchor: `138-public-investment-and-capital-projects-integrity.md`; joins: `110/118/130/133/134`.)

**T1.24 — Safety assurance is explicit and renewable (if risk is material):** For any high‑hazard system (infrastructure, transport, health, finance, automation), is there a public `SCC-*` safety case card, time‑bounded `SACR-*` assurance receipts at go‑live and material change, a live `RRE-*` risk register, and `IRR-*` incident receipts that feed follow‑through and evaluation loops? (Anchor: `139-risk-and-safety-assurance-governance.md`; joins: `104/105/115/118/130/133/134`.)

**T1.25 — Queues are legible, receipted, and seam-safe (if demand exceeds supply):** For any queued service (permits, housing, benefits, healthcare, utilities rationing, admissions), is there a public Queue Card (QC-*), a versioned Priority Criteria Registry (PCR-*), Queue Position Receipts (QPR-*) on entry and change, bounded Priority Decision Receipts (PDR-*) for overrides, non-reset Transfer Receipts (XFR-*), and a clocked remedy on deadline miss (auto-approve / interim protection / escalation)? (Anchor: `140-queues-and-prioritization-integrity.md`; joins: `108/109/114/118/130/134`.)

## T‑3: Anti‑capture & anti‑runaway

- **T3.1 — Capture sensors:** concentration of discretion, opaque contracting, revolving‑door risk, dominance of one funding stream.
- **T3.2 — Brakes exist:** automatic pause/review, audit escalation, conflict‑of‑interest firebreaks, and sunsetting for emergency powers (see `112-exception-control-and-emergency-powers.md`).
- **T3.3 — Adversarial testing:** red‑team the institution (not just the tech).
- **T3.4 — Lifecycle completeness:** charter includes renewal clock, exit/continuity plan, and an actual post‑charter review method (see `178-institutional-lifecycle-sunsets-and-scrutiny.md`).
- **T3.5 — Contracting legibility:** procurement publishes a stage-by-stage disclosure clock, change-order log, and competition exceptions (see `179-open-contracting-and-procurement-rails.md`).
- **T3.6 — DPI anti-capture:** DPI has separation of roles (steward/operator/auditor/redress), open standards + change control, and exclusion budgets (see `188-digital-public-infrastructure-governance.md`).
- **T3.6a — DPI Trust Framework exists:** a published rulebook defines connector eligibility, conformance tests, audit evidence, incident duties, and rights/redress hooks (see `212-dpi-trust-framework-and-interop-governance.md`).
- **T3.6b — DPG intake is procurement-real:** adopted components have decision records + renewal dates, reproducibility/assurance evidence for critical pieces, and a funded exit plan (see `213-digital-public-goods-intake-and-certification-rails.md`).

- **T3.7 — Budget openness & joinability:** can you trace budget lines to contracts/grants/outcomes/audits, and are cross-scope transfers/equalization rules receipted and appealable? (See `194-fiscal-federalism-open-budgets-and-participation-rails.md`.)

- **T3.7b — Public appointments integrity:** senior appointments publish criteria, panel charter, conflicts packet, and an Appointment Integrity Receipt; any override has reasons + challenge lane (see `228-public-appointments-and-board-governance-rails.md`).
- **T3.7c — Regulator independence is engineered:** independence surfaces are explicit (appointments/budget/case integrity), interference contacts are logged, and removals are bounded to enumerated grounds with public receipts (see `229-independent-regulators-and-agency-independence-rails.md`).
- **T3.7 — Legitimacy module completeness:** any added election/sortition/deliberation mechanism declares decision rights, interface, budget/staffing, and failure handling (see `180-legitimacy-engines-elections-sortition-deliberation-recall.md`).
- **T3.7a — Deliberation isn't theater:** any citizens' assembly/panel ships with a public Charter + draw receipt + balanced evidence plan + an auditable Response Duty, and has an evaluation receipt after completion (see `224-deliberative-processes-and-citizens-assemblies-rails.md` and `41-public-participation-and-deliberation-register.md`).
- **T3.8 — Polycentric compact completeness:** if multiple nodes share authority, there is a written compact with scope, interface obligations, shared registries, a dispute ladder, spillover rules, and exit terms (see `182-polycentric-governance-and-compacts.md`).
- **T3.8a — Shared services rails:** if a jurisdiction uses a shared operator/platform, there is a public Shared Service Card (`SSC-*`), a Shared Services Compact (`SSCMP-*`), and an Exit Artifact Package (`EXIT-*`)—and Decision Receipts join to the principal authority and rule version (see `219-shared-services-and-federated-administration-rails.md`).
- **T3.8b — Civic maintenance infrastructure exists:** the jurisdiction maintains a versioned Civic Interface Pack and participation→decision binding receipts, with pluralism safeguards and independent civic help lanes (see `220-civic-learning-and-democratic-maintenance-infrastructure.md`).
- **T3.9 — Externality pricing legitimacy:** any carbon/congestion/value‑capture charge publishes a Pricing Receipt (measurement method + error bounds, exemptions ledger, revenue disposition, equity lane, appeals + redress, sunset/review) (see `198-commons-externalities-and-value-capture-rails.md`).
- **T3.10 — Merit recruitment & contestability:** critical roles use published rubrics, structured scoring, and a process appeal lane; hiring exceptions are justified and audited (see `199-civil-service-merit-and-capacity-rails.md`).
- **T3.11 — Depoliticisation boundary & direction receipts:** political direction is logged and bounded; professional execution is protected from arbitrary purge; acting-appointment bypass is constrained (see `199-civil-service-merit-and-capacity-rails.md`).
- **T3.12 — Workforce capacity observability:** vacancy duration, time-to-hire, backlog age, attrition, and training coverage are measurable and published at safe granularity (see `199-civil-service-merit-and-capacity-rails.md`).
- **T3.15 — Asset legibility:** safety/continuity‑critical services declare their `AST-*` dependencies and the owner/operator responsibility line is public.
- **T3.16 — Maintenance funding honesty:** deferred maintenance is disclosed with method + trend (not hidden as “future capex”), and condition inspection cadences are defined.
- **T3.17 — Capital lifecycle discipline:** capital approvals include lifecycle cost (capex + opex + renewal) and publish the operating-cost commitments created by new assets (see `225-public-assets-maintenance-and-capital-planning-rails.md`).
- **T3.13 — Futures node joinability:** major decisions either reference an `FRR-*` foresight review (or a signed “not applicable”), and any material FRR warning is met with a `FAR-*` response or a time‑bounded deferment (see `201-futures-and-intergenerational-governance-institutions.md`).
- **T3.14 — Mutual recognition is compacted and contestable:** if a person presents a credential from another jurisdiction, there is a published Mutual Recognition Compact (`MRC-*`) and Equivalency Map (`EQM-*`), plus Recognition Decision Receipts (`RDR-*`) with clocked review and appeal lanes (see `203-mutual-recognition-of-credentials-licenses-and-status.md`).

(Links: `04-threat-models.md`, `105`.)

---

## T‑4: Proportionality & coercion safety

- **T4.1 — Least‑coercive effective means** is default.
- **T4.2 — Escalation ladder** is explicit and reviewable.
- **T4.3 — Abuse‑safe reporting** exists for people under the institution’s power.
- **T4.4 — Detention sites are inspectable:** an independent preventive inspection regime exists for *all* places of detention (no hidden sites), with published reports and follow‑through (see `232-corrections-and-incarceration-governance.md`, `130`, `226`, `227`).
- **T4.5 — Deaths/serious harm in custody trigger independent investigation:** deaths in custody and credible torture/sexual violence allegations are automatic oversight events with evidence preservation, family notification, publishable findings, and no “internal-only” closure (see `232`, `130`).
- **T4.6 — Segregation is bounded and reviewable:** solitary/segregation placements have reason codes, time limits, scheduled reviews, and published aggregate duration stats (see `232`, `116`).
- **T4.6a — Force policy is public and ranked (policing):** explicit bans/limits + duty-to-intervene + supervisor review requirements are published (see `233-policing-and-use-of-force-governance-rails.md`).
- **T4.6b — Independent serious-harm lane (policing):** death/serious injury during police contact triggers an independent investigation with evidence preservation and publishable findings (see `233`).
- **T4.6c — Force-event receipts (policing):** every force event generates a joinable record (type, duration, injury, medical response, supervisor signoff) and is statistically reported (see `233`).
- **T4.7 — Capture tripwires:** Are conflict‑of‑interest waivers and procurement exceptions visible, reviewable, and statistically monitored?
- **T4.8 — Influence ledger:** is lobbying/influence disclosure timely, searchable, and linked to major decisions with enforcement that actually runs? (see `181-influence-lobbying-transparency-and-integrity-rails.md`).
- **T4.9 — Anti-deadlock timers:** if a veto or inter-node dispute blocks action, escalation timers exist and are enforced; temporary authority migration is defined (see `182-polycentric-governance-and-compacts.md`).

(Links: `05-public-safety-and-coercion.md`, `116-coercion-use-of-force-and-detention-governance.md`.)

---

## T‑5: Performance under stress (latency, surge, and failure)

- **T5.1 — Time‑to‑answer** is bounded for critical pathways (appeals, shelter, child safety, medical eligibility).
- **T5.2 — Graceful degradation:** when overloaded, system prioritizes safety + rights and issues temporary decisions with later review.
- **T5.3 — Learning loop:** incidents become fixes (postmortems + policy patches) rather than blame theatre.
- **T5.4 — Change is reversible and evaluated:** material policy changes ship with an evidence charter, guardrails, and rollback triggers (and results are publishable). (Anchor: `190-policy-experimentation-and-evidence-rails.md`.)
- **T5.5 — Evidence commons exists:** material policies have a joinable evidence index (`EIR-*`) and evidence changes trigger `ECR-*` updates + review flags; where data can’t be open, there is a published safe access ladder (see `202-open-knowledge-evidence-commons-and-scientific-integrity-rails.md`).
- **T5.6 — Evidence system exists (learning agenda + evaluation plan + publishability):** the institution publishes a learning agenda (priority questions with owners + decision hooks) and an evaluation plan mapped to budget; negative findings are publishable without program veto (see `214-evaluation-learning-agendas-and-evidence-governance-rails.md`).

(Links: `09-public-service-and-state-capacity.md`, `104`.)


**T1.26 — Delegation is bounded, revocable, and auditable:** Whenever a proxy acts (representative, agent, guardian, administrator), can the affected person (or authorized advocate) retrieve: a delegation/mandate receipt (DLR/RMR), a verification receipt for the action (DVR), a revocation receipt path (DRR) with bounded clocks, and conflict joins (`120`)? (Anchor: `141-delegation-and-representation-integrity.md`; joins: `115/118/120/130/109/112/116`.)


**T1.27 — Metric power is receipted and purpose-bounded:** If a metric affects eligibility, funding, sanctions, or queue position, can you retrieve the metric definition (`MIC-*`), confirm its version, see any change receipt (`MCR-*`), and find a joinable metric‑use record (`MUR-*`) inside the Decision Receipt—plus a contest lane for measurement error or definition misfit? (Anchor: `142-metrics-and-indicators-integrity.md`; joins: `115/118/127/131/140/133/134`.)

**T1.28 — AI systems are registrable *and* operationally accountable (if AI mediates outcomes):** For any AI-mediated public service (including staff copilots that can influence outcomes), can you (a) point to an `AIS-*` service card and a corresponding `ADS/MOD-*` registry entry, (b) show a time‑bounded assurance receipt (AICC/SACR-style) at go‑live and after material change, (c) prove there are **no silent model swaps** via change receipts (`AICR-*`), (d) produce incident receipts (`AIIR-*`) and follow‑through when harms occur, and (e) demonstrate contestability and evidence export for appeals? (Anchor: `146-ai-assurance-and-public-sector-ai-ops.md`; joins: `42/31/118/130/133/139/127`.)


**T1.29 — Emergency powers are receipted, time-bounded, and reviewable:** If the institution can declare or operate under “emergency” mode, can an affected person retrieve an Emergency Declaration Receipt (EDR) that lists legal basis, measures, rights map (limitations vs derogations), end-date/sunset, renewal thresholds, and oversight/review paths—and do powers auto-expire unless renewed with a new receipt? (Anchor: `186-emergency-powers-derogations-and-sunset-discipline.md`; joins: `31/39/51/85/33/146`.)

**T1.30 — Integrity system exists as infrastructure (not vibes):** Can a member of the public trace a high-stakes decision to (a) interests/influence disclosures, (b) procurement artifacts and change orders, and (c) oversight findings + responses—and is there a credible enforcement path with deadlines and consequence receipts? (Anchor: `226-public-integrity-system-architecture.md`; joins: `187/181/179/130/227`.)

**T1.31 — Equal protection is operational (accessibility + language):** For any person-facing service, can a person request accommodations/language support and receive a bounded `AAR-*`/`LAR-*` receipt with interim support, a denial-with-reasons path, and an escalation lane—and are privacy-safe disparity indicators published so patterned harms can be contested and remediated? (Anchor: `209-equal-protection-accessibility-and-language-access-rails.md`; joins: `98/134/127/130/187`.)

**T1.32 — Transfers are legible, rule-based, and appealable (if money moves across jurisdictions):** Can the public retrieve (a) the current transfer formula and parameter values, (b) the indicators used for capacity/needs, (c) a per-jurisdiction allocation table (gross + net) with revision history, and (d) an appeal path with bounded clocks—and is there an independent body responsible for maintaining the system? (Anchor: `217-intergovernmental-fiscal-transfers-and-equalization-rails.md`.)

**T1.33 — Global commitments are measurable and escalation-ready (if governance scope is cross-border/global):** For each commitment, is there a registry entry with versioned targets, agreed accounting, uncertainty bounds, reporting cadence, independent review, and a published escalation ladder from disclosure to conditionality? (Anchor: `218-global-commons-governance-clubs-treaties-and-mrv-rails.md`.)


---

## Minimal scorecard (optional)

Track a few numbers that surface harm early:

- contest initiation rate + success rate by group
- median time to first meaningful response (not first auto‑reply)
- reversal rate and why (fact error vs rule error vs discretion abuse)
- “unknown / unexplainable decision” rate (should trend to zero)

(Links: `03-metrics-and-evidence.md`.)


## Child–family separation & alternative care (high-harm administrative action)
- **SDR required:** Any child–family separation must produce a Separation Decision Receipt (SDR) with authority, evidence ladder, alternatives considered, and remedy lanes. (See `158-child-family-separation-and-alternative-care-governance.md`.)
- **Clocked independent review:** emergency lanes must auto-schedule independent review; no open-ended emergency status.
- **Alternatives + resource constraints visible:** support/kinship alternatives attempted (or explicitly unavailable) must be logged and auditable.
- **Institution-last:** residential/institutional placements require higher scrutiny and are time-boxed.
