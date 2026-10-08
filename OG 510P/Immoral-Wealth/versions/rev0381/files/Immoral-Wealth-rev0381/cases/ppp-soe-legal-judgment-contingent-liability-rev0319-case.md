---
status: active_case
claim_kind: case_memo
route_role: public_balance_sheet_core
canonical_anchor: false
route_refs:
- public_balance_sheet_core
- case_calibration_core
supersedes: null
depends_on:
- ../docs/20-program/gate-20-public-balance-sheet-register-and-subgates.md
- ../docs/20-program/public-balance-sheet-seniority-waterfall.md
source_refresh_due: 2027-03-31
case_pressure: rev0319_gate_20_operationalization
---

# PPP, SOE, and legal-judgment contingent-liability case — rev0355

## Verdict

**provisional.** This is a Gate 20 stress case, not a full country certification. The unit of analysis is the public/private balance-sheet surface that can turn a nominal private market, tax preference, credit program, or public promise into a public-risk allocation.

## Dominant breach

PPPs, SOEs, guarantees, disaster obligations, and legal judgments can create public liabilities outside ordinary budget visibility.

## Fastest washout

public downside appears after private financing, construction, or service contracts have already captured upside.

## Gate 20 subgate findings

- **20C_contingent_liabilities_guarantees — blocked:** Contingent liabilities cannot be treated as invisible until called.
- **20D_crisis_backstop_governance — watch:** Renegotiation and guarantee calls need public crisis governance.
- **20E_public_upside_recovery — missing:** Public upside recovery is often absent from guarantee designs.

## Seniority waterfall under stress

1. **Contract creditors/concessionaires** — Often contractually protected. Availability payments and guarantees can seniorize private investors.
2. **Service users** — Need continuity but can pay via tariffs. User fees may become regressive repair channel.
3. **Taxpayers/local governments** — Residual guarantors. Called guarantees and judgments can crowd out services.
4. **Future budgets** — Deferred liability holders. Opaque contracts turn into later appropriations.

## Main scoreboard fields

- `public_balance_sheet_gate`: warning — Fiscal-risk toolkits treat contingent liabilities as a core public-balance-sheet management surface.
- `ppp_soe_contingent_liability_exposure`: warning — Government support and guarantees can create contingent liabilities that require explicit controls.
- `fiscal_risk_register_quality`: missing — A case cannot pass unless the jurisdiction publishes a comprehensive fiscal-risk register.
- `contingent_liability_disclosure`: warning — Disclosure and stress-testing are central; absence is an opacity penalty.
- `legal_judgment_and_disaster_claim_visibility`: missing — Judgments and disaster claims need register treatment alongside PPP/SOE guarantees.

## Opening package

The case should not receive a comfort verdict until it has a public balance-sheet register, a claimant seniority waterfall, stress assumptions, ordinary-claimant protection, and public-upside recovery where public downside is used.

## Evidence debt

- comprehensive register covering PPPs, SOEs, guarantees, disasters, litigation, and arrears
- maximum and expected exposure by contract/program
- risk-transfer versus disguised borrowing analysis
- termination/renegotiation and legal-judgment waterfall
- public-upside or value-for-money recapture provisions

## Research and speculation

The speculative risk is that this surface will look private or technocratic until a shock arrives. At that point, public authorities may protect market functioning, creditors, property values, or payment continuity first, while ordinary households absorb price increases, service cuts, claim delays, debt collection, or intergenerational repair. The cube should therefore score rescue priority before the rescue occurs, not only after an obvious bailout.

## Source anchors

[S350] [S381] [S382]

## rev0329 substantive hardening addendum

rev0329 promotes the paired scoreboard from `seed` to `active` because the evidence now supports operational public-balance-sheet scoring rather than placeholder stress doctrine.

### Active finding

PPP/SOE/legal-judgment risk is now an active contingent-liability case. Guarantees, availability payments, SOE support, termination payments, disasters, judgments, and arrears must be registered before they are called, with public-upside recovery and service-user protection.

### Current source anchors

[S350] [S381] [S382] [S457]

### Operator instruction

Do not certify this case with aggregate fiscal-capacity, public-asset, solvency, or guarantee language. The operator must show claimant seniority, ordinary-claimant protection, distributional incidence, loss sharing, currentness, and public-upside/recovery rules where public downside is present.
