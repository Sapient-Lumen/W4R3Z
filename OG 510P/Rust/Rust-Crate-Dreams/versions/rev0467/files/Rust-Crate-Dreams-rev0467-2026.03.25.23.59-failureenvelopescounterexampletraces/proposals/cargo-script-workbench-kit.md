---
id: P-0435
title: Cargo Script Workbench Kit — lock receipts, portability bundles, and export plans for single-file Rust packages
status: idea
domains: [cargo, scripting, devtools, education, prototyping, ci]
last_reviewed: 2026-03-22
evidence:
  - https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  - https://doc.rust-lang.org/cargo/reference/unstable.html#single-file-packages
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html
  - https://rust-lang.github.io/rfcs/3502-cargo-script.html
  - https://github.com/fornwall/rust-script
  - https://hackmd.io/%40rust-cargo-team/HJZ7cw5uxl
---

# Problem

Cargo script is no longer a vague someday feature.
By early 2026 it is close to stabilization, official docs already describe single-file packages, and the Rust project is explicitly promoting them as a strong fit for minimal reproducers, quick prototypes, tutorials, and tiny utilities.

That changes the missing-crate frontier.
The missing value is no longer “make Rust scripts possible at all.”
The missing value is the workflow layer that makes single-file packages **portable, reviewable, and supportable**.

Official Cargo docs already make several sharp boundaries clear:

- single-file packages may be passed directly to Cargo and selected via `--manifest-path`,
- unlike `Cargo.toml`, single-file packages are **not auto-discovered**,
- embedded manifests have real defaults and real disallowed fields,
- the default `CARGO_TARGET_DIR` for single-file packages lives under `$CARGO_HOME/target/<hash>`,
- the lockfile for single-file packages lives in that target-dir lane,
- and Cargo 1.94 notes make it explicit that cargo script is starting with workspace auto-discovery disabled while broader workspace/config discovery remains an active design problem.

That means a worthy crate here should not be another script runner.
It should be the thing that tells another person:

- what Cargo inferred,
- what directory/layout rules were in effect,
- what hidden config or workspace assumptions did **not** apply,
- where the lockfile and build outputs went,
- and how to turn a one-file repro into a normal package without losing provenance.

The missing crate is a **Cargo Script Workbench Kit**.

# Sharper reading after the 2026 Cargo updates

The 2026 signal makes this proposal stronger and narrower than before.

1. The Rust project is explicitly highlighting cargo script as a near-stable workflow for minimal reproducers and prototypes, not as a toy feature.
2. Cargo’s unstable docs now pin down concrete semantics for single-file packages: disabled auto-discovery, inferred defaults, disallowed manifest fields, target-dir hashing, and target-dir lockfile placement.
3. Cargo 1.94’s workspace/config discussion says cargo script is intentionally beginning with workspace auto-discovery disabled, which means single-file package portability needs to stay separate from broader workspace-boundary diagnosis.
4. Because single-file packages are easy to paste into issues, Markdown, temp dirs, and chat, the ecosystem will need a **boring handoff artifact** surprisingly quickly.

So the missing contribution is not “Cargo but for scripts.”
It is the **receipt / doctor / export-plan / bundle layer** above Cargo’s single-file package substrate.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What manifest fields were explicit versus inferred?**
2. **What workspace/config discovery rules were disabled or out of scope?**
3. **Where did the target directory and lockfile actually live?**
4. **What would need to change to export this into a normal package?**
5. **What parts of the result are stable Cargo facts versus advisory portability guidance?**

That is more valuable than another one-file launcher.

# What it provides

