---
id: P-0477
title: Cargo Publish Receipt Join Kit — local package facts, registry confirmations, publish identity, and release-history diffs
status: idea
domains: [cargo, publishing, registries, supply-chain, ci, release-engineering, auditing]
last_reviewed: 2026-03-23
evidence:
  - https://doc.rust-lang.org/cargo/reference/publishing.html
  - https://doc.rust-lang.org/cargo/reference/registry-index.html
  - https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
  - https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
  - https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
  - https://doc.rust-lang.org/cargo/reference/registries.html
  - https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://docs.rs/about/builds
---

# Problem

Rust now has enough publish substrate that the missing value is no longer another generic “release helper”.

The substrate is real:

- `cargo publish` and `cargo publish --dry-run` already package, verify, and upload crates,
- the registry index records checksums and additional per-version metadata,
- trusted publishing gives crates.io a modern OIDC-backed publish-identity path,
- crates.io now exposes **GitLab trusted publishing support**, **trusted-publishing-only mode**, and **`pubtime`** in index entries,
- and crate owners can receive **publish notifications**, which makes unauthorized or unexpected publishes easier to notice.

At the same time, crates.io’s February 2026 malicious-crate policy update clarified something important: incident communication and RustSec advisories remain a separate lane from routine publish-time evidence and release-history capture.

The March 21, 2026 Cargo advisory makes a second boundary newly important. It says crates.io deployed an upload-side mitigation on March 13 and audited all crates ever published there, but it also says alternate-registry users should verify their exposure with the registry vendor and that older Cargo on alternate registries may remain vulnerable even after Rust 1.94.1 ships. That means publish receipts now need to record not just *what was published*, but *what registry lane and protection scope the receipt actually depends on*.

That leaves a sharp maintainer gap.

Ordinary teams still lack a boring answer to questions like:

- did the `.crate` we reviewed locally match what the registry actually indexed,
- what checksum, `pubtime`, yanked-state, and identity facts should we archive for this release,
- was the release manual, token-based, or trusted-publisher based,
- did the expected repository / workflow / environment identity match what we believe happened,
- how do we compare two releases when the authentication mode or crates.io policy changed,
- what local artifact did our receipt actually come from once `cargo publish` stops leaving a durable tarball behind in some build-dir layouts,
- which post-publish observations are authoritative versus merely lagging public surfaces,
- and what single artifact should an auditor or incident responder inspect instead of CI logs, index fetches, screenshots, and emails?

The missing crate is not another publisher.
The missing crate is a **publish receipt join kit**: a cargo-adjacent crate that joins local package facts, registry/index confirmation, publish identity, and release-history drift into one portable receipt.

# What it provides

- `publish-join.lock` — declares registry target, packages/versions in scope, local digest policy, index-observation policy, identity expectations, and redaction posture.
- `local-package.receipt.json` — records local package facts: package path, tarball size, digest, Cargo version, dry-run outcome, and optional review-bundle references.
- `registry-accept.receipt.json` — captures registry-observed confirmation facts: package, version, checksum, yanked state, and index presence.
- `publish-identity.report.json` — records publish mode (`manual`, `token`, `trusted-publisher`), provider family when visible, and claim-level caveats.
- `capture-basis.receipt.json` — records what local or imported artifact the joined receipt actually used, including whether the tarball was retained locally, imported from CI, or re-acquired from the registry.
- `index-observation.report.json` — captures index metadata such as checksum, `pubtime`, schema caveats, and whether observation is complete or partial.
- `receipt-authority.report.json` — separates which receipt slices are authoritative for bytes, publish time, identity, and public visibility.
- `publication-visibility.report.json` — records whether the index is visible, whether docs.rs is queued/built/failed, and whether the release is Cargo-ready versus fully public-surface-ready.
- `registry-capability.receipt.json` — records which registry-side capabilities/enrichments actually apply to this release lane (`pubtime`, TP-only visibility, docs coupling, notifications, advisory posture) without pretending every registry matches crates.io.
- `protection-scope.report.json` — records which protective claims were actually in scope for the selected registry and client-version window, including crates.io-specific mitigations, historical audit coverage, and alternate-registry unknowns.
- `publish-join-bundle.manifest.json` — portable inventory of the joined publish-review pack so local bytes, identity, registry capability, protection scope, and visibility remain reopenable together.
- `publish-receipt.diff.json` — compares two release receipts and classifies `checksum_match`, `checksum_mismatch`, `publish_mode_changed`, `identity_drift`, `pubtime_missing`, `manual_review_required`, and `registry_observation_delayed`.
- `cargo publish-join capture --after <publish>` — generate one joined receipt.
- `cargo publish-join verify <receipt>` — re-check checksum and identity expectations against current observations.
- `cargo publish-join diff <old> <new>` — compare releases over time.
- `*.publishjoin.zip` — portable audit / incident / release-history artifact.

