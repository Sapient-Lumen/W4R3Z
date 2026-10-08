# rev0096 frozen-MLP neural response oracle

rev0096 reactivates the dormant neural branch in the smallest useful PSRO role: a bounded response oracle.

This is deliberately not a new RL project and not a promotion gate. The frozen rev0023 one-hidden-layer MLP action ranker is used as a pilot over the current public `DecisionFrame` interface. Candidate decks come from the current response population, the rev0092 admitted response, and top gameplay-MAP-Elites cells from rev0095. The experiment asks one narrow question:

> Can the old neural action-ranker family, without new training, find a profitable response to the current effective PSRO support?

## Target

The target is the nearly pure expanded-game support isolated in rev0094 and used again in rev0095:

```text
oracle_map_08_60_mixed_threats_counter_wall
included weight: 0.999920007199352
maximum pruning error bound: 0.00007999280064796555
challenge threshold: 0.520079992800648
```

## Candidate construction

`src/muc5/neural_oracle.py` builds candidates by combining:

- bounded deck sources from the current population, the admitted PSRO response, and rev0095 gameplay-MAP-Elites archive elites;
- the frozen rev0023 MLP action ranker;
- three frozen MLP/profile blends: threat, counter, and patient;
- at most two mulligan choices per deck source.

Duplicate signatures against the expanded population are rejected before evaluation.

The model audit records:

```text
model: rev0023_mlp_ranker_model.json
features: 81
hidden units: 32
activation: relu
held-out top-one imitation accuracy in original training summary: 0.9146
```

That imitation score is historical plumbing evidence, not response evidence.

## Result

The neural oracle evaluated 40 nonduplicate candidates. Selection used 320 balanced game rows. Holdout used 240 additional seed-disjoint rows. There were zero truncations and zero seed overlap across stages.

The best holdout candidate was:

```text
neural_01_counter_m2_60_mixed_threats_counter_wall
agent: mlp_ranker_blend_counter_rev0023
mulligan: land_band_business
mean vs admitted response: 0.14583333333333334
95% interval: [0.04492968866043645, 0.24673697800623023]
```

No neural candidate passed holdout. No confirmation stage was triggered. No strategy is promoted.

## Interpretation

This is a useful negative result. The old MLP branch is not merely underconfirmed; in this target setting it is directionally poor. The likely cause is not that neural methods are inherently bad. The rev0023 MLP was an imitation model trained before the information-state/lifecycle repairs and before the PSRO target ecology existed. It learned to copy earlier public policies, not to optimize response value against the current admitted response.

Therefore the next neural work should not be another passive evaluation of frozen historical rankers. A future neural branch should train directly against the solved opponent mixture, consume the rev0091 information state or an explicitly documented encoding, and pass through the same selection/holdout/confirmation gates as MAP-Elites and finite-catalog oracles.

## Refactor included

`src/muc5/oracle_reporting.py` factors repeated runner boilerplate into shared helpers for stable JSON output, rectangular CSV rows, flattened response-score rows, stage counts, and seed-overlap checks. `scripts/run_rev0095_gameplay_map_elites.py` now imports the shared reporting helpers instead of carrying local copies. This is a small but important refactor: method runners should share audit plumbing rather than copy it.

## Evidence

- `data/rev0096_neural_oracle_summary.json`
- `data/rev0096_neural_oracle_audit.json`
- `data/rev0096_neural_oracle_games.csv`
- `data/rev0096_neural_oracle_scores.csv`
- `data/rev0096_neural_oracle_catalog.csv`
- `data/rev0096_neural_oracle_deck_sources.csv`
