---
id: P-0470
title: Cargo Package Review Kit — workspace candidate receipts, manifest-normalization reports, and `.crate` review bundles
status: idea
domains: [cargo, publishing, packaging, ci, release-engineering, devtools, workspace]
last_reviewed: 2026-03-20
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-package.html
  - https://doc.rust-lang.org/cargo/reference/publishing.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
---

# Problem

Cargo already owns the packaging substrate, but the review layer is still too manual.

The official package docs now define a surprisingly rich source-bundle contract:

- `cargo package` creates the canonical `.crate` tarball,
- Cargo rewrites and normalizes `Cargo.toml`,
- `[patch]`, `[replace]`, and `[workspace]` sections are removed,
- `Cargo.lock` is included by default,
- `.cargo_vcs_info.json` is included but explicitly documented as **best-effort** rather than provenance,
- symlinks are flattened,
- Cargo rebuilds the extracted package from scratch to verify it,
- and Cargo checks that build scripts did not modify source files.

At the same time, newer Cargo changes make workspace and review posture more explicit than this proposal originally assumed:

- the changelog says `-Zpackage-workspace` now supports `cargo package --workspace` when workspace crates depend on one another and no longer requires those crates to publish to actual registries,
- the same changelog history already treated resolver settings and related workspace-derived policy as something that must survive packaging,
- release notes now say `.crate` tarballs should be treated as **package outputs of `cargo package`**, not incidental leftovers of `cargo publish`,
- and Cargo’s 1.90 development-cycle discussion made the workspace-license/readme copy-in problem explicit enough to name as a real review seam rather than an incidental packaging quirk.

That means the missing crate is **not** a new packager, not a registry client, and not a trusted-publishing tool.

The missing crate is a **Cargo Package Review Kit**: a Cargo-adjacent crate that turns one package candidate or one workspace package set into a compact, reviewable receipt.

# 2026-03-16 implementation refresh — workspace candidate sets and normalization truth

This proposal first became stronger by treating workspace candidate sets, manifest normalization, and copy-in behavior as explicit review objects rather than path-listing footnotes.


# 2026-03-20 implementation refresh — packaged-surface authority and extraction-state truth

This proposal is stronger again because Cargo’s packaging surface is now reviewable in a way the earlier archive version still underused.

Six details matter most:

1. `cargo package` still defines the canonical `.crate` archive and then extracts it again for verification.
2. The docs now expose an unstable JSON path-listing mode that records file lineage with `copy` and `generate`, including `Cargo.toml.orig` and generated `Cargo.toml`.
3. Cargo still documents `.cargo_vcs_info.json` as best effort rather than provenance, so byte authority remains a separate problem.
4. Cargo’s changelog now says generated files in package tarballs should have deterministic timestamps.
5. The changelog also says Cargo updates mtime for generated files after unpacking `.crate` source tarballs, which means extracted verification trees are not identical to archive bytes.
6. Rust 1.93.1 now tells maintainers to use `cargo package` rather than depending on `cargo publish` to retain a durable `.crate` artifact.

That means the crate should now freeze three sharper artifact lanes instead of hiding them inside prose:

- one **`packaged-surface.receipt.json`** that records which archive paths were reviewed and whether key files were copied or generated,
- one **`archive-authority.report.json`** that records which surface is authoritative for hashing/signoff claims,
- and one **`extraction-mutation.report.json`** that records what changed only after unpacking for verification.


This proposal is stronger now because Cargo’s official packaging story has become more clearly layered than the archive originally treated it.

Five details matter most:

1. `cargo package` is the canonical source-bundle producer and should be treated as the review anchor.
2. Release notes now explicitly warn people not to rely on `cargo publish` as the place `.crate` artifacts persist.
3. `-Zpackage-workspace` makes workspace-wide packaging of interdependent members more concrete, which means “what exactly was the candidate set?” is now a real artifact boundary.
4. Cargo package docs still say the manifest is rewritten and normalized, which means reviewers need one compact explanation of what changed before publication.
5. The 1.90 Cargo cycle made workspace-root license/readme copy-in questions explicit, which means external-file copy behavior is no longer safe to treat as invisible implementation trivia.

