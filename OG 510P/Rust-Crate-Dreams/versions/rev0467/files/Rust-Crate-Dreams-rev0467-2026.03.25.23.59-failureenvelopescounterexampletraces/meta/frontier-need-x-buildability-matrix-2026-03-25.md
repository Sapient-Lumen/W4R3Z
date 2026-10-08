# Frontier need × buildability matrix — 2026-03-25

This note separates two questions the archive had started to blur:

1. **How badly is this crate lane needed?**
2. **How buildable is a first honest release right now?**

Those are related but not identical.
A lane can be very needed and still have weak current substrate.
A lane can also become more buildable even if the pain level has not changed, simply because Cargo, docs.rs, crates.io, or official tooling exposed more machine-usable surfaces.

Scoring here is intentionally rough:
- **Need**: 1–5
- **Buildability now**: 1–5

The goal is not fake precision.
The goal is to keep the archive from ranking only by pain or only by implementation convenience.

| Proposal | Need | Buildability now | Why |
|---|---:|---:|---|
| **P-0509 Crate Ecosystem Pathfinder** | 5 | 5 | Survey/challenge material still shows crate choice and ecosystem discoverability pain; crates.io/Cargo/docs.rs now expose enough structure for decision packets. |
| **P-0536 Crate Knowledge Pack Kit** | 5 | 5 | docs.rs hosts rustdoc JSON, downloadable docs ZIPs, explicit build behavior, and target-aware hosted surfaces, which makes machine-usable review packs increasingly concrete. |
| **P-0486 Debuggability Support Contract Kit** | 5 | 4 | Debugging remains a live ecosystem problem; support/export artifacts are buildable, but the public support story remains uneven. |
| **P-0472 Docs.rs Build Parity & Evidence Kit** | 4 | 5 | docs.rs now states sandbox/nightly/default-target behavior and exposes download/queue/build facts clearly enough for a durable parity/evidence layer. |
| **P-0484 Toolchain & Target Support Contract Kit** | 4 | 5 | target tiers, docs.rs default-target changes, and Rust-for-Linux/safety-critical pressures make support truth both important and machine-addressable. |
| **P-0535 Dependency Lifecycle Transition Kit** | 4 | 4 | crates.io now surfaces security advisories more directly; official safety-critical guidance also names lifecycle/replacement concerns explicitly. |
| **P-0431 Public Dependency Boundary Kit** | 4 | 4 | public API / semver / SBOM concerns are increasingly operational, and rustdoc JSON / cargo-semver-checks substrate keeps improving. |
| **P-0496 Cargo Vendor & Source Parity Kit** | 4 | 4 | offline, mirror, and restricted-delivery workflows remain repeated operational pain, and infrastructure/security signals keep this lane relevant. |
| **P-0537 Compile Iteration Feedback Kit** | 4 | 3 | need is real, and Cargo build-analysis goals make the lane more plausible, but the substrate is still becoming product-shaped rather than already stable. |
| **P-0538 Concurrency Contract Kit** | 5 | 3 | async pain is unmistakable, but extracting portable semantic receipts across runtimes/primitives is slower and less substrate-driven than docs/build/support truth. |
| **P-0058 Native Deps Kit** | 4 | 3 | repeated pain across embedded, desktop, geo, and data/FFI stacks, but cross-platform substrate is still heterogeneous and adapter-heavy. |
| **P-0125 Cargo SBOM Precursor Workbench Kit** | 4 | 3 | strategically important, but precursor capture and normalization still require more route/coverage discipline than first-wave frontier crates. |

## Resulting view

### Highest need and highest buildability
These are the lanes most justified for immediate productization:
1. **P-0509**
2. **P-0536**
3. **P-0472**
4. **P-0484**
5. **P-0486**

### High need, medium buildability
These deserve strong research pressure and carefully scoped first releases:
- **P-0535**
- **P-0431**
- **P-0496**
- **P-0537**
- **P-0538**
- **P-0058**
- **P-0125**

## Cross-domain interpretation

This matrix also explains why sector variety still feeds the same frontier rather than forcing a reset.

### Domains that are active enough that the missing crate is mostly a control/evidence seam
- web / service backends
- geospatial
- local-first collaboration
- many protocol-heavy industrial/robotics lanes

These tend to strengthen:
- **P-0509**
- **P-0536**
- **P-0472**
- **P-0535**
- **P-0431**

### Domains that still need strong support/debug/build/package honesty
- GUI / desktop
- game development
- Wasm/plugin systems
- embedded device workflows

These tend to strengthen:
- **P-0486**
- **P-0537**
- **P-0484**
- **P-0496**
- native/build/package lanes

### Domains where evidence and lifecycle matter more than a “better framework”
- safety-critical
- mixed-language / C++ integration
- Rust-for-Linux / low-level systems
- enterprise offline / regulated distribution

These tend to strengthen:
- **P-0484**
- **P-0535**
- **P-0431**
- **P-0496**
- boundary/conformance/evidence kits

## Practical build queue after this matrix

1. **Front door** — **P-0509 + P-0536**
2. **Ground-truth ring** — **P-0472 + P-0484 + P-0535**
3. **Support truth** — **P-0486**
4. **Maintenance/distribution ring** — **P-0431 + P-0496**
5. **Iteration truth** — **P-0537**
6. **Semantic contract research** — **P-0538**

## Guardrail

Do not let a lane rise only because:
- it is broad,
- it is fashionable,
- it appears in many domain conversations,
- or it sounds “foundational”.

A lane should move up only when either:
1. its **need** is plainly high *and* its first release can be honest; or
2. its **buildability** has changed materially because the official ecosystem exposed new substrate.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://docs.rs/releases/queue
- https://www.arewewebyet.org/
- https://www.areweguiyet.com/
- https://arewegameyet.rs/
- https://www.arewelearningyet.com/
- https://github.com/rust-embedded/not-yet-awesome-embedded-rust
- https://georust.org/
- https://automerge.org/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
