# Scenario family — docs-visible item needs separate doctest and downstream usability witnesses

This fixture family exists for crates whose docs surface is wider than their ordinary usable surface.

It is meant to catch support drift such as:

- an item is visible because `#[cfg(any(target, doc))]` or a docs-only path kept it in generated docs,
- doctests still do not prove the same usability claim,
- downstream users on the non-matching target still cannot compile against the public path,
- and a coarse ledger mistakes visibility for real usability.

A good availability ledger should make four things explicit:

1. that **docs visibility** is recorded separately from downstream and doctest usability,
2. that a **docs-only witness** cannot silently become a downstream witness,
3. that doctest and downstream claims are separate even when both involve compilation,
4. and that doctor mode warns about missing audience-specific witnesses instead of flattening them together.