- `script-policy.toml` — optional declared intent for one-file packages: preferred edition, supported invocation style, allowed dependency classes, export expectations, and path-redaction rules.
- `script-manifest.view.json` — normalized view of explicit frontmatter plus inferred/defaulted fields and rejected fields.
- `script.lock.json` — portable lock/provenance record for a single-file package, including where the lock actually lived and what toolchain/config context influenced resolution.
- `script.receipt.json` — observed execution/build context: invocation path, cwd, target-dir choice, lockfile location, config roots considered, workspace auto-discovery posture, and diagnostic provenance.
- `script-doctor.report.json` — structured findings such as `edition_defaulted`, `frontmatter_parse_risk`, `disallowed_field_present`, `workspace_auto_discovery_disabled`, `parent_config_influence_present`, `tempdir_portability_risk`, `export_requires_layout_decision`, and `manual_review_required`.
- `script-export.plan.json` — conservative plan for materializing a standard package: package name, source path mapping, manifest fields to lift out, files to create, and ambiguities requiring human choice.
- `script-portability.diff.json` — compare two captures from laptop/CI/docs/example snippets and classify `semantics_equivalent`, `inference_changed`, `config_root_changed`, `target_dir_changed`, `lock_location_changed`, or `manual_review_required`.
- `cargo script-workbench capture` — freeze one single-file package receipt.
- `cargo script-workbench doctor` — explain what Cargo inferred and which portability risks remain.
- `cargo script-workbench export-plan` — emit a conservative export/handoff plan without mutating files.
- `*.scriptbundle.zip` — portable artifact for issue reports, tutorials, CI failures, and “please turn this repro into a repo” handoffs.

# What the crate should provide other people

1. **A reproducible handoff artifact** for single-file packages instead of raw pasted code plus folklore.
2. **An inference receipt** that distinguishes explicit frontmatter from Cargo defaults.
3. **A portability doctor** that surfaces temp-dir, config-root, and export risks early.
4. **A conservative export plan** for converting a one-file repro into a standard package without losing important context.
5. **A shared vocabulary** for single-file package support tickets, tutorials, and CI wrappers.
6. **A bridge** between official cargo-script support and ordinary editor/repo/release workflows.

# Persona / who it’s for

- maintainers sharing minimal bug reproducers
- educators shipping one-file examples
- developers writing small utilities or prototypes
- CI/tool authors integrating single-file packages into wrappers or examples
- reviewers asked to promote a one-file prototype into a maintained repository

# Users & user stories

- **Bug reporter**: “Attach one bundle that preserves the single-file package plus its inferred manifest, target-dir, and lock placement.”
- **Maintainer**: “Turn this issue comment repro into a normal package without rediscovering what Cargo assumed.”
- **Educator**: “Ship a one-file example and prove what learners will see when they run it.”
- **CI owner**: “Record which config roots and temporary paths influenced this single-file run so support stops being guesswork.”
- **Editor/tooling owner**: “Reuse a small stable receipt instead of reverse-engineering single-file package behavior ad hoc.”

# Prior art (and why it’s insufficient)

- The cargo-script project goal and RFC make the core package shape real.
- Cargo’s unstable docs now describe real single-file package semantics.
- `rust-script` proves user demand and ergonomic value.
- rust-analyzer/Cargo design notes show that editor integration details matter.

What remains missing is a **portable workflow artifact** above those pieces.
Cargo itself should not have to become the full handoff/review/export platform for single-file packages.

# Design goals

1. **Single-file native** — keep the source of truth as the one file.
2. **Inference-explicit** — record defaults, rejected fields, and disabled discovery rules plainly.
3. **Portability-first** — temp paths, config roots, and target-dir hashing must stay visible.
4. **Export-conservative** — provide plans and receipts before any automatic mutation.
5. **Diff-friendly** — allow laptop/CI/tutorial captures to be compared.
6. **Boundary-honest** — keep single-file portability separate from workspace-boundary and source-parity crates.

# MVP surface

- Minimal types: `ScriptPolicy`, `ScriptManifestView`, `ScriptLock`, `ScriptReceipt`, `ScriptDoctorReport`, `ScriptExportPlan`, `ScriptPortabilityDiff`, `ScriptBundle`
- Minimal functions:
  - `read_frontmatter()`
  - `capture_script_manifest_view()`
  - `freeze_script_lock()`
  - `capture_script_receipt()`
  - `doctor_script_portability()`
  - `plan_script_export()`
  - `diff_script_receipts()`
