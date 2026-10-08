# Cargo Vendor & Source Parity Kit — product plan for restricted-delivery evidence (2026-03-24)

This note upgrades **P-0496 Cargo Vendor & Source Parity Kit** from a useful boundary reminder into a more explicit product plan.

It answers:

> What should this crate provide other people in theory and practice, now that mirrors, trusted publishing, `pubtime`, build-dir churn, and hard-domain adoption all make restricted-delivery truth more important?

## Main judgment

The missing value is **not** another mirror, registry, review bot, or supply-chain score.

The missing value is one boring, reviewable bundle that tells another person:

1. what **logical source identities** resolved,
2. what **physical roots** and local replacements actually got used,
3. what portion of the graph is inside the claimed vendored / mirrored / offline boundary,
4. what imported mirror-verification evidence exists,
5. and where the claim must stop.

That is a small but surprisingly important seam.

## Who this crate is for

### Primary receivers
- release / CI engineers,
- platform engineers maintaining vendored or mirrored dependency flows,
- reviewers in air-gapped or regulated environments,
- maintainers trying to prove whether an “offline” recipe is honestly scoped.

### Secondary receivers
- security engineers importing mirror verification and trusted-publishing signals,
- tooling / assistants that need to explain the source basis of a build.

## Product promise

Given a workspace and a selected resolution context, the crate should output a **restricted-delivery review bundle** that makes these questions boring:

- Which source IDs resolved the graph?
- Which physical roots did those IDs collapse onto?
- Which dependencies still came from git/path or another uncovered source?
- Does “vendored” or “mirrored” actually cover the whole graph?
- What imported mirror verification exists, and what does it not settle?
- Is this build honestly replayable under the claimed restricted-delivery posture?

## `0.1` surface

### CLI
- `cargo source-parity inspect`
- `cargo source-parity doctor`
- `cargo source-parity bundle`
- `cargo source-parity diff`

### Library
Suggested crate split:
- `source_identity` — logical source IDs, aliases, replacement chains
- `coverage_model` — graph coverage, uncovered exception classes, parity verdicts
- `mirror_imports` — imported mirror-verification evidence with provenance labels
- `bundle` — emitters for review packets and manifests
- `doctor` — conservative checks and human-readable explanations

## `0.1` packet family

### 1. `source-origin.receipt.json`
States:
- each logical source ID,
- its canonical class (registry / replacement / local directory / path / git / other),
- and the physical root or fetch basis observed.

### 2. `source-parity.lock`
A frozen view of the source basis for the chosen resolution.
This is not a replacement for `Cargo.lock`.
It is a companion receipt focused on origin and parity claims.

### 3. `source-coverage.report.json`
Answers:
- what percentage / subset of the graph is inside the claimed vendored or mirrored boundary,
- what classes remain outside,
- whether the claim is full, partial, or blocked.

### 4. `vendor-parity.report.json`
Answers:
- whether the vendored content is logically equivalent to the expected source set,
- whether alias splits or local overrides changed the effective story,
- and which mismatches require manual review.

### 5. optional `mirror-verification.import.json`
Imports:
- mirror or TUF-style verification artifacts,
- provenance about where they came from,
- and a strict label that these are **imported trust receipts**, not workspace-local source-parity proof.

## First scenario families

### Scenario 1 — clean registry-to-vendor parity
Question:
- Did the vendored tree fully cover the registry-resolved graph?

### Scenario 2 — local mirror plus path/git exceptions
Question:
- Did a real mirror exist while meaningful parts of the graph still escaped its covered boundary?

### Scenario 3 — source replacement with alias split
Question:
- Did multiple logical source identities collapse onto one local root while still needing separate review labels?

### Scenario 4 — restricted-delivery review bundle
Question:
- Can a reviewer tell transfer, mirror verification, workspace parity, and local exception classes apart?

### Scenario 5 — air-gapped CI handoff
Question:
- Can another engineer inspect the bundle and know what additional local transfer or native prerequisite work is still missing?

## Practical command sketch

```text
cargo source-parity inspect
cargo source-parity doctor --claim offline
cargo source-parity bundle --with mirror-verification.import.json
cargo source-parity diff --against previous/source-parity.lock
```

## What it should refuse to claim

This crate must refuse to claim:
- that mirror verification proves full workspace-local parity,
- that vendoring proves whole-environment reproducibility,
- that a clean source graph proves native prerequisites are satisfied,
- that trusted publishing or a Security tab proves task fit,
- or that offline packaging and source parity are the same problem.

## Why now

Several current Rust signals make this more urgent and more buildable:

- official mirroring work explicitly targets local mirror use with cryptographic verification;
- crates.io now exposes stronger trust surfaces and `pubtime`, making replay and review workflows more actionable;
- Cargo is actively changing build-dir internals because projects rely on unspecified details;
- the latest Cargo extraction CVE shows that dependency acquisition and unpacking are part of the real risk surface;
- safety-critical and other hard-domain users still thin out where tooling evidence becomes blurry.

## Relation to adjacent lanes

### Not P-0026 `cargo-tuf-mirror`
That lane owns mirror infrastructure and verification distribution.

### Not P-0001 Cargo Snapshot / P-0018 Airgap SDK
Those lanes own transfer and disconnected-environment movement.

### Not P-0535 Dependency Lifecycle Transition
That lane owns off-ramp, anchor, and re-resolution risk.

### Not P-0470 package review
That lane owns package policy and inspection at a different layer.

**P-0496** owns the workspace-local answer to:
> what source basis did this build actually use, and how honest is the restricted-delivery claim?

## Product rule

A worthy `0.1` should succeed even if it only makes one reviewer conversation boring:

> “Show me exactly what was covered by vendoring/mirroring, what was not, and what imported trust evidence means here.”

If it can do that honestly, it is already valuable.

## Sources

- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
