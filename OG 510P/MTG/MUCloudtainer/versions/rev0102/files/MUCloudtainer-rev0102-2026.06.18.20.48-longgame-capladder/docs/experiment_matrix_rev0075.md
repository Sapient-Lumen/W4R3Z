# rev0075 experiment matrix

| Surface | Status | Evidence |
| --- | --- | --- |
| Underpowered high-mean stratum selection | complete | `data/rev0075_stratum_challenge_selected_cells.json` |
| Seed-disjoint targeted games | complete | 288 games in `data/rev0075_stratum_challenge_games.csv` |
| C++ parity sample | complete | 30,000 checked transitions, zero mismatches |
| Pooled pre/post gate comparison | complete | `data/rev0075_stratum_challenge_comparison.csv` |
| Boolean gate accounting | fixed/tested | `population_gate_bool`, `tests/test_rev0075_stratum_challenge.py` |
| Context-axis type fragmentation | fixed/tested | `_normalized_context_value`, rerun post gate has 3 rows |
| Promotion result | quarantined | 0/3 targeted cells pass; all fail low conservative floor |

Interpretation: rev0075 changed the selected cells from `underpowered_min_games` to `quarantined_low_security_floor`.  That is a stronger negative result than rev0074 had.
