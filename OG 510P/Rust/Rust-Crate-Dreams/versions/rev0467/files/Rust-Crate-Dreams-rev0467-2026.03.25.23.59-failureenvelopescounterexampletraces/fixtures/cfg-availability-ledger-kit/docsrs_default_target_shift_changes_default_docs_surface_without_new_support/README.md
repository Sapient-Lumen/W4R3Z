# Scenario family — docs.rs default-target shift changes default docs surface without new support

This fixture family exists for crates that left docs.rs target posture implicit.

It is meant to catch support drift such as:

- docs.rs changes its default target set,
- the crate’s default visible docs surface changes for readers,
- no new CI, downstream compile, or maintainer support evidence was added,
- and a coarse ledger interprets the wider hosted surface as a new support promise.

A good availability ledger should make four things explicit:

1. that the drift came from **hosted default-target policy**,
2. that visible-surface widening is not the same thing as **new support evidence**,
3. that the right action may be to **pin explicit targets** or review the support contract,
4. and that default-surface drift should stay reviewable even when the crate source did not change.
