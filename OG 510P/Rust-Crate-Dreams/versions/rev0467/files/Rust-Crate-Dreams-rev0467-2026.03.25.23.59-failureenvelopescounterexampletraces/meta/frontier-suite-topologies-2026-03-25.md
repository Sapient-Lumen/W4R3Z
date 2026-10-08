# Frontier suite topologies — 2026-03-25

This note keeps the frontier stable **while making it more package-real**.

The archive no longer needs more broad lane inflation.
It needs sharper answers to:
- what package family should be built,
- what surface each package serves,
- and what another team can actually install or import.

## Main judgment

The strongest missing Rust contributions are still mostly **receiver-facing control-plane kits**.
But many of them should now be planned as **small suite topologies** rather than single all-in-one crates.

## Suite-readiness board

### 1. P-0509 + P-0536 + minimal P-0535
**Role:** selection / knowledge / continuity front door

Why first:
- the receiver-facing job is already clear;
- the imported ecosystem surfaces already exist;
- and the package family can be named without overclaiming.

Recommended `0.1` family:
- `pathfinder-core`
- `pathfinder-schemas`
- `cargo-pathfinder`

Recommended `0.3` additions:
- `pathfinder-importers`
- `pathfinder-corpus`
- minimal continuity support inside the CLI or a tiny `pathfinder-recheck` add-on

What other people receive:
- one command surface,
- one embeddable decision API,
- one stable packet vocabulary,
- and one frozen basis/recheck story.

### 2. P-0472 + P-0484
**Role:** docs/build/target/toolchain support-envelope import ring

Why second:
- docs.rs and target/toolchain substrate is already machine-usable;
- support-envelope packets are easy to motivate across embedded, GUI, safety-critical, and cross-platform work;
- and adapter churn should be easy to isolate from stable packet meaning.

Recommended `0.1` family:
- `support-envelope-core`
- `support-envelope-schemas`
- `cargo-support-envelope`

Recommended `0.3` additions:
- `support-envelope-docsrs`
- `support-envelope-targets`
- `support-envelope-corpus`

### 3. P-0486
**Role:** debugger support envelope

Why third:
- the need remains real;
- the receiver/job is clear;
- but the matrix and corpus burden are heavier, so the family should stay narrower at first.

Recommended `0.1` family:
- `debug-support-core`
- `debug-support-schemas`
- `cargo-debug-support`

Recommended later additions:
- `debug-support-probes`
- `debug-support-corpus`

### 4. P-0431 + P-0496 + P-0125
**Role:** continuity / source-parity / public-boundary / inventory carry-forward ring

Why fourth:
- these lanes matter after initial adoption;
- they benefit from shared packet vocabulary;
- but they should not bloat the front door’s first release.

Recommended family shape:
- `carryforward-core`
- `carryforward-schemas`
- `cargo-carryforward`
- optional adapters: `carryforward-source-parity`, `carryforward-boundary`, `carryforward-sbom`
- `carryforward-corpus`

### 5. P-0537
**Role:** compile-iteration truth

Why fifth:
- very important,
- but still more substrate-dependent.

Recommended early family:
- `iteration-feedback-core`
- `iteration-feedback-schemas`
- `cargo-iteration-feedback`

### 6. P-0538
**Role:** concurrency semantics comparison

Why sixth:
- highly salient,
- but semantics are harder to stabilize than selection/support packets,
- so this should likely begin as a research-heavy suite.

Recommended early family:
- `concurrency-contract-core`
- `concurrency-contract-schemas`
- `cargo-concurrency-contract`
- `concurrency-contract-corpus`

## Shared seam rule

Across top lanes, the archive should prefer a common conceptual split:
1. **core semantics**
2. **stable schema / packet vocabulary**
3. **operator-facing CLI**
4. **substrate adapters**
5. **scenario corpus**

Do not force every lane to have the same number of crates.
Do force every lane to explain why each package exists.

## Promotion rule after this pass

Do not call a lane suite-ready until the archive can name:
1. the operator-facing package,
2. the embeddable package,
3. the stable packet/schema package,
4. the adapter boundary,
5. and the corpus or fixture boundary.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://rust-lang.github.io/rust-project-goals/2026/
- https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
