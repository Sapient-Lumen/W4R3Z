# Experiment matrix — rev0026 additions

| Axis | Current status | Next test |
|---|---|---|
| C++ transition parity | Shadow rollout checks 42,458 transitions with 0 mismatches | Attach to every new payoff/evolution script |
| RNG fairness | Public games now split transition RNG from agent RNG | Keep `transition_seed`/`agent_seed` in all payoff rows |
| Learned gameplay | Outcome-weighted ranker exists | Try search/rollout/improvement targets |
| Learned mulligans | Pseudo-oracle ranker exists | Train from terminal outcomes by shell/deck context |
| Population analysis | Statistical gate and meta-rank exist | Larger nontruncated tables before claims |
| Deck exploration | MAP-Elites archive exists | Sequential race archive cells through shadow rollout gate |

The rev0026 shadow table is not a strategic claim.  It is a measurement of the evaluation pathway.
