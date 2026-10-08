# Frontier salience refresh — 2026-03-22 (197)

## Why P-0455 deserved another pass

The archive already had a strong first pass for **P-0455 Doctest Extraction & Support Contract Kit**:
manifest extraction, rewrite lineage, execution-mode receipts, support-class reporting, and drift.
The remaining weak point was not “can we run doctests?”
It was **basis and comparability honesty**.

Current official and primary sources make that gap concrete:

1. The 2025 State of Rust survey still says online documentation is Rust’s preferred canonical reference, even as some learning traffic shifts toward LLM tooling.
2. The Rust-for-Linux tooling goal explicitly asks for stable rustdoc features to **extract and customize doc tests**.
3. The current rustdoc unstable-features docs expose `--output-format doctest` JSON with an explicit `format_version`, raw/original code, rewritten code, wrapper details, and computed doctest attributes.
4. The rustdoc docs keep preprocessing rules explicit: hidden lines, crate injection, wrapper insertion, and `#[cfg(doctest)]` all materially affect what gets compiled.
5. The current doctest docs and Rust 2024 edition guide make merged doctests a real semantic mode, with `standalone_crate` required when line-sensitive examples would otherwise drift.
6. Cargo’s current `cargo test` docs still warn that doctest execution details are not guaranteed and may change, which makes naive “the run passed before” comparisons weaker than they first appear.
7. Current release notes keep cross-compiled doctests, target-specific `ignore-*`, and stable `--test-runtool` / `--test-runtool-arg` in the official substrate.

That makes the sharper missing value here less “another docs tool” and more a **support-contract layer for extraction authority, grouping comparability, and portable handoff bundles**.

## Main ranked takeaway

**P-0455 Doctest Extraction & Support Contract Kit** remains a worthy high-salience lane because it can now offer something adjacent crates still do not:

- an `extraction-basis.receipt` for *what authority and format produced the manifest*,
- a `grouping-comparison.report` for *whether two doctest bundles can be compared honestly at all*,
- and a `doctest-support-bundle.manifest` that keeps basis, rewrites, execution mode, support classes, and drift separate.

## Why this beat adjacent ideas this pass

It beat another docs.rs parity pass because **P-0472** already owns hosted build/sandbox parity.
The unresolved question here was more local and more review-critical: *what exact doctest authority produced this manifest, and is this bundle comparable to the last one?*

It beat another coverage pass because **P-0476** and **P-0433** already own coverage and MC/DC evidence questions.
The unresolved question here was example-support truth above rustdoc’s extraction and grouping substrate.

It beat another runner-profile pass because **P-0481** already owns target/emulator runner policy.
What remained missing here was a basis/comparability contract that can import those runner facts without pretending they are the whole story.

## Boundaries to keep sharp

P-0455 should now own:

1. extraction-basis truth,
2. doctest manifest inventory,
3. rewrite-lineage honesty,
4. execution-mode truth,
5. support-class reporting,
6. grouping/comparison honesty,
7. docs-example drift,
8. and portable doctest-support bundles.

It should not silently become:

- a generic docs portal,
- a hosted docs.rs reproducer,
- a target/emulator runner framework,
- a public-API visibility checker,
- or a generic coverage dashboard.
