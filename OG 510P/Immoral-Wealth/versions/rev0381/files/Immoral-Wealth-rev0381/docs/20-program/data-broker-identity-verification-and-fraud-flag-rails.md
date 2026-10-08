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


# Data-broker, identity-verification, and fraud-flag rails

Use this rail when the case depends on a claimant proving identity, avoiding a fraud flag, opening an account, receiving a benefit/payment, passing KYC-like checks, or correcting identity-theft records.[S283][S289][S298][S299][S300]

## Required design

- **Multiple proof paths:** online, in-person, phone-assisted, mailed, advocate-supported, language-accessible, and disability-accessible.
- **No credit-file monopoly:** identity proofing cannot depend solely on credit-bureau knowledge or records.
- **Specific error reason:** the claimant is told whether the block is document mismatch, address mismatch, duplicate account, fraud flag, device risk, data-broker record, or vendor confidence score.
- **Fast human review:** time limits match the underlying need.
- **Payment bridge:** benefits, refunds, wages, and emergency aid have temporary payment routes during review.
- **Data retention limits:** false fraud flags and identity artifacts are deleted or suppressed after resolution.
- **Vendor audit:** public authority can inspect vendor data quality, accuracy, appeals, and false positives by subgroup.
- **Anti-churn:** a successful identity proof in one program should reduce repeated proofing unless risk changes.

## Routing

If identity verification blocks a tax refund, unemployment benefit, public dividend, starter account, housing claim, bank account, or medical/social claim, route to Gate 9 and Gate 17 together. The claim has not converted until proofing and fraud review are navigable.
