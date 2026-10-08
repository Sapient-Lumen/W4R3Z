# Fiscal & Budgetary Governance (Money as Legitimacy Infrastructure)

Budgets are where “values” become **resource commitments**. A government that cannot produce *credible accounts* or *credible commitments* loses legitimacy, even if its laws look ideal.

**Anchor set (start here):** see [BIB-IMF-FTC-2019] (code) and [BIB-IMF-FTH-2018] (handbook).
**Implementation measurement anchor:** see [BIB-PEFA-2016].

**Multi-level add-on:** for transfers/equalisation and the money-map interface across scopes, see `18-intergovernmental-finance.md`.

---

## A. Minimum viable fiscal constitution (MVF)
These are the smallest fiscal guarantees that make democratic control possible.

1) **One consolidated picture**
- MUST: consolidated budget + in-year execution + annual financial statements covering the general government (and state-owned entities where material).
- MUST: “no off-book government” rule (any extra-budgetary vehicle requires explicit authorization + reporting).

2) **Readable public budget**
- MUST: budget documents that a non-specialist can understand (programs, objectives, baseline vs new spending, distributional notes where feasible).
- SHOULD: publish a “citizen budget” summary.
- SHOULD: tag major spending and mandates using a shared functional taxonomy (baseline: **COFOG**) to make cross-scope comparisons and scope transfers auditable (see [BIB-UNSD-COFOG], [BIB-IMF-GFSM-2014]).

3) **Execution transparency**
- MUST: quarterly (or better) execution reports; deviations explained.
- SHOULD: where spending is via procurement, execution reports reference the relevant contract/process ID (`CON`, prefer OCID where using OCDS) so budget lines, payments, and deliverables can be audited end-to-end. See `38-contracting-and-procurement-register.md` and [BIB-OCDS].
- SHOULD: publish budget + execution as **joinable releases** (e.g., a budget ledger + an execution/payment ledger) using stable row keys and a revision log (`REL-*`). Where feasible, include `CON-*` (procurement), `TRF-*` (transfers/grants), and `PROG-*` (program) references on execution lines so money can be followed end-to-end (budget → award → payment → delivery). Anchors: Open Fiscal Data Package guidance [BIB-GIFT-OFDP] and the OCDS budget/spend linkage pattern [BIB-OCDS-BUDGETSPEND-EXT].
- MUST: publish major contract awards and beneficial ownership where feasible (pair with `OPEN-2`; see `22-public-integrity-and-procurement.md`).

4) **Independent audit and closure**
- MUST: a supreme audit institution with budget and mandate protection (`ACC-1`).
- MUST: publish audit findings and closure rates (time to implement recommendations).
- See: `32-oversight-institutions-and-follow-through.md` (follow-through protocol + OFRR pattern).

5) **Fiscal risk statement**
- MUST: disclose and manage major fiscal risks (debt, guarantees, pensions, SOEs, PPPs, disasters) + tax expenditures (SPE/SPV treatment: [BIB-IMF-SPEPS-2005]; PPP structuring risks: [BIB-WB-PPP-RG3]; off-book authorities as risk vectors: [BIB-ACIR-A22-1964]).
- MUST: treat **tax expenditures and subsidies** as a spending surface: publish an inventory with costing method + revisions, and join it to `TEX-*`/`GRT-*` records (`49-...`). Practical guidance: see [BIB-IMF-TE-2019] and evaluation guidance in [BIB-IMF-TE-EVAL-2022].
- SHOULD: publish a simple “risk register” and update at least annually.

6) **Public investment + asset lifecycle discipline**
- MUST: treat infrastructure as a lifecycle commitment (capex + maintenance + replacement), not a one-off project.
- MUST: publish an Asset & Infrastructure Register keyed by `AST-*` for material assets, and require capital approvals/awards and major maintenance deferrals to cite affected `AST-*` (see `48-asset-and-infrastructure-register.md`).
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
- **Procurement capture:** open contracting (`OPEN-2`) + rotation and conflict-of-interest rules (`ACC-2/5`).
- **Politicized forecasting:** IFI or equivalent independent costing office (`CAP-4`).

---

## E. Minimal metrics (portable)
Use a *small* subset and tie each to a decision loop. Prefer metric IDs from `03-metrics-and-evidence.md` packs.
- **Budget credibility:** variance between approved budget and execution [IPM-6].
- **Consolidation coverage + timeliness:** % spend/liabilities in published audited statements [IPM-7].
- **Audit closure:** % recommendations closed within 12/24 months [IPM-5].
- **Fiscal risk statement completeness:** guarantees/PPPs/SOEs/disasters/tax expenditures [IPM-8].
- **Transfer predictability (multi-level):** formula transparency + variance + timeliness [IPM-10].

