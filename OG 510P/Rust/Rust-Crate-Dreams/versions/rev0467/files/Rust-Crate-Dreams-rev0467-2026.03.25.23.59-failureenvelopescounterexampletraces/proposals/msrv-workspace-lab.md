---
id: P-0036
title: MSRV Workspace Lab — policy-activation receipts, command-family floor reports, and lockfile-authoring truth for mixed workspaces
status: idea
domains: [cargo, msrv, workspace, ci, devtools, libraries]
last_reviewed: 2026-03-22
evidence:
  - https://doc.rust-lang.org/cargo/reference/rust-version.html
  - https://doc.rust-lang.org/cargo/reference/resolver.html
  - https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://doc.rust-lang.org/cargo/faq.html
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  - https://github.com/rust-lang/cargo/issues/16597
  - https://github.com/rust-lang/cargo/issues/14414
  - https://docs.rs/crate/cargo-msrv/latest/source/
  - https://github.com/foresterre/cargo-msrv/blob/main/CHANGELOG.md
---

# Problem

Rust now has **more** MSRV substrate than it did a year ago, but that makes the receiver-facing gap sharper instead of smaller.

Cargo has a first-class `rust-version` field, multiple-policy guidance for workspaces, an MSRV-aware resolver mode, an Edition-2024 default that implies resolver v3, and fresh lockfile behavior tied to Rust-version compatibility.
At the same time, the live ecosystem still keeps rediscovering that “our MSRV is X” can hide several different truths:

- whether the repo’s **declared support policy** is one number or several split promises,
- whether the intended resolver policy is **actually active** for the workspace root,
- whether `build`, `metadata`, `doc`, `update`, or `package` succeed at the same floor,
- whether a mixed workspace’s older member drags dependency choices for a newer one,
- and whether the **lockfile authoring path** quietly needs a newer Cargo/Rust than the pinned build lane.

That means the worthy crate is **not** just another binary-search wrapper over old toolchains.
The missing crate is a **policy + observation + activation + command-family + lockfile-authoring contract** for MSRV work in real Cargo workspaces.

# Why this moved now

## 1. Cargo’s own MSRV docs now explicitly frame support as policy, not just one number

The Cargo Book recommends choosing a policy for what Rust versions a package supports and when that policy changes.
It also explicitly says Cargo allows multiple policies within one workspace, warns that shared dependencies may be forced down to the lowest common versions, and says `fallback` can let one package’s Rust version affect dependency versions selected for another package with a different Rust version.

## 2. Resolver v3 made policy activation easier to assume than to verify

Edition 2024 implies `resolver = "3"`, which in turn implies `resolver.incompatible-rust-versions = "fallback"`.
But the Edition Guide is explicit that the resolver is a global workspace setting, ignored in dependencies, and that **virtual workspaces still need an explicit `[workspace] resolver`** to opt in.
That creates a real review surface: “we thought fallback was active” is not the same thing as “fallback was active.”

## 3. Lockfile authoring now has a more visible floor story of its own

Cargo 1.83 made lockfile format v4 the default for creating or updating a lockfile and notes that Rust toolchains 1.78+ support it.
The changelog explicitly advises maintainers targeting earlier MSRVs to consider setting `package.rust-version` to 1.82 or earlier for compatibility.
Rust 1.85’s release notes then call out that Cargo now respects `rust-version` when generating the lockfile.
That makes the **authoring/update path** a separate support surface from “the crate still builds with a pinned old lockfile.”

## 4. Current issue traffic shows command-family divergence is not theoretical

A fresh Cargo issue shows a concrete case where `cargo run` succeeds while `cargo metadata` fails because an inactive target edge drags in a 2024-edition dependency under `fallback`.
Another issue captures the opposite workspace-side pain: mixed-MSRV workspaces can produce surprising dependency selection and lockfile pressure for newer members because the resolver must serve the oldest member too.

## 5. Existing tools still center “find one MSRV” more than “publish a support contract”

`cargo-msrv` is alive and useful: it finds a crate’s MSRV, supports workspace inheritance, package selection, verifying against a specific Rust version, and more.
But it is still fundamentally a **finder / verifier** tool.
What remains missing is the small review bundle that says:

