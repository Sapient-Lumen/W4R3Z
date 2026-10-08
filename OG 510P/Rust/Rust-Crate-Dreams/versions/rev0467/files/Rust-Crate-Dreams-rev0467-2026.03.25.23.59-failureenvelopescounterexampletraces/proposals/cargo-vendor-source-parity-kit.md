---
id: P-0496
title: Cargo Vendor & Source Parity Kit — source-identity locks, mirror-honesty reports, and offline coverage bundles
status: idea
domains: [cargo, supply-chain, offline, mirrors, build, workspace, ci]
last_reviewed: 2026-03-16
evidence:
  - https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
  - https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
  - https://doc.rust-lang.org/cargo/reference/source-replacement.html
  - https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
  - https://doc.rust-lang.org/cargo/faq.html#how-can-cargo-work-offline
  - https://doc.rust-lang.org/cargo/reference/registry-index.html
  - https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
  - https://github.com/rust-lang/cargo/issues/14821
  - https://github.com/rust-lang/cargo/issues/16141
  - https://github.com/rust-lang/cargo/issues/10134
---

# Problem

Rust already has serious substrate for vendoring, source replacement, local registries, and increasingly for **verified mirroring**.

By early 2026 the Rust project is explicitly discussing a crates.io mirroring and verification system built around secure chain-of-trust ideas, while Cargo’s docs keep a strict lower-level rule in place: source replacement assumes the replacement serves **exactly the same source code** and may not add crates not present in the original source.

Those are important facts, but they still do not answer the questions most teams actually have during offline, mirrored, or source-replaced builds:

- which logical sources really participated in resolution,
- which physical roots or mirrors they collapsed onto,
- what the vendored or mirrored boundary actually covered,
- which dependencies still leaked out to path or git sources,
- and where the answer is a hard Cargo fact versus a manual-review claim.

The new 2026 signal makes one boundary especially important:
**project-level mirror verification is not the same thing as workspace-level source parity.**
A team may have a cryptographically verified mirror and still have a misleading or incomplete local source story because of alias splits, path dependencies, git spillover, or partial vendoring.

So the missing crate is not another mirror implementation and not another TUF system.
The missing crate is a **Cargo vendor & source parity kit**: a crate and cargo-adjacent tool that turns “we use vendoring, source replacement, or mirrors” into a portable **source-identity lock, offline coverage report, mirror-honesty report, and drift bundle**.

# Sharper reading after the 2026 mirroring push

Several current facts make this proposal stronger and narrower than before.

1. The Rust project accepted a crates.io mirroring goal focused on secure verification and experimental infrastructure.
2. The 2026 program update says follow-on work is active and explicitly frames the need as ensuring mirrors serve the same content as crates.io.
3. Cargo source replacement still draws a hard line: replacements are assumed to be exact-source equivalents and are not the right tool for patching or private-registry semantics.
4. Cargo’s registry-index docs say protocol aliasing needs care too: when one registry offers both sparse and git-style protocols, one should be canonical and source replacement can map the other.
5. Cargo’s offline docs still warn that `--offline` can change resolution behavior, which means “offline” is not automatically the same as “equivalent.”
6. `cargo vendor` now has more policy-shaped knobs like `--respect-source-config`, which makes it even more important to preserve where source policy came from.

That means the worthy contribution here is not “download crates better.”
It is the crate that says:

- what source identities were intended,
- what source identities were observed,
- what external verification evidence existed,
- and what parity or coverage gaps remained anyway.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What logical source IDs did this graph use?**
2. **What physical directories, registries, or mirrors did they map onto?**
3. **What was actually covered by vendoring or mirrored/offline policy?**
4. **What outside verification evidence exists, and what does it still not prove?**
5. **Which conclusions are exact Cargo facts versus manual-review judgments?**

That is more useful than another source downloader or mirror daemon.

# What it provides

- `source-contract.toml` — intended source policy: canonical registry URLs, allowed replacement chains, vendored directories, local registries, mirror classes, permitted path/git exceptions, and required offline posture.
- `source-origin.receipt.json` — normalized record of where each resolved package actually came from: registry, directory source, local registry, path, git, or manual override.
- `source-parity.lock` — frozen graph-level record of logical source IDs, replacement chains, protocol aliases, physical roots, and exact/manual-review boundaries.
- `source-coverage.report.json` — states whether the workspace is actually covered by the vendored/mirrored/offline boundary and what still sits outside it.
- `vendor-parity.report.json` — classifies the current setup as `registry_equivalent`, `mirror_verified_but_mixed_sources`, `source_alias_split`, `patch_overlay_present`, `git_history_required`, `path_dependency_external`, `checksum_or_content_drift`, `missing_vendored_member`, `offline_resolution_may_differ`, or `manual_review_required`.
- `mirror-verification.import.json` — optional imported evidence from an external mirror-verification or TUF-style system, recorded as provenance instead of recomputed here.
- `source-replacement.diff.json` — compares two source contracts or receipts across CI/local/devcontainer/release environments.
- `cargo source-parity snapshot` — capture one source-origin and parity bundle.
- `cargo source-parity doctor` — explain whether vendored/source-replaced/mirrored dependencies are honestly aligned with the declared source policy.
- `cargo source-parity diff <old> <new>` — compare source receipts across revisions or environments.
- `*.sourcebundle.zip` — portable artifact for CI debugging, release review, support tickets, and offline-readiness discussion.

