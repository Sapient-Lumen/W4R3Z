# TimeSync rev0093 audit — temporal coherence reuse and validator refactor

## Read-deep finding

rev0092 closed the digest/canonicalization risk, but the next riskiest surface was temporal evidence reuse. Scope-composition guards had explicit evaluation windows and max-age checks. Other current-facing surfaces still repeated smaller timestamp checks locally, and several accepted observations that could be later than the evaluation or artifact creation event relying on them.

The risky pattern was not malformed timestamps. rev0091 already enabled JSON Schema `format` checking and strict date-time parsing. The risky pattern was coherent-looking evidence with valid timestamps in the wrong relation:

```text
checkpoint checked after anchor evaluation
witness observation after replay-visibility evaluation
policy revocation or drift check after policy lifecycle evaluation
aggregate lifecycle rollup window ending after the aggregate artifact was created
```

Each case can accidentally turn later knowledge into earlier current-use support.

## Corrective change

`tools/temporal_coherence.py` is no longer only a scope-composition helper. It now also contains reusable relation checks:

```text
check_time_not_after(...)
check_time_order(...)
check_freshness_age(...)
check_active_window_status(...)
```

`tools/validate_archive.py` now uses those helpers in replay transparency, witness/monitor evaluation, transparency trust-policy lifecycle status, aggregate correction-authority lifecycle/reference checks, and aggregate lifecycle rollups.

## New fail-closed vectors

rev0093 adds five semantic vectors that previously could pass as schema-valid or rely on local checks that did not cover the new relation:

```text
examples/negative/replay-transparency-checkpoint-after-evaluation-invalid.json
examples/negative/replay-transparency-witness-after-evaluation-invalid.json
examples/negative/transparency-policy-lifecycle-revocation-after-evaluation-invalid.json
examples/negative/transparency-policy-lifecycle-drift-after-evaluation-invalid.json
examples/negative/aggregate-lifecycle-rollup-window-after-artifact-invalid.json
```

## Refactor value

This is a small refactor with executable payoff. It does not create a new registry, a new spec family, or new vocabulary. It moves repeated timestamp relation logic out of the monolithic validator and gives the helper a self-test entry point. The monolithic validator is still large, but the most failure-prone time arithmetic is now more reusable and easier to extend.

## Remaining risk

FT-0090 should stay open. The archive still has other lifecycle and discovery surfaces with local timestamp semantics. The next highest-value continuation is to move discovery negotiation freshness and authorized-verifier portable-result window checks into the same helper style, then split the largest validator concern families only where the split reduces executable risk.
