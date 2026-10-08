---
id: P-0298
title: XBRL + Inline XBRL Conformance & Evidence Kit — taxonomy-aware validation, canonical facts, and filing repro bundles
status: idea
domains: [finance, regtech, file-formats, interoperability, compliance]
last_reviewed: 2026-03-06
evidence:
  - https://specifications.xbrl.org/specifications.html
  - https://www.xbrl.org/the-standard/what/ixbrl/
  - https://www.xbrl.org/news/xbrl-2-1-conformance-suite-updated-and-released/
---

# Problem

Rust has promising XBRL parsing momentum (`crabrl`, `xbrl-rs`, filing-oriented tooling like `edgarkit`), but the missing high-value layer is not “yet another XML parser.” The real gap is a **taxonomy-aware, conformance-first workbench** that can:

- validate XBRL and iXBRL against evolving conformance suites,
- canonicalize facts/contexts/units for stable diffs,
- subset large filings into shareable bug bundles,
- compare Rust results with incumbent tooling such as Arelle,
- make regulator/profile-specific checks reproducible in CI.

XBRL remains a standards-heavy ecosystem with active conformance work and large real-world filing populations, yet Rust lacks a default crate/workspace for **evidence-grade diagnostics**.

# What it provides

- `xbrl-canon` — canonical IR for facts, contexts, units, dimensions, footnotes, and duplicates.
- `ixbrl-extract` — stable extraction of Inline XBRL facts and presentation mapping from HTML.
- `xbrl-validate` — base-spec + profile-aware validation engine with explainable verdicts.
- `xbrl-fixtures` — conformance suite runners and regulator/profile fixture packs.
- `xbrl-diff` — semantic diffs between filings, facts, or validator outcomes.
- `cargo xbrl` — build `*.xbrlbundle.zip` artifacts for support, certification, and regression tracking.

# Users & user stories

- **Regtech teams**: “Why did this filing pass our pipeline but fail the reference validator?”
- **Data platform teams**: “Tell me whether two filings differ in fact meaning, not just raw XML/HTML layout.”
- **Rust library authors**: “Run the conformance corpus and compare our verdicts to Arelle.”
- **Compliance engineers**: “Bundle one minimized filing with taxonomy snapshot, extracted facts, and verdicts.”

# Prior art (and why it’s insufficient)

- Arelle is a mature open-source XBRL platform and the de facto reference point, but it is Python-first and not a small Rust-native library layer.
- XBRL International publishes conformance suites and evolving guidance, which is essential evidence but not a Rust crate story.
- Emerging Rust crates demonstrate demand and performance potential, but they do not yet provide a standard canonicalization/evidence workflow.

# Design goals

1. **Conformance-first** — the crate should live and die by running official suites and profile packs.
2. **Canonical facts** — normalize duplicate-fact handling, contexts, units, and dimensions for stable comparisons.
3. **HTML-aware iXBRL** — preserve enough source mapping to explain where extracted facts came from.
4. **Reference-comparable** — make it easy to diff Rust validator output against Arelle/reference outputs.
5. **Small repros** — issue bundles should support subsetting and redaction of large filings.

# Non-goals

- Not a general-purpose SEC filing crawler.
- Not a taxonomy authoring IDE.
- Not a replacement for all incumbent XBRL platforms on day one.

# Architecture & API sketch

```rust
pub struct FilingReport {
    pub fact_count: u64,
    pub duplicate_facts: Vec<DuplicateFact>,
    pub verdicts: Vec<Verdict>,
}

pub fn extract_ixbrl(html: &[u8]) -> Result<InlineDocument, Error>;
pub fn canonicalize(doc: &InlineDocument) -> Result<CanonicalFacts, Error>;
pub fn validate(bundle: &ValidationBundle, profile: &Profile) -> FilingReport;
```

Bundle draft: `filing.html`, `taxonomy.lock`, `facts.json`, `contexts.json`, `verdicts.json`, `reference-diff.json`, `notes.md`.

# Security / safety model

- Treat all XML/HTML/taxonomy inputs as hostile: entity expansion hardening, recursion/size limits, remote fetch policy control.
- Support redaction or hashing of issuer identifiers and non-public attachments in issue bundles.
- Make offline taxonomy resolution a first-class mode.

# Maintenance & governance plan

- Version bundle semantics against official conformance-suite snapshots.
- Keep base-spec validation separate from region/regulator profile packs.
- Encourage side-by-side comparison fixtures with Arelle rather than pretending reference diversity does not exist.

# Milestones

## 0.1
- Canonical fact/context/unit IR
- iXBRL extraction with source mapping
- Minimal base-spec validator

## 0.2
- Conformance suite runner
- Arelle comparison harness
- Filing subsetting + bug bundles

## 1.0
- Stable `*.xbrlbundle.zip`
- Official-suite coverage metrics
- Profile packs for common filing environments

# Open questions

- Which duplicate-fact policies should be exposed as configurable profile behavior?
- How much taxonomy caching/locking should live in-core versus a companion tool?
- Should there be a standard OIM-style export in the MVP?

# Sources

- XBRL specifications index: https://specifications.xbrl.org/specifications.html
- XBRL 2.1 + supporting documents: https://specifications.xbrl.org/work-product-index-group-base-spec-base-spec.html
- Inline XBRL overview: https://www.xbrl.org/the-standard/what/ixbrl/
- Inline XBRL specification group: https://specifications.xbrl.org/spec-group-index-inline-xbrl.html
- XBRL 2.1 conformance suite update: https://www.xbrl.org/news/xbrl-2-1-conformance-suite-updated-and-released/
- Arelle open source platform: https://arelle.org/arelle/ ; https://github.com/Arelle/Arelle
- Rust crates: https://crates.io/crates/crabrl ; https://lib.rs/crates/xbrl-rs ; https://crates.io/crates/edgarkit