- which policy was declared,
- whether the intended resolver policy actually activated,
- which command families were witnessed at which floor,
- which lockfile floor applies to update/package/generate paths,
- and which member, dependency, feature, or inactive edge explains divergence.

# Sharper reading after the latest 2026 signals

The most useful next step is not broader MSRV prose and not more brute-force search.
It is to elevate three first-class review objects:

1. **policy activation truth** — was the expected resolver/MSRV policy actually active for this workspace root?
2. **command-family floor truth** — which command families succeed at the claimed floor, and which require something newer?
3. **lockfile-authoring truth** — what floor is required to read/write/update the lockfile path, and is it higher than the supported build floor?

# What it provides

- `msrv-policy.toml` — declares package/member promises, support tiers, required command families, targets, feature profiles, and tolerated drift rules.
- `policy-activation.receipt.json` — records the expected resolver policy, the observed active policy, where it came from, and whether a virtual/root-workspace configuration silently left the intended policy inactive.
- `effective-workspace-promise.manifest.json` — normalized per-member support promises after inheritance and workspace policy splits.
- `toolchain-matrix.plan.json` — minimized, reviewable set of toolchain / package / feature / target / command-family checks to run.
- `msrv-observation.receipt.json` — one observed lane with exact toolchain, command family, resolver policy, target, features, and outcome.
- `command-family-floor.report.json` — compact per-command view of which lanes are supported at the policy floor versus requiring a newer toolchain or manual review.
- `lockfile-floor.receipt.json` — records lockfile version, read/write/update action, Cargo version, and whether authoring the lockfile requires a newer floor than the pinned build lane.
- `msrv-blame.report.json` — explains which dependency, feature, target edge, edition floor, or workspace coupling moved the effective floor upward.
- `resolver-lane.diff.json` — compares `allow` vs `fallback`, older vs newer lockfile behavior, or previous vs current policy-activation state.
- `policy-split-diff.report.json` — compares how member promises changed across revisions without flattening the workspace into one number.
- `msrv-support-bundle.manifest.json` — portable review bundle joining declared policy, activation, command-family floors, lockfile floor, and any split-policy drift.
- `adoption-plan.md` — human-readable plan: keep current split, raise one package only, split workspace promises, pin lockfile authoring separately, or accept manual-review debt.
- `cargo msrv-lab inspect` — capture policy-activation and lockfile-floor facts before expensive probing.
- `cargo msrv-lab matrix` — generate the smallest useful check matrix from policy.
- `cargo msrv-lab capture` — run one selected lane and emit a receipt.
- `cargo msrv-lab blame` — explain the raised floor conservatively.
- `cargo msrv-lab diff` — compare two policy or lockfile states.
- `cargo msrv-lab pack` — emit one portable bundle manifest plus the referenced receipts/reports.
- `*.msrvbundle.zip` — portable artifact for CI, release reviews, contributor docs, and downstream support incidents.

# What the crate should provide other people

1. **A policy-activation receipt** so teams can tell whether the intended MSRV-aware resolver is really in force.
2. **A command-family floor report** so “build works” stops masquerading as “the workspace support promise holds.”
3. **A lockfile-authoring receipt** so maintainers can separate “can still build from the committed lockfile” from “can safely run update/package/generate-lockfile on the promised floor.”
4. **A mixed-workspace planning tool** for teams where libraries, CLIs, examples, and internal products should not all share one support promise.
5. **A dependency/workspace blame report** that names the floor-raising edge instead of forcing maintainers to diff lockfiles and resolver traces by hand.
6. **A split-policy diff** so MSRV drift can say which member moved rather than implying that the whole workspace moved.
7. **A portable support bundle** suitable for MSRV raises, freezes, split-policy workspaces, and exception handling.

# Persona / who it’s for

- maintainers of mixed workspaces
- library authors promising a lower MSRV than their binaries/examples/tools
- CI and release engineers
- downstream users pinned to older Rust compilers
- regulated and safety-critical adopters who need an explicit support posture

# Users & user stories

