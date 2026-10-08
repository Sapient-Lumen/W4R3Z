# Frontier salience snapshot — 2026-03-20 (119)

This pass did **not** open another publisher, provenance verifier, or docs.rs lane.
It deepened **P-0470 Cargo Package Review Kit** by making another release-review truth explicit:

- **“we reviewed the package” is still too vague unless the crate can say which surface was authoritative, which packaged paths were copied or generated, and which mutations happened only after unpacking for verification.**

## Main judgment

The sharper missing layer is no longer merely “path listing + normalization summary + bundle diff”.
The sharper missing layer is an **packaged-surface / archive-authority / extraction-mutation contract**.

Current Cargo signals make that specific:

1. `cargo package` still defines the canonical packaged source bundle and then immediately extracts it again for verification.
2. Cargo’s package docs now expose a machine-readable path-origin story via `--list --message-format json`, including `Cargo.toml.orig` plus `copy`/`generate` lineage for packaged paths.
3. Cargo explicitly documents that `.cargo_vcs_info.json` is best effort and not provenance, which leaves “what bytes were actually reviewed?” as a separate problem.
4. Cargo’s changelog now calls out deterministic timestamps for generated files in tarballs and mtime updates after unpacking, which means extracted verification trees are not a transparent mirror of archive bytes.
5. Rust 1.93.1 explicitly tells maintainers to use `cargo package` when they need durable `.crate` artifacts, which makes raw archive capture more central to honest review.
6. Long-running tool authors have already reported that extracted packages differ from originally uploaded bytes because of `.cargo-ok` and manifest rewriting.

That means the next worthy move is not another checklist.
It is one conservative crate family that can publish:

- **packaged-surface truth**,
- **archive-authority truth**,
- **extraction-mutation truth**,
- and **reviewable blame** when authored trees, raw archives, and verification extracts diverge.

## Why this beat nearby work

The archive already had adjacent lanes for:

- post-publish receipt joins,
- trusted-publishing rehearsal,
- source parity / vendoring,
- docs.rs parity,
- and provenance / attestation work.

What it still lacked was one compact way to say:

- “the review approved raw `.crate` bytes, not just a later extraction,”
- “this path exists because Cargo generated or copied it during packaging,”
- and “this verification tree gained mutation after unpack, so do not hash or sign it as if it were the original archive.”

That is a real receiver-facing product boundary, not another CI convenience.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
4. **P-0470 Cargo Package Review Kit** — materially stronger after this pass because Cargo now exposes enough packaging substrate to make raw-archive review honest rather than folkloric.
5. **P-0477 Cargo Publish Receipt Join Kit** — still unusually strong because post-publish convergence is a different truth from pre-publish review.
6. **P-0036 MSRV Workspace Lab** — still unusually strong because Cargo policy/resolver/lockfile support remains easy to overclaim.
7. **P-0451 Cfg Availability Ledger Kit** — still unusually strong because docs-visible truth remains weaker than usable-support truth.
8. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown phase and aftermath truth cut across runtimes.

## What changed in the archive

Added:
- `entries/2026-03-20-299.md`
- `meta/frontier-salience-2026-03-20-119.md`
- `meta/cargo-package-review-product-plan-2026-03-20.md`
- `meta/cargo-package-review-extraction-boundaries-2026-03-20.md`
- `fixtures/cargo-package-review-kit/packaged-surface.receipt.schema.json`
- `fixtures/cargo-package-review-kit/archive-authority.report.schema.json`
- `fixtures/cargo-package-review-kit/extraction-mutation.report.schema.json`
- scenario families for authored-vs-packaged manifest basis and extraction-only mutations after unpack

Updated:
- `README.md`
- `INDEX.md`
- `proposals/cargo-package-review-kit.md`
- `fixtures/cargo-package-review-kit/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy package-review contribution for Rust should now provide more than a list of included paths.
It should provide:

- one explicit **packaged-surface receipt**,
- one explicit **archive-authority report**,
- one explicit **extraction-mutation report**,
- and one honest way to keep authored trees, packaged bytes, and verification-only mutations from masquerading as one review surface.

## Freshness anchors

- `cargo package` command docs — https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Publishing on crates.io — https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo changelog — https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust release notes — https://doc.rust-lang.org/beta/releases.html
- Cargo 1.90 development-cycle update — https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- `.cargo-ok` / modified extracted tree integrity issue — https://github.com/rust-lang/cargo/issues/6340
