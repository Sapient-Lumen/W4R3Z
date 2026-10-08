# Evidentiary-route fields

Revision: `rev0004`

A missing-half record should not merely say “this failed.” It should preserve how a claim became plausible before the failure.

## Required field family for medical negative-result records

- `hypothesis_or_claim_tested`: the proposition under test.
- `prior_evidentiary_route`: the path by which the claim became plausible or accepted.
- `hard_endpoint_result`: what happened when the claim met patient-relevant, field-relevant, or direct replication evidence.
- `positive_findings_preserved`: benefits or partial positives that should not be erased.
- `harms_preserved`: harms or counter-effects that changed the risk-benefit profile.
- `scope_cautions`: population, dose, route, era, endpoint, and use-case boundaries.
- `practice_lag_seed`: where to look for persistence in practice after literature status changed.

## Why this matters

Without these fields the corpus degenerates into a list of “wrong things.” With them, it becomes a status-history machine: claims can be narrowed, revived, split, superseded, or redirected without erasing why they once seemed reasonable.
