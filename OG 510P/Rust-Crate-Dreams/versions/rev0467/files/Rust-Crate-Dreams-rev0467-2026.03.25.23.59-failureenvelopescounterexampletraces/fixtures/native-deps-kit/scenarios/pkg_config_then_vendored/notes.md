# Scenario: pkg-config then vendored

This scenario exists to prove that **P-0058** must treat *attempt order* as part of the support contract.

The important artifact is not only the final success. It is the fact that:

1. system probing was attempted first,
2. it failed for a concrete reason, and
3. vendored fallback was allowed by policy and then selected.

That sequence is exactly the sort of support truth that usually gets lost inside handwritten `build.rs` logic.
