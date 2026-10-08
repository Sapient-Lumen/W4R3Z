# Scenario family — compile-fail contract exists, but it is not a runtime recipe

This fixture family exists for crates where the most important failure contract is a compiler diagnostic rather than a runtime behavior.

It is meant to catch support drift such as:

- compile-fail tests being treated as proof of an end-to-end runtime recipe,
- diagnostic witness origins disappearing from docs,
- or maintainers forgetting that compile-fail coverage and runtime/integration coverage are different support layers.

A good test-surface pack should keep three things separate:

1. compile-fail/diagnostic witness lineage,
2. runtime/integration fixtures,
3. and any manual-review gap between them.
