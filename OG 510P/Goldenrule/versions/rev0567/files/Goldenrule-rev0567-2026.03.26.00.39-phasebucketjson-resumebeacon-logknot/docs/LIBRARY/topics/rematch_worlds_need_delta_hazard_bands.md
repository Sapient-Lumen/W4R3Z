# Rematch worlds need delta hazard bands

The delta-frontier and delta-budget work already shows that a declared smallest effect of interest (`delta`) changes both interpretation and closure cost. The next compact refinement is to warn the inheritor where that closure-cost surface becomes locally ill-conditioned.

In the current proxy, the dangerous places are not broad swaths of the `delta` axis. They are narrow neighborhoods around the observed top-gap means themselves. If `delta` is chosen too close to one of those gaps, the fixed-precision closure proxy has to separate two nearly coincident hypotheses:

- “the leader is materially better than the runner-up”, or
- “the top gap is small enough to count as a practical tie”.

That is exactly the setting where noninferiority / equivalence planning becomes fragile: the prespecified margin matters, margins that are too tight can dramatically reduce power, and post hoc margin choices need explicit caution and transparency (`RS-GR-028`, `RS-GR-030`, `RS-GR-031`).

So the contract should become slightly sharper:

- publish the observed leader-gap deltas for each rematch top panel,
- publish compact hazard bands or a no-knife-edge buffer around those deltas,
- and do not let a coarse delta grid stand in for that warning.

This keeps the archive small. A few exact gap values plus a few hazard-band summaries are enough to tell the next inheritor where closure cost can explode without storing another large family of rerun tables.
