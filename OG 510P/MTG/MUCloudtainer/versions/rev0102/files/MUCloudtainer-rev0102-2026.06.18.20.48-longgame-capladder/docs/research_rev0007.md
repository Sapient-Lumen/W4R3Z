# rev0007 research notes

The gametable direction is reinforced by current game/RL tooling and by new work on programmatic policies.

## Action masks / state-dependent legal actions

PettingZoo's AEC API is meant for sequential turn-based multi-agent environments and PettingZoo's action-masking tutorial frames masking as the natural way to prevent invalid actions in games with state-dependent action sets. MUC-5 is exactly such a game: the legal menu changes by phase, stack state, mana, cards in hand, and pending choices.

Sources:

- https://pettingzoo.farama.org/api/aec/
- https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
- https://arxiv.org/abs/2006.14171

## Imperfect information methods remain roadmap, not rev0007 implementation

MUC-5 has hidden hands/libraries and visible public state. OpenSpiel remains a useful north-star because it supports search/planning/RL in games, including imperfect-information games and algorithms such as CFR, Deep CFR, NFSP, PSRO, AlphaZero, and Alpha-Rank-style analysis.

Sources:

- https://openspiel.readthedocs.io/en/latest/intro.html
- https://openspiel.readthedocs.io/en/latest/algorithms.html
- https://arxiv.org/abs/1603.01121
- https://arxiv.org/abs/1811.00164
- https://arxiv.org/abs/2007.13544

## Why the external gametable is more than convenience

Recent Code-Space Response Oracles work reframes best-response generation as LLM-produced, human-readable policy code instead of black-box neural policies. That points to a possible MUC-5 branch:

```text
use table snapshots + tournament feedback
  -> ask an LLM/human to write a small Python policy
  -> run the policy against the current population
  -> keep it if it adds strength/diversity
```

The external gametable is a small first step toward that: it gives an outside reasoner a clean legal-action menu and hidden-information observation. We can later turn repeated table decisions into executable policy code or tests.

Sources:

- https://arxiv.org/abs/2603.10098
- https://www.ijcai.org/proceedings/2025/1249.pdf
- https://arxiv.org/html/2403.02227v1

## Pushback / caution

Do not over-invest in the table UI before strategy measurement exists. The table is valuable because it helps inspect agents and lets an outside chooser produce moves. It should remain thin. The next strategic layer should be payoff tables and logged trajectories, not terminal polish.

