# Cargo Publish Receipt Join Kit — product plan (2026-03-20)

This note sharpens **P-0477 Cargo Publish Receipt Join Kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a universal publisher, a provenance signing platform, or a registry moderation system.
It should be a **small crate family plus CLI** that helps teams publish one reviewable answer to:

- what exact local package artifact or imported bundle this release receipt is based on,
- which post-publish observations are authoritative for checksum, publish time, identity, and visibility,
- whether Cargo-facing registry observation is complete,
- whether docs/public surfaces are still catching up,
- and what remains partial or manual-review-only after a release event.

The missing value is the **boring post-publish support layer** above today’s `cargo package`, `cargo publish`, crates.io index metadata, trusted publishing identity, and queued docs.rs build surfaces.

## What the crate should provide other people

For maintainers, release engineers, security reviewers, auditors, and incident responders, the crate should provide:

1. **One capture-basis receipt** instead of assuming the local `.crate` artifact still exists where the release ran.
2. **One receipt-authority report** instead of collapsing index truth, CI identity, and public docs visibility into one “publish succeeded” sentence.
3. **One publication-visibility report** instead of leaving teams to guess whether the release is Cargo-ready, docs-pending, or genuinely converged.
4. **One compact joined bundle** that another maintainer can inspect without replaying CI or clicking around multiple services.
5. **One diffable post-publish history** when auth mode, index facts, or visibility lag changes across releases.

## Three new first-class review objects

### 1. Capture-basis receipt

Named classes for `0.1` should focus on where the local artifact truth actually came from, such as:

- `cargo_package_output`
- `cargo_publish_dry_run_output`
- `cargo_publish_intermediate_artifact`
- `imported_ci_artifact`
- `registry_download_reacquired`
- `manual_review_required`

This object should answer:

- whether the receipt used a tarball retained by `cargo package`,
- whether it depended on a `cargo publish --dry-run` or `cargo publish` intermediate artifact,
- whether the local artifact had to be re-imported from CI or re-acquired from the registry,
- whether the digest comes from a local tarball, a downloaded tarball, or only the registry index checksum,
- and whether the artifact’s residency is stable enough for later audit.

### 2. Receipt-authority report

Named classes for `0.1` should focus on which observation is authoritative for which claim, such as:

- `local_artifact_authoritative`
- `index_checksum_and_pubtime_authoritative`
- `publish_identity_authoritative`
- `public_docs_surface_non_authoritative`
- `partial_authority_only`
- `manual_review_required`

This object should answer:

- whether local package bytes were directly observed,
- whether index checksum and `pubtime` have been observed,
- whether publish identity came from explicit trusted-publishing receipts or only coarse CI inference,
- whether docs/public surfaces are merely lagging or are part of the authoritative release truth,
- and what parts of the receipt remain non-authoritative or imported.

### 3. Publication-visibility report

Named classes for `0.1` should focus on convergence state, such as:

- `upload_ack_only`
- `index_visible`
- `index_visible_docs_pending`
- `docs_visible`
- `docs_failed`
- `manual_review_required`

This object should answer:

- whether Cargo-facing index observation is present,
- whether the publish command timed out before the index was observed,
- whether docs.rs is queued, built, failed, or not checked,
- whether the release is ready for Cargo consumers even if docs lag,
- and whether the public story is still partial.

## Recommended `0.1` command surface

### `cargo publish-join capture`
Capture local package facts plus imported post-publish observations and emit:
- `local-package.receipt.json`
- `capture-basis.receipt.json`
- `registry-accept.receipt.json`
- `index-observation.report.json`
- `publish-identity.report.json`

### `cargo publish-join visibility`
Normalize registry/docs visibility into:
- `publication-visibility.report.json`

### `cargo publish-join explain`
Render a human-readable summary of what is authoritative, what is partial, and what remains pending.

### `cargo publish-join diff`
Compare two joined release bundles across auth-mode changes, index visibility changes, or visibility lag patterns.

### `cargo publish-join bundle`
Produce one compact `.publishjoin.zip` containing receipts, notes, and selected imports.

## Recommended crate/workspace split

- `publish_join_model`
- `publish_join_capture`
- `publish_join_index`
- `publish_join_identity`
- `publish_join_visibility`
- `cargo-publish-join`

## `0.1` artifact set

Core artifacts should be:
- `publish-join.lock`
- `local-package.receipt.json`
- `capture-basis.receipt.json`
- `registry-accept.receipt.json`
- `index-observation.report.json`
- `publish-identity.report.json`
- `receipt-authority.report.json`
- `publication-visibility.report.json`
- `publish-notes.summary.md`

## Discovery order

1. **Capture local package basis**
   - direct `cargo package` or dry-run tarball
   - retained publish artifact when still present
   - imported CI artifact
   - registry re-download only if needed
2. **Observe registry/index facts**
   - checksum
   - `pubtime`
   - `yanked` state
   - incomplete / timed-out observation state
3. **Observe publish identity**
   - trusted-publisher receipt
   - provider/repository/workflow identity when available
   - token/manual/coarse CI inference when not
4. **Normalize authority**
   - what is authoritative for bytes
   - what is authoritative for publish time
   - what is authoritative for identity
   - what is merely lagging public visibility
5. **Normalize visibility**
   - index visible or not
   - docs.rs queued / built / failed / not checked
   - receiver-facing readiness class
6. **Render bundle / diff**
   - compact notes
   - release-to-release drift
   - manual-review-required causes

## Ranking discipline

A good `0.1` should not let “published” become the whole contract.
It should keep separate:

- `capture_basis_known`
- `index_authority_known`
- `publish_identity_known`
- `public_visibility_known`
- `partial_receipt`
- `manual_review_required`

Do not let the tool flatten any of these into one success verdict.

## Recommended first proving grounds

1. **Tarball retention drift**
   - a release run where `cargo publish` no longer leaves a final `.crate` artifact under `build.build-dir`
2. **Index authoritative, docs lagging**
   - index checksum and `pubtime` observed while docs.rs is still queued
3. **Publish poll timeout**
   - `cargo publish` timed out waiting for the index, but a later observation completes the receipt
4. **Identity drift**
   - token/manual publish replaced by trusted publishing on a later release

## Non-goals for `0.1`

- Not a replacement for `cargo publish`
- Not a provenance attestation framework
- Not a docs.rs parity tool
- Not a malware-reporting or registry moderation surface
- Not a universal multi-registry abstraction

## Freshness anchors

- `cargo publish` command docs — https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- Publishing on crates.io — https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo registry index format — https://doc.rust-lang.org/cargo/reference/registry-index.html
- Rust release notes — https://doc.rust-lang.org/beta/releases.html
- crates.io development update (2026-01-21) — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io development update (2025-02-05) — https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- docs.rs builds page — https://docs.rs/about/builds
