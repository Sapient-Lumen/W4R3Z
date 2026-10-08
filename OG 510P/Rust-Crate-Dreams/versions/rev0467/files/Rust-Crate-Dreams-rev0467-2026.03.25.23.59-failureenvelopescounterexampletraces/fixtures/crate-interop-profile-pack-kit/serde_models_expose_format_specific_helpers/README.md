# Scenario — Serde model crates quietly expose format-specific helper types

This scenario exists to force **P-0511** to keep separate:

- the claimed shared ecosystem profile,
- the obligations needed to fit that profile,
- pairwise compatibility reality,
- and raw “these crates use the same broad ecosystem” vibes.

## Why it matters

A crate can claim to sit at a neutral Serde data-model boundary while still leaking JSON- or transport-specific helpers into the public API that narrow reuse and increase lock-in.

## Expected artifact pressure

- `boundary-obligation.receipt.json` should record that format-specific helpers are expected to stay internal or explicitly profile-breaking.
- `migration-hazards.report.json` should classify new public format-specific helpers as interop narrowing hazards.
- `profile-class.policy.json` should keep format-neutral model profiles distinct from adapter-heavy bridge profiles.
