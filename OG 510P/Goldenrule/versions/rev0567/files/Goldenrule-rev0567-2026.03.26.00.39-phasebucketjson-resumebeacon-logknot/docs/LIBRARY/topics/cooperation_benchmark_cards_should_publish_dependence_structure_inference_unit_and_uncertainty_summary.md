# Cooperation benchmark cards should publish dependence structure, inference unit, and uncertainty summary

A compact cooperation benchmark card is still too weak if it reports a comparison or top-line effect without saying **how certainty was computed**.
Repeated-turn, repeated-episode, repeated-partner, and repeated-participant data are often nested rather than independent.
If the archive treats every row as fresh evidence when the real dependence lives at the dyad, episode, partner, task, or participant level, the retained result can look much more certain than it really is.

Recent methodology work makes the archive rule clear:

- `RS-GR-076` says evaluation metrics are estimates of unobserved estimands with non-negligible uncertainty and argues that statistical models should explicitly account for clustering and other evaluation assumptions.
- `RS-GR-078` argues benchmark infrastructures should report uncertainty alongside point estimates because point estimates alone invite fallacious model-comparison conclusions.
- `RS-GR-079` explains that when outcomes are correlated within clusters, analyses must account for that dependence to avoid incorrect inference.

## Minimum contract

Whenever a retained cooperation result is used comparatively, publish three short inferential fields on the card or neighboring compact receipt:

1. **dependence / clustering structure** — e.g. turns nested in episodes, episodes nested in dyads, repeated tasks nested in participants, or matched sets nested in one partner pool;
2. **inference / resampling unit** — the unit treated as approximately independent for standard errors, intervals, bootstrap resamples, permutation tests, or model-based inference;
3. **primary uncertainty summary** — e.g. standard error, confidence interval, credible interval, or equivalence band for the declared primary contrast, including the level when relevant.

If the retained object is descriptive only and no inferential claim is intended, label it that way instead of letting readers assume row-wise independence by default.

## Implementor consequence

Do not let repeated turns or repeated trials automatically become the effective sample size.
If dependence lives at the dyad, participant, task, or partner-pool level, state that directly and compute uncertainty at that level or with a model that encodes the dependence.
A narrow interval built on the wrong independence assumption is not a compact virtue; it is a misleading claim boundary.

## Archive consequence

Keep the retained object tiny.
One short dependence / inference-unit / uncertainty trio is enough.
That prevents future sessions from laundering many correlated observations into an overconfident inheritor-facing cooperation result while still keeping the archive compact.
