---
id: P-0484
title: Toolchain & Target Support Contract Kit — rust-toolchain intent, component/target receipts, and support-drift bundles
status: idea
domains: [rustup, cargo, toolchains, cross-compilation, ci, docs, devtools, release]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
  - https://rust-lang.github.io/rustup/overrides.html
  - https://rust-lang.github.io/rustup/concepts/profiles.html
  - https://rust-lang.github.io/rustup/concepts/components.html
  - https://rust-lang.github.io/rustup/cross-compilation.html
  - https://doc.rust-lang.org/cargo/reference/rust-version.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
  - https://docs.rs/about/metadata
  - https://docs.rs/about/builds
  - https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
  - https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
  - https://blog.rust-lang.org/2025/05/26/demoting-i686-pc-windows-gnu/
  - https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
  - https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
---

# Problem

Rust teams increasingly have enough substrate to describe *pieces* of their support story, but still lack one boring artifact that says what they actually support.

Today that story is scattered across:

- `rust-toolchain.toml` and rustup override rules,
- selected profiles/components/targets,
- linker or cross-compilation setup,
- docs.rs target and feature metadata,
- CI matrices,
- and tribal knowledge about which targets are “supported”, “best effort”, “docs only”, or “compile only”.

That is enough to make support *possible* but not enough to make support *reviewable*.

The support surface also moved recently in ways that make silent drift more likely.
Fresh 2026 ecosystem guidance also makes the missing layer sharper: the March 2026 Rust challenges work explicitly calls out cross-compilation friction and `no_std` gaps, while the January 2026 safety-critical post effectively asks for a target-focused readiness checklist that tells another team which targets exist, which are `no_std` only, what the last known tested environment was, and what blockers still remain.

The support surface also moved recently in ways that make silent drift more likely. Cargo’s own 2026 build-dir-layout-v2 call-for-testing now says many projects rely on unspecified build-dir details due to missing features, which means even artifact discovery can be part of the support contract. Meanwhile, recent target demotions show that official target support can narrow while downloads still continue, so maintainers need a clearer way to restate their own project support class.

The support surface also moved recently in ways that make silent drift more likely:

- docs.rs changed its default target set in October 2025, replacing `x86_64-apple-darwin` with `aarch64-apple-darwin` and `i686-unknown-linux-gnu` with `aarch64-unknown-linux-gnu`,
- the docs.rs metadata page now spells out a default-target / targets / additional-targets matrix that many crate owners still do not make explicit,
- rustup 1.29 added official Solaris hosts and a rust-analyzer PATH fallback, which is a reminder that “Rust environment” is broader than one blessed workstation shape,
- and rustup’s own docs make clear that `path` toolchains ignore `components`, `targets`, and `profile`, while cross-compilation usually still needs non-rustup linker/toolchain setup.

Maintainers still end up asking questions like:

- which toolchain does this repo actually require,
- which extra components or targets are mandatory versus optional,
- does our current CI/docs.rs posture match the promise we think we are making,
- did a PR quietly widen or narrow our support surface,
- what changed because docs.rs default targets moved,
- and what should a contributor or downstream integrator install before they hit mysterious failures?

Rustup documents how overrides are chosen, how toolchain files can request components/targets/profile, how profiles affect installation, and how cross-compilation requires target stdlibs plus often external linkers.
Docs.rs also documents target/feature/rustdoc metadata and build behavior.
So the gap is no longer “Rust cannot express toolchains or targets.”

The sharper missing crate is a **toolchain and target support contract kit**: a read-first, diffable workflow that turns toolchain intent, override lineage, component availability, exercise scope, target posture, docs posture, and CI evidence into one compact support artifact.


## 2026-03-22 implementation refresh — imported authority, public docs surface, and portable bundles

The current official substrate now makes three more receiver-facing review objects worth promoting.

### 1. Upstream facts need an explicit import receipt

The strongest support-shaping facts often come from **upstream authority** rather than the project itself:

- Rust-project target tiers and target-status announcements,
- rustup-supported host availability,
- docs.rs default-target behavior and metadata rules,
- Cargo path/config rules for `target-dir` and `build-dir`.

Those facts matter, but they do **not** automatically prove the project’s own support class.
A buildable crate should therefore promote **`upstream-support-authority.import.json`** into first-class status so another engineer can see what was imported, what question it supports, and what it still does not prove.

### 2. Public docs surface is not the same thing as real support class

Current docs.rs docs now make explicit:

- the effective default target,
- explicit versus implicit target lists,
- hosted sandbox/resource limits,
- and the fact that service defaults can change over time.

That means the crate should promote **`public-docs-surface.receipt.json`** into first-class status.
A support bundle should tell another person not just that docs.rs exists, but what target/default posture was actually exposed and whether that surface came from explicit metadata or inherited service defaults.

