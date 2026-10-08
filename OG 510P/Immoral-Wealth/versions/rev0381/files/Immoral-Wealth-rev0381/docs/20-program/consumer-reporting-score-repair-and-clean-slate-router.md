---
status: active_bridge
claim_kind: program_protocol
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0315_score_mediated_exclusion
---


# Consumer reporting, score repair, and clean-slate router

Use this router when the blocked threshold moment depends on a credit report, specialty consumer report, medical debt, collection, identity-theft record, checking-account report, utility/telecom report, or subprime/rent-to-own report.[S281][S282][S283][S284][S285]

## Route steps

1. **Name the report family.** Nationwide credit bureau, tenant, employment, checking-account, insurance, medical/prescription, utility/telecom, low-income/subprime, retail, fraud/identity, or supplementary report.
2. **Name the decision.** Credit price, rental denial, deposit, account opening, utility connection, insurance premium, job decision, benefit payment, or fraud hold.
3. **Name the harmful datum.** Medical debt, collection, eviction filing, judgment, account closure, overdraft, thin file, unscored record, identity mismatch, fraud flag, stale public record, or proprietary score.
4. **Test predictiveness.** Does the datum predict the relevant risk or only encode previous hardship?
5. **Test correction time.** Can the person correct the datum before losing the apartment, account, job, benefit, loan, or insurance?
6. **Apply suppression/clean-slate.** Suppress paid/small/old/medical/disputed/irrelevant records where predictive value is weak or dignity/circulation cost is high.
7. **Preserve the transaction.** Require pauses, conditional approvals, escrow, or temporary continuation when a dispute is plausible.

## Minimum evidence

- number and type of reports used;
- adverse-action reason specificity;
- dispute volume and correction outcomes;
- median correction time;
- subgroup incidence;
- share of denials caused by records not relevant to the actual decision;
- vendor/furnisher audit history.

## Verdict consequence

If the file cannot identify the report family and correction rail, mark `proof_debt` at minimum. If the missing visibility is produced by vendor secrecy or fragmented reporting, apply an opacity penalty.
