# Scenario — build-script metadata and artifact messages share one session identity

This scenario exists because build artifacts, build-script observations, and later diagnostics must still be attributable to one concrete Cargo invocation.

The point of this fixture is to keep **event sequencing** and **session provenance** explicit.
