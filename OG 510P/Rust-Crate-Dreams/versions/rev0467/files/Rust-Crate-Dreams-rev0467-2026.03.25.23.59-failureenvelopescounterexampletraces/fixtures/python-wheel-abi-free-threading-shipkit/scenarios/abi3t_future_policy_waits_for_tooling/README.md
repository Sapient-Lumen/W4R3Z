# Scenario: abi3t policy is planned but tooling is not yet ready

This scenario models a project that wants to adopt accepted `abi3t` support when the Rust/Python tooling stack can produce and verify it reliably.

It exists to resist a common false conclusion:

> “The PEP was accepted, therefore today’s release should already claim full abi3t support.”

The expected outcome is a variant-horizon report that marks `abi3t` as planned-but-blocked rather than silently pretending support exists.
