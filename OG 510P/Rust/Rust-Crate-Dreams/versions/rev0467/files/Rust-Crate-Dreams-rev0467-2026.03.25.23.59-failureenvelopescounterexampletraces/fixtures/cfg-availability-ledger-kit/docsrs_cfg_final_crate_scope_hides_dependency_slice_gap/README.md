# Scenario family — `cfg(docsrs)` on the final crate hides a dependency slice gap

This fixture family exists for crates whose top-level documentation view is widened for docs.rs, while a dependency or workspace member still lacks the same slice.

It is meant to catch support drift such as:

- the final crate enables extra docs-only visibility under `cfg(docsrs)`,
- a dependency does not receive that same cfg because docs.rs only applies it to the final crate,
- the public docs still make the surface look broader than the dependency-backed usable slice,
- and a coarse ledger fails to distinguish hosted display from end-to-end availability.

A good availability ledger should make four things explicit:

1. that the witness is a **docs.rs-scoped slice**,
2. that `cfg(docsrs)` scope stops at the final crate,
3. that any dependency-backed claim without direct evidence stays uncertain,
4. and that doctor mode warns about final-crate-scope mismatch rather than pretending the matrix is settled.