That means the crate should now freeze four sharper artifact lanes instead of hiding them inside prose:

- one **`workspace-package-set.report.json`** that records which workspace members were reviewed, their inter-dependencies, and whether the package set was shaped by workspace packaging policy,
- one **`manifest-normalization.report.json`** that records which fields/sections were rewritten, removed, copied in, or left manual-review-only,
- one **`path-explanation.report.json`** that records why key packaged paths appeared or were absent,
- and one **`evidence-source.receipt.json`** that says which conclusions came directly from Cargo surfaces versus conservative reconstruction.

# Main judgment

A worthy crate here should hand another person a boring answer to:

1. **What exact package candidate or workspace package set did we review?**
2. **What did Cargo normalize, strip, synthesize, or copy into the packaged source bundle?**
3. **Why is this file present, absent, flattened, or copied from outside the package root?**
4. **Which parts of the review are direct Cargo facts and which are conservative explanation?**
5. **What changed in the packaged source surface since the last candidate or release?**

That is more durable than another publish checklist or path listing.

# What it provides

- `package-review.lock` — pins Cargo version, package or workspace selection, package-workspace posture, redaction mode, and capture scope.
- `workspace-package-set.report.json` — records reviewed workspace members, publish candidate order, inter-member dependency edges, excluded members, and whether the capture was single-package or workspace-shaped.
- `crate-contents.json` — canonical listing of packaged files with size, packaged path, source root, and high-level path class.
- `packaged-surface.receipt.json` — exact archive-path review receipt for key packaged files, including `copy` versus `generate` lineage when available and whether the raw archive bytes were captured.
- `archive-authority.report.json` — explicit authority class for review/signoff claims (`raw_archive`, `json_listing_plus_archive`, `extracted_verification_tree`, or weaker mixed/manual modes).
- `extraction-mutation.report.json` — review of verification-only changes after unpack, such as `.cargo-ok`, normalized manifest replacement, or mtime adjustments.
- `manifest-normalization.report.json` — records removed sections, normalized manifest changes, path/git stripping behavior, lockfile posture, external readme/license copy facts, and symlink flattening notes.
- `path-explanation.report.json` — coarse explanations for included, excluded, copied-in, flattened, or manual-review-only paths.
- `package-policy.report.json` — warnings for oversized assets, suspicious generated files, missing/ambiguous license/readme posture, unexpected workspace leakage, or changed package-shape rules.
- `vcs-snapshot.review.json` — normalized `.cargo_vcs_info.json` plus explicit “best effort, not provenance” caveats.
- `evidence-source.receipt.json` — what came from direct Cargo package output, what came from file inspection, and what remained inferred.
- `package.diff.json` — added/removed/changed packaged paths and changed policy findings across two candidates.
- `cargo package-review capture` — build one review bundle for a package or workspace package set.
- `cargo package-review diff <old> <new>` — compare two packaged source surfaces.
- `cargo package-review explain <path>` — explain why one path landed in the `.crate` or why it did not.
- `*.packreview.zip` — portable artifact for PR review, release signoff, distro intake, or workspace publish rehearsal.

# What the crate should provide other people

1. **A boring publish-readiness receipt** above `cargo package`.
2. **A workspace-aware candidate-set report** instead of “we ran something from the workspace root.”
3. **A packaged-surface receipt** that says what archive paths were actually reviewed and whether key files were copied or generated.
4. **An archive-authority report** that keeps raw `.crate` bytes, Cargo JSON listings, authored trees, and extracted verification trees from borrowing each other’s authority.
5. **An extraction-mutation report** that keeps `.cargo-ok`, normalized-manifest replacement, and mtime-only changes visible.
6. **A manifest-normalization explanation** that preserves Cargo’s rewrite/remove/copy-in behavior.
7. **A compact diffable artifact** for release review, CI, or distro/compliance intake.
8. **A clear boundary** between source-bundle review, publish identity, and post-publish registry receipts.

# Persona / who it’s for

- crate maintainers publishing to crates.io or private registries
- release engineers reviewing package candidates from workspaces
- distro or compliance teams inspecting source bundles
- CI owners who want package-shape gates before publish
- teams rehearsing future workspace-wide publish flows

# Users & user stories

