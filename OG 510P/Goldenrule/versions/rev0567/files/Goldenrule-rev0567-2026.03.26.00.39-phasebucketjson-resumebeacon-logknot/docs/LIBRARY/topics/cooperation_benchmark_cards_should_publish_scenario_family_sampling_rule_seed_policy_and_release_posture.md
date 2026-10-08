# Cooperation benchmark cards should publish scenario family, sampling rule, seed policy, and release posture

A compact cooperation benchmark card is still too weak if the published result quietly depends on **which worlds or scenarios were drawn** and **how exposed those worlds were before evaluation**.
Even when wrapper, adjudication stack, and scoring rule are fixed, a cooperation result can move because the benchmark used one curated slice, one lucky seed bundle, one hidden reroll policy, or one public/private holdout posture that stays implicit.

Recent evaluation work makes the archive rule clear:

- `RS-GR-074` argues that benchmark metadata about design assumptions and evaluation methodology should be standardized rather than left scattered or implicit.
- `RS-GR-091` shows that random seeds can induce significant macro-level and micro-level variability in benchmark outcomes, so one seed bundle should not silently stand in for the whole evaluation object.
- `RS-GR-092` finds that many widely used benchmarks do not make replication easy, which supports publishing the scenario family and draw policy rather than leaving them as internal scaffolding.
- `RS-GR-093` shows that release posture matters: private held-out evaluation and repeated-query exposure create different contamination and overfitting risks than fully public benchmark release.

## Minimum contract

Whenever a retained cooperation result depends on a fixed suite, generated world family, task-template family, stochastic simulator, or randomized assignment procedure, publish four short fields on the card or neighboring compact receipt:

1. **scenario / world / template family** — the fixed suite, generator family, world bank, task template family, or assignment pool from which evaluation instances came;
2. **sampling / randomization rule** — how scenarios, partner assignments, tasks, or worlds were drawn, stratified, or filtered before scoring;
3. **seed set / reroll / stopping policy** — the declared seeds or seed-generation policy, plus any reroll, replacement, or stop-after-seeing-results rule;
4. **release posture / holdout exposure** — whether the scored set was public, private, hosted, partially released, replayable offline, or exposed only through a submission API.

If the benchmark uses a single fixed public suite with no stochastic draws, say that directly.
If it uses a public dev slice plus a private hosted holdout, say that directly too.

## Implementor consequence

Do not let one lucky draw masquerade as a cooperation gain.
A retained result from a fixed public suite, a generated-world distribution, a curated “hard” subset, or a hosted private holdout is not automatically the same evaluation object.
If benchmark worlds were rerolled until they “looked right,” if only one seed bundle was kept, or if the main claim relies on a private hosted set with different exposure risk, the comparison license should narrow accordingly.

## Archive consequence

Keep the retained object tiny.
One short scenario-family / draw-rule / seed-policy / release-posture quartet is enough.
That prevents future sessions from laundering world-draw luck or holdout exposure into an inheritor-facing cooperation claim while still keeping the archive compact.
