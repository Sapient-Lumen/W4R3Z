# rev0015 experiment matrix update

## Newly tested

| Axis | New rev0015 artifact | Purpose |
|---|---|---|
| C++ probe acceleration | `rev0015_cpp_probe_benchmark.json` | Measure whether C++ kernels are worth using for constructor loops |
| MAP-Elites gameplay truth | `rev0015_mapelite_eval_*` | Test selected static archive cells in real public games |
| Reward-hack resistance | `rev0015_stall_adversary_*` | Force truncation behavior to verify gates expose it |
| Neural prep | `src/muc5/action_features.py` | Stable action vectors for imitation/ranking/neural agents |

## Reprioritized near-term order

```text
1. Keep hardening simulator/replay/promotion gates.
2. Move stable hotspots into C++ only behind differential tests.
3. Build sequential racing / candidate pruning over MAP-Elites and oracle candidates.
4. Add Alpha-Rank/meta-rank over promoted payoff tables.
5. Add tiny action-ranker imitation model using public observations + action features.
6. Only then try heavier neural RL.
```

## Questions worth asking next

```text
Can C++ accelerate legal-action generation without changing DecisionFrame semantics?
How much of constructor search can be screened by C++ probes before expensive gameplay?
Which MAP-Elites cells remain good after public gameplay evaluation?
Can a stall adversary ever pass promotion under any reasonable truncation rule?
Do action-feature imitation models learn policy style or just copy obvious legal phases?
Should 40-vs-60 and 20-vs-40 be treated as domain-randomization axes or separate empirical games?
```