- **Maintainer**: “Show me what the `.crate` actually contains and whether workspace packaging changed the candidate set.”
- **Reviewer**: “Tell me what Cargo normalized or copied in before publish, not just which paths exist.”
- **CI owner**: “Fail the release if package shape or policy drifted, but leave one diffable receipt.”
- **Distro packager**: “Give me one artifact proving which source bundle was reviewed and why unusual files were present.”
- **Workspace steward**: “Show me which members were in scope for a workspace packaging rehearsal and which members were still excluded.”

# Prior art (and why it’s insufficient)

- Cargo’s package and publishing docs explain the workflow, but the review layer is still manual.
- `cargo package --list` shows paths, but not a compact bundle with candidate-set facts, normalization explanations, size/policy warnings, or diffs.
- `.cargo_vcs_info.json` gives useful VCS context, but the docs explicitly warn that it is **not** verified provenance.
- Trusted publishing improves release authorization, but it is a different layer from source-bundle review.
- Post-publish receipt joins help after upload, but they do not tell reviewers what source bundle they approved before upload.

What remains missing is a **reviewable package-shape artifact** that other tools and humans can exchange without re-running the full ritual.

# Design goals

1. **Review-first** — optimize for release signoff, not repackaging.
2. **Workspace-aware** — preserve whether one package or a workspace candidate set was reviewed.
3. **Authority-honest** — make archive bytes, JSON path listings, authored trees, and extracted verification trees distinct review surfaces.
4. **Normalization-honest** — make Cargo’s rewrite/remove/copy behavior explicit.
5. **Mutation-honest** — keep verification-only unpack mutations visible instead of letting them masquerade as archive bytes.
6. **Reason-aware** — explain paths conservatively rather than pretending Cargo exposes a complete trace.
7. **Diff-friendly** — package-shape changes must be easy to compare.
8. **Cargo-honest** — preserve direct Cargo facts versus conservative inference.

# MVP surface

- Minimal types: `PackageReviewLock`, `WorkspacePackageSetReport`, `CrateContents`, `PackagedSurfaceReceipt`, `ArchiveAuthorityReport`, `ExtractionMutationReport`, `ManifestNormalizationReport`, `PathExplanationReport`, `PackagePolicyReport`, `VcsSnapshotReview`, `EvidenceSourceReceipt`, `PackageDiff`, `PackageReviewBundle`
- Minimal functions:
  - `capture_package_review()`
  - `capture_workspace_package_set()`
  - `capture_packaged_surface_receipt()`
  - `classify_archive_authority()`
  - `classify_extraction_mutation()`
  - `diff_packaged_contents()`
  - `explain_packaged_path()`
  - `check_package_policy()`
  - `summarize_manifest_normalization()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `diff`
  - `policy`
  - `workspace`
  - `markdown`

# Compatibility story

- Works above current `cargo package` and `cargo publish --dry-run` behavior.
- Must remain useful when the candidate set is one package, a workspace subset, or a future workspace packaging rehearsal.
- Must preserve whether a path explanation came from direct Cargo output, package docs, or conservative reconstruction.
- Should remain useful even if Cargo later grows richer package introspection, because the review/diff bundle still matters.
- Must treat external readme/license copy behavior and future template/extra-file discussions as **review posture**, not guaranteed packaging provenance.

# Conformance & fixtures

- one fixture with interdependent workspace members captured as a workspace package set
- one fixture with external `license-file` / readme copy-in posture
- one fixture with authored `Cargo.toml.orig` and generated packaged `Cargo.toml` that must not share a hash basis
- one fixture where the extracted verification tree gains `.cargo-ok` and mtime drift after unpack
- one fixture with a subdirectory package and dirty VCS snapshot
- one fixture with generated or oversized assets that should trigger a policy warning
- goldens for `workspace_candidate_set`, `external_file_copy_in`, `packaged_surface_captured`, `archive_authority_classified`, `extraction_mutation_classified`, `size_budget_exceeded`, `workspace_manifest_normalized`, and `manual_review_required`

# Path to boring stability

- Freeze the candidate-set / packaged-surface / authority / mutation vocabularies before adding richer dashboards.
- Start with read-only capture and comparison.
- Keep path explanations coarse and conservative until Cargo exposes richer reason traces.
- Prefer explicit uncertainty over pretending Cargo exposed every packaging reason directly.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 5/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that run one package or workspace packaging rehearsal, capture the packaged file list plus candidate-set, packaged-surface, authority, and extraction-mutation facts, explain obvious include/exclude/copy-in outcomes conservatively, and emit a diffable review bundle.

# De-risk plan

1. Start with capture / diff / policy warnings, not publish orchestration.
2. Use Cargo’s own package output as ground truth instead of predicting packaging independently.
3. Keep inclusion and normalization categories coarse until fixtures prove more detail is trustworthy.
4. Validate first on one interdependent workspace, one subdirectory package, and one accidental-package-bloat case.

# Non-goals

- Not a replacement for `cargo package` or `cargo publish`.
- Not a provenance verifier.
- Not a trusted-publishing orchestrator.
- Not a post-publish registry receipt joiner.
- Not a new registry client.

# Architecture & API sketch

```rust
pub struct PackagedPath {
    pub path: String,
    pub size_bytes: u64,
    pub path_class: String,
    pub explanation: Option<String>,
}

