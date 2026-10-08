# rev0058 — fused streaming schedule tax

rev0058 targets the next risky systems overclaim after rev0057: a sparse selector that stores all dense QK scores is not yet a fused-kernel result.

The new native CPU probe compares three schedules on deterministic Q/K/V regimes:

1. `dense_online_one_pass` — one streaming QK+V pass, no score materialization.
2. `materialized_score_histogram_mass_0p95` — one QK pass, global score writes, histogram mass selection, selected V reads.
3. `streaming_recompute_histogram_mass_0p95` — no global score storage, but multiple QK passes to recover a mass threshold and accumulate selected values.

The important result is the schedule tax:

- Materialized histogram looks faster than dense in these CPU rows, but it writes all `1024` scores per row.
- Streaming histogram writes zero scores, but pays roughly `3.03×–4.00×` dense QK dot work depending on selected width.
- The score-storage-free streaming path is slower than dense in every tested regime.
- The value-tail outlier still breaks mass-only selection, keeping the rev0046/rev0050 warning alive.

This does not prove that a GPU fused kernel cannot win. It blocks a narrower but dangerous claim: **do not promote materialized dense-score sparse results as fused attention speed evidence.**

Current checks:

```bash
python experiments/fused_streaming_schedule/run_fused_streaming_schedule.py
python tools/fused_streaming_schedule_audit.py
python tools/current_scientific_run_audit.py
python tools/evidence_integrity_audit.py
python tools/smoke_validate.py
```
