# Rematch worlds should publish one compact decision-contract bundle

The final SG-003 tranche is already phrased as ten machine-checkable artifact questions (`SQ-017` through `SQ-026`). That is a strong signal that the archive should stop thinking in terms of one report per subquestion and instead publish one compact decision-contract bundle.

For the current rematch proxy, the relevant decision surface is spread across seven JSON reports covering delay robustness, live contenders, winner certification, materiality gating, delta topology, topology-preserving anchors, and question-targeted probe routing. Those seven JSONs together consume `188599` bytes. The compact decision-contract snapshot serializes the same decision surface in one machine-checkable JSON at a small fraction of that size.

The bundle should expose three sections only:

1. **Delay contract**: minimal robustness probes, live contender sets, dead contender sets, and winner intervals over the tested delay band.
2. **Winner contract**: paired-seed certification, practical-equivalence bounds, and budget-aware triage status for each leaderboard panel.
3. **Delta contract**: budget-admissible parent bands, knife-edge flags, parent-anchor buffers, and topology-preserving anchors.

This is enough to answer all ten phase-3 questions without storing full crossover tables or dense multi-delta grids.

The important implementation move is not merely to compress bytes, but to compress *decision surfaces*. The next inheritor should treat the bundle as the long-term retained artifact and demote richer per-question expansions to temporary scratch unless a new benchmark truly needs them as standing evidence.
