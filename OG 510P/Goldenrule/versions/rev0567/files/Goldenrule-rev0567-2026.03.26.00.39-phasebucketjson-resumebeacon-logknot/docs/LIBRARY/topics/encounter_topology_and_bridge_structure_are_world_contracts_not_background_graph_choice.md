# Encounter topology and bridge structure are world contracts, not background graph choice

Recent work adds a missing layer to Concord's future reciprocity lanes: **who can meet whom, and through which bridges, is part of the institution**.

- `RS-GR-183` shows that correlations between cooperativeness and social connectedness can materially change whether cooperation survives, and that degree assortativity can let bridge regions slow or block the spread of defection.
- The same paper further shows that these effects differ across network families such as scale-free versus Poisson networks, so the same local policy can look stronger or weaker because the encounter graph changed.
- `RS-GR-184` adds empirical evidence that positive reciprocity, negative reciprocity, and punishment operate in real network-structured communities rather than in a featureless well-mixed pool.
- Together, these results warn that a benchmark can look more cooperative simply because cooperators sit on hubs or because defectors struggle to cross bridge areas.

## Why this matters for Concord

A future benchmark should not treat encounter structure as harmless graph garnish.

There is a real institutional difference between:
1. well-mixed encounters;
2. sparse clustered networks with bridge bottlenecks;
3. hub-dominated or degree-heterogeneous networks;
4. networks where cooperative or defective roles are non-randomly concentrated on influential positions.

Those choices do not merely change simulation size.
They change whether cooperation is supported by local policy, by protective clustering, by hub occupancy, or by defection being unable to travel far.

## Minimal implementor handoff

If Concord adds networked reciprocity, trust, or helping worlds, publish at least:

1. the encounter topology family and key summary statistics (degree heterogeneity, clustering, assortativity, and bridge structure or their nearest equivalents);
2. whether cooperative or defective roles are randomly placed or systematically concentrated at hubs / bridges;
3. whether results are reported both locally (within neighborhoods or clusters) and globally (network-wide access / welfare);
4. whether any headline improvement survives a well-mixed or degree-neutral companion baseline.

Without that compact contract, future inheritors can mistake graph position effects for Golden-Rule progress.
