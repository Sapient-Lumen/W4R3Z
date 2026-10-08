---
status: active_doctrine
claim_kind: framework_note
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- ../20-program/score-mediated-exclusion-gate-and-scorecard.md
source_refresh_due: 2026-12-31
case_pressure: rev0315_score_mediated_exclusion
---


# Data brokers, fraud flags, and identity lockout

Fraud prevention is necessary, but fraud infrastructure can become a private or public gatekeeping system. Data brokers, identity-verification vendors, bank-account screens, retail-return monitors, utility/telecom reports, and government identity proofing can block people from accounts, benefits, refunds, work, housing, or transactions.[S283][S289][S298][S299]

The CFPB consumer-reporting company list is important because it shows how many markets use specialty reports, not just the three nationwide credit bureaus. These include checking-account history, tenant screening, employment screening, insurance, low-income/subprime reports, supplementary reports, utility/telecom reports, and retail-return systems.[S283]

## Lockout pattern

A lockout breach occurs when:

1. a consumer is flagged as risky, fraudulent, unverifiable, or duplicate;
2. the flag is shared or reused across systems;
3. the affected person cannot see the underlying source;
4. correction requires online access, documentation, time, language, stable address, or device capacity the person lacks;
5. the threshold moment expires before correction.

## Required rails

- offline and assisted identity proofing;
- reason codes specific enough to fix;
- human review before irreversible denial or account closure;
- data minimization, retention limits, and deletion after false positives;
- vendor accountability and audit access;
- freeze/suppression rights for identity-theft victims;
- emergency benefit/payment paths during review.

## Certification rule

A claim cannot count as converted if identity verification, fraud flagging, or data-broker screening can block the claimant without timely explanation, correction, alternate path, and preservation of the underlying right.
