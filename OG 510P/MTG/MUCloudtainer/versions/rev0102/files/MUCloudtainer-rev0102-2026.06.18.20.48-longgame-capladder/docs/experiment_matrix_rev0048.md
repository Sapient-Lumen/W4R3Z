# rev0048 experiment matrix

| Experiment | Purpose | Status |
|---|---|---|
| rev0047 baseline yield-ranker panel | expose truncation-heavy policy comparison | inherited |
| rev0048 high-ceiling rerun | resolve truncations under same seeds/schedule | complete |
| rev0048 by-strategy truncation table | find truncation-prone policies/shells | complete |
| rev0048 by-pair truncation table | find specific stall-prone pairings | complete |
| C++ full-panel shadow | verify longer terminal-clean games stay in C++ parity | complete |
| Replay trace + C++ trace sample | deterministic replay/provenance check | complete |

Next experiments:

```text
terminal-clean larger yield-screen collection
matched label-yield audit with decisive-per-rollout target
MAP-Elites/meta-rank only on low-truncation promoted tables
```
