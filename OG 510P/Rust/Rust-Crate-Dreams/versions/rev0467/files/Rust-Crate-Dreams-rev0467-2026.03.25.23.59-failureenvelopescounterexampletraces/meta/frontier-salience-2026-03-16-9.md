# Frontier salience scan — 2026-03-16 (delegated build-script units and artifact-bridge adoption)

This pass added one new top-level proposal and refreshed one older one.
The stronger move was to sharpen a gap between **delegated build-script planning** and **artifact-dependency bridge adoption**.

The two focal crates are:

- **P-0508 Cargo Build Script Delegation Kit**
- **P-0495 Cargo Artifact Dependency Adoption Kit**

## Main judgment

The newest official Rust/Cargo signals now point to a more concrete build-time frontier.

The important signals are:

- GSoC 2025 explicitly says delegation to reusable build-script packages depends on multiple build scripts, deterministic order, parameter passing via manifest metadata, and then artifact dependencies.
- Cargo unstable docs already expose metabuild, multiple build scripts, and any build script metadata.
- Stable build-script docs already describe metadata passing, `links` overrides, order-sensitive outputs, and persistent `OUT_DIR` behavior.
- Cargo 1.93 discusses a build-script artifact directive as a possible bridge/polyfill lane and names real open questions around collisions, copy semantics, and connection to artifact dependencies.

Together, that suggests the ecosystem is missing two boring but useful crate layers:

1. a **delegation contract / receipt / fallback** crate for ordered reusable build-script units, and
2. an **artifact bridge adoption** crate for target-aware env bindings, renamed multi-target cases, and stable-vs-nightly bridge posture.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0508 Cargo Build Script Delegation Kit**
4. **P-0495 Cargo Artifact Dependency Adoption Kit**
5. **P-0244 SemVer API Diff Evidence Kit**
6. **P-0478 Cargo Future-Incompat Triage Kit**
7. **P-0507 Cargo Fix Campaign Kit**
8. **P-0432 Cargo Plumbing Interop Kit**
9. **P-0431 Public Dependency Boundary Kit**
10. **P-0477 Cargo Publish Receipt Join Kit**
11. **P-0175 Trusted Publishing Tooling Kit**
12. **P-0484 Toolchain & Target Support Contract Kit**

## Why P-0508 rose now

Earlier archive work already had diagnostics, testing, output handoff, and host/target scope around build scripts.
What it did not have was the more strategic “how do we actually centralize and reuse build-time logic honestly?” layer.

The official delegation direction makes that a real seam:

- named units,
- deterministic order,
- manifest-supplied parameters,
- artifact bridge posture,
- and fallback plans where stable Cargo is not yet enough.

That is a real crate opportunity, not just a note in the docs.

## Why P-0495 rose again now

Artifact dependencies looked interesting before, but the fresh delegation story gives them a stronger role.
They are not just for consuming another package’s helper binary.
They are now part of the likely bridge between ordinary packages and reusable external build helpers.

That makes target-matrix/env-var/fallback receipts more strategically important than a narrow unstable-feature demo.

## What this pass did not do

It did **not** collapse:

- build-script UX,
- build-script tests,
- native output exports,
- artifact dependency adoption,
- delegated reusable units,
- and host/target execution scope

into one giant “modern build scripts” proposal.

That restraint improved the archive.

## Sources

- GSoC 2025 results: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 development-cycle update: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
