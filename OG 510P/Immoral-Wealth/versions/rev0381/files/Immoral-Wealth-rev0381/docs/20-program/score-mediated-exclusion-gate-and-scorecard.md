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


# Score-mediated exclusion gate and scorecard

## Gate 17 — score-mediated exclusion, risk pricing, and algorithmic denial

A case cannot pass when credit files, specialty reports, tenant screens, employment dossiers, insurance scores, fraud flags, identity-proofing tools, personalized prices, or public-benefit algorithms convert prior hardship into higher prices or blocked access.

Gate 17 asks: **Can the person cross the threshold moment without being silently scored out, risk-priced out, or trapped in an uncorrectable data shadow?**

## Scorecard fields

| Field | Pass | Warning | Fail |
|---|---|---|---|
| credit reporting accuracy and dispute access | correction is fast and preserves the transaction | rights exist but timing is weak | errors or stale hardship routinely block access |
| credit invisibility / unscored status | safe thin-file alternatives exist | alternatives are partial | no-file or unscored households face exclusion or high prices |
| medical-debt credit-file risk | medical debt is suppressed or non-dispositive | state/product variation | illness debt travels into credit/housing/insurance decisions |
| specialty consumer-report coverage | all relevant reports are auditable | only some reports visible | banking, tenant, employment, insurance, utility, or subprime reports are ignored |
| tenant screening accuracy | exact records and relevance can be contested before denial | dispute exists after loss | eviction/criminal/credit/risk-score screens block entry opaquely |
| employment background algorithmic score | FCRA notice, consent, reason, and dispute work | compliance uncertain | opaque scores affect hiring, retention, or pay without usable rights |
| insurance credit/external-data scoring | factors are lawful, tested, and explainable | state variation | credit/location/proxy data make necessary coverage unaffordable |
| surveillance pricing | no consequential individualized pricing without disclosure | study/audit pending | personal data sets different prices with no meaningful exit |
| identity / fraud flag lockout | alternate proof and fast human review | review slow | claimant loses account, benefit, refund, job, or payment path |
| public-benefit algorithmic eligibility | notice, explanation, human review, audit, and emergency continuation | partial safeguards | automated suspicion or eligibility scoring blocks subsistence claims |
| model audit and disparate-impact testing | regular public/agency audit | vendor-only audit | no testing for protected-class, disability, language, place, or income effects |
| score repair claimability | repair is simple, timely, and transaction-preserving | repair after loss | burden falls on claimant after irreversible denial |

## Certification effects

- Gate 17 can directly block `near_ideal` and `acceptable` verdicts.
- Gate 17 hardens Gate 2 when the floor depends on digital eligibility, payment rails, or fraud screening.
- Gate 17 hardens Gate 3 when deposit, rental, job, insurance, or account moments depend on clean reports.
- Gate 17 hardens Gate 5 when score errors raise prices or push households into higher-cost markets.
- Gate 17 hardens Gate 8 when medical debt, student debt, criminal-legal debt, or collections keep traveling through reports.
- Gate 17 hardens Gate 9 when claim conversion depends on identity proofing, data matching, or automated review.
- Gate 17 hardens Gate 11 when remedy access is too slow or vendor systems are not auditable.

## Opening package

Use the least romantic package: report access, pre-denial notice, adverse-action specificity, one-stop dispute routing, transaction-preserving correction, clean-slate suppression, specialty-report inventory, algorithmic audit, data-minimization, vendor accountability, human review, emergency continuation, and anti-retaliation.

Score-mediated exclusion should not be solved by making every poor person manage a larger data bureaucracy. The preferred rail is **less harmful data, fewer reusable shadows, faster correction, and stronger rights at the moment of decision**.
