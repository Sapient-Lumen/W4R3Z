# rev0022 MAP-Elites ranker variants

rev0014 created a static MAP-Elites-style construction archive. rev0015 evaluated selected archive cells through gameplay. rev0022 adds a more surgical question:

> Holding a MAP-Elites deck shell fixed, which public pilot family uses it best?

For the top diverse cells, rev0022 creates same-deck variants:

```text
linear_ranker_rev0021
ranker_blend_threat_rev0022
code_overlord_clock_rev0013
counter_happy
```

The resulting panel is small: three deck shells times four pilots = twelve strategy bundles.

Generated artifacts:

```text
data/rev0022_mapelite_ranker_variants_games.csv
data/rev0022_mapelite_ranker_variants_aggregate.csv
data/rev0022_mapelite_ranker_variants_standings.csv
data/rev0022_mapelite_ranker_variants_same_deck_pilots.csv
data/rev0022_mapelite_ranker_variants_pairwise.csv
data/rev0022_mapelite_ranker_variants_stat_standings.csv
data/rev0022_mapelite_ranker_variants_replay_traces.jsonl
data/rev0022_mapelite_ranker_variants_replay_results.json
data/rev0022_mapelite_ranker_variants_cpp_trace_rows.csv
data/rev0022_mapelite_ranker_variants_cpp_trace_summary.json
data/rev0022_mapelite_ranker_variants_summary.json
```

`same_deck_pilots.csv` is the most important diagnostic. If a pilot looks strong only on one deck shell, it may be an interaction rather than a generally better controller.

## Caveat

This is still smoke-scale gameplay. The correct conclusion is not "pilot X is best." The correct conclusion is whether the archive/ranker/pilot comparison machinery is now clean enough to spend larger budgets.
