# Scenario family — semantic-convention / schema upgrade changes query surface

This fixture family exists for crates that align some or all of their emitted signals with OpenTelemetry semantic conventions.

It is meant to catch support drift such as:

- a release changes the claimed schema URL,
- a field or metric name follows a semantic-convention rename,
- a crate mixes conventional names with custom extensions without marking the boundary,
- or a release silently changes query expectations while still calling the signal surface stable.

A good observability pack should make four things explicit:

1. which signal families are semconv-aligned versus crate-custom,
2. which schema URL or convention version the crate is claiming,
3. whether cross-version query compatibility is expected, migrated, or only best-effort,
4. and whether release notes are required when names or schema posture change.

This family keeps “we use OpenTelemetry conventions somewhere” separate from “downstream users can safely carry queries and alerts across releases”.
