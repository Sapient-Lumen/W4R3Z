---
id: P-0295
title: ORC Interop & Canonicalization Kit — stable Arrow/ORC round-trips, semantic diffs, and evidence bundles
status: idea
domains: [data, analytics, file-formats, interoperability, lakehouse]
last_reviewed: 2026-03-06
evidence:
  - https://orc.apache.org/specification/
  - https://orc.apache.org/specification/ORCv1/
  - https://crates.io/crates/orc-rust
---

# Problem

The Rust ORC story is improving quickly, but the ecosystem still lacks a **boring, trusted interop layer** for ORC round-trips, capability reporting, and canonical diffs. `orc-rust` is becoming strong enough that a fresh “replace everything” proposal would be wrong. The real gap is the missing layer around it:

- stable fixture corpora,
- deterministic metadata normalization,
- explainable semantic diffs,
- feature-capability reporting (compression, bloom filters, encryption, predicate pushdown expectations),
- shareable bug bundles.

# What it provides

- `orc-canon` — normalize schemas, stripes, statistics, and metadata into a stable IR.
- `orc-diff` — semantic ORC vs ORC and ORC vs Arrow comparisons.
- `orc-fixtures` — cross-engine fixture packs and round-trip test corpora.
- `orc-inspect` — capability/feature report for a file.
- `cargo orc` — inspect, normalize, diff, and emit `*.orcbundle.zip` artifacts.

# Users & user stories

- **Data infrastructure teams**: “Did this rewrite change meaning or only encoding/layout?”
- **Engine authors**: “Can we validate our ORC output against a known-good corpus?”
- **Lakehouse teams**: “Share one small bug bundle instead of the full production file.”
- **Arrow/DataFusion maintainers**: “Expose capability mismatches clearly instead of vague reader errors.”

# Prior art (and why it’s insufficient)

- `orc-rust` is a real native Rust implementation and should be treated as the main substrate, not duplicated.
- Older crates such as `orc-format` and `orcrs` help demonstrate prior demand but do not define a shared canonicalization/evidence layer.
- Apache ORC docs explain the file format and features like column encryption, but not a Rust-native conformance workflow.

# Design goals

1. **Complement, do not compete with, `orc-rust`.**
2. **Semantic diffs over byte diffs** — distinguish layout changes from data meaning changes.
3. **Small repro bundles** — subset/stripe extraction for issue reports.
4. **Feature-awareness** — bloom filters, encryption, compression, stripe stats, indexes.
5. **Arrow-native UX** — compose naturally with Arrow/DataFusion tooling.

# Non-goals

- Not a new ORC engine.
- Not a replacement for large-scale query execution engines.
- Not a warehouse catalog layer.

# Architecture & API sketch

```rust
pub struct OrcFeatureReport {
    pub schema: SchemaSummary,
    pub compression: Vec<CompressionKind>,
    pub encrypted_columns: Vec<String>,
    pub has_bloom_filters: bool,
}

pub fn canonicalize<R: std::io::Read>(reader: R) -> Result<CanonicalOrc, Error>;
pub fn semantic_diff(a: &CanonicalOrc, b: &CanonicalOrc) -> DiffReport;
```

Bundle draft: `report.json`, `schema.json`, `stats.json`, `subset.orc`, `canonical.json`, `notes.md`.

# Security / safety model

- Default issue bundles should permit row/stripe subsetting and hashing.
- Treat ORC parsing as hostile-input territory: size limits, decompression limits, recursion bounds.
- Avoid leaking raw plaintext from encrypted-column files unless explicitly requested.

# Maintenance & governance plan

- Track Apache ORC spec versions and `orc-rust` releases explicitly.
- Co-own fixture corpora with DataFusion/Arrow-adjacent users where possible.
- Keep canonicalization rules versioned and additive.

# Milestones

## 0.1
- Feature report
- Canonical metadata IR
- Semantic diff for schemas/statistics

## 0.2
- Bundle subsetting
- Cross-engine fixture corpus
- Arrow round-trip assertions

## 1.0
- Stable `*.orcbundle.zip`
- CI-friendly conformance suite
- Clear interop guidance for `orc-rust` adopters

# Open questions

- Which metadata fields should be normalized versus preserved verbatim?
- Should semantic diffs understand Arrow tolerance/ordering policy explicitly?
- What is the smallest useful repro subset for large ORC bugs?

# Sources

- Apache ORC specification: https://orc.apache.org/specification/
- ORC v1 spec: https://orc.apache.org/specification/ORCv1/
- Apache ORC project: https://github.com/apache/orc
- `orc-rust` crate: https://crates.io/crates/orc-rust
- `orc-rust` repository: https://github.com/datafusion-contrib/orc-rust
- `orc-format` crate: https://crates.io/crates/orc-format
- `orcrs` crate: https://crates.io/crates/orcrs
- Arrow ORC docs: https://arrow.apache.org/docs/python/orc.html
