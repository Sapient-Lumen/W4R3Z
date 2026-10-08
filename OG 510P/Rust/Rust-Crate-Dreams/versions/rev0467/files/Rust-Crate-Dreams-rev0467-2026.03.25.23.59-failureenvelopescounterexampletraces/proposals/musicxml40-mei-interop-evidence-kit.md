---
id: P-0346
title: MusicXML 4.0 + MEI Interop & Evidence Kit — schema-aware notation conversion, semantic loss reports, and portable score bug bundles
status: idea
domains: [music, digital-humanities, publishing, notation, musicxml, mei, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.musicxml.com/for-developers/
  - https://music-encoding.org/
  - https://github.com/music-encoding/music-encoding
  - https://crates.io/crates/musicxml
  - https://crates.io/crates/verovioxide
---

# Problem

Rust has enough notation and XML substrate now that the missing leverage is no longer “one more parser”. The hard problems sit at the boundary between **exchange-oriented notation and research/critical-edition encodings**:

- MusicXML files that validate but lose or reshape meaning when pushed toward MEI-style workflows,
- conversion pipelines that preserve notes but not editorial or layout semantics,
- score bugs that are hard to share because the problem is a tiny semantic mismatch hidden inside a large score,
- and toolchains that still cannot explain whether a difference is engraving-only, playback-relevant, or scholarly/semantic loss.

The worthy crate contribution is an **interop and evidence kit** that makes score conversion and validation reproducible, explainable, and small enough to ship around.

# What it provides

- `score-ir` — canonical IR for score structure, measures, parts, notes, directions, layout hints, editorial metadata, and provenance.
- `score-profile` — lockfiles pinning MusicXML version, MEI schema/guideline family, conversion assumptions, and validator settings.
- `score-verify` — normalized schema and semantic checks for MusicXML and MEI inputs.
- `score-convert` — explainable MusicXML↔MEI subset conversion with loss reports.
- `score-diff` — semantic diffs such as “playback-equivalent but engraving-different”, “editorial markup lost”, or “structure changed from partwise assumptions”.
- `cargo score-evidence` — emit `*.scorebundle.zip` for notation-tool interop, corpus curation, and digital-humanities debugging.

# What the crate should provide other people

1. **A boring default for notation interchange diagnostics** in Rust.
2. **Explainable conversion-loss reports** instead of silent score drift.
3. **Profile-pinned validation** tied to exact schema/guideline assumptions.
4. **Small bug bundles** rather than full project exports.
5. **A bridge between practical notation workflows and scholarly/archival encodings**.

# Persona / who it’s for

- Notation software/tooling developers
- Digital-humanities and musicology projects
- Corpus curators and format-conversion teams
- QA teams for score interchange workflows

# Users & user stories

- **Notation developer**: “Tell me whether this issue is schema validity, playback semantics, or engraving-only drift.”
- **Digital-humanities maintainer**: “Convert a MusicXML corpus to an MEI subset and report what meaning was lost.”
- **Corpus curator**: “Ship a tiny bundle that reproduces the problematic score difference.”
- **Research engineer**: “Pin the exact schema/guideline versions used in a transformation pipeline.”

# Prior art (and why it’s insufficient)

- MusicXML 4.0 is an established exchange format with official schemas.
- MEI publishes schemas and guidelines for rich machine-readable music documents.
- Rust has real substrate in `musicxml`, `muxml-rust`, and Verovio bindings such as `verovioxide`.
- But Rust still lacks a shared **IR + conversion-loss reporting + semantic diff + portable evidence bundle** layer for notation interoperability.

# Design goals

1. **Meaning over markup** — distinguish structural, playback, engraving, and editorial differences.
2. **Subset-aware conversion honesty** — do not promise universal lossless translation.
3. **Schema-plus-semantics** — valid XML is not enough.
4. **Adapter-first** — complement existing parsers/renderers and schema validators.
5. **Corpus-friendly bundles** — issue artifacts should be tiny and reproducible.

# MVP surface

- Minimal types: `ScoreDoc`, `ScoreProfile`, `ScoreFinding`, `ConversionLoss`, `ScoreReport`
- Minimal functions:
  - `load_musicxml()`
  - `load_mei()`
  - `verify_score()`
  - `convert_subset()`
  - `diff_score()`
  - `write_bundle()`
- Feature flags:
  - `musicxml-4-0`
  - `mei`
  - `serde`

# Compatibility story

- MVP targets MusicXML 4.0 and a documented MEI subset/round-trip surface first.
- It should complement schema validators and renderers such as Verovio.
- It intentionally avoids becoming a full notation editor or engraving engine.

# Conformance & fixtures

- Tiny scores covering partwise structure, tuplets, repeats, articulations, lyrics, and directions.
- Known-invalid schema and semantic examples.
- Conversion fixtures with explicit “preserved / transformed / lost” expectations.
- Diff fixtures separating engraving-only from playback/significant semantic changes.

# Path to boring stability

- Stabilize the cross-format IR around a documented overlap subset first.
- Freeze the loss-report taxonomy before feature expansion.
- Keep playback vs engraving vs editorial semantics explicit.
- Hash schema/guideline packs into every bundle.

# Scorecard

- Impact: 3/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A validator and converter workbench for small MusicXML 4.0 scores that pins an MEI profile, reports semantic loss/diff information, and emits a replayable `*.scorebundle.zip`.

# De-risk plan

1. Start with a narrow documented overlap subset.
2. Reuse official schemas and existing render/validation tools where practical.
3. Focus on loss reporting and semantic diffing, not full-format support.
4. Validate on tiny public-domain scores and synthetic fixtures first.

# Non-goals

- Not a notation editor.
- Not a full engraving/rendering engine.
- Not a claim of complete MusicXML↔MEI equivalence.

# Architecture & API sketch

```rust
pub struct ScoreReport {
    pub profile_id: String,
    pub schema_findings: Vec<Finding>,
    pub semantic_findings: Vec<Finding>,
    pub conversion_losses: Vec<LossFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_score(profile: &ScoreProfile, doc: &ScoreDoc) -> ScoreReport;
pub fn convert_subset(profile: &ScoreProfile, doc: &ScoreDoc) -> Result<ScoreDoc>;
```

Bundle draft: `profile.toml`, `source/`, `normalized.json`, `findings.json`, `conversion-loss.json`, `semantic-diff.json`, `notes.md`.

# Security / safety model

- Guard XML parsing and archive/container handling.
- Keep bundle capture focused on tiny score excerpts.
- Record exact schema/guideline/renderer versions where used.
- Preserve provenance for editorial and layout-loss reports.

# Maintenance & governance plan

- Keep core focused on IRs, validation adapters, and loss reporting.
- Version MusicXML/MEI profile packs separately from bundle layout.
- Prefer public-domain or license-clear scores for fixtures.
- Explicitly document unsupported notation families rather than silently dropping them.

# Milestones

## 0.1
- MusicXML loader
- MEI subset loader
- shared IR and bundle draft

## 0.2
- explainable conversion-loss reporting
- semantic diffs
- renderer/validator adapters

## 1.0
- stable `*.scorebundle.zip`
- corpus fixture pack
- versioned profile packs

# Open questions

- What is the sharpest useful overlap subset for MVP?
- How should editorial and engraving semantics be separated in the diff model?
- Should renderer-based semantic checks live in optional adapters only?

# Sources

- MusicXML 4.0: https://www.musicxml.com/for-developers/
- Music Encoding Initiative: https://music-encoding.org/
- MEI schema/guidelines repository: https://github.com/music-encoding/music-encoding
- `musicxml`: https://crates.io/crates/musicxml
- `verovioxide`: https://crates.io/crates/verovioxide
