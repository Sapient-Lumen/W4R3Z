# ADR-0038: Toolchain trust tiers (Rust bootstrap)

- Status: accepted
- Date: 2026-02-23

## Context

Rust toolchains are self-hosting and commonly rely on a prebuilt stage0 compiler.

## Decision

DeriveBSD introduces three explicit trust tiers for toolchains:

- Tier 0: pinned vendor stage0, bootstrap-only
- Tier 1: self-hosted with reproducible rebuild evidence
- Tier 2: bootstrappable chain (longer, reduces binary trust)

Toolchains are first-class Artifacts with Build Records and policy knobs.

## Consequences

- Trust boundaries become explicit and reducible.
- Early versions can ship pragmatically while leaving a path to stronger assurance.
