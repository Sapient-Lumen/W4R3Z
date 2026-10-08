# rev0032 experiment matrix additions

| Experiment | Status | Output | Why it matters |
|---|---:|---|---|
| Batched C++ no-choice segment finalization | Built | `rev0032_segment_shadow_summary.json` | Moves from per-game segment checking toward batch-oriented C++ acceleration. |
| MAP-Elites construction shell × pilot/mulligan variants | Built | `rev0032_segment_shadow_same_deck.csv` | Separates construction quality from pilot and pregame policy quality. |
| Promotion-gated segment-shadow payoff | Built | `rev0032_segment_shadow_games.csv` | Ensures segment-shadow data has provenance/reward/interface columns. |
| C++ segment actor-refresh bug test | Built | `tests/test_rev0032_segment_shadow.py` | Guards against state-carry drift across multi-action forced runs. |
| No-choice segment execution benchmark | Next | TBD | Measures whether actual C++ segment execution is worth integrating into rollouts. |
| Larger MAP-Elites race | Next | TBD | Tests whether shell/pilot/mulligan differences persist with more games. |