# What the crate should provide other people

1. **A boring post-publish receipt** that joins local package review with registry-visible confirmation.
2. **A release-history artifact** that captures checksum, `pubtime`, yanked state, and publish mode in one place.
3. **A capture-basis receipt** that says what the local artifact truth actually came from.
4. **A publish-identity record** that stays distinct from deeper provenance attestations.
5. **A visibility-state report** that keeps index readiness distinct from docs/public-surface convergence.
6. **A registry-capability receipt** so crates.io-specific enrichments and protections do not get silently generalized to alternate registries.
7. **A protection-scope report** so upload blocking, audits, advisory visibility, and client-version caveats remain visible.
8. **A diffable audit surface** when workflows migrate from manual or token publishing to trusted publishing or between different registry lanes.
9. **A compact incident handoff artifact** when maintainers need to investigate an unexpected release event.

# Persona / who it’s for

- maintainers publishing security-sensitive or business-critical crates
- release engineers running mixed manual and CI releases
- organizations adopting trusted-publishing-only mode
- auditors reviewing release history
- incident responders reconstructing suspicious or unexpected publishes

# Users & user stories

- **Maintainer**: “Show that the crate I dry-ran locally is the same package the registry indexed.”
- **Release engineer**: “Record whether this release used trusted publishing, and whether the identity surface matched expectations.”
- **Auditor**: “Give me one compact receipt with checksum, publish mode, publish time, and index facts.”
- **Incident responder**: “Compare two releases and tell me whether the auth mode, checksum, or index observations changed.”

# Prior art (and why it’s insufficient)

- Cargo’s publishing docs explain the mechanics of publishing, but they do not leave a durable joined receipt.
- The registry index stores checksums and other low-level metadata, but it is not itself a review artifact.
- crates.io trusted publishing improves **how** a release is authorized, but it does not join local package review and registry observation.
- crates.io publish notifications help detect suspicious release events, but they are not a durable release-history bundle.
- crates.io’s malicious crate notification policy clarifies how malware incidents are communicated, but that is still a separate lane from routine publish receipts.
- The archive already has **P-0175 Trusted Publishing Tooling Kit**, which is about **rehearsal and provider/trigger policy before publish**.
- The archive already has **P-0015 Cargo Attest**, which is about **artifact provenance and attestation publication**.

What remains missing is the **join layer** above package review, registry metadata, and publish identity.


## 2026-03-23 registry-coverage refresh

This proposal is stronger now because current crates.io and Cargo material no longer supports one flat “registry publish succeeded” story.

Three current facts especially matter:

- crates.io now has meaningful publish-side enrichments such as Trusted Publishing Only mode, blocked-trigger policy for trusted publishing, and `pubtime` in index entries;
- Cargo’s registries docs still frame alternate registries as a capability-based surface where publishing depends on what the registry actually implements;
- the March 2026 Cargo advisory explicitly distinguishes crates.io mitigations from alternate-registry exposure and says alternate-registry users should verify with the registry vendor.

That means this crate should promote three more receiver-facing review objects into first-class status:

- `registry-capability.receipt.json`
- `protection-scope.report.json`
- `publish-join-bundle.manifest.json`

The missing value is therefore not just a joined post-publish receipt.
It is a joined receipt that can say **what this registry lane can tell us**, **what protections actually applied**, and **where manual review still begins**.

# Design goals

1. **Join-first** — connect facts that already exist in different systems.
2. **Capture-basis-explicit** — the receipt must say what concrete artifact it used.
3. **Checksum-grounded** — local package and registry checksum facts must remain first-class.
4. **Identity-explicit** — publish authorization mode must be visible but not over-claimed.
5. **Authority-honest** — index facts, imported identity receipts, and lagging public surfaces must not be flattened together.
6. **Registry-honest** — model crates.io enrichments like `pubtime` explicitly, without pretending other registries expose the same facts.
7. **Audit-friendly** — export compact, redacted, durable artifacts.

# MVP surface

