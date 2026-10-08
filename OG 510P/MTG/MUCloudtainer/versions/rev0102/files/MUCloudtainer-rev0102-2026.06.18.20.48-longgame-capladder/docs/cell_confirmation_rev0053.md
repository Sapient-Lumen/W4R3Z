# rev0053 Cell Confirmation / Confluence Gate

rev0052 softened the large apparent life-total flips from rev0051.  rev0053 changes the agenda from "find more life flips" to "confirm concrete target/opponent cells that still look strategically actionable."

The selector consumes public audit artifacts only:

- `rev0052_life_flip_target_life_cells.csv`
- `rev0052_life_flip_retest.csv`
- `rev0050_terminal_meta_claim_ledger.csv`
- `rev0051_deep_claim_target_summary.csv`
- `rev0051_deep_claim_claim_ledger.csv`

It assigns a confluence score to target/opponent pairs using prior retest score, lower confidence bounds, whether either/both life totals were favored, whether the cell looked stable across 20/40 life, and whether the target had prior population/deep-claim support.

This is an agenda generator, not a theorem.  The chosen cells are then retested terminal-clean with both life totals, both target seats, both starting-player positions, replay samples, and C++ transition shadow checks.

## Selected agenda

The rev0053 selected cells were:

1. `cf34_counter_wall` vs `pub_threat_overlord` — both life totals favored in rev0052.
2. `cf34_counter_wall` vs `cf47_counter_wall` — high-average watch after life-split softening.
3. `code_jace60` vs `cf34_counter_wall` — control watch; included because the central pair remained strategically important even after the old life flip softened.

## Gate

The new `cell_confirmation_gate` requires:

- terminal-clean rows,
- C++ transition shadow parity,
- no skipped C++ events,
- sufficient games per target/life cell,
- replay samples that pass,
- at least clean artifact shape for the selected agenda.

The gate does not promote a gameplay policy.  It determines whether the concrete-cell retest is trustworthy enough to inform the next agenda.
