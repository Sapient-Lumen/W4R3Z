# rev0012 research notes

## Why PSRO still looks right

Policy-Space Response Oracles maintain a population of policies and expand it by adding responses to mixtures of the current population. That maps cleanly onto MUC-5 because a “policy” is not just a neural pilot; it can be a deck + mulligan + pilot bundle.

Source: https://arxiv.org/abs/2403.02227

## Why Code-Space Response Oracles are especially tempting here

Code-Space Response Oracles replace black-box RL response oracles with generated source-code policies. MUC-5 is small enough that a future assistant or sandperson could write a policy function, drop it into the population, and have the promotion gate evaluate it.

Source: https://arxiv.org/abs/2603.10098

## Why Alpha-Rank belongs after payoff tables

Alpha-Rank is designed for ranking agents in empirical multi-agent games and OpenSpiel documents using payoff tables / heuristic payoff tables as inputs. This fits our population payoff artifacts better than a single Elo ladder, especially if the strategy ecology becomes intransitive.

Sources:

```text
https://openspiel.readthedocs.io/en/latest/alpha_rank.html
https://www.nature.com/articles/s41598-019-45619-9
```

## Why invalid-action masking remains a core design choice

MUC-5 legal moves are state-dependent. The referee should emit legal actions and the policy should rank them. Invalid-action masking research supports masking valid/invalid action sets instead of making agents learn legality through penalties.

Source: https://arxiv.org/abs/2006.14171

## Why quality-diversity / MAP-Elites belongs on the idea shelf

The MUC-5 deck space is small but weird. We might not want only the highest win-rate deck; we may want an archive of good decks across descriptors such as land fraction, Force density, Jace/Overlord split, 40-vs-60 size, mulligan aggressiveness, and pilot personality. MAP-Elites-style quality-diversity methods explicitly search for diverse high-performing solutions across descriptor space.

Sources:

```text
https://quality-diversity.github.io/papers.html
https://arxiv.org/html/2401.08632v2
```

## Fabulous scale-appropriate tests worth attempting

```text
1. Public-vs-omniscient gap: how much strength do trusted-state agents gain?
2. Mulligan learning: does learned mulligan policy change deck construction?
3. Life-known vs life-unknown construction: does robust construction converge to 60-card piles?
4. Alpha-Rank smoke: do strategy standings disagree with mean win rate?
5. Response-oracle loop: can mutation/static priors find candidates that beat seed bundles?
6. Code-policy oracle: can an assistant-written Python policy beat public_heuristic?
7. MAP-Elites archive: illuminate land_frac × threat_frac × Force_frac niches.
8. Stall adversary: can a policy intentionally force max_decisions, and can the gate catch it?
9. Action-featurization: compare raw slot-index imitation vs action-kind/card/mode features.
10. Replayable surprise mining: find high-upset games and replay/annotate them.
```
