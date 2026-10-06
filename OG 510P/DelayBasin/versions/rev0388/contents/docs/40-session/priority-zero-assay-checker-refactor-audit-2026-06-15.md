# Priority-0 assay checker refactor audit — 2026-06-15

## Finding

The Priority-0 assay family had started to duplicate the same invariant checks in separate checker files: metric-id shape, variant score sums, scorecard totals, operator-cost positivity, negative canaries, and compact/full/no-archive/sham ordering. That duplication was small enough to ignore for one smoke slice, but by the rotated slice it had become a drift risk: one checker could allow a partial scorecard, another could require exact metric coverage, and future replay fixtures could fork the meaning of “passes the canary.”

## Refactor

`rev0364` adds `tools/priority_zero_assay_lib.py` and routes the smoke, rotated, and role-blind replay checkers through shared helpers for:

- metric contract shape;
- variant identity and score integrity;
- scorecard sum checks;
- operator-cost positivity;
- required negative-canary presence;
- surface-existence checks for the role-blind packet/key pair.

The individual checkers still keep their historical specificity. `tools/check_priority_zero_smoke_slice_contract.py` remains anchored to `rev0361`; `tools/check_priority_zero_rotated_smoke_slice_contract.py` remains anchored to the `rev0363` rotated fixture; `tools/check_priority_zero_role_blind_replay_contract.py` enforces the new `rev0364` responder/scorer separation.

## Why this is a burden cut

This is not a style cleanup. It prevents a wasteful failure mode where every new smoke-slice variant creates a fresh wall of near-identical scoring logic. Shared invariants now live once, while fixture-specific checks remain local and diagnostic.

## Guardrails

The refactor does not create a Priority-0 review court. The shared helper cannot declare an assay meaningful; it only checks internal arithmetic, required controls, and separation boundaries. The substantive interpretation remains in the fixture, session report, self-sufficiency ledger, and open-question routing.

## Reopen trigger

Reopen this audit if a future Priority-0 checker duplicates scorecard arithmetic instead of using the helper, if shared helpers hide which fixture failed, or if the helper is treated as semantic proof that the compact cue is sufficient.
