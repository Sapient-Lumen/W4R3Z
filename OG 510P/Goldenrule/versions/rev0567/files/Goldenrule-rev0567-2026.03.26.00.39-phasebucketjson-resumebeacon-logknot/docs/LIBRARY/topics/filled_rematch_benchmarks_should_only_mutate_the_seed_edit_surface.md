# Filled rematch benchmarks should only mutate the seed edit surface

The first endogenous rematch-world benchmark should not be treated as permission to rewrite everything in the retained seed.

The seed already tells the inheritor which parts are world-dependent and which parts are copied contract state.

That means the right implementation discipline is narrower than “edit whatever seems helpful.”

The filled benchmark should mutate only the seed edit surface:

1. bind `benchmark_id`,
2. flip `artifact_state`,
3. flip the five world-section statuses to `filled`, and
4. fill the five world-data prefixes that actually depend on the chosen endogenous rematch world.

Everything else should stay frozen, especially:

- the copied `compact_decision_bundle`,
- the publication-contract pointers,
- the decision-contract pointers, and
- the six-section publication shape itself.

This is important for archive size as well as correctness. The row-based world sections stay open enough to add real benchmark rows inside the retained artifact, so the inheritor does not need extra occupancy, tempo, or ranking sidecars just to publish richer measurement tables.

The archive should therefore treat the first real benchmark as one in-place mutation of one retained seed object, guarded by a completion gate plus a mutation-surface guard, not as a new branch of benchmark-planning documents.
