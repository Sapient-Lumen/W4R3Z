# Frontier salience snapshot — 2026-03-20 (117)

This pass did **not** open another brute-force MSRV finder, CI matrix expander, or resolver explainer.
It deepened **P-0036 MSRV Workspace Lab** by making another support-critical truth explicit:

- **“the workspace says MSRV X” is still too vague unless the crate can say whether the intended resolver policy was actually active, which command families really work at that floor, and whether lockfile authoring quietly needs something newer.**

## Main judgment

The sharper missing layer is no longer merely “find the minimum compiler.”
The sharper missing layer is a **policy-activation / command-floor / lockfile-authoring contract**.

Current Cargo and Rust signals now make that specific:

1. Cargo’s `rust-version` docs say support should be treated as a policy and explicitly allow multiple policies within one workspace.
2. Those docs also say shared dependencies may be forced to lowest-common versions and that `fallback` can let one package’s Rust version affect dependency choices for another.
3. The Edition Guide says `edition = "2024"` implies resolver v3 and `fallback`, but also says the resolver is global and virtual workspaces still need explicit `[workspace] resolver = "3"`.
4. Cargo 1.83 made lockfile v4 the default for creating/updating a lockfile and says toolchains 1.78+ support it.
5. Rust 1.85’s release notes say Cargo now respects `rust-version` when generating the lockfile.
6. Cargo’s FAQ still treats `Cargo.lock` as a deterministic snapshot useful for verifying an older MSRV, which helps but also highlights that pinned-lockfile buildability is not the same contract as ongoing authoring/update compatibility.
7. Cargo issue #16597 shows a live case where `cargo run` works while `cargo metadata` fails because an inactive target edge still drags a newer edition into the metadata/update path.
8. Cargo issue #14414 shows mixed-workspace MSRV pressure remains real for shared dependency selection.
9. `cargo-msrv` continues to improve, but it is still primarily a finder/verifier, not a workspace support-contract bundle.

That means the next worthy move is not “another search strategy.”
It is one conservative crate family that can publish:

- **policy activation truth**,
- **command-family floor truth**,
- **lockfile-authoring truth**,
- and **reviewable blame** when those slices diverge.

## Why this beat nearby work

The archive already had adjacent lanes for:

- Cargo resolver explanation,
- update policy,
- minimal-version witness work,
- public API readiness,
- and crate-health / pathfinder / upgrade support.

What it still lacked was one compact way to say:

- “the workspace expected `fallback`, but the root configuration never activated it,”
- “the build lane still works at the policy floor, but `metadata` or `package` does not,”
- and “the pinned lockfile remains usable, but ongoing lockfile authoring requires a newer floor.”

That is a real receiver-facing product boundary, not just another CI convenience.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
4. **P-0036 MSRV Workspace Lab** — materially stronger after this pass because Cargo’s policy/resolver/lockfile substrate is real, but the reviewable support contract above it is still missing.
5. **P-0451 Cfg Availability Ledger Kit** — still unusually strong because docs-visible truth remains weaker than usable-support truth.
6. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown phase and aftermath truth cut across runtimes.
7. **P-0028 open-table-format-kit** — still unusually strong because the Rust lakehouse substrate is real while the contract above it is weak.
8. **P-0134 spiffe-identity-kit** — still stronger because the workload-identity contract above live SPIFFE substrate remains missing.

## What changed in the archive

Added:
- `entries/2026-03-20-297.md`
- `meta/frontier-salience-2026-03-20-117.md`
- `meta/msrv-workspace-lab-product-plan-2026-03-20.md`
- `meta/msrv-command-and-lockfile-boundaries-2026-03-20.md`
- `fixtures/msrv-workspace-lab/policy-activation.receipt.schema.json`
- `fixtures/msrv-workspace-lab/command-family-floor.report.schema.json`
- `fixtures/msrv-workspace-lab/lockfile-floor.receipt.schema.json`
- `fixtures/msrv-workspace-lab/scenarios/virtual_workspace_needs_workspace_resolver3_to_activate_fallback_policy/README.md`
- `fixtures/msrv-workspace-lab/scenarios/virtual_workspace_needs_workspace_resolver3_to_activate_fallback_policy/policy-activation.receipt.example.json`
- `fixtures/msrv-workspace-lab/scenarios/lockfile_v4_update_path_can_raise_authoring_floor_without_raising_build_floor/README.md`
- `fixtures/msrv-workspace-lab/scenarios/lockfile_v4_update_path_can_raise_authoring_floor_without_raising_build_floor/command-family-floor.report.example.json`
- `fixtures/msrv-workspace-lab/scenarios/lockfile_v4_update_path_can_raise_authoring_floor_without_raising_build_floor/lockfile-floor.receipt.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/msrv-workspace-lab.md`
- `fixtures/msrv-workspace-lab/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy MSRV contribution for Rust should now provide more than one inferred floor and one build receipt.
It should provide:

- one explicit **policy-activation receipt**,
- one explicit **command-family floor report**,
- one explicit **lockfile-floor receipt**,
- and one honest way to keep “pinned lockfile still builds” from masquerading as “the ongoing support promise still holds for update/package work.”

## Freshness anchors

- Cargo rust-version docs — https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo resolver docs — https://doc.rust-lang.org/cargo/reference/resolver.html
- Edition Guide, Rust-version aware resolver — https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- Cargo config docs — https://doc.rust-lang.org/cargo/reference/config.html
- Cargo changelog — https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust release notes — https://doc.rust-lang.org/beta/releases.html
- Cargo FAQ — https://doc.rust-lang.org/cargo/faq.html
- Rust safety-critical post — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Cargo issue #16597 — https://github.com/rust-lang/cargo/issues/16597
- Cargo issue #14414 — https://github.com/rust-lang/cargo/issues/14414
- cargo-msrv docs — https://docs.rs/crate/cargo-msrv/latest/source/
- cargo-msrv changelog — https://github.com/foresterre/cargo-msrv/blob/main/CHANGELOG.md
