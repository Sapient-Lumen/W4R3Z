# Specimen: Build-State Evidence packet (`advance`)

Status: **illustrative specimen, not a live portfolio verdict**

## Identity
- candidate: **Build-State Evidence**
- macro-program: **Evidence Spine**
- specimen role: `review-packet/v0`
- requested verdict: `advance`

## Why now
- Cargo's build-analysis goal is explicitly prototyping recorded build metadata across invocations, rebuild reasons, timing data, and `cargo report` subcommands.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Build-dir-layout work is explicitly motivated by fine-grained locking, reduced Cargo/Rust-Analyzer contention, GC, and a cross-workspace shared cache.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo already offers narrow companion seams for third-party tools: `cargo metadata`, JSON messages, and custom subcommands.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- The March 2026 challenges writeup keeps compilation/resource friction in the universal pain band.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Kernel and artifact family
- kernel: **local-first report/pack family for rebuild explanation and build-state comparison**
- first artifact family:
  - `build-state-pack/v0`
  - `build-state-diff/v0`
  - `build-state-doctor/v0`
- allowed imports:
  - `cargo metadata --format-version=1`
  - `--message-format=json`
  - unstable or experimental Cargo report/build-analysis outputs only with explicit caveat tags

## Stage / proof status
- current stage: **kernel proof with strong stage-1 bridge**
- earned proof:
  - official upstream direction exists for rebuild/timing introspection;
  - realistic companion integration seam exists already;
  - broad pain is current and non-niche.
- missing proof:
  - final stable upstream schemas do not exist;
  - proving-ground pack examples still need more shared workspace comparisons.

## Practical decision improved
A developer or build steward can answer:
- what rebuilt,
- why it rebuilt,
- what changed between two runs,
- and whether contention or configuration drift explains the pain.

## Proving grounds
- shared local workspace with both `cargo build` and Rust Analyzer activity
- CI vs local rebuild comparison
- repeated builds over time with changing flags/features

## Negative states
- unstable upstream formats remain unstable;
- the pack may explain *that* rebuilds happened without fully explaining the optimal fix;
- hosted dashboards and persistent build services are still refused.

## Owner shape / upkeep
- first owner shape: **companion-tool maintainer or small build-infra team**
- upkeep reality: format adapters, drift receipts, proving-ground refresh, and doc updates
- maintenance warning: do not promise “set and forget”; maintenance is multiplicative and mostly invisible work.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

## Adjacency / refused larger forms
- beats: vague build dashboards without machine-readable imports
- remains adjacent to: Cargo-internal analysis work and Rust-Analyzer contention fixes
- refuses:
  - hosted control plane
  - remote build cache empire
  - pretending prototype goals already equal stable contracts

## Bounded v0
A worthy v0 is:
- one local command family,
- one portable pack format,
- one diff view,
- one doctor summary,
- and one proving-ground README with explicit unsupported states.

## Expiry / reissue triggers
Reissue this packet if:
- Cargo stabilizes or materially changes build-analysis/report surfaces;
- build-dir-layout changes invalidate current adapter assumptions;
- a better narrow upstream seam appears;
- or proving grounds show the pack is not actually helping decisions.

## Source candor
- Cargo Book / External tools: **operational narrow-contract evidence**
- project goals: **prototype-direction evidence, not stable contract**
- challenges writeup: **broad pain framing only**

## Packet judgment
Why `advance` instead of `deepen`:
- the kernel is already narrow, companion-first, and evidence-shaped.
Why not `hold`:
- the pain, seam, and artifact family are all current enough to justify bounded stage movement now.
