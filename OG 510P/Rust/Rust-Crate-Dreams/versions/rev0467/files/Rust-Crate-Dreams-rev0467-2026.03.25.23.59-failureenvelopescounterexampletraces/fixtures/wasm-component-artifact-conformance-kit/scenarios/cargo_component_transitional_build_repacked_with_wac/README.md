# Scenario: cargo-component transitional build repacked with WAC

This scenario models a project that still uses a transitional `cargo-component` workflow and then performs explicit composition with WAC before publishing a bundle.

It exists to resist a common false conclusion:

> “The component exists, therefore the exact tooling path no longer matters.”

The expected outcome is an explicit tooling-lineage report rather than a fake “native component build” verdict.
