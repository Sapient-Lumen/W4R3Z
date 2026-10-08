# mixed_binding_stack_must_not_claim_uniform_callback_or_coverage_strength

This scenario represents a crate that mixes:

- a plain C header exported via `cbindgen`,
- a UniFFI surface for Swift/Kotlin/Python,
- and a Diplomat surface for a separate consumer.

The kit should keep callback/runtime posture and check strength explicit per surface instead of marketing one uniform multi-language support claim.
