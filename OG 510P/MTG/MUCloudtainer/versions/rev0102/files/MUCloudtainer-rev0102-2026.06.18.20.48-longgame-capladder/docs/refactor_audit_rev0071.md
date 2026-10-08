# Refactor audit — rev0071

Substantive refactors in this revision:

1. `aggregate_population_summary_rows` pools seed-disjoint population summaries with weighted means and recomputed confidence intervals. This prevents duplicate population rows from being overwritten when context axes are intentionally coarsened.
2. `run_cpp_shadow_outcome_rows` separates fast outcome generation from per-transition C++ shadow construction. The heavy brute-force path still needs more engineering, but the core now has an explicit outcome-only runner that preserves game-row semantics.
3. `sample_prepared_cpp_shadow_rollout` centralizes the even transition-sampling helper that rev0070 had embedded in one script.
4. `evidence_derivatives` creates compact profiles for bulky raw evidence that had no derivative path.
5. `scripts/audit_cube.py` now checks rev0071's pooled power-floor quarantine and evidence-derivative unlock.

Known remaining risk: fine-grained size/life population cells still do not have enough games to pass precision individually. rev0071 addresses this with pooled negative evidence, not with size-specific certification.
