---
id: P-0348
title: WARC 1.1 + CDXJ + WACZ Web-Archive Interop & Evidence Kit — replayable archive packages, index/package audits, and portable preservation bug bundles
status: idea
domains: [web-archiving, digital-preservation, libraries, archives, packaging, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/
  - https://specs.webrecorder.net/cdxj/latest/
  - https://specs.webrecorder.net/wacz/1.2.0/
  - https://docs.rs/warc
  - https://docs.rs/wacksy
  - https://docs.rs/warcat
---

# Problem

Rust can already read and write WARC files and even assemble WACZ packages, but the operational failures that matter to archivists and replay-tool authors usually live **between** the layers:

- WARC content exists but the CDXJ index does not actually point to the right records,
- a WACZ package is technically zipped correctly but incomplete or replay-hostile,
- range-based replay tools disagree about what constitutes a valid package,
- deduplication/revisit semantics get lost when moving between archive stores and distributable packages,
- and support cases still require mailing giant binary blobs around with no compact explanation of what is broken.

The missing epic contribution is a **package-and-replay evidence kit** that treats WARC records, CDXJ indexes, and WACZ packaging as one auditable surface.

# What it provides

- `warc-ir` — a canonical Rust IR for WARC records, payload digests, request/response relationships, revisit chains, and packaging metadata.
- `cdxj-check` — canonical checks that an index actually resolves into the packaged WARC content it claims to describe.
- `wacz-audit` — package-level verification for layout, manifest metadata, archive members, indexes, and random-access assumptions.
- `warc-replay` — deterministic replay metadata suitable for smoke-testing browser or service replay stacks.
- `warc-diff` — semantic diffs such as “same crawl content, changed digest chain”, “missing request mate”, or “WACZ index drift from packaged WARC”.
- `cargo warc-evidence` — emit `*.warcbundle.zip` for repository migration, preservation triage, or replay-tool debugging.

# What the crate should provide other people

1. **A boring default archive triage bundle** that can be shared without sending an entire multi-gigabyte crawl.
2. **One place to pin expectations about replayability and package completeness**.
3. **Audits across WARC ↔ CDXJ ↔ WACZ boundaries**, which is where many expensive bugs actually live.
4. **A preservation-friendly diff layer** that explains logical drift rather than only ZIP or byte differences.
5. **A bridge between archival storage workflows and browser/service replay tooling**.

# Persona / who it’s for

- Web-archive platform maintainers
- Digital-preservation engineers
- Replay-tool authors
- Library/archive technology teams
- Researchers shipping distributable web archives

# Users & user stories

- **Archivist**: “Tell me whether this WACZ package is missing archive members, has stale CDXJ entries, or just uses a different but acceptable packaging layout.”
- **Replay developer**: “Give me a minimized bundle showing exactly why replay fails on this archived page.”
- **Migration engineer**: “Compare archive package A and B semantically and report what preservation-relevant information moved or disappeared.”
- **Institutional repository operator**: “Verify that our published WACZ packages can support random-access replay without exposing the full WARC store.”

# Prior art (and why it’s insufficient)

- The IIPC publishes the **WARC 1.1** specification.
- Webrecorder publishes specs for **CDXJ** and **WACZ** packaging.
- Rust has `warc`, `warcat`, and `wacksy` as real substrate.
- But there is no boring-default Rust crate family for **cross-layer archive audits + replay metadata + semantic diffs + portable preservation evidence bundles**.

# Design goals

1. **Layer-aware correctness** — treat WARC, indexes, and package containers as distinct but linked surfaces.
2. **Preservation-first** — findings should prioritize missing, drifted, or unverifiable archival meaning.
3. **Replay-aware** — package checks should reflect browser/service replay needs, not only storage correctness.
4. **Compact evidence** — small bundles must be able to describe large archive failures.
5. **Implementation-neutral** — useful whether the downstream tool is pywb, browsertrix, or a custom service.

# MVP surface

- Minimal types: `ArchiveSnapshot`, `IndexSnapshot`, `PackageSnapshot`, `ReplayReport`, `DiffFinding`
- Minimal functions:
  - `scan_warc()`
  - `check_cdxj()`
  - `audit_wacz()`
  - `build_replay_probe()`
  - `write_bundle()`
- Feature flags:
  - `warc`
  - `wacz`
  - `hashes`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **WARC 1.1**, **CDXJ**, and **WACZ 1.x** packaging first.
- The crate should complement existing replay stacks instead of trying to become a full replay engine.
- Package checks should tolerate acceptable layout variation where the specs allow it.
- Optional signing/trust extensions should stay out of core until the base evidence model is stable.

# Conformance & fixtures

- Tiny public crawl fixtures with request/response pairs, revisit records, and intentional index/package mistakes.
- Goldens for missing member, wrong digest, wrong byte-range target, and malformed WACZ layout.
- Replay probes for a few known archived pages with expected capture structure.
- Corpus adapters that normalize validation findings into stable JSON.

# Path to boring stability

- Stabilize the IR and bundle format before adding richer replay semantics.
- Keep initial package checks deterministic and filesystem-local.
- Freeze diff vocabulary only after validating it against real migration incidents.
- Add signing/trust extensions later rather than bloating MVP.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A CLI and library that scan WARC content, verify CDXJ pointers, audit a WACZ package, and emit a compact `*.warcbundle.zip` with hashes, structural findings, and replay probes for a handful of URLs.

# De-risk plan

1. Start with structural and index/package audits before tackling full replay correctness.
2. Prefer tiny synthetic/public fixtures.
3. Keep bundle payloads mostly to metadata, hashes, and selected reduced records.
4. Let replay-tool adapters live on top of a stable core IR.

# Non-goals

- Not a full web crawler.
- Not a browser replay engine.
- Not a giant preservation repository platform.

# Architecture & API sketch

```rust
pub struct ReplayReport {
    pub profile_id: String,
    pub warc_findings: Vec<Finding>,
    pub index_findings: Vec<Finding>,
    pub package_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn audit_wacz(pkg: &PackageSnapshot, profile: &ArchiveProfile) -> Result<ReplayReport>;
pub fn check_cdxj(index: &IndexSnapshot, archive: &ArchiveSnapshot) -> Result<Vec<Finding>>;
```

Bundle draft: `archive.json`, `profile.toml`, `warc-hashes.json`, `index.json`, `package.json`, `replay-probes.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat archive contents as untrusted and potentially hostile.
- Avoid embedding full payload bodies by default.
- Support redaction of URLs, cookies, and sensitive headers in bundles.
- Capture enough hashing and structural metadata to allow reproducible debugging.

# Maintenance & governance plan

- Keep the core focused on IRs, audits, and evidence bundles.
- Version bundle format separately from profile packs.
- Grow via adapters to replay stacks, not by subsuming them.
- Prefer public synthetic fixtures and small public-domain captures.

# Milestones

## 0.1
- WARC scan
- CDXJ check
- WACZ audit

## 0.2
- replay probes
- semantic diffs
- redaction support

## 1.0
- stable `*.warcbundle.zip`
- documented migration/replay fixture corpus
- adapter APIs for downstream replay tools

# Open questions

- How much replay-specific metadata is needed in core?
- Should revisit/dedup semantics be first-class in MVP or phase two?
- Which package-level findings are most preservation-relevant versus merely cosmetic?

# Sources

- WARC 1.1 specification: https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/
- CDXJ specification: https://specs.webrecorder.net/cdxj/latest/
- WACZ 1.2.0 specification: https://specs.webrecorder.net/wacz/1.2.0/
- `warc`: https://docs.rs/warc
- `wacksy`: https://docs.rs/wacksy
- `warcat`: https://docs.rs/warcat
