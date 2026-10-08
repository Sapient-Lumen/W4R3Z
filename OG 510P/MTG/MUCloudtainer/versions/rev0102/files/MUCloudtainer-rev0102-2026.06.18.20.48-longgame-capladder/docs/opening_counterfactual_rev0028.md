# rev0028 opening-hand counterfactual probes

rev0028 builds the next mulligan-learning target: paired keep-vs-mulligan branches from the same first seven-card look.

The previous outcome mulligan ranker learned from behavior-policy choices that happened to occur in terminal-winning games.  That is useful, but it still cannot answer the smaller question:

```text
Given this exact opening hand, was KEEP better than TAKE MULLIGAN?
```

The new probe makes that question explicit.

## Branch design

For each sampled opening situation:

```text
same deck0 library order
same first seven-card look for player 0
same opponent pregame state
same starting life
same starting player
same transition seed
same agent seed
```

Then two branches are played:

```text
branch A: force player 0 to keep the first seven
branch B: force player 0 to take the first mulligan, then delegate later mulligan/bottom decisions to the fallback mulligan agent
```

This isolates the first decision.  Later gameplay is still stochastic and path-dependent, so one paired branch is not a proof.  It is a better training target than plain outcome-weighted behavior cloning because both legal alternatives are actually sampled.

## Generated files

```text
data/rev0028_opening_counterfactual_branch_games.csv
  one row per played branch game

data/rev0028_opening_counterfactual_pairs.csv
  one row per opening situation, comparing keep score to mulligan score

data/rev0028_opening_counterfactual_context_summary.csv
  small aggregation by deck/life/start/hand-quality bin

data/rev0028_opening_counterfactual_cpp_transitions.csv
  C++ shadow transition rows for the branch games

data/rev0028_opening_counterfactual_summary.json
  run summary and gate counts
```

## Smoke result

```text
paired opening situations:   72
branch games:                144
C++ transition events:       36,342
C++ skipped events:          0
C++ mismatches:              0
truncations:                 0
mulligan-better pairs:       18
keep-better pairs:           15
tie pairs:                   39
mean mulligan-minus-keep:    +0.0417
```

These numbers are diagnostic, not MUC theory.  The sample is deliberately small and uses current public/code/ranker baselines.

## Why this matters

A learned mulligan policy should eventually learn from counterfactuals, not merely from what a behavior policy did.  The natural next dataset is:

```text
MulliganObservation + legal action
  -> estimated branch value
```

That can train a policy to prefer keep or take mulligan from paired alternatives, while preserving the same agent-facing legal-action surface.
