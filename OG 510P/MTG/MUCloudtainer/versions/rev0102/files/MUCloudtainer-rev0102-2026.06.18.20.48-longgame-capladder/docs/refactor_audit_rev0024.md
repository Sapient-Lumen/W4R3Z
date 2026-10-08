# rev0024 refactor and audit notes

## Refactor

rev0024 adds:

```text
src/muc5/mulligan_ranker.py
```

and updates:

```text
src/muc5/mulligan.py
src/muc5/engine.py
src/muc5/public_payoff.py
src/muc5/payoff.py
src/muc5/replay.py
src/muc5/cpp_trace.py
src/muc5/strategy_sets.py
```

The biggest semantic change is that mulligan observations now include allowed pregame context:

```text
starting_life
deck_counts
```

The biggest fairness/audit change is that replay traces can now store:

```text
mulligan_agents
```

rather than only `mulligan_policies`.

## Audit checks added

`scripts/audit_cube.py` now checks:

```text
rev0024 model JSON exists
model feature count matches code feature names
loaded learned mulligan agent can choose a legal keep/take action
learned mulligan strategy panel has 12 bundles
learned mulligan payoff table has 576 games
promotion/statistical gates passed
C++ trace checker has 0 skipped events, 0 mismatches, 0 Python replay errors
keep model accuracy is above a sanity threshold
bottom model beats random candidate-card selection
required rev0024 files exist
```

## Caveat

The learned mulligan model is pseudo-oracle seeded. It is a pipeline and evaluation object, not proof of optimal London mulligan strategy.
