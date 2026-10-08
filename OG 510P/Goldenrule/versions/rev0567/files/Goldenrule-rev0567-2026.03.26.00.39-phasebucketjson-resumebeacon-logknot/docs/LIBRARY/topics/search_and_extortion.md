# Extortion and the Limits of Random Search

## Findings (2026-01-02)

Against a Press-Dyson extortionate strategy ($\chi=3, P=1$), random search over the Memory-One space $[0,1]^5$ yielded the following:

1.  **Exploitation Resistance**: In short matches (50 rounds), random strategies can occasionally "beat" the extortionist by exploiting its $p_{DD}=0$ fragility or through noise/drift.
2.  **Long-term Enforcement**: In long matches (1000 rounds), the extortionist successfully enforces its surplus relationship. The best strategies found via random search (100 trials) achieved an average payoff of ~1.84, while the extortionist took ~3.08.
3.  **Mutual Cooperation Gaps**: Mutual cooperation is extremely difficult to sustain against an extortionist who is programmed to "bend" the other player. Random search only achieved a mutual cooperation rate of ~48%.
4.  **Hill Climbing Success**: Transitioning from random search to local Hill Climbing (500 trials, $\sigma=0.2$) significantly improved the defense. The best discovered strategy reached an average payoff of ~2.21 (vs ~1.84 for random search), achieving ~70% mutual cooperation. This suggests that the payoff landscape against extortion has smooth "ridges" that simple local search can exploit.

## Implications for Concord

- **Iterative Search**: Stage 4 needs more than random search (e.g., Evolutionary Strategies or Gradient Ascent on the payoff landscape). Hill climbing is a strong first step.
- **Meta-Strategies**: We should investigate if "second-order" strategies (those that recognize they are being extorted) can be represented in the current StrategySpec.
- **Vampire Gating**: The Vampire Suite should be a standard hurdle for any "Golden Rule" candidate. If it can be extorted, it isn't robust.
