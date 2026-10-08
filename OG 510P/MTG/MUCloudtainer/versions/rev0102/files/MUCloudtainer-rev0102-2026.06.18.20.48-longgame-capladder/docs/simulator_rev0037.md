# rev0037 simulator status

The simulator is still Python-authoritative and C++-shadowed.

## Working surfaces

```text
public DecisionFrame gameplay
London mulligan agents
hidden-information observations
public payoff tables
replay/promotion/statistical gates
C++ transition shadow checks
C++ no-choice segment checks
counterfactual branch labels for unchosen legal actions
```

## New rev0037 confidence layer

Matched label comparison now checks whether two offline label allocators agree when they consume the same branch-outcome matrix.  This is a simulator-adjacent trust layer: if labels change because the allocator changes, future policy results are suspect.

## Current caution

The simulator is usable for automated experiments, but strategic claims should still require:

```text
promotion gate
statistical gate
replay samples
C++ shadow/parity checks
truncation labels
label-allocation audit for counterfactual datasets
```