### 3. The lane wants one compact portable bundle manifest

The repo already had many useful receipts, but it still lacked one compact inventory saying which toolchain/target support artifacts belong together for review.
A worthy `0.1` should therefore export **`toolchain-support-bundle.manifest.json`** so other tools, release reviewers, and downstream integrators do not have to guess what a complete handoff contains.

# What it provides

Working build sketch: `meta/toolchain-target-support-product-plan-2026-03-17.md`.

- `toolchain-support.toml` — declares intended toolchain channel/version policy, required/optional components, target classes, docs posture, and manual-review zones.
- `toolchain-intent.snapshot.json` — normalized view of `rust-toolchain.toml`, override facts, requested profile/components/targets, and related workspace support declarations.
- `toolchain-environment.receipt.json` — exact observed local/CI environment: active toolchain, installed components, installed targets, host triple, linker notes, and docs.rs-facing metadata.
- `support-surface.report.json` — classifies support axes such as `fully_supported`, `ci_verified`, `docs_default_surface`, `docs_only`, `compile_only`, `nightly_only`, `manual_setup_required`, and `unknown`.
- `target-readiness.report.json` — target-focused readiness checklist capturing Rust-project tier, project support class, `std` / `no_std` posture, last known tested environment, key blockers, and real exercise scope for one target lane.
- `support-drift.diff.json` — compares two snapshots/receipts and classifies widened, tightened, or ambiguous support changes.
- `support-class.policy.json` — defines what support classes mean and what minimum evidence they expect.
- `support-evidence.report.json` — traces each support claim back to declaration, local observation, docs.rs metadata, CI import, or manual note.
- `external-prerequisite.manifest.json` — linkers, runners, SDKs, env vars, board/device requirements, and manual setup classes per target or host lane.
- `override-lineage.receipt.json` — records which rustup selection mechanism actually won (`+toolchain`, `RUSTUP_TOOLCHAIN`, directory override, toolchain file, or default) and which project requests were shadowed or ignored.
- `component-availability.report.json` — records requested versus effective components/toolchain state, including nightly fallback or profile-driven drift when a requested component is unavailable.
- `exercise-scope.report.json` — records which scopes are genuinely covered for a lane (`compile`, `docs`, `run`, `test`, `bench`, `host_build_script`, `host_proc_macro`) instead of flattening everything into one vague support class.
- `artifact-route.receipt.json` — records how release/test/docs/support workflows actually discover relevant artifacts, whether through stable Cargo interfaces, docs.rs metadata, CI artifact names, `target/` conventions, or brittle build-dir internals.
- `host-target-topology.receipt.json` — records which phases compile or execute on the host, which produce target artifacts, and which still depend on runners, emulators, devices, or hosted services.
- `upstream-support-authority.import.json` — records imported Rust-project / rustup / docs.rs / Cargo facts that shape the support story without pretending they are project-local promises.
- `public-docs-surface.receipt.json` — records the effective docs.rs public target/default posture, whether defaults were implicit, and which hosted limits materially shaped the surface.
- `toolchain-support-bundle.manifest.json` — inventories the portable support handoff so authority imports, local policy, docs posture, prerequisites, route/topology receipts, and readiness reports stay joined but not flattened.
- `bootstrap-hints.md` — contributor/downstream-facing install and setup hints derived from the contract.
- `cargo support-contract capture` — emit one normalized support bundle.
- `cargo support-contract diff <old> <new>` — compare support promises across branches or releases.
- `cargo support-contract doctor` — flag suspicious situations such as missing requested targets, profile drift, docs.rs mismatch, path-toolchain overrides that nullify requested components, or nightly-only claims without explicit marking.
- `cargo support-contract import-authority` — emit imported-upstream authority receipts for target-tier, rustup-host, docs.rs-default, and Cargo path/config facts.
- `cargo support-contract docs-surface` — emit the public docs-surface receipt without pretending it proves runtime support.
- `*.supportbundle.zip` — portable support artifact for contributors, CI owners, release reviewers, or downstream packagers.

# What the crate should provide other people