# What the crate should provide other people

1. **A boring answer to “what source roots and identities did this build really use?”**
2. **A source-identity lock** that preserves protocol aliases and replacement chains instead of flattening everything into one `vendor/` story.
3. **An offline coverage report** that says what the claimed hermetic boundary does **not** cover.
4. **A mirror-honesty report** that distinguishes external verification evidence from local source-policy truth.
5. **A shared vocabulary** for vendoring, source replacement, sparse/git aliasing, and mixed-source exceptions.
6. **A bridge** between Cargo’s source-management substrate and higher-level crates.io mirroring/verification work.

# Persona / who it’s for

- release engineers preparing offline or mirrored builds
- enterprises with vendored dependency policies
- CI engineers comparing laptop, container, and release-builder source roots
- maintainers debugging “works online, fails offline” incidents
- teams consuming verified mirrors but still needing workspace-level source honesty
- build-system authors who need to explain what remains outside the trusted source boundary

# Users & user stories

- **Release engineer**: “Show whether this vendored tree and replacement chain are still honestly equivalent to the registry policy we think we ship.”
- **CI engineer**: “Explain why the container build and laptop build both pointed at one vendor directory but still used different logical source identities.”
- **Support engineer**: “Tell me whether the offline failure came from path/git spillover, incomplete vendoring, or protocol aliasing.”
- **Security reviewer**: “Record external mirror verification evidence, but also tell me what it does **not** prove about local path and patch behavior.”
- **Tool author**: “Reuse a stable source-parity schema instead of inventing another ad hoc representation of Cargo source state.”

# Prior art (and why it’s insufficient)

- Cargo source replacement and `cargo vendor` provide the raw mechanisms, but not a portable review artifact above them.
- Cargo’s offline docs help set expectations, but explicitly do not guarantee identical resolution outcomes.
- The accepted crates.io mirroring goal and 2026 follow-up work are about **secure mirror verification infrastructure**, not workspace-local parity and coverage diagnosis.
- The archive already has **P-0026 cargo-tuf-mirror**. That proposal is about verified mirrors and trust distribution.
- The archive already has **P-0001 Cargo Snapshot** and **P-0018 Airgap SDK**. Those proposals are about moving or staging Rust dependency substrate across environments.
- Existing path/patch/registry mechanisms are useful, but they do not freeze one small **source-identity and parity bundle** for review.

What remains missing is the **source-parity workflow** that answers: “which logical sources, which physical roots, what external verification evidence, what coverage gaps, and how honest is our offline claim?”

# Design goals

1. **Source-identity first** — preserve logical source IDs and replacement/protocol-alias chains, not just final paths.
2. **Coverage-honest** — say explicitly what remains outside the vendored/mirrored boundary.
3. **Verification-import aware** — record external mirror proofs without pretending to recreate them.
4. **Parity-aware** — distinguish registry-equivalent, mirror-verified-but-mixed, alias-split, patch/path/git, and manual-review cases.
5. **Exactness-aware** — mark what is exact Cargo fact versus conservative diagnosis.
6. **Reviewable** — artifacts should travel cleanly between CI, release, compliance, and support.

# MVP surface

