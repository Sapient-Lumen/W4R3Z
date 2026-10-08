# rev0009 Research Notes

This revision focused on API boundaries, action masking, reward hacking, and throughput.

## Action masking remains central

MUC-5 has state-dependent legal actions. The model should not learn by being punished for illegal Magic moves; the referee should mask them. This matches PettingZoo's action-mask framing for environments with valid/invalid actions, and the invalid-action-masking literature argues masking is especially important as invalid action space grows.

Relevant sources:

- PettingZoo AEC/action masking docs: https://pettingzoo.farama.org/api/aec/ and https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
- Huang and Ontañón, *A Closer Look at Invalid Action Masking in Policy Gradient Algorithms*: https://arxiv.org/abs/2006.14171
- Zabounidis et al., *Overcoming Valid Action Suppression in Unmasked Policy Gradient Algorithms*: https://arxiv.org/abs/2603.09090

## Population methods still fit the project

The strategy object is naturally a bundle:

```text
deck construction + mulligan policy + pilot/controller
```

That makes payoff tables and PSRO-like population growth more natural than a single champion. OpenSpiel includes algorithms such as CFR, NFSP, PSRO, AlphaZero, and Alpha-Rank-style evaluation; the PSRO survey is a useful guide for growing strategy populations in large games.

Relevant sources:

- OpenSpiel algorithms docs: https://openspiel.readthedocs.io/en/latest/algorithms.html
- OpenSpiel GitHub overview: https://github.com/google-deepmind/open_spiel
- PSRO survey: https://arxiv.org/abs/2403.02227

## Imperfect-information methods stay on the later branch

MUC-5 hides hands and libraries. AlphaZero-style self-play is useful inspiration, but pure perfect-information search is not the final form. ReBeL, Deep CFR, NFSP, and PSRO remain later candidates once the referee is stable.

Relevant source:

- ReBeL: https://arxiv.org/abs/2007.13544

## Reward hacking / specification gaming

Even in a tiny game, agents can exploit measurement choices. The immediate traps are:

- stalling to reach max decisions if truncation is scored favorably
- optimizing short games if speed is accidentally rewarded
- using state-object access to see hidden information
- using action masks for the wrong player
- training on open-decklist data and evaluating as if decklists were closed

Relevant source:

- Reward-hacking empirical study: https://arxiv.org/html/2507.05619v1

## Throughput

Environment execution can become the bottleneck in RL. EnvPool is a useful reference point for that issue, even though MUC-5 is not ready for compiled batched envs.

Relevant sources:

- EnvPool docs: https://envpool.readthedocs.io/
- EnvPool paper: https://arxiv.org/abs/2206.10558
