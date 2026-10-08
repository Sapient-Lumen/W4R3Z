# Design: Interop Commons Kit (`cargo commons`, `commons-pack/v0`)

## Goal
Define a portable contract for identifying, specifying, validating, diffing, and reviewing **neutral shared building blocks** in the Rust ecosystem: common types, traits, adapter rules, and conformance vectors that let otherwise independent libraries compose.

This should help answer questions like:
- when does an ecosystem seam deserve a shared building block,
- what belongs in that shared layer versus crate-specific ergonomics,
- how existing crates adapt to it,
- what edge cases or semantic guarantees must be preserved,
- how stewardship and adoption should be made explicit,
- and what evidence shows the common layer is actually working.

It should **not** replace domain-specific frameworks, registries, curated recommendation sites, or every existing adapter crate.
It should make interop deliberate and auditable.

## References (signals)
- The Rust vision work explicitly recommends enabling smoother interop, calls out key interop traits and standard building blocks as potential answers, and notes that coherence rules make incremental ecosystem interop traits difficult.  
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 async project-goal updates say progress toward the next generation of async libraries has been blocked on stable solutions for async traits and streams.  
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
  https://blog.rust-lang.org/2025/04/08/Project-Goals-2025-March-Update/
- The 2025 State of Rust survey still reports resource usage as a major productivity problem and notes continuing concern about developer/maintainer support and ecosystem complexity.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s own development updates keep stressing that plugins matter because Cargo cannot be everything to everyone; that is a strong signal that shared building-block work should often live as a companion ecosystem layer first, not as a demand for immediate standardization inside Cargo.  
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The `http` crate is explicit precedent for a successful neutral shared building block: common HTTP types, but not a specific client/server implementation.  
  https://docs.rs/http
- Tower treats `Service` and `Layer` as stable integration points, and `tower-http` explicitly says its middleware works across ecosystems using `http` and `http-body`.  
  https://docs.rs/tower
  https://docs.rs/tower-http
- `axum` and `tonic` both expose Tower-based interoperability in practice.  
  https://docs.rs/axum/latest/axum/
  https://docs.rs/tonic/latest/tonic/service/index.html
  https://docs.rs/tonic/latest/tonic/transport/server/struct.Server.html

## Design principles
1. **Common ground must be earned.** Only propose a shared layer where multiple serious adopters already exist and repeated adapter churn is visible.
2. **Neutral core, opinionated edges.** The shared building block should stay small; richer ergonomics stay in framework crates.
3. **Adapters must be honest.** Lossy conversions, allocation costs, buffering, blocking, runtime assumptions, and feature gates must be first-class in adapter profiles.
4. **Conformance beats vibes.** Shared seams need golden vectors and negative cases, not just README claims.
5. **Do not flatten semantic differences.** If two ecosystems disagree materially, say so; do not hide it behind a vague common trait.
6. **Version and stewardship matter.** Common seams become infrastructure. Their ownership and migration posture must be visible.
7. **Atlas consumes commons, not vice versa.** The interop layer should create neutral building blocks that Ecosystem Atlas can reference; it should not become a recommendation site.
8. **Support “not ready yet.”** A good commons system must be able to say a seam is promising but not mature enough for standardization.

## Proposed artifact family

### 1) `interop-seam/v0`
Declares the seam under consideration.

Fields should include:
- seam id and title
- problem scope
- in-scope / out-of-scope semantics
- candidate adopter families
- why a common layer is justified
- known semantic fault lines
- related domain kits / existing crates
- atlas domains/lanes that would likely consume this seam if it succeeds

Examples:
- `http-request-response`
- `http-body`
- `service-middleware`
- `async-stream`
- `object-store-buffer`

### 2) `shared-building-block/v0`
Describes the neutral common layer itself.

Fields should include:
- types / traits / error vocabulary
- semantic invariants
- ownership / borrowing / async / blocking posture
- feature flags / optional capabilities
- MSRV and no_std posture
- explicit exclusions
- extension points

This is where the archive's “small common vocabulary” idea lives.
Not the whole framework.

### 3) `adapter-profile/v0`
Describes how a specific crate or framework maps to and from the shared building block.

Fields should include:
- adapter id
- source crate(s) and versions
- supported conversions or wrapper modes
- lossy edges
- allocation / buffering / boxing / pinning costs
- runtime assumptions
- feature-flag requirements
- unsupported cases

This artifact is crucial: most real interop failures happen here.