- **Library maintainer**: “My library supports 1.70, but examples and docs tooling do not. Keep that distinction explicit.”
- **Release engineer**: “Show whether this dependency update only raised the lockfile authoring floor or also the supported build floor.”
- **Contributor**: “Tell me whether fallback is active for this workspace or just assumed because one member is edition 2024.”
- **Reviewer**: “Show me whether this change affected declared policy, resolver activation, command-family floors, or only one inactive target edge.”
- **Enterprise adopter**: “Give me one bundle I can archive that explains our supported compiler window, update path, and known exceptions.”

# Prior art (and why it’s insufficient)

- Cargo’s `rust-version`, resolver, and config surfaces provide the underlying policy mechanism.
- Cargo’s docs explicitly discuss workspace policy splits and `fallback` interactions.
- `cargo-msrv` finds or verifies an MSRV for a chosen crate/lane and has been adding workspace and version-selection features.
- Cargo issues and changelogs document real command-family and lockfile-floor surprises.

What remains missing is the **policy-activation + command-family-floor + lockfile-authoring** layer above those pieces.

# Design goals

1. **Lane-honest** — keep declared support promise, policy activation, command-family floors, and lockfile authoring separate.
2. **Workspace-first** — do not assume one repo wants one MSRV promise.
3. **Root-aware** — resolver activation must track the actual workspace root and source of truth.
4. **Lockfile-aware** — distinguish build support from update/generate/package support.
5. **Blame-first** — every raised floor should point to a concrete dependency, feature, target edge, edition floor, or workspace coupling reason where possible.
6. **CI-sized** — prefer a minimized test plan over combinatorial explosion.
7. **Cargo-adjacent** — observe Cargo behavior instead of trying to out-resolve Cargo.

# MVP surface

- Minimal types: `MsrvPolicy`, `PolicyActivationReceipt`, `ToolchainMatrixPlan`, `MsrvObservationReceipt`, `CommandFamilyFloorReport`, `LockfileFloorReceipt`, `MsrvBlameReport`, `ResolverLaneDiff`, `AdoptionPlan`
- Minimal functions:
  - `inspect_policy_activation()`
  - `plan_matrix()`
  - `capture_lane()`
  - `summarize_command_floors()`
  - `inspect_lockfile_floor()`
  - `blame_floor()`
  - `diff_lanes()`
  - `write_bundle()`
- Feature flags:
  - `serde`
  - `rustup`
  - `ci`
  - `cargo-metadata`
  - `html-summary`

# Compatibility story

- Works with declared `package.rust-version` today.
- Records Cargo resolver policy from the root workspace/config rather than assuming defaults.
- Treats target-specific dependency edges and command-family mismatches as first-class findings.
- Separates pinned-lockfile buildability from lockfile-authoring compatibility.
- Can integrate with `cargo update`, `cargo generate-lockfile`, and packaging review workflows without replacing Cargo.
- Should remain useful even if Cargo evolves stronger built-in MSRV reporting later.

# Conformance & fixtures

- One mixed-workspace fixture where the library lane stays lower than the product lane.
- One inactive-target-edge fixture where `cargo build` remains green but `metadata` reveals a higher floor.
- One **virtual workspace activation** fixture where member edition expectations do not activate resolver v3 without `[workspace] resolver = "3"`.
- One **lockfile-authoring** fixture where updating or generating the lockfile requires a newer floor than the pinned build lane.
- Goldens for `policy_active`, `policy_expected_but_inactive`, `build_floor_supported`, `metadata_floor_higher_than_build_floor`, `lockfile_authoring_floor_higher_than_build_floor`, and `manual_review_required`.

# Path to boring stability

- Freeze the artifact vocabulary before optimizing search strategies.
- Keep “build floor”, “command-family floor”, and “lockfile-authoring floor” separate in every report.
- Treat binary-search inference as optional and secondary to receipts and blame.
- Prefer conservative `manual_review_required` over fake certainty.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A crate and cargo subcommand that read a workspace MSRV policy, emit one policy-activation receipt, generate a compact toolchain matrix, capture observed command-family results for chosen lanes, and emit one blame report plus one lockfile-floor receipt.

# De-risk plan

1. Start with policy-activation and lockfile-floor receipts, not exhaustive inference.
2. Add command-family floor summaries before adding binary-search tooling.
3. Treat metadata/build/package/update mismatches as explicit lanes, not bugs in the crate.
4. Keep target-specific edge handling conservative and review-friendly.

# Non-goals

