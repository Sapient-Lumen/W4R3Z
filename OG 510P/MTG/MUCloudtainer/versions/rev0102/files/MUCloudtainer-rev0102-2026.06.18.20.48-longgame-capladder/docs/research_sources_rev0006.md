# rev0006 research sources

This revision used the following online research anchors while shaping the mulligan/action-mask/imperfect-information roadmap.

## Rules anchor

- Wizards, "The London Mulligan" (2019-06-03). Key point: each player draws a starting hand, may take mulligans, and after keeping puts a number of cards equal to mulligans taken on the bottom of their library.

## Environment/action-mask anchors

- PettingZoo action masking tutorial. Key point: in many game environments, masks are the natural way to prevent invalid actions rather than treating invalid actions as no-ops.
- OpenSpiel docs/GitHub. Key point: OpenSpiel is a research framework for RL/search/planning in games, including imperfect-information games and algorithms such as CFR, NFSP, PSRO, AlphaZero, and Alpha-Rank.

## Imperfect-information learning anchors

- Deep CFR. Key point: neural approximation can reduce reliance on manual abstraction in counterfactual regret minimization.
- ReBeL. Key point: combines deep RL and search for imperfect-information games and motivates public-belief/search thinking.
- PSRO survey. Key point: population-based response-oracle methods are appropriate when a single self-play champion may be brittle.

## Local design takeaway

For rev0006, do not implement these heavy algorithms yet. Use them to keep the MUC-5 API compatible with later work:

```text
hidden-information observations
explicit legal action lists
masked action slots
saved payoff tables
strategy populations
pregame mulligan policy as part of strategy identity
```
