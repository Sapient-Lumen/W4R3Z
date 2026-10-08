# Scenario: delta write surface and hudi read surface must not collapse into one common profile

This scenario exists because `deltalake` and `hudi-rs` now both look credible from a distance, but they do **not** expose the same public capability shape.

The fixture keeps future archive passes from flattening:
- Delta’s broad storage/operation matrix,
- and Hudi’s documented snapshot / time-travel / incremental / DataFusion surface

into one fake “open table format parity” claim.
