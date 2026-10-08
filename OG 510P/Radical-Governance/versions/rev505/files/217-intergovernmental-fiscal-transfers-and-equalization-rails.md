# Intergovernmental Fiscal Transfers and Equalization Rails

**Stack relation:** use `302-fiscal-state-budget-revenue-and-transfers-routing-guide.md` for the canonical route across the fiscal-state / budget / revenue / transfers family. This memo is the formula-transfer / equalization / Transfer Commission specialization; `18` is the broad intergovernmental-finance front door; `194` is the open-budgets / participation / fiscal-scrutiny specialization; `07` is the broad fiscal-governance front door; `110` / `135` remain the budget-allocation and revenue-integrity neighbors.

## Purpose
Design transfer systems that:
- equalize **fiscal capacity** and **expenditure needs** (so basic services don’t depend on postcode)
- preserve **local autonomy** (subsidiarity) without tolerating capability collapse
- reduce capture, bargaining chaos, and perverse incentives

**Definition (working):** fiscal equalization transfers are transfers across or down levels of government intended to offset differences in revenue-raising capacity and/or expenditure needs. See OECD’s framing and evaluations for the standard concept.

## Core rails

### R1. Separate the three transfer jobs
1. **Vertical gap**: align responsibilities with resources (general revenue sharing).
2. **Horizontal equalization**: mitigate regional disparities in capacity/needs.
3. **Externalities & national priorities**: conditional/earmarked grants for spillovers (e.g., climate, public health).

Keeping these distinct improves legibility and prevents “everything grants” that no one can audit.

### R2. Formula-first; politics-last
- Default to **rule-based formulas** with public parameters.
- Allow negotiated supplements only via:
 - time-bounded exceptional instruments
 - published rationale + counterfactual + sunset
 - independent review

OECD and World Bank guidance repeatedly emphasize predictable, rules-based systems to improve efficiency, equity, and accountability.

### R3. Make equalization target *capability*, not just spend
Equalization should ensure jurisdictions can meet **minimum service standards** (see service SLO/SLAs elsewhere in archive). That implies a **needs index**, not only revenue capacity.

A common approach is to equalize to a benchmark (e.g., national-average tax effort), using a capacity index and an expenditure-needs index. The World Bank practitioner guidance summarizes this design space and tradeoffs.

### R4. Don’t punish growth or reward stagnation
Introduce incentive-compatible design:
- avoid cliff effects by smoothing formulas
- avoid “revenue effort penalties” where raising local revenue reduces transfers one-for-one
- include lagged measures to reduce manipulation

OECD work discusses trade-offs and side effects in grant design (including incentive distortions).

### R5. Use negative equalization sparingly (but admit it exists)
In principle, very high-capacity jurisdictions can face **negative equalization** (net contributions), but the legitimacy requirements are higher:
- explicit legal basis
- maximum burden caps
- transparency on net positions

IMF work on designing sound fiscal relations discusses the “horizontal gap” logic and the possibility of negative equalization in principle.

### R6. Publish the transfer system like a public API
Minimum publish set, machine-readable:
- formula and parameter values
- underlying indicators and provenance
- per-jurisdiction allocations (gross and net)
- revisions (why did a number change?)
- appeals channel + adjudication timeline

## Governance of the transfer system

### G1. Independent Transfer Commission
Mandate:
- maintain indicators (capacity, needs, costs)
- run the formula
- publish allocations
- conduct periodic model review

Safeguards:
- public methods
- open hearings
- conflict-of-interest rules
- auditability

### G2. Review cycle
- annual parameter refresh
- 3–5 year structural review
- emergency adjustment mechanism (time-bounded)

## Minimal formula sketch (conceptual)
For jurisdiction *i*:
- **Capacity**: estimated revenue at benchmark rates
- **Needs**: standardized cost to meet minimum service bundle

Equalization transfer:
- base = max(0, needs_i − capacity_i)
- plus: spillover grants (separate)
- minus: contribution rule if capacity_i exceeds benchmark by threshold

(Exact implementation should be jurisdiction-specific; the rail is *separation + auditability + incentive checks*.)

## Failure migration tie-in
If a jurisdiction cannot meet minimum service bundle even after equalization and support:
- trigger capability failure protocol
- migrate delivery authority temporarily upward (with local representation)
- remediate capacity; restore

## References (external)
- OECD: evaluating equalization and design trade-offs.
- OECD (2025): intergovernmental fiscal transfers & equalization under consolidation pressures.
- World Bank: practitioner guidance on intergovernmental fiscal transfers and equalization design.
- IMF: fiscal relations design principles (horizontal/vertical gaps).
