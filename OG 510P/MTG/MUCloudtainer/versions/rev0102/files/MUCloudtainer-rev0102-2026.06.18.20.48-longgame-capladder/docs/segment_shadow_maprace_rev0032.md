# rev0032 — segment shadow MAP-Elites race

rev0032 turns the no-choice segment checker into an evaluation gate for a small MAP-Elites-derived population.

The panel uses MAP-Elites construction shells from `data/rev0014_map_elites_archive.csv`, then crosses each shell with four controller/pregame pairings:

- `code_overlord_clock_rev0013` + `land_band_business`
- `counter_happy` + `mulligan_outcome_ranker_rev0027`
- `outcome_ranker_blend_counter_rev0025` + `mulligan_repeated_counterfactual_ranker_rev0030`
- `mlp_ranker_blend_threat_rev0023` + `mulligan_repeated_counterfactual_ranker_rev0030`

This is deliberately a smoke-scale diagnostic, not a claim that any construction shell is best. The point is to keep construction, gameplay pilot, and mulligan policy visible as separate parts of the strategy bundle while also attaching the C++ segment checker to real payoff traffic.

Generated files:

```text
data/rev0032_segment_shadow_games.csv
data/rev0032_segment_shadow_aggregate.csv
data/rev0032_segment_shadow_standings.csv
data/rev0032_segment_shadow_stat_standings.csv
data/rev0032_segment_shadow_pairwise.csv
data/rev0032_segment_shadow_segments.csv
data/rev0032_segment_shadow_same_deck.csv
data/rev0032_segment_shadow_replay_traces.jsonl
data/rev0032_segment_shadow_replay_results.json
data/rev0032_segment_shadow_summary.json
```

Archived smoke result:

```text
strategies:                  8
games:                       96
segments:                    6,314
forced actions checked:      17,289
C++ segment mismatches:      0
C++ skipped events:          0
truncations:                 0
replay samples:              8 / 8 passed
promotion gate:              passed
statistical gate:            passed
estimated compression:       ~1.57x
```

The `same_deck` artifact is the most useful human-facing view. It groups strategy standings by the MAP-Elites construction shell so we can ask whether a deck was bad, or merely badly piloted/mulliganed.
