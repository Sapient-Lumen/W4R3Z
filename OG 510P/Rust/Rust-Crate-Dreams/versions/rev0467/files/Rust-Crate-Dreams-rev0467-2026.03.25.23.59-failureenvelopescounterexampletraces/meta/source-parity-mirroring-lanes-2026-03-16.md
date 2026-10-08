# Source parity and mirroring lane boundaries — 2026-03-16

This note exists because the Rust project is now openly pushing on crates.io mirroring and verification while Cargo still maintains stricter, narrower source-replacement and offline rules.

The result is a tempting but dangerous collapse:

> “If mirrors are getting verified, then vendoring/source parity is basically solved.”

That is false.

## Lane 1: verified mirrors / trust distribution

**Proposal:** `P-0026 cargo-tuf-mirror`

This lane should own:

- TUF- or quorum-style mirror verification,
- trusted metadata and signature distribution,
- and mirror-serving infrastructure.

The central question is:

> “Can a client verify that the mirror served the right crates.io content?”

## Lane 2: workspace-local source parity / coverage truth

**Proposal:** `P-0496 Cargo Vendor & Source Parity Kit`

This lane should own:

- logical source identities,
- replacement chains,
- protocol aliases,
- vendored versus uncovered source classes,
- and imported verification evidence as provenance.

The central question is:

> “What source identities and uncovered exceptions actually participated in this build?”

A verified mirror can exist while this lane still reports `mirror_verified_but_mixed_sources`.

## Lane 3: offline transport / staged transfer

**Proposals:** `P-0001 Cargo Snapshot`, `P-0018 Airgap SDK`

These lanes should own:

- moving Rust dependency/toolchain substrate between environments,
- staging artifacts for disconnected or constrained systems,
- and transfer-bundle concerns.

Their central question is:

> “How do we move the needed Rust substrate into the target environment safely and repeatably?”

That is not the same thing as proving source identity inside one workspace.

## Lane 4: package mutation / patching / overrides

Cargo already has `[patch]`, path dependencies, and override mechanisms.
These should remain visible as **exceptions to parity** rather than hidden implementation details.

The central question is:

> “Did this build intentionally stop being registry-equivalent?”

## Working rule

When a future pass touches vendoring, mirrors, or offline Cargo, it must state explicitly whether the new value is about:

1. **mirror verification infrastructure**,
2. **workspace-local source parity / coverage**,
3. **artifact transfer into constrained environments**,
4. or **intentional graph mutation via patch/path overrides**.

Do not let the archive flatten these into one fake “offline trust” story.
