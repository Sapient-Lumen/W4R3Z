# Frontier salience snapshot — 2026-03-20 (118)

This pass did **not** open another publish orchestrator, provenance system, or registry-auth doctor.
It deepened **P-0477 Cargo Publish Receipt Join Kit** by making another release-support truth explicit:

- **“the crate was published” is still too vague unless the crate can say what local artifact the receipt came from, which observations are authoritative, and which public surfaces have actually converged.**

## Main judgment

The sharper missing layer is no longer merely “local digest + registry checksum + publish identity”.
The sharper missing layer is a **capture-basis / receipt-authority / publication-visibility contract**.

Current Cargo and ecosystem signals make that specific:

1. `cargo publish` uploads and then polls the index, but may timeout, so completion/visibility can remain partial.
2. Cargo’s publishing guide still points maintainers at the generated `.crate` and `cargo package --list` as the practical source-bundle review surface.
3. Rust 1.93.1 says `cargo publish` no longer keeps `.crate` tarballs as final artifacts when `build.build-dir` is set, and warns that `cargo package` is the right path when a retained tarball artifact matters.
4. The index format now documents `pubtime` and says index JSON should not be modified after insertion except for `yanked`, which makes index observation a different authority class from other public surfaces.
5. docs.rs automatically builds docs for released crates, but says builds may take a while because of the queue.
6. crates.io’s 2025–2026 updates made publish identity more visible via trusted publishing, trusted-publishing-only mode, and publish notifications.

That means the next worthy move is not another uploader.
It is one conservative crate family that can publish:

- **capture basis truth**,
- **receipt authority truth**,
- **publication visibility truth**,
- and **reviewable blame** when local artifacts, index facts, and public docs surfaces diverge in time.

## Why this beat nearby work

The archive already had adjacent lanes for:

- trusted-publishing rehearsal,
- registry-auth diagnosis,
- provenance attestations,
- docs.rs parity,
- and package review.

What it still lacked was one compact way to say:

- “this receipt came from `cargo package`, not from a tarball still lying around after `cargo publish`,"
- “the index checksum and `pubtime` are authoritative even while docs are still queued,”
- and “the upload probably succeeded, but the authoritative post-publish observation is still partial.”

That is a real receiver-facing product boundary, not another CI convenience.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
4. **P-0477 Cargo Publish Receipt Join Kit** — materially stronger after this pass because Cargo/crates.io/docs.rs now expose enough substrate for honest post-publish receipts, but not the contract above it.
5. **P-0036 MSRV Workspace Lab** — still unusually strong because Cargo policy/resolver/lockfile support remains easy to overclaim.
6. **P-0451 Cfg Availability Ledger Kit** — still unusually strong because docs-visible truth remains weaker than usable-support truth.
7. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown phase and aftermath truth cut across runtimes.
8. **P-0011 Crate Health Contract Kit** — still very strong because support/succession posture remains distinct from trust or release identity.

## What changed in the archive

Added:
- `entries/2026-03-20-298.md`
- `meta/frontier-salience-2026-03-20-118.md`
- `meta/cargo-publish-receipt-join-product-plan-2026-03-20.md`
- `meta/cargo-publish-receipt-visibility-boundaries-2026-03-20.md`
- `fixtures/cargo-publish-receipt-join-kit/capture-basis.receipt.schema.json`
- `fixtures/cargo-publish-receipt-join-kit/receipt-authority.report.schema.json`
- `fixtures/cargo-publish-receipt-join-kit/publication-visibility.report.schema.json`
- scenario families for tarball-retention drift, index-authority vs docs lag, and partial post-publish visibility

Updated:
- `README.md`
- `INDEX.md`
- `proposals/cargo-publish-receipt-join-kit.md`
- `fixtures/cargo-publish-receipt-join-kit/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy post-publish contribution for Rust should now provide more than a checksum join.
It should provide:

- one explicit **capture-basis receipt**,
- one explicit **receipt-authority report**,
- one explicit **publication-visibility report**,
- and one honest way to keep “upload accepted”, “index authoritative”, and “public docs visible” from masquerading as one release fact.

## Freshness anchors

- `cargo publish` command docs — https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- Publishing on crates.io — https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo registry index format — https://doc.rust-lang.org/cargo/reference/registry-index.html
- Rust release notes — https://doc.rust-lang.org/beta/releases.html
- crates.io development update (2026-01-21) — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io development update (2025-02-05) — https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- docs.rs builds page — https://docs.rs/about/builds
