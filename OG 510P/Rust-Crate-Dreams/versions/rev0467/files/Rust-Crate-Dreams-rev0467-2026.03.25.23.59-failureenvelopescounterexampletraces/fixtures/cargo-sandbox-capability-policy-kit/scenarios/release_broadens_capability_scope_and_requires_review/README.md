# Scenario: release broadens capability scope and requires review

A new release of a crate adds outbound network access for its build script and changes the effective policy source from crate-local to CI override.
The build still succeeds, but the policy story is materially broader.

This scenario exists so the diff format can force review instead of letting a green build hide a trust expansion.
