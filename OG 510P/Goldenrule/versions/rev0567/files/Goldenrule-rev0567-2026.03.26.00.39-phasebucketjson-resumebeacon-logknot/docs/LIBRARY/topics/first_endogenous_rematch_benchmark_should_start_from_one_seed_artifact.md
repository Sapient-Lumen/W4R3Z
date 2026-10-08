# The first endogenous rematch benchmark should start from one seed artifact

The archive now says exactly what the first endogenous rematch benchmark must publish, but the inheritor still benefits from a concrete starting object.

That starting object should be one retained seed artifact, not a new family of planning sidecars.

The seed lives at `examples/snapshots/rematch_world_benchmark_seed.json` and does three useful things.

1. It keeps the six-section publication shape explicit.
2. It copies the standing compact decision bundle unchanged, so phase-3 work does not fan back out.
3. It leaves only the genuinely world-dependent telemetry fields null, so the first implementor can replace placeholders in place instead of inventing extra benchmark report surfaces.

That means the next implementor-facing workflow is compact:

1. regenerate the seed,
2. bind it to the chosen endogenous rematch world,
3. replace the null occupancy / tempo / ranking measurements with emitted results,
4. keep the compact decision bundle intact,
5. publish one artifact.

The archive-growth implication is as important as the benchmarking implication: when the first world benchmark lands, progress should look like one seed becoming one result, not like six new retained report families.
