# rev0016 sequential racing scaffold

rev0016 adds a small sequential-racing scaffold:

```text
src/muc5/sequential_race.py
scripts/run_rev0016_sequential_race.py
```

The goal is to avoid wasting games on obviously weak candidates once payoff rows become expensive. It is not yet a formal best-response optimizer.

## Current race shape

Candidates come from selected MAP-Elites deck cells. Each candidate is converted into a strategy bundle:

```text
deck construction
+ mulligan policy
+ public/code-policy pilot
```

Candidates play against a small benchmark opponent set over:

```text
20 and 40 life
both starting-player seats
stage reps: 1, then 2
```

After each stage, the race computes bounded-score confidence intervals. A candidate can be eliminated if its upper confidence bound is below the best candidate's lower confidence bound.

## rev0016 smoke result

```text
candidate count: 6
opponent count: 4
games: 512
stages: 2
truncations: 0
statistical gate: passed
stage 1 eliminations: 1
stage 2 eliminations: 0
```

Data lives at:

```text
data/rev0016_sequential_race_games.csv
data/rev0016_sequential_race_standings.csv
data/rev0016_sequential_race_pairwise.csv
data/rev0016_sequential_race_stages.json
data/rev0016_sequential_race_summary.json
```

## Pushback

This is a pruning scaffold, not truth. Early elimination can create false negatives if the candidate/opponent panel is too narrow. For now it should be used to triage candidates, not to publish MUC-5 theory.
