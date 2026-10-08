# Scenario family — `cfg(doc)` makes an item visible but not generally usable

This fixture family exists for crates that intentionally widen *documentation* visibility without widening ordinary use.

It is meant to catch support drift such as:

- an item appears in generated docs because it is guarded by `#[cfg(any(target, doc))]`,
- but a downstream crate on the wrong target still cannot use it,
- and doctests do not see the same `cfg(doc)` world anyway,
- so a coarse “it is in the docs” interpretation would overstate real availability.

A good availability ledger should make four things explicit:

1. that the item is **docs-visible**,
2. that the origin includes **`cfg_doc_visibility`**,
3. that the fidelity is **`docs_only_observation`** unless another slice directly confirms usability,
4. and that doctor mode warns about `docs_visible_but_not_usable` rather than pretending the matrix is settled.