pub fn capture_package_review(root: &Path, package: Option<&str>) -> Result<PackageReviewBundle>;
pub fn capture_workspace_package_set(root: &Path) -> Result<WorkspacePackageSetReport>;
pub fn diff_packaged_contents(old: &PackageReviewBundle, new: &PackageReviewBundle) -> PackageDiff;
pub fn explain_packaged_path(bundle: &PackageReviewBundle, path: &str) -> Option<String>;
pub fn summarize_manifest_normalization(bundle: &PackageReviewBundle) -> ManifestNormalizationReport;
```

Bundle draft: `package-review.lock`, `workspace-package-set.report.json`, `crate-contents.json`, `packaged-surface.receipt.json`, `archive-authority.report.json`, `extraction-mutation.report.json`, `manifest-normalization.report.json`, `path-explanation.report.json`, `package-policy.report.json`, `vcs-snapshot.review.json`, `evidence-source.receipt.json`, `package.diff.json`, `notes.md`.

# Security / safety model

- Preserve Cargo’s explicit warning that VCS snapshot information is not provenance.
- Support redaction of local paths and unpublished workspace member names in exported bundles.
- Never hide packaged files merely because they are “probably harmless”.
- Keep policy findings advisory by default until teams opt into stricter gates.

# Maintenance & governance plan

- Track Cargo package/publish behavior and packaging-related changelog changes.
- Track workspace packaging evolution like `-Zpackage-workspace` without claiming stable guarantees too early.
- Track archive-versus-extraction differences such as `.cargo-ok`, generated timestamps, and unpack-time mutation classes.
- Keep reason and warning taxonomies small, versioned, and conservative.
- Maintain fixtures for workspace packaging, external-file copy-in, authored-vs-generated manifest basis, extraction-only mutation, VCS-state caveats, and accidental package bloat.

# Milestones

## 0.1
- one-package capture
- workspace candidate-set report
- path listing
- basic policy warnings
- manifest-normalization summary

## 0.2
- bundle diffing
- VCS snapshot review
- explain subcommand
- external-file copy review
- archive-authority reporting
- extraction-mutation reporting

## 1.0
- stable bundle schema
- curated workspace corpus
- CI adapters for publish gates

# Open questions

- Should `archive-authority.report.json` treat Cargo JSON path lineage plus a retained `.crate` as the default review basis, or should raw tarball capture remain mandatory for `signoff_ready` posture?
- How much inclusion/exclusion explanation can be trusted without Cargo exposing a first-class reason trace?
- Should workspace candidate ordering live in the core schema or in an optional rehearsal profile?
- How should external-file copy behavior be represented when Cargo discussion is still evolving beyond `license-file` / `readme`?

# Sources

- `cargo package`: https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Publishing on crates.io: https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo changelog (`-Zpackage-workspace` and packaging updates): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust release notes (`cargo publish` artifact behavior): https://doc.rust-lang.org/beta/releases.html
- Cargo 1.90 development cycle (workspace license/readme copy discussion): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- Cargo 1.94 development cycle (workspace/config discovery context): https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
