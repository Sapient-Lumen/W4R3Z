# rev0097 learned response oracle

rev0097 is the first deliberately trained response-policy probe after the frozen rev0023 MLP negative control. It does not train a large neural policy. It creates a small registry-backed linear action scorer over public action, context, and durable information-state features, then learns score vectors by direct rollout search against the current effective PSRO support.

## Why this revision exists

rev0096 showed that the old imitation MLP is intact but weak as a current response oracle. That result did not answer whether a policy trained for the current opponent mixture can find a useful deviation. rev0097 answers the smaller, safer question first: can a compact information-state-aware scorer learn a response by gameplay search without adding a black-box RL stack?

## Method

The target is still the effective sole support isolated in rev0094:

```text
oracle_map_08_60_mixed_threats_counter_wall
```

The learner uses 47 features. These include ordinary action features, a readable public-profile baseline score, interaction terms for Force pitch and counter targets, closure/pressure terms, and explicit information-state terms for known top cards and public Force-pitch history.

The training path is:

1. sample six generation-0 score-vector agents around threat-pressure and threat-surge templates;
2. evaluate twelve generation-0 strategy candidates on the best gameplay-derived deck source;
3. recenter eight generation-1 children around the highest-scoring parent vectors;
4. evaluate forty-four final candidates across two deck sources and two mulligan policies;
5. hold out the top five candidates on seed-disjoint games;
6. require a lower confidence bound above the response threshold before confirmation.

All agents are stored in `data/rev0097_learned_response_agent_registry.json` and loaded through the ordinary `make_public_agent()` path. This ensures the learned wrappers use the same episode reset, information-state, and seat-isolation contracts as other public agents.

## Result

The learner produced a classic screen-versus-holdout failure:

```text
best generation-0 training mean: 0.875
best generation-0 training CI low: 0.630
best final selection mean: 0.750
best final selection CI low: 0.429
best holdout mean: 0.4375
best holdout CI: [0.2629, 0.6121]
```

The generation-0 and final-selection point estimates show the learner can overfit a small rollout screen. The seed-disjoint holdout retracts the response. No candidate triggers confirmation and no strategy is promoted.

## Interpretation

This is still forward progress. The cube now has a live learned-response oracle path rather than only a frozen historical imitation model. The negative holdout result is useful because it proves the admission gate can reject a learned policy that looked promising during training.

The immediate next risk is not another larger learned search. It is rollout overfitting. The next improvement should add a common oracle gate that automatically reports selection-to-holdout optimism and either increases holdout budget or uses a familywise correction when many candidates are screened.

## Files

- `src/muc5/learned_response_oracle.py`
- `data/rev0097_learned_response_agent_registry.json`
- `scripts/run_rev0097_learned_response_oracle.py`
- `tests/test_rev0097_learned_response_oracle.py`
- `data/rev0097_learned_response_oracle_summary.json`
- `data/rev0097_learned_response_oracle_audit.json`
- `data/rev0097_learned_response_oracle_games.csv`
- `data/rev0097_learned_response_oracle_scores.csv`
- `data/rev0097_learned_response_oracle_catalog.csv`
- `data/rev0097_learned_response_agent_registry.csv`
- `data/rev0097_learned_response_deck_sources.csv`

This is not a promotion gate. It is a method-branch probe and a guard against mistaking learned-policy training wins for solved-game evidence.
