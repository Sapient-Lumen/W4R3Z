---
status: active_doctrine
claim_kind: scoreboard_protocol
route_role: certification_core
canonical_anchor: true
route_refs:
- certification_core
- policy_pathway_core
supersedes: null
depends_on:
- scoreboard-spec.md
- scoreboard-schema.json
- verdict-engine-and-certification-gates.md
source_refresh_due: 2026-12-31
case_pressure: rev0306_liability_stack
---

# Liability-stack scorecard and router

rev0306 adds a liability-stack module. The module exists because wealth-order failure often appears as **claims against the poor**, not only absence of assets.

## Scorecard fields

Add these fields to case scoreboards whenever the case has debt/floor pressure:

| Field | Pass | Watch | Fail / veto | Source order |
|---|---|---|---|---|
| `liability_stack_drag` | debts are serviceable and do not block threshold moments | debt stress exists but relief works | multiple debt types block housing, care, transport, credit, or safe exit | household finance + credit panel + subgroup data |
| `health_medical_debt_drag` | medical costs do not create credit/care loss | medical debt exists but shielded | medical debt/collections/skipped care blocks floor | health-cost surveys + credit records |
| `student_debt_drag` | debt has payoff and safe repayment | delayed entry or subgroup stress | default/delinquency blocks first footholds | official portfolio + credit panel + SCF |
| `criminal_legal_debt_drag` | ability-to-pay and decoupling rules hold | fees exist with partial relief | sanctions or revenue reliance extract from subordinated groups | court/state data + subgroup data |
| `disability_care_interruption` | income, care, housing, and assets survive interruption | protections exist but late/thin | onset/care forces spend-down, debt, or household dependence | disability + health + admin data |
| `collections_credit_drag` | collections do not block essentials | collections common but bounded | credit file blocks lease, utilities, car, work, or business | credit-panel data |

## Gate effects

- A `fail` on `liability_stack_drag` blocks Gate 2 unless the case proves that protected minima, bankruptcy/forgiveness, and claimability repair are already operating.
- A `fail` on `criminal_legal_debt_drag` also pressures Gate 4 because legal-system debt is usually a group/person veto surface.
- A `fail` on `health_medical_debt_drag` can move the verdict to `emergency_repair` when skipped care, collections, or credit damage is widespread.
- A `fail` on `student_debt_drag` usually routes to early-footholds rather than only education policy.

## Router

| Dominant liability | First lane | Second lane | Rail lane | Reopening trigger |
|---|---|---|---|---|
| medical debt | floor-first stabilization | claimability/health-cost shield | credit-report and collections rules | medical debt in collections or skipped-care rate rises |
| student debt | early-entry anti-family-gate | income-contingent/hardship relief | portfolio transparency by subgroup | serious delinquency/default rises or family-paid/debt-paid split widens |
| criminal-legal debt | group/person veto closure | floor-first stabilization | court/local revenue replacement | nonpayment sanctions or subgroup fee gap persists |
| disability/care | floor-first stabilization | person-level ownership/control | paid leave, care credits, accessible housing | disability onset still causes spend-down or housing loss |
| high-cost credit/collections | floor-first stabilization | anti-extraction enforcement | licensing and rate/fee controls | collections block lease, utilities, transport, or work |

## Evidence-debt rule

Do not infer a liability pass from aggregate household debt. Missing debt composition is at least medium evidence debt. Missing subgroup liability data is high evidence debt. State-created debt that is not measurable is an opacity penalty.[S104][S108][S110][S111]
