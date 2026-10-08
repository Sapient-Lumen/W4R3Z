# rev0008 research notes

The research pass this turn focused on two questions:

1. How should MUC-5 expose dynamic legal actions to future learning methods?
2. How should we think about simulator throughput before it becomes the bottleneck?

## Action masks remain the right interface

PettingZoo's AEC API explicitly supports action masks for environments where only some actions are valid at a given turn. Its action-masking tutorial frames masks as the natural way to prevent invalid actions in state-dependent games.

Sources:

```text
https://pettingzoo.farama.org/api/aec/
https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
```

This supports the current MUC-5 design:

```text
referee emits exact legal macro-actions
agent ranks only those legal actions
```

## Invalid-action masking is not just convenience

Huang and Ontañón's invalid-action masking paper gives theoretical and empirical support for masking invalid actions in policy-gradient algorithms. A 2026 paper on valid-action suppression argues that unmasked policy-gradient training can suppress actions that are invalid in visited states but valid elsewhere, due to shared parameters.

Sources:

```text
https://arxiv.org/abs/2006.14171
https://arxiv.org/abs/2603.09090
```

This makes MUC-5's legal-action slot design more than a UI choice. If/when we train neural policies, masking should be in the model path from the start.

## Card-game RL references

RLCard remains a useful card-game benchmark reference because it targets reinforcement learning in card games and imperfect-information domains. OpenSpiel remains useful because it collects algorithms like CFR, Deep CFR, NFSP, PSRO, AlphaZero, and Alpha-Rank-style tools in a game-environment frame.

Sources:

```text
https://github.com/datamllab/rlcard
https://rlcard.org/
https://openspiel.readthedocs.io/en/latest/algorithms.html
```

## PSRO/population direction

The PSRO survey is relevant because MUC-5 should probably not search for one champion bot too early. The natural unit is a population strategy:

```text
deck + mulligan policy + pilot
```

A payoff table over those bundles is the first step toward best-response iterations.

Source:

```text
https://arxiv.org/html/2403.02227v1
```

## Throughput references

EnvPool is the large-scale RL example of treating environment execution as a first-class bottleneck. It uses a high-performance parallel environment pool with compatible APIs. That does not mean MUC-5 needs EnvPool now; it means we should keep simulator profiling artifacts and avoid designing learning loops that assume simulation is free.

Sources:

```text
https://proceedings.neurips.cc/paper_files/paper/2022/hash/8caaf08e49ddbad6694fae067442ee21-Abstract-Datasets_and_Benchmarks.html
https://github.com/sail-sg/envpool
```

Numba remains a possible later tool for tight numerical loops, but rev0008's profile says the current bottleneck is dynamic Python game-state/object work, not obvious numeric loops.

Source:

```text
https://numba.pydata.org/numba-doc/dev/user/5minguide.html
```

## rev0008 conclusion

The right immediate path is:

```text
legal-action masks stay
payoff tables become first-class
profile every simulator-relevant revision
optimize Python structure before compiled rewrites
```
