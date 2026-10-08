# rev0005 Research Notes

## Action masks remain the right interface

PettingZoo's action-masking tutorial frames invalid-action masks as the natural way to prevent invalid moves in environments like chess. MUC-5's legal macro-action list is exactly this: the referee emits the valid actions, and the learner ranks them.

References:

- https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
- https://pettingzoo.farama.org/api/aec/

## Imperfect-information methods still belong later

MUC-5 is small, but it has hidden hands/libraries. That makes pure AlphaZero a less natural first identity than population/search/imperfect-information methods.

Useful later references:

- NFSP: https://arxiv.org/abs/1603.01121
- Deep CFR: https://proceedings.mlr.press/v97/brown19b.html
- OpenSpiel algorithms list: https://openspiel.readthedocs.io/en/latest/algorithms.html

NFSP is interesting because it was designed for self-play in imperfect-information games. Deep CFR is interesting because it replaces some hand abstraction with neural approximation. OpenSpiel remains a useful north star for a clean game-environment boundary.

## Population methods fit deck + pilot ecology

The deck+pilot setting should avoid collapsing to one brittle champion too early. Population-based and PSRO-style work is relevant because it asks which policies survive against a population, not just against their latest clone.

References:

- PSRO survey: https://www.ijcai.org/proceedings/2024/0880.pdf
- OpenSpiel Alpha-Rank/PSRO tooling reference: https://openspiel.readthedocs.io/en/latest/algorithms.html
- Population robustness paper: https://arxiv.org/abs/2208.05083

## Evolutionary CCG baselines are still worth building

Evolutionary algorithms have been used for collectible-card-game evaluation/deckbuilding. That supports keeping evolutionary constructors/pilots as a serious baseline rather than a toy detour.

References:

- Evolving evaluation functions for collectible card game AI: https://www.scitepress.org/Papers/2022/108069/108069.pdf
- Deck building in CCGs using genetic algorithms: https://www.researchgate.net/publication/358079628_Deck_Building_in_Collectible_Card_Games_using_Genetic_Algorithms_A_Case_Study_of_Legends_of_Code_and_Magic

## Mulligan research/practice note

The official London mulligan gives each mulligan a seven-card look, then bottoms cards equal to mulligans taken. That matters for MUC-5 because 40-card decks with no four-of limit may be especially sensitive to consistency assumptions.

Reference:

- https://magic.wizards.com/en/news/announcements/london-mulligan-2019-06-03

## Current recommendation

Near-term build order after rev0005:

```text
1. Pair payoff tables for life-context constructor cohorts.
2. Human CLI over legal macro-actions.
3. First evolutionary constructor using heuristic or sampled arena fitness.
4. Listwise policy/value dataset from game transcripts.
5. Masked neural pilot only after transcript/action-space data is stable.
```
