# Fiscal & Budgetary Governance (Money as Legitimacy Infrastructure)

**Stack relation:** use `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md` for the canonical route across the fiscal-state / budget / revenue / transfers family. This memo is the broad fiscal-governance front door; `110` handles budget readability and procurement-capture mechanics; `135` handles revenue-rule integrity and replayable receipts; `93` is the operational revenue-administration / dispute / collection pipeline; `18` is the intergovernmental-finance seam; `194` / `217` are the open-budgets and equalization-transfer specializations; `97` / `138` remain the capital-allocation and major-project neighbors.

**Purpose:** make money decisions (budgets, spending, deficits) traceable and contestable so resource power can’t hide in spreadsheets.

See also: `157-monetary-and-financial-stability-governance.md` (monetary/financial stability + payments as legitimacy infrastructure); `110-budget-procurement-integrity.md` (open contracting baseline + procurement anti-capture mechanics); `162-procurement-as-governance-lever-and-guardrails.md` (procurement as market/rights/resilience lever with guardrails); `135-taxation-and-revenue-integrity.md` (revenue rules + replayable receipts + clocks).

**Person served:** the person who pays and depends—especially those for whom delays, fees, debt collection, or austerity become coercion—and who needs budgets that are legible, reviewable, and rights‑protecting.

**From-below:** So you can see where money went, contest unfair bills or collections, and stop budgets from quietly cutting the services you rely on.

**EXP pointer:** EXP-02 (Waiting), EXP-03 (Proof burden), EXP-07 (Indifference), EXP-08 (Invisibility) (see `98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** any identifiers/joins/releases introduced here MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers or safe aggregates). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**Material floor (one sentence):** assumes funded records/audit/publication/remedy capacity; in degraded mode preserve minimum budget+execution disclosure and person‑facing receipting for bills/fees/collections so fiscal constraint can’t become coercion‑by‑omission. (See `31`, `32`, `82`, `93`; `101-claude-rev142-normative-requirements.md` (NR-13, NR-02).)
**As-of & corrections:** any joinable artifacts introduced here MUST be versioned and “as‑of” answerable; corrections are append‑only and propagate across dependent systems via `31`/`53` and joins via `70` (no silent overwrites). (See `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)

Budgets are where “values” become **resource commitments**. A government that cannot produce *credible accounts* or *credible commitments* loses legitimacy, even if its laws look ideal.

**Anchor set (start here):** see [BIB-IMF-FTC-2019] (code) and [BIB-IMF-FTH-2018] (handbook).
**Implementation measurement anchor:** see [BIB-PEFA-2016].

**Multi-level add-on:** for transfers/equalisation and the money-map interface across scopes, see `18-intergovernmental-finance.md`.

**Revenue administration add-on:** for the coercive/service interface (assessment → dispute → collection) and joinable receipts (`DRR-*`), see `93-tax-and-revenue-administration.md`.