1. **One compact support contract** instead of a scavenger hunt across toolchain files, docs.rs metadata, linker notes, and CI YAML.
2. **A reusable vocabulary** for target posture: not every target is equally supported, and that nuance should be explicit.
3. **Override-lineage truth** so contributors can see whether the repository pin actually won or whether `+toolchain`, `RUSTUP_TOOLCHAIN`, or a directory override silently changed the effective toolchain.
4. **Component-availability honesty** so maintainers do not confuse requested components with actually available ones, especially on nightly or unusual host lanes.
5. **Exercise-scope truth** so `compile`, `docs`, `run`, `test`, `bench`, and host-built helper scopes stay separate instead of collapsing into one fake “supported target” claim.
6. **A drift detector** so patches do not silently drop components, targets, docs defaults, or contributor requirements.
7. **A contributor handoff artifact** that says what to install, what is optional, and what still needs external linker/manual setup.
8. **A release-review receipt** for whether the repository’s declared support still matches reality.
9. **A target-readiness checklist** so a downstream team can distinguish “Rust target exists” from “this project has a credible lane for that target.”
10. **Artifact-discovery honesty** so release/test/docs workflows stop depending on silent `target/` or build-dir folklore.
11. **Host-target-topology honesty** so build-script/proc-macro success is not mistaken for full target-lane execution.

# Persona / who it’s for

- maintainers of libraries and tools with nontrivial target matrices
- app teams shipping across desktop/mobile/server/embedded targets
- CI owners maintaining cross-target workflows
- downstream packagers and enterprise integrators
- support engineers triaging “works on CI but not locally” issues

# Users & user stories

- **Library maintainer**: “Show me whether we silently dropped a target or component from our promised support surface.”
- **CI owner**: “Compare the intended target/toolchain contract with what CI actually exercised.”
- **Contributor**: “Tell me which targets and components I must install before running the project.”
- **Downstream integrator**: “Give me one artifact that says whether this crate is stable-only, which targets are real, which ones are docs.rs-only, and where manual linker setup is still required.”

# Prior art (and why it’s insufficient)

- rustup already supports override rules and project toolchain files.
- rustup profiles/components/targets already capture parts of installation intent.
- docs.rs metadata already lets crates request features, targets, rustdoc args, and more.
- docs.rs now documents both its default target list and its current build behavior more clearly than before.
- the target-tier policy documents what good target support ought to explain.
- older archive ideas like MSRV workspace work, linker-lane diagnosis, and docs.rs parity cover adjacent but different seams.

What remains missing is the **joined support artifact** above these pieces: the thing that says “this is the toolchain/target/docs contract we mean to support, this is what was actually observed, and this is what drifted.”

# Design goals

1. **Support-contract-first** — optimize for human review and contributor handoff.
2. **Joined, not magical** — join rustup, docs.rs, linker/manual-setup, and CI facts without pretending to infer everything perfectly.
3. **Target-posture explicitness** — distinguish `supported`, `docs_default_surface`, `docs_only`, `compile_only`, and `manual_setup_required` states.
4. **Environment honesty** — preserve exact host/toolchain/component/target observations.
5. **Diffability** — support changes must be reviewable across time.
6. **Evidence honesty** — a project support class should say whether it is declared, locally observed, CI-verified, docs-only, or still manual-review territory.
7. **Override-lineage honesty** — requested toolchains and effective toolchains must not be conflated.
8. **Scope honesty** — compile, docs, run, test, bench, and host-helper coverage must remain separately reviewable.
9. **External-prerequisite honesty** — non-Rust requirements like linkers, runners, SDKs, and device access must be explicit instead of leaking out as mysterious failures.

# MVP surface

- Minimal types: `SupportPolicy`, `ToolchainIntentSnapshot`, `ToolchainEnvironmentReceipt`, `OverrideLineageReceipt`, `ComponentAvailabilityReport`, `ExerciseScopeReport`, `SupportAxis`, `SupportSurfaceReport`, `SupportDrift`, `SupportBundle`
- Minimal functions:
  - `capture_toolchain_intent()`
  - `capture_environment_receipt()`
  - `capture_override_lineage()`
  - `compute_component_availability()`
  - `compute_exercise_scope()`
  - `compute_support_surface()`
  - `diff_support_bundles()`
  - `generate_bootstrap_hints()`
- Feature flags:
  - `rustup`
  - `cargo-metadata`
  - `docsrs`
  - `serde`
  - `markdown`

# Compatibility story

- Works on read-only repository state first; it should not require changing build pipelines.
- The contract must preserve which facts came from `rust-toolchain.toml`, rustup observation, docs.rs metadata, CI declarations, linker config, or manual policy files.
- Missing or ambiguous target support should remain explicit rather than guessed away.
- The crate should remain useful even if Rustup/Cargo evolve, because maintainers still need one boring support artifact.

# Conformance & fixtures

