# rev0022 experiment matrix additions

| Experiment | Question | Data | Gate |
|---|---|---|---|
| Ranker sequential race | Can ranker/code/public bundles survive staged racing? | `rev0022_ranker_race_*` | promotion + stat + replay + C++ trace |
| MAP-Elites ranker variants | Which pilot uses the same archived deck shell best? | `rev0022_mapelite_ranker_variants_*` | promotion + stat + replay + C++ trace |
| Blended ranker agents | Does a tiny readable style prior help the linear imitation policy? | race + variant tables | public DecisionFrame only |
| Public payoff agent cache | Can bulk payoff loops avoid reloading ranker models? | source/audit | no hidden-state change |

## Do not overclaim

Both rev0022 game tables are smoke-scale. They are infrastructure tests and early hints, not strategic conclusions about MUC-5.
