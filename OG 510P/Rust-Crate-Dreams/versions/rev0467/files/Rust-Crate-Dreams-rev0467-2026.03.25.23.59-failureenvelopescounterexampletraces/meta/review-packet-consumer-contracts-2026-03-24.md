# Review packet consumer contracts — 2026-03-24

This note exists to stop the archive from acting as if packet production is the whole product.

It is not.
A packet-producing crate only becomes truly useful when another person or tool can import the packet **without losing the meaning of its basis, route, and caveats**.

## Why this matters now

Current Rust substrate keeps getting more machine-readable, but not more uniform:
- `cargo metadata` explicitly requires consumers to pin a format version.
- Cargo’s registry index says its JSON is **not the same** as the Publish API or `cargo metadata`.
- Cargo’s JSON build stream includes compiler messages, produced artifacts, and build-script results, which means importers must keep event-route truth rather than flattening everything into “build facts”.
- `cargo package` exposes `.cargo_vcs_info.json`, but explicitly says the file is a best-effort snapshot and **not verified provenance**.
- docs.rs rustdoc JSON says parsers must respect the `format_version`.
- docs.rs download archives are useful processing inputs but are not directly usable offline docs and can require extra asset fetching.

A worthy crate above this substrate should therefore publish **consumer contracts**, not just producer schemas.

## What a consumer contract is

A consumer contract tells another system:
1. what artifacts may be imported,
2. how route resolution is recorded,
3. what schema/version guarantees apply,
4. what materialization modes are supported,
5. what degrades or stays partial,
6. and what non-claims the consumer must preserve.

## The five consumers that matter most

### 1. Reviewer / teammate

Needs:
- one intake receipt saying what was imported,
- one materialization plan saying what was actually prepared for review,
- and one manual-review zone list.

The reviewer does **not** need a giant crawler log.
They need a compact statement of what evidence they are looking at and what it still cannot prove.

### 2. CI / policy gate

Needs:
- stable enough schemas,
- explicit unknown-field handling,
- clear failure classes (`hard_fail`, `partial_import`, `manual_review_required`),
- and reproducible route resolution.

A CI consumer must be allowed to reject “success with hidden degradation”.

### 3. Offline / air-gapped reviewer

Needs:
- a materialization plan,
- local file references,
- explicit declarations of what still points to live remote assets,
- and a ceiling explaining what cannot be made portable.

This is where docs.rs download archives matter.
They are valuable source material, but not a magic “offline-ready” flag.

### 4. Incident / recheck operator

Needs:
- fast re-intake of changed facts,
- trigger linkage to the prior basis lock,
- delta-friendly imports,
- and a way to reopen review without rewriting history.

This consumer lives right next to **P-0535**.

### 5. Assistant / search surface

Needs:
- pinned basis references,
- claim traces,
- query support boundaries,
- and a prohibition against silently switching from frozen materials to live latest pages.

This is the consumer most likely to flatten uncertainty unless the contract is explicit.

## Minimum artifact set for a worthy consumer contract

A first usable release should export at least:

1. `intake.receipt.json`
   - what was imported,
   - where it came from,
   - how it was pinned or resolved,
   - and what compatibility caveats came with it.

2. `materialization-plan.json`
   - which imported surfaces were transformed into reviewable materials,
   - which stayed live remote,
   - which became partially portable,
   - and which could not be materialized honestly.

3. `manual-review-zones`
   - one explicit list rather than a vague prose disclaimer.

Optional but valuable:
- `degradation.report.json`
- `route-resolution.report.json`
- `materialization-gap.report.json`

## Non-claims that must stay visible

A consumer contract must refuse these common lies:

- “registry index == cargo metadata == publish API”
- “`.cargo_vcs_info.json` proves source provenance”
- “docs.rs download archive means offline docs are solved”
- “latest docs.rs URL is a pinned citation surface”
- “import succeeded, therefore no meaning was lost”

## What this means for the top crates

### P-0509 Pathfinder
Must emit decision packets that name the **consumer contract** they expect downstream systems to use.

### P-0536 Crate Knowledge Pack
Should now own the **intake** and **materialization** story for review bundles.
This is the sharper missing layer from this pass.

### P-0535 Dependency Lifecycle Transition Kit
Should import the same intake/materialization artifacts when opening later rechecks.

### P-0472 Docs.rs Build Parity Kit
Must keep hosted/local drift and materialization caveats separate.

### P-0496 Source Parity
Must preserve route truth for local mirrors, vendored trees, and imported verification receipts.

## Worthy first-release test

A crate clears the bar here when another team can:
1. import a packet,
2. understand how it was pinned,
3. see what was materialized for review,
4. see what stayed partial,
5. and continue using that packet without silently switching to live remote guesses.

If that cannot happen, the crate still feels like a producer demo, not an ecosystem contribution.

## Sources

- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