- Minimal types: `SourceContract`, `SourceOriginReceipt`, `SourceParityLock`, `SourceCoverageReport`, `VendorParityReport`, `MirrorVerificationImport`, `SourceReplacementDiff`, `SourceParityBundle`
- Minimal functions:
  - `capture_source_origin_receipt()`
  - `freeze_source_parity_lock()`
  - `evaluate_source_coverage()`
  - `import_mirror_verification()`
  - `classify_vendor_parity()`
  - `diff_source_receipts()`
  - `write_source_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `offline`
  - `markdown`
  - `redaction`

# Compatibility story

- Must remain useful whether teams use registry replacement, `cargo vendor`, local registries, or externally verified mirrors.
- Must treat path and git dependencies as first-class facts rather than flattening them into a fake mirror story.
- Must preserve distinct logical source IDs even when they currently collapse onto one physical root.
- Should work when some source policy comes from layered Cargo config instead of a single manifest.
- Should make it obvious when external mirror verification exists but local workspace source parity is still incomplete.
- Must stay honest when one registry offers both sparse and git-style protocols and source replacement is being used to alias them.

# Conformance & fixtures

- clean registry-to-vendored parity
- sparse/git protocol alias mapped through source replacement
- external mirror verification present while path dependency spillover keeps the workspace from being fully covered
- git dependency where replacement still needs git-history semantics
- missing vendored member or checksum/content drift
- goldens for `registry_equivalent`, `mirror_verified_but_mixed_sources`, `source_alias_split`, `git_history_required`, `path_dependency_external`, `offline_resolution_may_differ`, and `manual_review_required`

Current implementation-shaping target:
- freeze `source-parity.lock`, `vendor-parity.report.json`, and `mirror-verification.import.json`
- prove the model on three scenario bundles before adding deeper content-verification adapters

# Path to boring stability

- Freeze source-identity and coverage vocabulary before adding broad policy engines.
- Treat external verification imports as provenance, not proof of every local claim.
- Keep offline-readiness and registry-equivalence conservative.
- Prefer receipts and diffs over automatic source mutation.
- Preserve exact/manual-review boundaries in every verdict.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that read one workspace’s effective source setup, freeze the logical source identities and replacement chains that actually participated in resolution, import any external mirror-verification evidence, classify whether vendored/source-replaced resolution is honestly equivalent enough, and emit a coverage report naming what still sits outside the trusted boundary.

# De-risk plan

1. Start with registry, directory source, local registry, path, git, and verification-import lanes.
2. Freeze source-identity and coverage vocabulary before deeper content auditing.
3. Validate on one clean vendored workspace, one protocol-alias workspace, and one mixed-source workspace.
4. Avoid becoming a mirror implementation, registry service, or universal hermeticity prover.

# Non-goals

- Not a replacement for Cargo registries or mirrors.
- Not another TUF/mirroring implementation.
- Not a universal proof of hermeticity.
- Not a dependency updater.
- Not a replacement for Cargo’s own fetching or vendoring commands.

# Architecture & API sketch

```rust
pub enum VendorParityClass {
    RegistryEquivalent,
    MirrorVerifiedButMixedSources,
    SourceAliasSplit,
    PatchOverlayPresent,
    GitHistoryRequired,
    PathDependencyExternal,
    ChecksumOrContentDrift,
    MissingVendoredMember,
    OfflineResolutionMayDiffer,
    ManualReviewRequired,
}

pub fn capture_source_origin_receipt(root: &Path, contract: &SourceContract) -> Result<SourceOriginReceipt>;
pub fn freeze_source_parity_lock(receipt: &SourceOriginReceipt, contract: &SourceContract) -> Result<SourceParityLock>;
pub fn evaluate_source_coverage(lock: &SourceParityLock, contract: &SourceContract) -> Result<SourceCoverageReport>;
pub fn import_mirror_verification(path: &Path) -> Result<MirrorVerificationImport>;
pub fn classify_vendor_parity(lock: &SourceParityLock, coverage: &SourceCoverageReport) -> VendorParityReport;
pub fn diff_source_receipts(old: &SourceParityLock, new: &SourceParityLock) -> SourceReplacementDiff;
```

Bundle draft: `source-contract.toml`, `source-origin.receipt.json`, `source-parity.lock`, `source-coverage.report.json`, `vendor-parity.report.json`, `mirror-verification.import.json`, `source-replacement.diff.json`, `notes.md`.

# Security / safety model

- Treat path roots, internal registries, mirror URLs, and filesystem details as potentially sensitive and support redaction.
- Do not claim content equivalence unless the observed facts justify it.
- Preserve the difference between external mirror verification and local workspace source coverage.
- Treat git, path, and manual overrides as first-class policy risks.
- Prefer portable receipts over live mutation of Cargo source configuration.

# Maintenance & governance plan

- Track Cargo source-replacement, vendoring, offline, and registry-index behavior closely.
- Track crates.io mirroring/verification work only as an import boundary, not a feature-catchall.
- Keep the verdict vocabulary small and review-oriented.
- Maintain fixtures for clean parity, protocol aliases, mirror-import-with-spillover, git blockers, and incomplete vendoring.
- Add more source kinds only when they sharpen real workflow review.

# Milestones

## 0.1
- source contract format
- source-origin receipt capture
- source-parity lock
- source-coverage classification
- verification-import record
- parity verdicts

## 0.2
- diff support
- layered-config awareness
- better redaction controls
- protocol-alias coverage

## 0.3
- richer CI/release support-bundle docs
- checksum/content-drift auditing adapters
- policy adapters for hermetic build review

# Open questions

- What is the smallest useful definition of “registry-equivalent enough” when mirror verification is present but path/git spillover remains?
- How much checksum/content verification should the MVP attempt before it becomes a mirror verifier?
- How should the crate model sparse/git protocol aliasing without overclaiming semantic equivalence?
- What is the right imported schema boundary for TUF-style external proofs?

# Sources

- Program management update (crates.io mirroring and verification): https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Secure quorum-based cryptographic verification and mirroring for crates.io: https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- Cargo source replacement: https://doc.rust-lang.org/cargo/reference/source-replacement.html
- `cargo vendor`: https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- Cargo offline FAQ: https://doc.rust-lang.org/cargo/faq.html#how-can-cargo-work-offline
- Cargo registry index docs: https://doc.rust-lang.org/cargo/reference/registry-index.html
- Cargo dependency overrides: https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- Cargo issue #14821: https://github.com/rust-lang/cargo/issues/14821
- Cargo issue #16141: https://github.com/rust-lang/cargo/issues/16141
- Cargo issue #10134: https://github.com/rust-lang/cargo/issues/10134
