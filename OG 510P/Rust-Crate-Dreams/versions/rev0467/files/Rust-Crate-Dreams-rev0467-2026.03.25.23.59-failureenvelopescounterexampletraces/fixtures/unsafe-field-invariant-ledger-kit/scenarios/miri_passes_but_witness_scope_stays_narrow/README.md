# Scenario: Miri passes but witness scope stays narrow

A crate runs a Miri test over one constructor path and records success.
That is useful evidence, but it does not automatically justify the broader claim that every safe mutator and deserialization path preserves the same initialization invariant.
