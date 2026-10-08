---
status: active_case
claim_kind: case_memo
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- ../docs/20-program/score-mediated-exclusion-gate-and-scorecard.md
source_refresh_due: 2026-09-30
case_pressure: rev0315_score_mediated_exclusion
---


# Data broker, fraud flag, and identity-lockout case — rev0355

## Verdict

**Correction required.** Identity verification, fraud controls, and specialty reporting can protect public and private systems, but they fail the wealth-order test when false positives, stale records, identity theft, or thin documentation block claims without quick human correction.[S283][S289][S298][S299][S300]

## Dominant breach

The breach is **claimant lockout by verification and fraud infrastructure**. A person can have a legal right to a benefit, account, refund, or payment and still fail to receive it because a vendor or data system treats them as unverifiable or risky.

## Core reading

CFPB's consumer-reporting company list shows specialized data systems beyond credit bureaus, including checking-account history, low-income/subprime reports, utilities, retail, and supplementary reports.[S283] FTC's Consumer Sentinel data anchors the scale of identity theft/fraud reporting pressure.[S289] GAO's Login.gov and IRS identity-proofing work supplies a government-delivery stress surface.[S298][S299]

## Gate 17 finding

Gate 17 is **blocked for comfort certification** unless identity proofing has multiple paths, specific error reasons, timely human review, vendor auditability, false-positive correction, data-retention limits, and a payment bridge for urgent claims.

## Opening package

Offline and assisted identity proofing; no sole reliance on credit-file knowledge; specific error notices; temporary payment bridges; vendor audit rights; identity-theft suppression; fraud-flag deletion after correction; and anti-churn reuse of successful proofing.

## Evidence debt

False-positive rate by subgroup, documentation failure reasons, time to manual review, benefit/payment loss during review, vendor data-retention policy, and correction success after identity theft.

## rev0330 activation note

The data-broker/fraud/identity case is now an active claim-conversion case. Fraud controls remain necessary, but the cube must score whether low-documentation, identity-theft, digitally excluded, or false-positive claimants can obtain fast human correction, temporary access, and vendor-wide deletion after relief.

Operational certification remains blocked unless the scoreboard can prove transaction-preserving correction: specific notice, report/model visibility, human review, dispute or appeal timing before the threshold moment is lost, deletion/suppression after relief, and subgroup outcome evidence. [S459] [S461]

## Source anchors

[S283][S289][S298][S299][S300][S459][S461]


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S288]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.

## Rev0346 source-fit note

Rev0346 marks the CFPB consumer-reporting-company list as coverage-caveated: it remains a useful map of report families and consumer access points, but it is not exhaustive and does not determine FCRA or supervisory status for each company. The identity-lockout verdict therefore still needs vendor-by-vendor proof, not just list membership.[S283]
