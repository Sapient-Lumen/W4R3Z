---
status: active_doctrine
claim_kind: measurement_doctrine
route_role: measurement_uncertainty_core
canonical_anchor: true
route_refs:
- measurement_uncertainty_core
- certification_core
supersedes: null
depends_on:
- ../20-program/top-tail-audit-and-uncertainty-bounds.md
- ../20-program/wealth-data-reconciliation-workflow.md
source_refresh_due: 2026-12-31
---

# Measurement uncertainty and false precision

rev0308 adds a measurement doctrine because the archive had become good at saying what a decent wealth order requires, but too willing to let a single point estimate carry moral weight. Wealth shares are not like thermometer readings. They are assembled from surveys, tax records, national accounts, capitalization assumptions, pension valuation, private-business valuation, owner tracing, imputation, nonresponse adjustment, and sometimes rich-list supplementation.

The new rule is:

> **A case cannot pass by false precision. When data uncertainty is asymmetric around the top tail, opacity hardens the verdict rather than softening it.**

This does not mean every uncertain case fails. It means uncertainty must be routed. If uncertainty is ordinary sampling error around a broad middle-class measure, it may remain proof debt. If uncertainty concerns offshore wealth, trusts, private companies, top-tail nonresponse, hidden property ownership, or survey accreditation, it becomes a certification problem.[S141][S146][S147][S148][S149][S150][S151]

## What counts as false precision

A wealth claim is false precision when it:

1. gives a top 1% or top 0.1% share without stating whether the source captures the very rich;
2. compares countries while mixing survey-only, tax-capitalized, rich-list-adjusted, and national-accounts-consistent series;
3. treats private pensions, public pension promises, home equity, business equity, and liquid deposits as equally available claimant wealth;
4. ignores offshore, trust, entity, and nominee structures;
5. uses household-level wealth to certify person-level control;
6. reports a national average while suppressing group, citizenship, region, or owner-type uncertainty;
7. counts private-company and private-market values without a liquidity/control haircut.

## Directional uncertainty

Some uncertainty is morally symmetric: the true figure might be better or worse. Top-tail wealth uncertainty is often asymmetric. Surveys tend to miss or understate the very rich; hidden offshore wealth and ownership via legal arrangements usually move concentration upward, not downward; private-market access is often concentrated among high-net-worth households; and unobserved debts, liens, or claimant frictions often move lower-half usable wealth downward.[S141][S146][S152][S431][S155][S157][S160][S161]

So the archive uses a **conservative moral bound**:

- when the upper bound still passes, the case may certify on the share surface;
- when the lower and upper bounds straddle a gate, the case is `proof_debt` or `watch`, not pass;
- when hidden ownership or weak survey quality probably worsens top-tail concentration, the case receives an opacity penalty;
- when lower-half usable wealth is uncertain because of liquidity, lockup, debt, or title problems, the case cannot count face-value wealth at full weight.

## Case implications

Measurement uncertainty now produces four case-level outputs:

| Output | Meaning | Consequence |
|---|---|---|
| `survey_quality_warning` | response, coverage, or accreditation problem | no soft pass from survey-only estimate |
| `top_tail_audit_required` | rich-list/tax/administrative adjustment materially changes top share | gate 1 cannot pass until bounded |
| `ownership_visibility_blocked` | entity/trust/offshore ownership prevents tracing control | gate 10 blocked |
| `valuation_haircut_required` | nontraded or locked assets counted at face value | asset-composition and floor gates re-read |

This doctrine is deliberately stricter than ordinary social-science caution. The archive is not trying to publish a neutral descriptive table; it is deciding whether a wealth order deserves moral certification. A morally relevant estimate must be good enough for action, not merely good enough for a chart.
