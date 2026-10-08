# Gap: target support envelopes and runtime baselines

Rust has serious platform machinery: target tiers, host-tool distinctions, docs.rs target metadata, cross-compilation helpers, `build-std`, target-aware dependency tables, and active Cargo discussion about `supported-targets`.
What it still lacks is a **shared support contract with reviewable evidence**.

Right now a project cannot cleanly say, in one portable artifact:
- which **development hosts** it supports natively,
- which **source-build targets** it claims to compile for,
- which **released artifacts** it ships and stands behind,
- which **docs targets** are representative versus convenience-only,
- which **runtime floors** the claim depends on (minimum OS version, kernel, libc, SDK, ABI, CPU-feature assumptions),
- what level of evidence exists for each lane (`compile`, `test`, `package`, `run-smoke`, field validation, manual review),
- and how that support contract changed between releases.

That missing layer matters because support truth is currently scattered across:
- README prose,
- CI YAML,
- `target.*.dependencies` tables,
- docs.rs metadata,
- release notes,
- cross-tool defaults,
- and maintainer memory about what “supported on Linux/macOS/Windows/Wasm/embedded” actually means.

Sources:
- https://doc.rust-lang.org/beta/rustc/platform-support.html
- https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://github.com/rust-lang/rfcs/pull/3759
- https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- https://embarkstudios.github.io/cargo-deny/checks/cfg.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://doc.rust-lang.org/rustc/targets/custom.html
- https://github.com/cross-rs/cross
- https://github.com/rust-cross/cargo-zigbuild
- https://github.com/rust-cross/cargo-xwin

## The current seam is still awkward
Rust already has real pieces of the story:
- the rustc platform-support page distinguishes plain build targets from targets with **host tools**, which is already a hint that “can compile for” and “can develop on” are different claims;
- the target-tier policy makes clear that target levels carry different guarantees and that host-tool support is a separate approval surface;
- docs.rs lets authors configure `default-target`, `targets`, and `additional-targets`, and changed its default target set in October 2025 to follow platform reality;
- Cargo is actively discussing `supported-targets` so packages can declare where they are meant to build;
- cargo-deny already asks users to name the targets that actually matter for policy checks;
- `cross`, `cargo-zigbuild`, and `cargo-xwin` already provide serious provisioning and execution lanes;
- `build-std` and custom targets prove that “source-build support” can differ sharply from “Rust ships a prebuilt stdlib for this target” or “we ship binaries for this target”.

But those pieces do not yet compose into a reusable contract:
- rustc target tiers describe **Rust-project guarantees**, not a crate’s concrete support promise;
- docs.rs target choices shape user expectations, but do not prove anything about runtime floors or test coverage;
- `supported-targets` is about manifest-level declaration, not a portable evidence/report bundle;
- cross-compilation wrappers help produce binaries, but do not standardize how projects record glibc floors, SDK floors, minimum OS versions, or field-validation posture;
- and `build-std` / custom-target usage means some projects have meaningful source-build stories even when their released-artifact story is narrower.

The result is recurring ambiguity:
- does “supports Windows” mean *building from Linux to MSVC is supported*, or only *native development on Windows*, or only *released binaries*?
- does “supports Linux” mean glibc 2.17+, some newer floor, musl, or “whatever the maintainer’s CI image happened to have”?
- are docs.rs targets representative of supported runtime surfaces, or merely useful docs landing pages?
- which targets were compiled, which were tested, which were smoke-run, and which are only aspirational?
- when Rust’s own target tiers change, or docs.rs changes defaults, where is that drift made reviewable at the crate/release level?

Sources:
- https://doc.rust-lang.org/beta/rustc/platform-support.html
- https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://github.com/rust-lang/rfcs/pull/3759
- https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- https://embarkstudios.github.io/cargo-deny/checks/cfg.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://doc.rust-lang.org/rustc/targets/custom.html
- https://github.com/cross-rs/cross
- https://github.com/rust-cross/cargo-zigbuild
- https://github.com/rust-cross/cargo-xwin

## Why this matters
This is bigger than “cross compilation is annoying.”
It affects:
1. **crate selection and trust** — users need to know what is supported *in what sense*, not just what happened to compile once;
2. **workspace ergonomics** — mixed workspaces often contain host-only tools, Wasm crates, firmware crates, and desktop/server crates side by side;
3. **release engineering** — released binaries often carry hidden libc/OS/SDK assumptions that are more user-visible than the nominal target triple;
4. **docs and discoverability** — docs.rs landing targets and built-target lists are ecosystem-facing support signals;
5. **policy and dependency review** — target-aware policy tools already need an explicit target set to avoid lying about irrelevant dependencies;
6. **source-build / artifact-build divergence** — `build-std`, custom targets, and provisioned toolchains create real support lanes that are not captured by a flat target list;
7. **support drift over time** — target tiers, docs.rs defaults, and release artifacts change, but projects rarely publish structured support diffs.

Sources:
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://embarkstudios.github.io/cargo-deny/checks/cfg.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://doc.rust-lang.org/rustc/targets/custom.html
- https://doc.rust-lang.org/beta/releases.html

## What “good” looks like
A worthy contribution here is **not** another cross-build wrapper, badge, or hosted compatibility matrix.
It is a shared support-contract substrate:
- one `support-envelope/v0` for the declared support contract,
- one `runtime-floor-report/v0` for explicit OS/kernel/libc/SDK/ABI/CPU-feature floors,
- one `support-observation-report/v0` for what was actually checked and by which lane/toolchain,
- one `support-diff-report/v0` for reviewable support drift,
- one optional `support-waiver/v0` for temporary exceptions,
- and one `support-pack/v0` bundle for CI, docs, release, policy, atlas/discoverability, and archaeology.

The winning design must preserve a few non-negotiable distinctions:
- **development host support** is not the same thing as **source-build target support**,
- **source-build support** is not the same thing as **released-artifact support**,
- **docs target coverage** is not the same thing as **runtime support**,
- **declared support** is not the same thing as **validated support**,
- and a **target triple** is not a sufficient substitute for **runtime floors**.

That would let rustc target tiers, docs.rs metadata, Cargo manifest declarations, CI matrices, toolchain wrappers, and runtime probes participate in one reviewable story instead of remaining disconnected rituals.