- One fixture with a `minimal` rustup profile in CI but contributor docs that assume `rustfmt` and `clippy`.
- One fixture where docs.rs default-target drift after the October 2025 target-list change silently changes the project’s public docs posture.
- One fixture with a `path` toolchain where requested `components` and `targets` are intentionally ignored.
- One fixture where a target remains `compile_only` because the Rust stdlib exists but the external linker is still missing.
- One fixture where a new official rustup host exists but the project does **not** yet claim that host as supported.
- One fixture with a virtual workspace where `resolver = "3"` and mixed `rust-version` policies make the top-level support story easy to misread.
- One fixture where a cross target has a runner requirement for `cargo test`/`cargo run`, so “builds” does not imply “testable” or “runnable”.
- One fixture where `RUSTUP_TOOLCHAIN` or `cargo +toolchain` masks the repository pin and the support bundle must explain why.
- One fixture where a requested nightly component is missing, rustup falls back to an older nightly, and the effective toolchain subtly diverges from the requested channel.
- One fixture where `--target` or `build.target` means target-specific flags apply only to the target while host-built build scripts or proc macros remain on a different exercise lane.
- Goldens for `missing_target`, `docsrs_default_drift`, `path_toolchain_ignores_profile`, `workspace_rust_version_policy_split`, `runner_required_for_tests`, `override_masks_repo_pin`, `nightly_component_fallback`, `host_helper_scope_split`, `support_tightened`, and `manual_setup_required`.

# Path to boring stability

- Stabilize the support vocabulary before adding CI mutators or installers.
- Start with capture/diff/doctor rather than trying to automate every bootstrap step.
- Keep target-posture classes small and reviewer-friendly.
- Treat ambiguous cases as first-class output, not failure.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that read project toolchain/target/docs support signals, normalize them into one support bundle, compare two revisions, and emit contributor/reviewer-friendly drift reports.

# De-risk plan

1. Start with read-only capture from toolchain files, rustup observations, docs.rs metadata, and optional linker notes.
2. Keep the initial support-state vocabulary coarse.
3. Validate on one desktop/server workspace, one cross-target crate, and one docs.rs-sensitive library.
4. Add deeper CI adapters only after the bundle schema proves useful.

# Non-goals

- Not a replacement for rustup, docs.rs, or CI systems.
- Not an installer or cross-compilation linker manager.
- Not a docs.rs parity emulator; that belongs to a neighboring crate.
- Not a full release-compatibility gate for runtime behavior.

# Architecture & API sketch

```rust
pub enum SupportState {
    FullySupported,
    CiVerified,
    DocsDefaultSurface,
    DocsOnly,
    CompileOnly,
    NightlyOnly,
    ManualSetupRequired,
    Unknown,
}

pub fn capture_toolchain_intent(root: &Path) -> Result<ToolchainIntentSnapshot>;
pub fn capture_environment_receipt(root: &Path) -> Result<ToolchainEnvironmentReceipt>;
pub fn compute_support_surface(intent: &ToolchainIntentSnapshot, env: &ToolchainEnvironmentReceipt) -> SupportSurfaceReport;
pub fn capture_artifact_routes(root: &Path) -> Result<Vec<ArtifactRouteReceipt>>;
pub fn capture_host_target_topology(root: &Path) -> Result<HostTargetTopologyReceipt>;
pub fn diff_support_bundles(old: &SupportBundle, new: &SupportBundle) -> SupportDrift;
```

Bundle draft: `toolchain-support.toml`, `toolchain-intent.snapshot.json`, `toolchain-environment.receipt.json`, `support-surface.report.json`, `target-readiness.report.json`, `artifact-route.receipt.json`, `host-target-topology.receipt.json`, `support-drift.diff.json`, `bootstrap-hints.md`, `notes.md`.

# Security / safety model

- Treat repository metadata and environment observations as untrusted input.
- Support redaction of local paths, internal target aliases, and private CI hostnames.
- Preserve what was observed locally versus declared in policy.
- Never imply that installed targets alone prove end-to-end portability.

# Maintenance & governance plan

- Track rustup override/toolchain-file evolution, docs.rs metadata/build behavior changes, and target-policy expectations.
- Keep the support vocabulary small and versioned.
- Maintain fixtures covering stable-only, nightly-only, docs-default-surface, docs-only, and manual-linker cases.
- Publish guidance for when support drift should block release versus require manual review.

# Milestones

## 0.1
- toolchain-file and rustup observation capture
- support bundle export
- support drift diff

## 0.2
- docs.rs alignment report
- bootstrap hints
- support-state policy gates

## 1.0
- stable schema
- CI adapter helpers
- curated multi-target fixture corpus

# Open questions

- What is the smallest durable vocabulary for support posture across libraries and apps?
- How much CI evidence should be imported directly versus referenced externally?
- When should “official rustup host exists” be treated as weaker than “docs/test/CI verified”? 
- Should docs.rs default-target changes automatically trigger support-review warnings, or only when the project left the target set implicit?

# Sources

- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rustup/concepts/profiles.html
- https://rust-lang.github.io/rustup/concepts/components.html
- https://rust-lang.github.io/rustup/cross-compilation.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
- https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
