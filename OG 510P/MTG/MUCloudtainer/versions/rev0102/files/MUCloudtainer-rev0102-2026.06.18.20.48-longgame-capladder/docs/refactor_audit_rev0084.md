# rev0084 refactor audit

rev0084 adds a small reusable transfer-audit layer instead of another one-off script.

## Code changes

- `src/muc5/population_candidate_transfer.py`
  - Builds a guard-vs-stabilizer candidate transfer panel.
  - Generates seed-paired C++ specs by size, threat axis, life total, target seat, starting player, and rep.
  - Produces pairwise guard/candidate delta rows.
  - Summarizes transfer contexts into dominance, mixed, indistinguishable, and negative-transfer statuses.

- `scripts/run_rev0084_candidate_transfer_audit.py`
  - Runs the selected-cell holdout and broader transfer panel.
  - Marks all candidate rows as non-broad-pool and non-candidate-pool eligible.
  - Writes compact game, paired-delta, context-summary, axis-summary, mechanism, aggregate, and C++ sample artifacts.

- `tests/test_rev0084_candidate_transfer.py`
  - Tests seed pairing and actual artifact-level quarantine behavior.

## Risk removed

Before this revision, the rev0083 stabilizer existed as an adaptive candidate with only a selected-cell probe. That was enough for narrative drift: later work could accidentally treat it as a legitimate population row.

rev0084 centralizes candidate-transfer evidence and makes the quarantine machine-readable. The candidate now fails a seed-disjoint transfer audit and remains excluded from broad promotion pools.

## Remaining risk

This is still not automated counter-policy search. It only prevents one hand-written adaptive candidate from contaminating broad population conclusions. The next substantive improvement should be either a preregistered third-row population candidate from an external search procedure, or a deck/policy counterfactual generator with holdout gates from the beginning.
