# rev0010 research notes

The research direction is still environment-first:

- PettingZoo's AEC/action-mask pattern is a useful reference because MUC-5 is turn-based and has state-dependent legal actions.
- OpenSpiel remains a roadmap source for imperfect-information algorithms and population/equilibrium tooling such as CFR, NFSP, PSRO, AlphaZero-style baselines, and Alpha-Rank.
- Hypothesis-style stateful testing is conceptually relevant because it lets a tester generate action sequences, not merely single inputs. Hypothesis is not currently part of the cube's dependency contract, so rev0010 uses a custom deterministic fuzzer.
- Official Magic rules remain the external reference, but MUC-5 should stay a narrow five-card referee, not become a general Magic engine.

## New research/build idea from this pass

Treat simulator readiness itself as an experiment axis. A future strategy evaluation should record the simulator/audit gate it passed under:

```text
strategy result = deck + mulligan + pilot + life context + simulator_revision + audit_gate
```

This prevents old heuristic payoff rows from being mistaken for results under a later, stricter referee.

## Next method-level targets

- Build a small best-response/evolutionary constructor against the payoff bundle population.
- Add a low-rep PSRO-shaped population loop: evaluate population, generate candidate response, add if it improves.
- Keep all learned/search agents on DecisionFrame or SlotEnv.
- Add a scenario ID to game logs so future transcript models can distinguish rules-regression games from organic self-play.
