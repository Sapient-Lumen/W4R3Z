# Design: Resolution Strategy Kit (`cargo resolve-plan`, `resolution-strategy-pack/v0`)

## Goal
Define a portable contract for **reviewing, diffing, and exchanging dependency-resolution strategy** in Rust.

This kit is for the layer *above* chosen-graph evidence:
- what objective was pursued,
- what constraints and preferences shaped the search,
- what alternatives mattered,
- what tradeoffs were accepted,
- and what downstream consumers may safely conclude.

This should **not** replace Cargo’s resolver, PubGrub, `cargo tree`, lockfiles, Policy Kit, or Resolution Doctor Kit.
It should turn strategy into a reviewable artifact instead of a mix of CLI flags, local config, and maintainer memory.

## Primary signals
- PubGrub-in-Cargo explicitly frames the work as groundwork for better MSRV support, CVE-aware resolution, and richer Cargo extensions:
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Rust 1.84 stabilized the MSRV-aware resolver:
  https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/
- Rust 2024 / resolver v3 implies `incompatible-rust-version = "fallback"` by default:
  https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- Cargo’s `rust-version` docs say multiple policies in one workspace get complicated:
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo unstable features expose `minimal-versions`, `direct-minimal-versions`, and `msrv-policy` as explicit alternative objectives:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 is actively exploring publish-time-aware resolution and `minimumReleaseAge`:
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- `cargo-semver-checks` still needs accurate recursive dependency-feature truth from Cargo interfaces:
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

## Core UX: `cargo resolve-plan`
- `cargo resolve-plan explain`
  - emit the declared objective, constraints, preferences, and chosen graph imports
- `cargo resolve-plan diff --against <report|git-ref|lockfile>`
  - show how strategy or accepted tradeoffs changed
- `cargo resolve-plan compare --profile <latest|minimal|direct-minimal|msrv|publish-time>`
  - produce candidate summaries for a bounded set of named strategies
- `cargo resolve-plan verify-pack <path>`
  - verify schema versions, checksums, and redaction state
- `cargo resolve-plan handoff --to <migration|api|policy|support>`
  - emit consumer-specific import notes without silently recomputing strategy

## Artifact set
### `resolution-objective/v0`
Declare what kind of resolution was intended.

Should record:
- subject identity (workspace / package selection / target selection / toolchain)
- strategy profile (`latest`, `msrv-fallback`, `direct-minimal-check`, `publish-time`, etc.)
- relevant config and CLI posture
- workspace unification posture
- rust-version posture
- publish-time / minimum-release-age posture when used
- override / patch / replace posture
- redaction notes

### `resolution-candidate-report/v0`
Describe the bounded set of strategies or candidate outcomes that were actually examined.

Should record:
- candidate id and profile
- whether it was solved, partial, or inconclusive
- high-level graph/result summary
- blocker categories and reason codes
- why it was not chosen or why it remained uncertain

Design rule: **candidate reporting is optional and bounded.**
The kit must not pretend to enumerate the whole search space.

### `resolution-decision-report/v0`
The main review artifact.

Should record:
- imported `resolve-report/v0` / `feature-report/v0` pointers
- declared objective profile
- accepted tradeoffs
- rejected alternatives or why none were examined
- confidence / incompleteness notes
- intended consumers (`migration`, `publish-review`, `support`, `policy`, `release`, etc.)

### `resolution-strategy-diff/v0`
Compare two strategy states.

Should record:
- objective-profile drift
- config / CLI / manifest / workspace-selection drift
- accepted-tradeoff drift
- consumer-impact hints
- explicit unknowns

### `resolution-strategy-pack/v0`
Portable bundle containing:
- `manifest.json`
- `resolution-objective.json`
- `resolution-decision-report.json`
- optional `resolution-candidate-report.json`
- optional `resolution-strategy-diff.json`
- imported dependency-control report references
- checksums and provenance notes

## Design principles
1. **Objective first, chosen graph second.** Reviewers should know what problem was being solved before they are asked to bless a lockfile.
2. **Do not fork Cargo’s truth.** Import chosen-graph and feature truth from Dependency Control artifacts rather than re-deriving them.
3. **Alternatives must stay bounded and honest.** The kit should compare named strategies, not claim omniscient search.
4. **Tradeoffs are first-class.** Newer vs older, lower vs latest, MSRV fallback, workspace unification, publish-time fencing, and candidate incompleteness all belong in the report.
5. **Downstream consumers remain downstream.** Strategy artifacts can feed Migration, Public API, Policy, Support Envelope, and Release work without turning into those kits.
6. **Redaction and private-registry posture are first-class.** Strategy reports must survive enterprise or alternate-registry usage.

## Relationship to nearby kits
- **Resolution Doctor Kit** owns chosen packages / versions / sources / conflict explanations / reproducers.
- **Feature Kit** owns activation why-chains, unification deltas, and capability posture.
- **Policy Kit** owns verdicts and waivers, not resolution objectives.
- **Migration Kit** owns source→destination change programs, not one specific resolution strategy profile.
- **Public API Kit** owns release-boundary exposure and semver truth, not strategy selection.
- **Manifest Surface Kit** owns authored/defaulted/published manifest truth that strategy reports may import.

## What an epic contribution would look like in practice
A strong contribution here would make it normal to attach a small pack explaining:
- whether a release aimed for latest, MSRV-safe, direct-minimal validation, publish-time replay, or another named strategy;
- what Cargo-native data was imported;
- what alternatives were considered and rejected;
- and what downstream consumers may reuse without reconstructing the whole decision from CI logs.

That would give Rust something many ecosystems still lack:
**reviewable dependency-strategy truth, not just lockfiles and blame.**
