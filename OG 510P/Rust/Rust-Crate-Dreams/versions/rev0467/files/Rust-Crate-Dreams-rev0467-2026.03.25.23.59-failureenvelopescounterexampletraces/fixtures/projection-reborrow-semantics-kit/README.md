# Projection & Reborrow Semantics Kit fixtures

This fixture pack keeps **P-0440** concrete.
It focuses on four receiver-facing artifacts:

- `projection-authority.receipt.json`
- `borrow-semantics.matrix.json`
- `semantics-witness.report.json`
- `projection-support-bundle.manifest.json`

The scenarios are intentionally about **honesty boundaries**:
macro presence is not authority by itself, a generalized-reborrow claim is not one boolean, and a green Miri run is not the same thing as full semantic coverage.
