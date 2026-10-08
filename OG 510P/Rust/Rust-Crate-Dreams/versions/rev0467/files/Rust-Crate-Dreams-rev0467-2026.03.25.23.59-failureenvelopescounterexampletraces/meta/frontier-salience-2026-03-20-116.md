# Frontier salience snapshot — 2026-03-20 (116)

This pass did **not** open another docs renderer, SemVer checker, or generic rustdoc-JSON consumer.
It deepened **P-0451 Cfg Availability Ledger Kit** by making another product-critical truth explicit:

- **“the docs show it” is still too vague unless the crate can say whether a slice is merely docs-visible, actually downstream-compile-usable, actually doctest-usable, and whether docs.rs default-surface drift changed visibility without changing support.**

## Main judgment

The sharper missing layer is no longer merely “a feature/target availability matrix.”
The sharper missing layer is a **crate-authored usability witness / default-surface drift kit**.

The current Rust documentation substrate now makes that specific:

1. The 2025H2 `doc_cfg` goal says Rust is trying to make item-availability conditions visible in documentation.
2. RFC 3631 says rendered cfg markers help answer why users can see an item but still not use it, while also explicitly not duplicating inactive configurations in docs.
3. rustdoc’s advanced-features docs say `#[cfg(doc)]` can keep items visible in docs while dependent crates still cannot use them, and also say that cfg is not passed to doctests.
4. Cargo’s doctest model remains a separate rustdoc-driven compile/run path, so “docs-visible” and “doctest-usable” are not the same witness.
5. docs.rs now hosts rustdoc JSON but warns consumers to respect `format_version`, which keeps hosted imports from masquerading as timeless direct evidence.
6. docs.rs documents hard hosted-build limits and metadata-driven behavior, which means visible docs surface is partly an environment story.
7. the October 2025 docs.rs default-target shift proved that default visible surface can move even when maintainers do not change explicit support declarations.
8. Cargo feature unification still means slice-specific availability can drift in ways that a coarse docs surface does not capture.

That means the next worthy move is not “another rustdoc dashboard.”
It is one conservative crate family that can publish:

- **usability witness truth**,
- **default-surface drift truth**,
- **audience-specific availability truth**,
- and **reviewable uncertainty** when docs, doctests, and downstream compile slices diverge.

## Why this beat nearby work

The archive already had adjacent lanes for:

- docs.rs parity / issue bundles (**P-0472**),
- whole-project toolchain and target support contracts (**P-0484**),
- public API readiness and SemVer review,
- and raw rustdoc-JSON / docs coverage tooling.

What it still lacked was one compact way to say:

- “this item is visible under `cfg(doc)` but not yet witnessed as downstream-usable,”
- “this doctest compiles in its own path but that does not widen normal downstream availability,”
- and “docs.rs default targets changed what readers see first, but no new supported-target promise was made.”

That is a real receiver-facing product boundary, not just another docs workflow tweak.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
4. **P-0451 Cfg Availability Ledger Kit** — materially stronger after this pass because Rust’s docs substrate is improving, but audience-specific usability truth above it is still missing.
5. **P-0028 open-table-format-kit** — still unusually strong because the Rust lakehouse substrate is finally real while the support contract above it is still weak.
6. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown phase and aftermath truth cut across runtimes.
7. **P-0134 spiffe-identity-kit** — still stronger because the workload-identity contract above live SPIFFE substrate remains missing.
8. **P-0027 text-input-kit** — still unusually strong because edit-path, geometry, and accessibility-mirror truth cut across toolkits.

## What changed in the archive

Added:
- `entries/2026-03-20-296.md`
- `meta/frontier-salience-2026-03-20-116.md`
- `meta/cfg-availability-ledger-usability-boundaries-2026-03-20.md`
- `fixtures/cfg-availability-ledger-kit/usability-witness.receipt.schema.json`
- `fixtures/cfg-availability-ledger-kit/default-surface-drift.report.schema.json`
- `fixtures/cfg-availability-ledger-kit/cfg_doc_visible_item_needs_separate_doctest_and_downstream_usability_witness/README.md`
- `fixtures/cfg-availability-ledger-kit/cfg_doc_visible_item_needs_separate_doctest_and_downstream_usability_witness/usability-witness.receipt.example.json`
- `fixtures/cfg-availability-ledger-kit/docsrs_default_target_shift_changes_default_docs_surface_without_new_support/README.md`
- `fixtures/cfg-availability-ledger-kit/docsrs_default_target_shift_changes_default_docs_surface_without_new_support/default-surface-drift.report.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/cfg-availability-ledger-kit.md`
- `meta/cfg-availability-ledger-product-plan-2026-03-17.md`
- `fixtures/cfg-availability-ledger-kit/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy conditional-API contribution for Rust should now provide more than gate markers and more than one captured matrix.
It should provide:

- one explicit **usability witness receipt**,
- one explicit **default-surface drift report**,
- one compact way to compare docs-visible versus downstream-usable versus doctest-usable truth,
- and one honest way to keep hosted default-surface drift from masquerading as real support growth.

## Freshness anchors

- Rust project goal: `doc_cfg` stabilization — https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- RFC 3631 — https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- rustdoc advanced features (`cfg(doc)`) — https://doc.rust-lang.org/rustdoc/advanced-features.html
- Cargo doctest docs — https://doc.rust-lang.org/cargo/commands/cargo-test.html
- Cargo features docs — https://doc.rust-lang.org/cargo/reference/features.html
- docs.rs builds page — https://docs.rs/about/builds
- docs.rs default-target change announcement — https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- docs.rs rustdoc JSON page — https://docs.rs/about/rustdoc-json
