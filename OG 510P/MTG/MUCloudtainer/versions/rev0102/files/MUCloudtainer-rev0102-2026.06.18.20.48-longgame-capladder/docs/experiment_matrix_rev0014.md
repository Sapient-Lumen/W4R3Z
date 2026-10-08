# rev0014 experiment matrix

| Experiment | Status | Output | Purpose |
|---|---:|---|---|
| Public/code-policy payoff with 3 reps | Built | `rev0014_statgate_payoff_games.csv` | Higher-rep smoke table after public-agent parameter fixes |
| Statistical standings | Built | `rev0014_statgate_standings.csv` | Rank by lower confidence bound rather than raw mean |
| Pairwise uncertainty table | Built | `rev0014_statgate_pairwise.csv` | Label matchup/life cells as favored/uncertain |
| Replay samples | Built | `rev0014_statgate_replay_traces.jsonl` | Keep promotion/replay discipline attached to statgate rows |
| Static MAP-Elites archive | Built | `rev0014_map_elites_archive.csv` | Preserve diverse deck niches for future simulation |
| Public-agent parameter-name audit | Built | tests + cube audit | Prevent distorted baseline scoring |
| Alpha-Rank adapter | Not yet | none | Population analysis after payoff rows have enough reps |
| Sequential racing / SPRT | Not yet | none | Future candidate-pruning acceleration |
| Gameplay-evaluated MAP-Elites cells | Not yet | none | Turn static archive into real matchup candidates |
| Neural/action-feature encoder | Not yet | none | Still waiting for comparison gates and more stable targets |
