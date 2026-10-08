# Scenario: coherence default does not mean global solver parity

This scenario keeps solver-lane claims honest.

Stable Rust already enables the next-generation trait solver for coherence, but that is not the same thing as saying the entire crate was exercised under `-Znext-solver=globally`.

The receipt should preserve:

1. that the lane was `coherence_default_only`,
2. that the result is useful for previewing overlap/coherence behavior,
3. but that it is not strong enough to claim full solver parity for type checking, rustdoc, or lints.
