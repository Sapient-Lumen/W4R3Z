# Rustdoc JSON Support Contract Kit — version-window plan (2026-03-23)

This note sharpens the next implementation step for **P-0051**.

## Main judgment

The next `0.2`-quality surface should make four truths boring to export:

1. where the JSON came from,
2. which `format_version` / toolchain windows are truly supported,
3. what the normalized IR lost or downgraded,
4. and what bundle another tool can reopen later.

## New receiver-facing artifacts worth shipping

- `source-route.receipt.json`
- `format-window.matrix.json`
- `normalization-loss.report.json`
- `rustdoc-json-support-bundle.manifest.json`

## What each artifact should do

### `source-route.receipt.json`
Record:
- local-vs-import route,
- generator/import authority,
- toolchain selector,
- target triple,
- crate identity,
- observed `format_version`,
- compression and redirect notes for docs.rs imports,
- and whether the route is direct, imported, or mixed.

### `format-window.matrix.json`
Record:
- supported format-version spans,
- adapter classes,
- support class (`native`, `translated`, `legacy-import-only`, `unsupported`),
- query classes that are considered safe or provisional,
- and any toolchain-window notes.

### `normalization-loss.report.json`
Record:
- raw facts omitted from the stable IR,
- unresolved cross-crate references,
- missing manifest-only facts,
- intentionally downgraded relations,
- and whether downstream manual review is required.

### `rustdoc-json-support-bundle.manifest.json`
Bundle route, window, raw/normalized file paths, and loss report without flattening them.

## What the crate should provide other people

A good implementation should let another engineer answer:

- “Did this JSON come from a local nightly build, docs.rs, or rustup toolchain docs?”
- “Does the consumer actually support this `format_version`?”
- “Which information was preserved versus only partially represented?”
- “Can I safely build a semver or docs query above this capture, or do I need manual review?”

## Guardrails

Keep separate:
- parse success,
- format-window support,
- normalization quality,
- and downstream query confidence.

A crate that only parses or only downloads files still sits below the missing support layer.
