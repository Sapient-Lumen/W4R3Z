# Rustdoc JSON Support Contract Kit — frontier note (2026-03-23)

This note records the sharper frontier for **P-0051 Rustdoc JSON Support Contract Kit**.

## Main judgment

The next missing layer is **not** another parser and **not** another consumer-specific compatibility shim.
The sharper missing layer is a reviewable support contract for:

1. **source route**,
2. **format-version / toolchain windows**,
3. **normalization loss**,
4. **portable support bundles**.

## Why this is sharper now

Current primary sources make the seam much more concrete than before:

- rustdoc still documents JSON output as experimental;
- Cargo still documents `output-format` for rustdoc as unstable;
- docs.rs now hosts rustdoc JSON directly and tells consumers to inspect `format_version`;
- docs.rs keeps older format-version downloads around after rebuilds, and older releases may still lack downloadable JSON until rebuild coverage reaches them;
- the cargo-semver-checks goal now states very plainly that one tool can support a range of rustdoc JSON formats at once, while still documenting important blind spots like cross-crate item visibility and manifest-only SemVer changes.

That means the archive should stop treating “we parse rustdoc JSON” as one sufficient support statement.

## Receiver-facing truths worth shipping

A credible next iteration should export:

- `source-route.receipt.json`
- `format-window.matrix.json`
- `normalization-loss.report.json`
- `rustdoc-json-support-bundle.manifest.json`

## Scope guardrail

Keep this lane distinct from:

- **P-0472** docs.rs build parity (hosted-vs-local docs build behavior),
- **P-0536** crate knowledge packs (assistant/search handoff),
- **P-0455** doctest extraction,
- and consumer-specific semver or docs frontends.

P-0051 should own the **raw JSON support contract** those lanes can import.
