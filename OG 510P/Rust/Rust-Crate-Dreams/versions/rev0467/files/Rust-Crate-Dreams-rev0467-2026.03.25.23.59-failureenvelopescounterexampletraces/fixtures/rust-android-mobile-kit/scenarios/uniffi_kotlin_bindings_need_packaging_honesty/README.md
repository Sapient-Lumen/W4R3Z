# Scenario: UniFFI Kotlin bindings need packaging honesty

This scenario models a Rust library that successfully generates Kotlin bindings through UniFFI but does not yet have an honest Android packaging story.

It exists to resist a common false conclusion:

> “Kotlin bindings were generated, therefore Android library shipping is solved.”

The expected outcome is explicit `binding_mode` / ABI-coverage output plus a doctor summary that keeps packaging/manual-review gaps visible.