- Feature flags:
  - `serde`
  - `offline`
  - `markdown`
  - `rust-analyzer`
  - `redaction`

# Compatibility story

- Works above official Cargo single-file package support rather than replacing it.
- Can ingest recognizable `rust-script`-style files when semantics overlap enough to preserve honesty.
- Must preserve which facts came from explicit frontmatter, inferred Cargo defaults, cwd/config probing, or tool-specific wrappers.
- Should remain useful before and after stabilization because the handoff problem survives stabilization.
- Must stay honest when the package was intentionally ephemeral and cannot be exported without human decisions.

# Conformance & fixtures

- detached-file run with hashed target-dir and target-dir lockfile
- omitted-edition script where Cargo defaulted the edition and emitted a warning-worthy portability finding
- parent workspace/config presence where auto-discovery stayed disabled but parent config still influenced execution context
- export-plan fixture where a minimal repro becomes a multi-file package with explicit decisions still required
- goldens for `edition_defaulted`, `workspace_auto_discovery_disabled`, `parent_config_influence_present`, `target_dir_changed`, and `export_requires_layout_decision`

Current implementation-shaping target:
- freeze `script.receipt.json`, `script-doctor.report.json`, and `script-export.plan.json`
- prove the model on three tiny scenario bundles before adding editor adapters or vendoring modes

# Path to boring stability

- Freeze the receipt/doctor/export vocabulary before adding fancy offline or editor integrations.
- Treat tempdir and config-root facts as first-class output.
- Prefer portable bundles over automatic repo creation.
- Keep advisory portability warnings separate from exact Cargo facts.
- Preserve the disabled-auto-discovery story explicitly so future changes remain diffable.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A crate and cargo subcommand that read one single-file package, capture what Cargo inferred plus where the target-dir/lockfile lived, emit a portability doctor report, and produce an export plan plus shareable bundle another maintainer can review.

# De-risk plan

1. Start from official Cargo semantics rather than inventing a parallel script format.
2. Freeze receipts before adding repo-mutation or vendoring features.
3. Validate on minimal repro, tutorial, and CI-wrapper scenarios.
4. Keep workspace-boundary and source-parity imports optional rather than required.

# Non-goals

- Not a replacement for Cargo’s core single-file package support.
- Not a shell-task runner.
- Not a general script package manager.
- Not a workspace-boundary doctor.
- Not a mirror/offline source-management crate.

# Architecture & API sketch

```rust
pub enum ScriptDoctorVerdict {
    Ok,
    EditionDefaulted,
    FrontmatterParseRisk,
    DisallowedFieldPresent,
    WorkspaceAutoDiscoveryDisabled,
    ParentConfigInfluencePresent,
    TempdirPortabilityRisk,
    ExportRequiresLayoutDecision,
    ManualReviewRequired,
}

pub fn capture_script_manifest_view(path: &std::path::Path) -> Result<ScriptManifestView>;
pub fn freeze_script_lock(path: &std::path::Path, out: &std::path::Path) -> Result<ScriptLock>;
pub fn capture_script_receipt(path: &std::path::Path) -> Result<ScriptReceipt>;
pub fn doctor_script_portability(policy: &ScriptPolicy, receipt: &ScriptReceipt) -> Result<ScriptDoctorReport>;
pub fn plan_script_export(receipt: &ScriptReceipt, out: &std::path::Path) -> Result<ScriptExportPlan>;
pub fn diff_script_receipts(old: &ScriptReceipt, new: &ScriptReceipt) -> ScriptPortabilityDiff;
```

Bundle draft: `script-policy.toml`, `script-manifest.view.json`, `script.lock.json`, `script.receipt.json`, `script-doctor.report.json`, `script-export.plan.json`, `script-portability.diff.json`, `notes.md`.

# Security / safety model

