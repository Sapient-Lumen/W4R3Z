# rev0042 — hard-frame racing label-density audit

rev0042 attaches adaptive/racing label allocation to the public-only hard-frame queue introduced in rev0041.

The goal is not to promote a new policy.  The goal is to measure whether adaptive branch allocation can preserve useful labels while spending fewer branch rollouts.

Pipeline:

```text
public behavior games
  -> public DecisionFrames
  -> public-only hard-frame queue
  -> selected high-action/high-disagreement frames
  -> Python semantic referee branches legal actions
  -> C++ shadows every transition
  -> fixed-equal and adaptive-prefix labelers consume the same branch matrix
```

The adaptive labeler is intentionally conservative.  It consumes prefix rollout samples only:

```text
one base rollout for every candidate action
extra rollouts go to current best / runner-up actions
stop early if margin clears the configured threshold
```

This means it can be compared to a future online branch racer without cheating by looking at later rollout samples first.

## Smoke results

```text
selected hard situations:       12
high-action selected:           12
branch games:                  240
branch truncations:              0
C++ checked transitions:    42,567
C++ skipped transitions:         0
C++ mismatches:                  0

fixed rollouts spent:          240
adaptive rollouts spent:       140
adaptive rollout savings:      100
fixed decisive situations:       2
adaptive decisive situations:    2
best-set agreement rate:       0.8333
adaptive changed labels:         2
```

## Interpretation

This is a useful infrastructure result.  The adaptive audit spent fewer rollouts while preserving the same number of decisive labels in this sample, but it changed two best-action sets.  That is not automatically bad: the fixed labeler used later rollout samples that the adaptive prefix labeler intentionally skipped.

The next target is an online adaptive collector that uses this prefix discipline directly rather than generating a full branch matrix first.