## Kernel anchors (do not repeat)
- Person-facing fiscal interfaces (receipts, deadlines, safe dispute): `98-persons-path-and-accessibility-invariants.md`, `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`.
- Decision receipts (person-facing) default to `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields).
- Protective legibility for budgets (publish usable facts without enabling retaliation): `99-protective-legibility-and-adoption-dynamics.md`.
- Service standards for payment plans / intake / navigation (no AI-only gates): `47-service-catalog-and-access-journeys-register.md`, `82-service-standards-and-minimum-service-guarantees.md`.
- Oversight with teeth (audit findings must bind or escalate): `32-oversight-institutions-and-follow-through.md`.

## Named tensions (design must surface these)
- **Transparency vs retaliation:** procurement/budget whistleblowing needs protected lanes (`83`).
- **Austerity vs rights floors:** fiscal constraint does not erase minimum service/relief obligations.
- **Progressivity vs mobility/capture:** tax fairness competes with capital flight and political sabotage.
- **Speed vs due process:** emergency spending and collections must still emit receipts and preserve contestation.
- **Adoption is part of the spec:** “rights floors” that depend on unfunded staff time, hidden discretion, or unreadable releases will not be adopted; publish uptake + backlog + failure signals and make underfunding contestable. (`99-protective-legibility-and-adoption-dynamics.md`; `101-claude-rev142-normative-requirements.md` (NR-03).)


---

## A. Minimum viable fiscal constitution (MVF)
These are the smallest fiscal guarantees that make democratic control possible.

0) **Fund governance infrastructure (legibility + remedy are not free)**
- MUST: budget explicit line items for records/registry operations, translation/accessibility, remedy intake/navigation, independent oversight (audit/ombuds/inspection), and publication integrity.
- SHOULD: treat these as **protected baselines** (do not fund them only from fines/fees that create perverse incentives or deter access).
1) **One consolidated picture**
- MUST: consolidated budget + in-year execution + annual financial statements covering the general government (and state-owned entities where material).
- MUST: “no off-book government” rule (any extra-budgetary vehicle requires explicit authorization + reporting).

2) **Readable public budget**
- MUST: budget documents that a non-specialist can understand (programs, objectives, baseline vs new spending, distributional notes where feasible).
- SHOULD: publish a “citizen budget” summary.
- SHOULD: tag major spending and mandates using a shared functional taxonomy (baseline: **COFOG**) to make cross-scope comparisons and scope transfers auditable (see [BIB-UNSD-COFOG], [BIB-IMF-GFSM-2014]).

3) **Execution transparency**
- MUST: quarterly (or better) execution reports; deviations explained.
- SHOULD: for material spend systems, publish internal **control map + testing** releases (prevent/detect/correct) so execution failures are auditable in near‑real time (see `84-internal-controls-and-continuous-assurance.md`).
- SHOULD: where spending is via procurement, execution reports reference the relevant contract/process ID (`CON`, prefer OCID where using OCDS) so budget lines, payments, and deliverables can be audited end-to-end. See `38-contracting-and-procurement-register.md` and [BIB-OCDS].
- SHOULD: publish budget + execution as **joinable releases** (e.g., a budget ledger + an execution/payment ledger) using stable row keys and a revision log (`REL-*`). Where feasible, include `CON-*` (procurement), `TRF-*` (transfers/grants), and `PROG-*` (program) references on execution lines so money can be followed end-to-end (budget → award → payment → delivery). Anchors: Open Fiscal Data Package guidance [BIB-GIFT-OFDP] and the OCDS budget/spend linkage pattern [BIB-OCDS-BUDGETSPEND-EXT].
- MUST: publish major contract awards and beneficial ownership where feasible (pair with `OPEN-2`; see `22-public-integrity-and-procurement.md`).

4) **Independent audit and closure**
- MUST: a supreme audit institution with budget and mandate protection (`ACC-1`).
- MUST: publish audit findings and closure rates (time to implement recommendations).
- See: `32-oversight-institutions-and-follow-through.md` (follow-through protocol + OFRR pattern).

5) **Fiscal risk statement**
- MUST: disclose and manage major fiscal risks (debt, guarantees, pensions, SOEs, PPPs, disasters) + **revenue risk** (concentration, volatility, collection collapse, enforcement failure) + tax expenditures (SPE/SPV treatment: [BIB-IMF-SPEPS-2005]; PPP structuring risks: [BIB-WB-PPP-RG3]; off-book authorities as risk vectors: [BIB-ACIR-A22-1964]).
- SHOULD: treat **ecological depletion and restoration liabilities** as fiscal risks (natural-capital loss, remediation obligations, transition costs) and publish joinable methods/assumptions where feasible (`11-commons-and-ecological-governance.md`, `65-energy-and-decarbonization-governance.md`).
- MUST: treat **tax expenditures and subsidies** as a spending surface: publish an inventory with costing method + revisions, and join it to `TEX-*`/`GRT-*` records (`49-...`). Practical guidance: see [BIB-IMF-TE-2019] and evaluation guidance in [BIB-IMF-TE-EVAL-2022].
- SHOULD: publish a simple “risk register” and update at least annually.

6) **Public investment + asset lifecycle discipline**
- MUST: treat infrastructure as a lifecycle commitment (capex + maintenance + replacement), not a one-off project.
- MUST: publish an Asset & Infrastructure Register keyed by `AST-*` for material assets, and require capital approvals/awards and major maintenance deferrals to cite affected `AST-*` (see `48-asset-and-infrastructure-register.md`).
- SHOULD: for major projects, require stage-gated approvals that emit `DRR-*` receipts (baseline + change control + post-implementation review). See `97-public-investment-and-capital-project-governance.md`.
- SHOULD: use PIMA-style checks across planning/allocation/implementation and OECD life-cycle governance principles to reduce “capex theatre,” deferred maintenance, and off-book liabilities. Anchors: [BIB-IMF-PIMA-2022]; [BIB-OECD-INFRA-2020]; asset-management baseline: [BIB-ISO-55000].

---

## B. Rules that help (and when they backfire)
### 1) Fiscal rules (debt/deficit/expenditure)
- SHOULD: a small ruleset with an explicit **escape clause** for shocks (war, disaster, severe recession) and a return path (align with `23-emergency-governance-and-exceptions.md`).
- Fails via: creative accounting, shifting liabilities off-budget, pro-cyclical austerity.

### 2) Independent fiscal institution (IFI) pattern (`CAP-4`)
- SHOULD: independent analysis of forecasts, costings, and compliance with rules.
- Anchor: see [BIB-OECD-IFI].

### 3) Medium-term frameworks
- SHOULD: 3–5 year expenditure and revenue baselines to reduce “annual surprise politics.”
- MUST: show future-year implications of today’s commitments.

---

## C. Intergovernmental money (if multiple scopes exist)
- MUST: avoid unfunded mandates.
- SHOULD: formula-based transfers and equalisation with transparent objectives and published calculations (`CAP-5`).
- Anchor: see [BIB-WB-IGFT-2007].

---

## D. Top failure modes (and the minimal countermeasure)
- **Off-budget state:** consolidated accounts + audit + disclosure of SOEs/PPPs/guarantees.
- **Fiscal illusion (hidden future costs):** publish tax expenditures + long-run commitments + sensitivity analysis.
- **Revenue risk (collapse / shortfall / enforcement failure):** treat revenue as part of fiscal risk—publish revenue-source concentration + shock scenarios, tax-expenditure growth, and collection performance (join to `93-...` releases/metrics). (See `101-claude-rev142-normative-requirements.md` (NR-13).)
- **Coercive collection disguised as “administration”:** coercive revenue enforcement is coercion; it MUST emit `DRR-*` receipts and be logged as `ENF-*` events with a contest lane (`93-...`, `43-...`). (See `101-claude-rev142-normative-requirements.md` (NR-13).)
- **Procurement capture:** open contracting (`OPEN-2`) + rotation and conflict-of-interest rules (`ACC-2/5`).
- **Politicized forecasting:** IFI or equivalent independent costing office (`CAP-4`).

---

## E. Minimal metrics (portable)
Use a *small* subset and tie each to a decision loop. Prefer metric IDs from `03-metrics-and-evidence.md` packs.
- **Budget credibility:** variance between approved budget and execution [IPM-6].
- **Consolidation coverage + timeliness:** % spend/liabilities in published audited statements [IPM-7].
- **Audit closure:** % recommendations closed within 12/24 months [IPM-5].
- **Fiscal risk statement completeness:** guarantees/PPPs/SOEs/disasters/tax expenditures **and material revenue risks** (base volatility, collection failure) [IPM-8]. (See `101-claude-rev142-normative-requirements.md` (NR-13).)
- **Transfer predictability (multi-level):** formula transparency + variance + timeliness [IPM-10].

## C. Person-facing fiscal interfaces (burden, coercion, and the right to contest)
Fiscal systems govern people not only through “spending decisions” but through **burdens**: assessments, bills, fees, fines, audits, and collections. A fiscal constitution is incomplete if it treats these as back-office.

**Minimum (tie to `98` and revenue admin in `93`):**
- **Comprehension-tested bills/assessments:** any *rights/obligations* created by taxation, fees, penalties, or debt service MUST be accompanied by a portable receipt (`DRR-*`) that a person can understand, with cited rule basis (`RULE-*` as-of) and a discoverable remedy lane (`AL-*`). (See `31`, `93`, `98`.)
- **Delay is harm:** publish and enforce time promises for disputes (acknowledgement, first substantive contact, decision), including tail metrics (`82`, `03`). When the state’s delay imposes penalties/interest, interim protection SHOULD apply while a contest is pending.
- **Once-only proof + assisted retrieval:** when the state already holds relevant evidence (income, residency, identity), the default SHOULD be assisted retrieval rather than repeated proof demands; exceptions must be explicit.
- **Safe contestation:** fiscal disputes are coercive; remedy lanes MUST support confidential filing and safe representation/advocacy where retaliation or intimidation is plausible (`08`, `36`, `98`).
- **No perverse funding loops:** avoid funding core remedy/oversight via fines/fees tied to enforcement volume (incentive to deter access or over-collect).