- Minimal types: `PublishJoinLock`, `LocalPackageReceipt`, `CaptureBasisReceipt`, `RegistryAcceptReceipt`, `PublishIdentityReport`, `IndexObservationReport`, `ReceiptAuthorityReport`, `PublicationVisibilityReport`, `PublishReceiptDiff`, `PublishJoinBundle`
- Minimal functions:
  - `capture_publish_join_bundle()`
  - `compute_local_package_receipt()`
  - `capture_basis_receipt()`
  - `observe_registry_index_entry()`
  - `build_publish_identity_report()`
  - `build_receipt_authority_report()`
  - `build_publication_visibility_report()`
  - `diff_publish_receipts()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `crates-io`
  - `trusted-publishing`
  - `markdown`

# Compatibility story

- Works for manual publish flows, token-based CI flows, and trusted-publishing flows.
- Must distinguish facts from:
  - local package generation,
  - registry/index observation,
  - and CI/provider identity material.
- Should remain useful when index observation is delayed or partial.
- Must distinguish index authority from docs/public-surface lag.
- Must not claim that publish notifications or RustSec advisories are part of the same artifact lane.
- Should compose with provenance attestations rather than duplicating them.

# Conformance & fixtures

- One fixture for manual publish with local package receipt plus later index observation.
- One fixture for trusted publishing with repository/workflow/environment identity and trusted-publishing-only expectations.
- One fixture where local package digest and observed registry checksum disagree.
- One fixture where the receipt must record a capture basis because `cargo publish` no longer left a durable local tarball artifact.
- One fixture where index facts are authoritative while docs/public surfaces are still catching up.
- One fixture where publish mode changes across releases and should surface as a review event.
- One fixture where crates.io-only enrichments and TP-only posture must not be generalized to an alternate registry.
- One fixture where a crates.io mitigation/audit story still leaves alternate-registry protection scope at manual review.
- Goldens for `checksum_match`, `checksum_mismatch`, `trusted_publisher_verified`, `capture_basis_known`, `index_visible_docs_pending`, `publish_mode_changed`, and `manual_review_required`.

# Path to boring stability

- Freeze the join schema before adding many registry-specific enrichments.
- Start with crates.io-first observation and diffing.
- Keep identity categories coarse and reviewable.
- Prefer explicit partial receipts over pretending every publish exposes the same evidence.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that record one local package digest, fetch or ingest the corresponding registry/index facts, label the publish authorization mode, and emit one diffable post-publish receipt bundle.

# De-risk plan

1. Start with crates.io-first observation before attempting multi-registry support.
2. Keep identity capture coarse: provider family, workflow/repository/environment, and policy mode.
3. Treat delayed index observation as first-class partial data.
4. Make capture basis explicit instead of assuming the publish-run tarball is still on disk.
5. Validate on one manual flow and one trusted-publishing CI flow.

# Non-goals

- Not a replacement for `cargo publish`.
- Not a provenance attestation system.
- Not another CI publish orchestrator.
- Not a malware-notification or RustSec advisory system.

# Architecture & API sketch

```rust
pub struct RegistryAcceptReceipt {
    pub package: String,
    pub version: String,
    pub checksum_sha256: String,
    pub pubtime: Option<String>,
    pub publish_mode: String,
}

pub fn capture_publish_join_bundle(root: &Path, package: &str) -> Result<PublishJoinBundle>;
pub fn compute_local_package_receipt(root: &Path, package: &str) -> Result<LocalPackageReceipt>;
pub fn observe_registry_index_entry(registry: &str, package: &str, version: &str) -> Result<IndexObservationReport>;
pub fn diff_publish_receipts(old: &PublishJoinBundle, new: &PublishJoinBundle) -> PublishReceiptDiff;
```

Bundle draft: `publish-join.lock`, `local-package.receipt.json`, `capture-basis.receipt.json`, `registry-accept.receipt.json`, `publish-identity.report.json`, `index-observation.report.json`, `receipt-authority.report.json`, `publication-visibility.report.json`, `registry-capability.receipt.json`, `protection-scope.report.json`, `publish-join-bundle.manifest.json`, `publish-receipt.diff.json`, `notes.md`.

# Security / safety model

- Redact access tokens, OIDC tokens, and sensitive CI env values by default.
- Preserve enough identity metadata to support review without leaking secrets.
- Never claim registry confirmation before an actual observation or trusted imported receipt exists.
- Treat publish-mode inference as best-effort unless the workflow/provider emitted explicit trusted-publishing facts.

# Maintenance & governance plan

- Track crates.io publishing docs, index metadata evolution, and trusted-publishing changes.
- Keep schemas compact and versioned.
- Maintain fixtures for manual, token, trusted-publishing, and delayed-observation cases.
- Publish guidance on how publish receipts compose with trusted-publishing rehearsal and provenance attestations.

# Milestones

## 0.1
- local package receipt
- index observation
- bundle export

## 0.2
- publish identity report
- receipt diffing
- CI adapters for common trusted-publishing flows

## 1.0
- stable bundle schema
- curated release-history corpus
- issue/audit-template integrations

# Open questions

- What is the smallest identity vocabulary that is still useful across manual, token, and trusted-publisher releases?
- How should delayed or eventually consistent registry/index observations be represented?
- Which visibility states should be first-class without turning the crate into a general service monitor?
- Which crates.io-specific enrichments belong in the core schema versus optional adapters?

# Sources

- Publishing on crates.io: https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo registry index format: https://doc.rust-lang.org/cargo/reference/registry-index.html
- RFC 3691 trusted publishing: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
- crates.io development update (GitLab support, trusted-publishing-only mode, `pubtime`): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io development update (publish notifications): https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- crates.io malicious crate notification policy update: https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
