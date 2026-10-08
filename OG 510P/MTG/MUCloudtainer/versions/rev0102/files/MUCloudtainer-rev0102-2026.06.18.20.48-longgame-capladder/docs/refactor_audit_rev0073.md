# rev0073 refactor audit

## Refactor target

The riskiest implementation detail was not another missing registry entry.  It was that a promotion gate used approximate fictitious play for the current 2x3 population matrix even though the exact row maximin can be solved directly.  A second smaller process risk was that the new cold-evidence workflow from rev0072 hardcoded `rev0072_evidence_tiering_catalog.json`, which would make every later lean revision depend on stale literal paths.

## Changes made

1. `src/muc5/population_frontier.py` now exposes `exact_two_row_maximin()` and `zero_sum_maximin()`.
   - One- and two-row games use exact line-intersection / dual-support enumeration.
   - Larger games continue to use `zero_sum_fictitious_play()` as the fallback.
   - Security and precision-gate rows report `mixed_solution_method`.

2. `scripts/run_rev0073_pool_robustness.py` evaluates fifteen source/size/life pooling cuts and writes gate, security, pooled-arm, and summary artifacts.

3. `src/muc5/evidence_tiering.py` now discovers the newest `data/rev*_evidence_tiering_catalog.json` rather than hardcoding rev0072.
   - `catalog_row_count()` uses the newest catalog by default.
   - `materialize_evidence_bundle()` accepts an optional catalog override and otherwise discovers the newest catalog.
   - `finalize_package.py` uses discovery before pruning verified cold materializations.

4. rev0073 carries forward the verified rev0072 sidecar as `data/rev0073_evidence_tiering_catalog.json`, with the current cube name recorded as `source_cube`.  No cold evidence was re-expanded into the core.

## Audit findings

The pooling audit produced fifteen gate rows.  All fifteen use `exact_two_row`; none promote; none are underpowered; none fail on CI width.  This rules out a narrow version of the pooling concern: the quarantine conclusion does not depend on one source revision, one size axis, or one life total carrying the aggregate.

The evidence-tiering refactor keeps the lean package process intact.  Catalog discovery prefers `rev0073_evidence_tiering_catalog.json`, core validation still finds six hot records present and seventy-two cold records absent, and the cold sidecar remains byte-addressed by the rev0072 bundle hash.

## Remaining risks

This does not certify a size-specific strategy.  The result still says that `public_counter_guard` should remain quarantined.  The next useful strategic work is either new policy generation against the worst cuts, especially `counter60_vs_threat60`, or adding a third row policy so the fallback solver path is exercised by a real larger empirical game.