### 4) `conformance-vector-set/v0`
Golden vectors, edge cases, and invariants for the seam.

Fields should include:
- vector id
- input/state description
- expected behavior
- negative/failure expectations
- transport/runtime/env assumptions
- fixture references

This keeps “compatible” from meaning “works in the happy path demo only.”

### 5) `adoption-profile/v0`
Captures the social/operational posture of the common layer.

Fields should include:
- maintainers / owning org or working group
- release/versioning policy
- semver / MSRV promises
- feature-gating rules
- migration notes
- policy for ecosystem changes and new adopters

This is how the kit stays honest about the politics of blessed building blocks without pretending politics do not exist.

### 6) `seam-readiness-report/v0`
Explains whether a candidate seam is ready.

Fields should include:
- motivation summary
- repeated-friction evidence
- adopter diversity
- unresolved semantic blockers
- language/compiler blockers if any
- recommendation (`promote`, `pilot`, `watch`, `defer`)

This is the artifact that prevents premature pseudo-standardization.

### 7) `interop-check-report/v0`
Records what was actually tested.

Fields should include:
- seam and version ids
- adapter matrix exercised
- vectors run / skipped
- pass/fail/partial status
- lossy or degraded paths encountered
- environment details
- attached logs or raw fixtures

### 8) `commons-pack/v0`
Bundle of the above plus human-facing docs, diagrams, and migration notes.

## CLI shape
`cargo commons` should aim to be a thin adapter/orchestrator.

Potential commands:
- `cargo commons init` — scaffold an interop seam
- `cargo commons readiness` — explain whether a seam is mature enough
- `cargo commons export` — emit current seam/building-block/adapter artifacts
- `cargo commons check` — run vectors across selected adapters
- `cargo commons diff` — compare seam/adapter changes across versions
- `cargo commons pack` — bundle a `commons-pack/v0`

The tool should prefer pointers and attachments over monolithic blobs.

## Initial targets
The first credible version should **not** start from scratch on an unproven seam.
It should start where the ecosystem already shows a pattern:
1. **HTTP request/response/body**
   - `http`
   - `http-body` / `http-body-util`
   - adapters around Hyper, Axum, Tonic, Reqwest, Ureq-style clients where practical
2. **Tower service/layer interoperability**
   - `tower-service`
   - `tower-layer`
   - `tower-http`
   - Axum / Tonic integration proofs
3. **One “not yet ready” candidate seam**
   - likely async-stream-style interop
   - recorded as a seam-readiness case, not prematurely stabilized into a common crate

This is important: the kit should support both **promotion** (a seam is ready) and **deferral** (a seam is not ready yet, and the reasons are now explicit). See [`design/interop-commons-pilot-program.md`](./interop-commons-pilot-program.md) for the ranked rollout, readiness scorecards, and explicit watch/wait seam lane.

## What good adoption looks like
A good v1 does not need dozens of adopters.
It needs a few serious proofs that the artifact family clarifies real interop work.

Success would look like:
- one common seam report explaining why a shared layer exists,
- multiple crates shipping adapter profiles against it,
- conformance vectors catching real regressions,
- one atlas entry pointing to the seam as a stable common vocabulary,
- and migration notes that let a new framework plug in without bespoke archaeology.

## Boundaries with other archive proposals
- **Ecosystem Atlas Kit** recommends stacks; Interop Commons Kit creates the shared building blocks those stacks can rely on.
- **Semantic Context Kit** can help harvest machine-usable facts about candidate ecosystems, but it does not decide what should become a neutral seam.
- **Service / Protocol / Event / Identity / Dataset / Replica / Model / Media / Geospatial Surface Kits** describe domain boundaries; Interop Commons Kit handles lower-level common vocabulary when many stacks inside or across those domains need it.
- **Build Interop Kit** is about workspace/build/plumbing reuse, not runtime/library vocabulary.
- **Schema Contract Kit** is about payload/interface schemas, not neutral shared trait/type seams.
- **Runtime Capability Kit** handles authority and least privilege, not common ecosystem abstractions.

## Failure modes to avoid
- a “universal adapter” crate that secretly chooses one framework's semantics;
- a too-large common layer that blocks experimentation;
- no conformance vectors, leaving compatibility as a social claim;
- versioning without explicit stewardship;
- using this kit as a soft-power mechanism to bless favorites without technical justification;
- or letting Atlas-style recommendation pressure silently force a seam that is not actually ready.
