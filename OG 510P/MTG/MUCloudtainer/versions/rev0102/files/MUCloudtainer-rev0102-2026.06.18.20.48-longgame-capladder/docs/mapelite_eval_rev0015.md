# rev0015 MAP-Elites gameplay evaluation

rev0014 created a static MAP-Elites-style deck archive. rev0015 takes the next step: selected archive cells are evaluated through actual public DecisionFrame games.

The script:

```bash
python scripts/run_rev0015_mapelite_eval.py
```

selects top archive cells from:

```text
data/rev0014_map_elites_archive.csv
```

then creates six strategy bundles by pairing selected decks with public heuristic/threat pilots. It runs a smoke public payoff table across:

```text
20 and 40 starting life
both starting-player settings
2 reps per cell
```

Generated artifacts:

```text
data/rev0015_mapelite_eval_games.csv
data/rev0015_mapelite_eval_aggregate.csv
data/rev0015_mapelite_eval_standings.csv
data/rev0015_mapelite_eval_pairwise.csv
data/rev0015_mapelite_eval_replay_traces.jsonl
data/rev0015_mapelite_eval_replay_results.json
data/rev0015_mapelite_eval_summary.json
```

The promotion gate and statistical gate pass for this smoke table, but the results remain early evidence only. Static MAP-Elites quality is a candidate generator; gameplay evaluation is the actual test.
