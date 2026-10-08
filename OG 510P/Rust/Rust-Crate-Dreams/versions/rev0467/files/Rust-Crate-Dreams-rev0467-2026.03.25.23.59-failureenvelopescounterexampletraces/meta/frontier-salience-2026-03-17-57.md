# Frontier salience snapshot — 2026-03-17 (57)

This pass did **not** promote a new lane.
It sharpened an already-strong cross-cutting proposal:

- **P-0484 Toolchain & Target Support Contract Kit** — because the archive still needed a more reviewable answer to the question “what toolchain and target support did this project actually exercise, and why should I believe that support story?”

## Main judgment

The next worthy move here was **not** another installer wrapper, another linker doctor, another CI matrix dashboard, or another docs.rs preflight helper.
Those already cover important substrate slices.

The sharper missing layer is the **whole-project support contract** above them, especially once three more facts are separated cleanly:

- explicit **override-lineage receipts**,
- explicit **component-availability reports**,
- explicit **exercise-scope reports**,
- plus the already-added support-class, evidence, prerequisite, docs-posture, and drift artifacts.

That move is better grounded now because:

- rustup override precedence is explicit, and proximity rules can let a nearby toolchain file beat a farther directory override while `RUSTUP_TOOLCHAIN` or `cargo +toolchain` still win overall;
- `path` toolchains ignore `components`, `targets`, and `profile`;
- rustup profiles are materially different, and the `complete` profile should never be used because it will almost always fail;
- nightly toolchains may be published with missing non-default components, and rustup may automatically select an older nightly that has the required components;
- Cargo’s config model separates `build.target`, target-specific linker/runner configuration, and the host-vs-target behavior of `rustflags` when `--target` is used;
- Cargo target kinds mean `compile`, `run`, `test`, `bench`, and docs are not one flat lane;
- docs.rs metadata and sandbox policy shape the public docs surface but do not prove runtime or test support;
- Rust’s target-tier policy explicitly expects documentation about how to build and run tests for a target, along with baseline expectations;
- and the current survey plus vision work still support the broader thesis that users need better supportive interfaces from crates and projects.

So the gap is no longer “Rust cannot express targets or toolchains”.
The gap is that maintainers still rarely publish a **reviewable override-lineage / component-availability / exercise-scope contract** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — stronger now because override lineage, component availability, and exercise scope make “real machines, real targets” support more falsifiable.
4. **P-0451 Cfg Availability Ledger Kit** — still the sharpest item-level conditional-support truth lane.
5. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0524 Crate Example Surface Pack Kit** — still the strongest first-success support lane.
8. **P-0525 Crate Diagnosis Surface Pack Kit** — still the strongest steady-state troubleshooting lane.
9. **P-0522 Crate Persistence Surface Pack Kit** — still one of the strongest “durable bytes / recovery truth” lanes.
10. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.

## Why this won over adjacent candidates right now

- It beat **more lifecycle or shutdown follow-ons** because projects still need one boring contract for which machines, channels, components, and target scopes they actually support before any crate-level lifecycle promise matters.
- It beat **more docs.rs parity follow-ons** because hosted docs posture is only one slice of the broader support surface.
- It beat **more linker-only work** because a linker or runner prerequisite is just one piece of the whole-project support story.
- It beat **more MSRV-only or CI-only ideas** because toolchain/target support still needs a joined artifact above `rust-version`, rustup state, docs posture, and imported CI facts.

## What changed in the archive

Added:
- `meta/frontier-salience-2026-03-17-57.md`
- `fixtures/toolchain-target-support-contract-kit/override-lineage.receipt.schema.json`
- `fixtures/toolchain-target-support-contract-kit/component-availability.report.schema.json`
- `fixtures/toolchain-target-support-contract-kit/exercise-scope.report.schema.json`
- `fixtures/toolchain-target-support-contract-kit/scenarios/env_override_masks_repo_pin/`
- `fixtures/toolchain-target-support-contract-kit/scenarios/nightly_component_fallback_changes_effective_channel/`
- `fixtures/toolchain-target-support-contract-kit/scenarios/explicit_target_build_splits_host_helper_scope/`
- `entries/2026-03-17-237.md`

Updated:
- `proposals/toolchain-target-support-contract-kit.md`
- `meta/toolchain-target-support-product-plan-2026-03-17.md`
- `fixtures/toolchain-target-support-contract-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- the repository’s requested toolchain,
- the contributor’s effective selector,
- the currently installed components,
- the effective nightly after fallback,
- target compile success,
- docs.rs visibility,
- runner-backed testability,
- and host-helper scope behavior

into one fake “supported target” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rustup/concepts/profiles.html
- https://rust-lang.github.io/rustup/concepts/channels.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