- Support redaction of local paths, temp directories, usernames, and shell wrapper details.
- Never hide which manifest fields were inferred or rejected.
- Preserve exact-vs-advisory distinctions in every report.
- Treat config roots and environment facts as potentially sensitive input.
- Prefer export plans over silent source mutation.

# Maintenance & governance plan

- Track official cargo-script stabilization and single-file package semantics.
- Keep schemas tiny and versioned.
- Expand adapters only where the core receipt remains clear.
- Maintain fixtures for tempdir, omitted-edition, parent-config, and export-plan scenarios.
- Publish a short compatibility note when Cargo changes single-file discovery or lock placement.

# Milestones

## 0.1
- frontmatter capture
- manifest view
- receipt + doctor report

## 0.2
- lock capture
- export plan
- shareable bundle export

## 1.0
- stable schemas
- portability diffs
- editor / CI adapter notes

# Open questions

- How much of the target-dir/lockfile story should be preserved when paths are redacted?
- Should the export plan distinguish “mechanically safe” from “policy choice still needed” at a finer level?
- What is the smallest useful receipt for issue comments and tutorial pages?
- How should the crate represent eventual future workspace support without pretending it exists today?

# Sources

- Program management update (cargo-script): https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo 1.94 development cycle: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo unstable docs, single-file packages: https://doc.rust-lang.org/cargo/reference/unstable.html#single-file-packages
- Cargo-script project goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html
- Cargo-script RFC: https://rust-lang.github.io/rfcs/3502-cargo-script.html
- `rust-script`: https://github.com/fornwall/rust-script
- cargo/rust-analyzer design notes: https://hackmd.io/%40rust-cargo-team/HJZ7cw5uxl


# 2026-03-22 implementation refresh — frontmatter authority, discovery scope, and export lineage

This proposal is more implementation-ready now because official Cargo surfaces make several previously fuzzy seams explicit.

Five details especially matter:

1. Cargo’s unstable docs now define **embedded frontmatter** plus inferred/defaulted manifest fields and disallowed fields for single-file packages.
2. The same docs explicitly say single-file packages **cannot be auto-discovered** and place their default target-dir under `$CARGO_HOME/target/<hash>` with the lockfile in that lane.
3. Cargo documents that `cargo <path>` and `cargo run --manifest-path <path>` are **not equivalent**, including config-root and verbosity differences.
4. Cargo 1.94 notes say cargo script is intentionally **starting with workspace auto-discovery disabled** while broader workspace/config discovery remains under design.
5. The cargo-script goal makes rustfmt, rust-analyzer, rustc frontmatter handling, and Cargo diagnostics part of the stabilization path.

That means a worthy crate here should now freeze six first-class review objects instead of letting them hide inside one generic `script.receipt` blob:

- `frontmatter-authority.receipt.json` — records which manifest facts were explicit, inferred, defaulted, rejected, or advisory-only.
- `discovery-scope.receipt.json` — records whether workspace auto-discovery was disabled, which config roots were considered, and which parent influences still applied.
- `invocation-interpretation.receipt.json` — records whether Cargo used manifest-command or subcommand semantics and what behavioral consequences followed.
- `cache-residency.receipt.json` — records target-dir, lockfile, hash basis, persistence expectation, and portability notes.
- `export-lineage.plan.json` — records the conservative path from single-file package to multi-file package, including unresolved human choices.
- `script-support-bundle.manifest.json` — joins the above artifacts into a compact handoff bundle.

## Sharper receiver-facing questions

After this pass, the crate should help another person answer:

1. **What exactly was authored in frontmatter versus inferred by Cargo?**
2. **Which discovery rules were intentionally disabled, and what still influenced the run anyway?**
3. **What invocation mode was actually used?**
4. **Where did cache and lock state live?**
5. **What would need to change to export the script into a conventional package?**
6. **Which findings are hard semantics versus portability guidance?**

## Design refinement

The v0.1 stance should now be:

- explanation-first rather than launcher-first,
- provenance-first rather than convenience-first,
- conservative export planning rather than automatic synthesis,
- and explicit separation between **Cargo semantics** and **support guidance**.
