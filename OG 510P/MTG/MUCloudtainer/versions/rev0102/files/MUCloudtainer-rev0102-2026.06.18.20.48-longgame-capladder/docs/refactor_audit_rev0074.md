# rev0074 refactor audit

## Refactor target

The riskiest implementation surface after rev0073 was lineage, not another registry.  The population conclusions were built from arm summaries that were small and easy to inspect, but the raw game rows were the real evidence.  If those summary rows became stale, edited, or key-collided, the exact maximin gate could be exact over the wrong numbers.

## Changes made

1. Added `src/muc5/population_lineage.py`.
   - Recomputes population arm summaries from raw game rows.
   - Compares recomputed rows against shipped source summaries.
   - Builds a compact lineage index.
   - Adds `source_qualified_game_id()` because local `cpp_shadow_game_id` values are not archive-global.

2. Added `scripts/run_rev0074_population_lineage_audit.py`.
   - Reads raw rev0069 and rev0070 population games.
   - Emits a 432-row lineage index.
   - Emits a 72-row recomputed raw arm summary.
   - Writes mismatch, fine-security, fine-gate, and summary artifacts.

3. Added tests for the lineage-key collision, summary recomputation, and raw-lineage balance checks.

4. Carried the lean evidence-tier catalog forward to rev0074 so finalization still discovers the newest catalog and does not re-expand cold evidence into the core.

## Audit findings

The raw recomputation exactly matches all 72 source summary rows.  There are no seed, transition-seed, or agent-seed duplicates; no truncations; no non-terminal clean rows; and no imbalanced source/arm/life seat-start-player groups.

One local C++ shadow id is duplicated across source revisions.  That is precisely why the source-qualified key now exists.  The duplicate does not imply duplicated evidence: the associated rev0069 and rev0070 seeds differ and the qualified ids are unique.

## Remaining risks

The fine raw strata are complete but underpowered.  Four fine point-estimate rows are at or above a 0.50 pure-security floor, including one at 0.75, but all have at most 8 games per observed cell and cannot support promotion.  The next high-value work is a targeted, seed-disjoint expansion of those fine strata or a new policy row designed against the weakest `counter60_vs_threat60` cuts.
