---
status: active_bridge
claim_kind: calibration_protocol
route_role: case_calibration_core
canonical_anchor: false
route_refs:
- case_calibration_core
- certification_core
supersedes: null
depends_on:
- threshold-moment-registry.md
- evidence-debt-register-and-data-plan.md
- scoreboard-calibration-matrix.md
source_refresh_due: 2026-12-31
case_pressure: rev0306_calibration
---

# Proxy-to-threshold calibration rules

## Why this exists

The case portfolio increasingly uses proxy evidence: rent burden instead of deposit rejection; medical debt instead of full health-cost exposure; student-loan delinquency instead of lifetime repayment drag; disability earnings penalty instead of person-level wealth loss. Proxies are useful, but they must not quietly become certified thresholds.

## Calibration ladder

| Reading | Proxy standard | Required language |
|---|---|---|
| `pass` | direct threshold evidence exists and no subgroup veto appears | “passes on direct evidence” |
| `watch` | proxy suggests pressure but a plausible protective rail exists | “watch; route depends on next evidence” |
| `warning` | proxy strongly suggests a threshold block | “warning; no soft certification” |
| `fail` | direct or convergent proxy evidence shows threshold block | “fails this gate” |
| `veto_pressure` | subgroup/person/status data show constitutional closure or missingness hides it | “veto pressure; national average cannot pass” |
| `missing` | evidence absent and not reasonably inferable | “missing; evidence debt applies” |

## Convergent proxy rule

Three independent proxies can produce a `fail` when they point to the same threshold block. Example: rising rents, high deposit/guarantor dependence, and falling young-adult homeownership can fail early housing entry even before a perfect parental-transfer dataset exists.

## Non-convergent proxy rule

One proxy cannot certify a pass. Example: high public health spending does not prove medical-debt security unless skipped care, out-of-pocket exposure, claimability, and debt/collections evidence also support the pass.

## Debt-specific rule

For liabilities, one direct debt measure is insufficient unless it identifies consequence. A debt becomes threshold-relevant when it affects at least one of:

- housing access;
- credit score or formal borrowing;
- transport/license;
- employment or credential;
- legal/civic status;
- medical access;
- safe household exit;
- first savings or business stake.

## Evidence-debt conversion

- Missing direct threshold data = medium debt.
- Missing subgroup threshold data = high debt.
- Missing data because of ownership secrecy, administrative non-collection, or state-created opacity = blocking or opacity penalty.

## Case memo instruction

Each case must now include a short “Proxy status” paragraph answering:

1. Which readings are direct?
2. Which readings are proxy?
3. Which proxy, if wrong, would most change the verdict?
4. What new evidence would promote or demote the case?