- Not a replacement for Cargo’s resolver.
- Not a promise to explore every feature combination.
- Not a single universal ecosystem MSRV policy.
- Not a magical guarantee that “minimal compiler found once” equals a credible support promise.
- Not a claim that a green build proves safe lockfile authoring on the same toolchain.

# Architecture & API sketch

```rust
pub struct PolicyActivationReceipt {
    pub workspace_kind: WorkspaceKind,
    pub expected_policy: ResolverPolicy,
    pub observed_policy: ResolverPolicy,
    pub activation_state: ActivationState,
    pub resolver_source: ResolverSource,
}

pub struct LockfileFloorReceipt {
    pub action: LockfileAction,
    pub lockfile_version: LockfileVersion,
    pub build_floor: String,
    pub authoring_floor: Option<String>,
    pub floor_state: FloorState,
}

pub fn inspect_policy_activation(req: &InspectRequest) -> Result<PolicyActivationReceipt>;
pub fn plan_matrix(policy: &MsrvPolicy) -> Result<ToolchainMatrixPlan>;
pub fn capture_lane(request: &LaneRequest) -> Result<MsrvObservationReceipt>;
pub fn summarize_command_floors(receipts: &[MsrvObservationReceipt]) -> Result<CommandFamilyFloorReport>;
pub fn inspect_lockfile_floor(req: &LockfileInspectRequest) -> Result<LockfileFloorReceipt>;
pub fn blame_floor(receipts: &[MsrvObservationReceipt]) -> Result<MsrvBlameReport>;
```

Bundle draft: `msrv-policy.toml`, `policy-activation.receipt.json`, `toolchain-matrix.plan.json`, `msrv-observation.receipt.json`, `command-family-floor.report.json`, `lockfile-floor.receipt.json`, `msrv-blame.report.json`, `resolver-lane.diff.json`, `adoption-plan.md`.

# Security / safety model

- No network by default except optional rustup installation lanes.
- Preserve which facts came from Cargo config, manifest, lockfile inspection, or trial execution.
- Support redaction of local paths and private registry details.
- Treat toolchain/version absence as a first-class outcome, not silent failure.

# Maintenance & governance plan

- Keep schemas small and versioned.
- Track Cargo resolver and lockfile behavior explicitly in docs and fixtures.
- Prefer portable CI recipes and fixture packs over bespoke environment logic.
- Maintain a compact finding taxonomy so downstream tools can reuse it.

# Milestones

## 0.1
- `msrv-policy.toml`
- `policy-activation.receipt.json`
- `toolchain-matrix.plan.json`
- per-lane capture receipts
- first blame report

## 0.2
- `command-family-floor.report.json`
- `lockfile-floor.receipt.json`
- resolver-lane diffing
- inactive-target-edge classification
- human-readable adoption plan output

## 1.0
- stable schemas
- deeper CI integration
- optional binary-search inference layered on top of the receipt model

# Open questions

- Should `update`, `generate-lockfile`, and `package` always be modeled separately, or should they collapse into one lockfile-authoring lane unless a repo opts into finer granularity?
- What is the smallest target-edge model that still catches “inactive edge breaks metadata or lockfile authoring” honestly?
- How should the crate represent “supported by policy, but only build-witnessed under a pinned lockfile” versus “supported for ongoing update/package work on that same toolchain”?

# Sources

- Cargo rust-version docs: https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo resolver docs: https://doc.rust-lang.org/cargo/reference/resolver.html
- Edition Guide, Rust-version aware resolver: https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- Cargo config docs (`resolver.incompatible-rust-versions`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo changelog (lockfile v4 default): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust 1.85 release notes (respect rust-version when generating lockfile): https://doc.rust-lang.org/beta/releases.html
- Cargo FAQ (`Cargo.lock` and verifying MSRV): https://doc.rust-lang.org/cargo/faq.html
- Rust safety-critical post: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Cargo issue #16597: https://github.com/rust-lang/cargo/issues/16597
- Cargo issue #14414: https://github.com/rust-lang/cargo/issues/14414
- cargo-msrv docs: https://docs.rs/crate/cargo-msrv/latest/source/
- cargo-msrv changelog: https://github.com/foresterre/cargo-msrv/blob/main/CHANGELOG.md
