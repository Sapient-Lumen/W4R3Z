# Scenario — merged 2024 doctests and standalone-sensitive receipts are not like-for-like

This scenario compares two bundles from the same crate family:
- the older bundle came from an Edition 2021 crate where examples compiled separately;
- the newer bundle came from an Edition 2024 crate where compatible doctests merged, except line-sensitive examples that now require `standalone_crate`.

The point of the report is to keep trend language honest:
- both bundles may say “doctests passed”,
- but line-sensitive examples, grouping semantics, and target-scope imports changed enough that the comparison is not a simple green-to-green trend.
