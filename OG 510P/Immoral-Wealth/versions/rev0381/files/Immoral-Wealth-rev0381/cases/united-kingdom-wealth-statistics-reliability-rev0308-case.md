---
status: active_case
claim_kind: case_memo
route_role: case_calibration_core
canonical_anchor: false
route_refs:
- case_calibration_core
- measurement_uncertainty_core
- certification_core
supersedes: null
depends_on:
- ../docs/20-program/top-tail-audit-and-uncertainty-bounds.md
- ../docs/20-program/measurement-source-quality-ladder.md
source_refresh_due: 2026-09-30
case_pressure: rev0308_uk_survey_reliability_case
---

# United Kingdom wealth-statistics reliability case — rev0355

## Verdict

**Verdict:** `proof_debt` as a measurement subsystem case.  
**Mode:** source-quality demotion and recertification.  
**Dominant breach:** wealth-share evidence depends on a survey whose accredited status was suspended for quality concerns.  
**Fastest washout:** treating an official survey output as if its source-quality warning did not exist.

## Why this case was added

The United Kingdom already appears in the portfolio for housing, inheritance, and household wealth structure. rev0308 adds a measurement case because the Office for Statistics Regulation suspended the official statistics status of the Wealth and Assets Survey, and ONS requested suspension for core outputs from Round 8 onward.[S147][S148][S149]

This does not make the Wealth and Assets Survey useless. It changes its certification role. A demoted source can still inform a case, but it cannot alone carry a comfort verdict.

## Gate readings

| Gate | Reading | Reason |
|---|---|---|
| Source quality | warning | official status/accreditation concern must be surfaced |
| Share plausibility | proof debt | survey outputs need corroboration before certification |
| Top-tail audit | required | survey response and top-tail coverage need adjustment/cross-check |
| Case recertification | required | earlier UK case readings should be refreshed when improved evidence appears |

## Proof debt

- Confirm response-rate, mode, sample-composition, and imputation effects.
- Compare WAS outputs with tax, rich-list, land-registry, pension, and national-accounts evidence.
- Report uncertainty bands rather than a single wealth-share estimate.
- Reopen the UK country case when ONS/OSR status, method, or replacement data improves.

## Opening package

The archive should continue using UK wealth statistics, but mark them. Any operator-facing chart should label the source-quality warning directly. The UK case is now the model for the rule: **official does not mean certification-grade when the statistical authority itself signals uncertainty**.


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S159]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.
