# Scenario — example target hidden by required features needs viability truth

A crate has an `examples/stream.rs` target, but it is gated behind `required-features = ["stream"]`.
The README mentions the example casually, while the official quickstart is a smaller local path.

This fixture keeps these truths separate:

- the example target exists,
- Cargo may skip it when features are absent,
- and example presence alone is not enough to claim a viable first-success path.
