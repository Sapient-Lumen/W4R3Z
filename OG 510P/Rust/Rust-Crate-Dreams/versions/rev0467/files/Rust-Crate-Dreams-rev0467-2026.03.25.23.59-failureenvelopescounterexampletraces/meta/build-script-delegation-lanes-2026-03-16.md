# Build-script delegation lanes — 2026-03-16

This note exists to stop the archive from collapsing several adjacent build-time ideas into one vague “better build scripts crate”.

Recent official Rust/Cargo signals sharpen the boundary:

- the 2025 GSoC results say build-script delegation to reusable packages depends on **multiple build scripts**, deterministic order, metadata parameters, and then **artifact dependencies**,
- Cargo’s unstable docs already expose **metabuild**, **multiple build scripts**, and **any build script metadata**,
- stable build-script docs already define **metadata passing**, **`links` overrides**, and order-sensitive emitted instructions,
- and Cargo 1.93 design notes discuss a concrete **artifact build-script directive** as a bridge/polyfill lane.

That means the archive now has multiple real lanes and should keep them separate.

## Lane 1: build-script diagnostics and support UX

**Proposal:** `P-0046 buildscript-ux-kit`

This crate should own:

- structured warnings/errors,
- hidden-warning surfacing,
- concise summaries,
- and policy gates for noisy or failing build scripts.

The central question is:

> “What happened during this build script run, what was hidden, and what should I do next?”

It should not absorb delegation planning or artifact-bridge semantics.

## Lane 2: build-script fixture testing

**Proposal:** `P-0059 buildscript-testkit`

This crate should own:

- hermetic execution,
- mocked discovery tools,
- normalized directive outputs,
- and golden tests for build behavior.

The central question is:

> “Does this build-time logic keep emitting the same contract under controlled inputs?”

It is about fixture confidence, not reusable delegate-package planning.

## Lane 3: native output/export handoff

**Proposal:** `P-0050 build-interop-kit`

This crate should own:

- exported native headers/libraries/tool paths,
- sidecar manifests for downstream consumers,
- and how a dependency discovers those outputs.

The central question is:

> “What build outputs are meant for downstream consumption?”

This is different from build-script delegation even if the delegate eventually produces those outputs.

## Lane 4: artifact-dependency adoption and bridge posture

**Proposal:** `P-0495 Cargo Artifact Dependency Adoption Kit`

This crate should own:

- target-aware artifact contracts,
- env-var receipts,
- multi-target rename patterns,
- stable fallback posture,
- and the bridge seam where a reusable helper is consumed through artifact dependencies.

The central question is:

> “What artifact contract did we depend on, what bindings appeared, and what fallback or bridge posture does that imply?”

It should not become the universal plan/doctor crate for delegated build-script units.

## Lane 5: delegated build-script units and parameter contracts

**Proposal:** `P-0508 Cargo Build Script Delegation Kit`

This crate should own:

- named build-script units,
- deterministic order,
- parameter sources,
- metadata/artifact bridge diagnosis,
- and stable-vs-nightly fallback plans for reusable build helpers.

The central question is:

> “Can this package’s build logic be expressed as ordered, reusable delegate units, and what still blocks or complicates that?”

It should not swallow diagnostics, hermetic tests, or every artifact-handoff concern.

## Lane 6: host/target execution scope

**Proposal:** `P-0505 Cargo Host/Target Scope Contract Kit`

This crate should own:

- host-only versus target-only config scope,
- `host.*` / `target.*` behavior,
- host runners and mixed-build diagnosis,
- and same-triple-but-different-lane surprises.

The central question is:

> “Which config and execution rules applied to host build targets like build scripts and proc macros?”

This is adjacent to delegation but still a separate diagnosis lane.

## Working rule

When touching build-time Cargo ideas, future revisions must say explicitly whether the crate owns:

1. **diagnostics / support UX**,
2. **fixture testing**,
3. **native output/export handoff**,
4. **artifact-dependency adoption / bridge posture**,
5. **delegated build-script units / parameter contracts**,
6. or **host/target execution scope**.

Do not let the archive silently collapse:

- reusable delegate packages,
- metadata parameter flow,
- artifact-dependency bridge posture,
- build-script testing,
- build-script support bundles,
- and host/target execution scope

into one fake “build script modernization” result.

## Sources

- GSoC 2025 results: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 development-cycle update: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
