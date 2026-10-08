---
id: P-0327
title: Crossref 5.4.0 + JATS 1.4 Deposit & Validation Workbench Kit — profile-pinned scholarly XML transforms, explainable deposit failures, and replayable registration bundles
status: idea
domains: [publishing, scholarly, metadata, crossref, jats, xml, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://jats.nlm.nih.gov/publishing/1.4/
  - https://www.crossref.org/documentation/schema-library/metadata-deposit-schema-5-4-0/
  - https://www.crossref.org/documentation/register-maintain-records/direct-deposit-xml/testing-your-xml/
  - https://www.crossref.org/documentation/register-maintain-records/direct-deposit-xml/jats-xml/
  - https://crates.io/crates/crossref-xml
---

# Problem

Rust is now close enough to serious scholarly-XML work that the missing contribution is no longer “just parse some tags.” The pain lives in the **boundary between author/article XML and deposit XML**:

- JATS that is locally acceptable but fails when transformed for deposit,
- Crossref schema revisions and helper workflows drifting underneath publisher pipelines,
- submission logs that say “invalid XML” without explaining the scholarly meaning of the failure,
- brittle XSLT- or hand-mapping pipelines that are hard to regression-test,
- and support escalations that still move around as opaque XML files, screenshots, and email snippets.

The worthy crate contribution is a **deposit and validation workbench** that turns JATS/Crossref transformations, schema checks, and registration attempts into deterministic, explainable, replayable artifacts.

# What it provides

- `article-ir` — a canonical Rust IR for article metadata, contributors, abstracts, references, funders, licenses, relations, identifiers, and publication dates.
- `jats-bridge` — ingestion and normalization for JATS 1.4 publishing/archiving inputs into the IR, preserving line-of-origin and namespace context.
- `crossref-profile` — lockfiles pinning exact Crossref schema version, optional helper conventions, journal/repository policy, and organization-specific field requirements.
- `deposit-verify` — structural and semantic checks that explain failures in publishing language: “funder identifier malformed”, “reference list collapsed”, “translated title missing language context”, “relation type lost in transform”.
- `deposit-replay` — deterministic replay for JATS→IR→Crossref mappings, local schema validation, and deposit-response interpretation.
- `deposit-diff` — semantic diffs between two scholarly records or two transforms: “citation list changed”, “license URL normalized”, “author order shifted”, “ORCID dropped”.
- `cargo crossref` — emit `*.depositbundle.zip` for regression CI, vendor/platform handoff, or publisher support escalations.

# What the crate should provide other people

1. **A boring default for scholarly XML debugging** instead of XSLT archaeology and screenshots.
2. **Version/profile pinning** for the exact Crossref and JATS assumptions a workflow depends on.
3. **Semantic error explanations** that speak in publishing terms instead of raw schema line numbers alone.
4. **Replayable deposits** that make “worked last month, fails today” regressions testable.
5. **A neutral bridge** above manuscript systems, repository software, and platform-specific submission tooling.

# Persona / who it’s for

- Journal platform maintainers
- University press and repository engineers
- Submission/workflow tool authors
- Metadata operations teams
- Rust developers building scholarly publishing infrastructure

# Users & user stories

- **Platform maintainer**: “Show me why this JATS article transformed into Crossref XML that now fails under the pinned 5.4.0 profile.”
- **Publisher ops team**: “Diff this week’s deposit output against the last known-good issue and tell me what changed semantically.”
- **Repository engineer**: “Redact depositor credentials and author emails, but keep the bug reproducible.”
- **Integrator**: “Prove that our JATS subset still round-trips into the deposit workflow we claim to support.”

# Prior art (and why it’s insufficient)

- JATS 1.4 provides formal tag sets and schemas.
- Crossref publishes the current recommended deposit schema, local-validation guidance, and a basic JATS-to-Crossref conversion path.
- Rust now has fresh substrate in `crossref-xml`, plus older retrieval/API crates.
- But there is still no boring-default Rust crate family for **profile pinning + explainable deposit validation + semantic diffs + replayable registration bundles**.

# Design goals

1. **Bridge-first** — the transformation boundary is the unit of value.
2. **Explainability over mere validity** — every failure should be phrased in domain terms a publishing team can act on.
3. **Version explicitness** — every report must say exactly which JATS/Crossref assumptions were used.
4. **Round-trip awareness** — enough provenance should survive to tell users where a bad field came from.
5. **Implementation neutrality** — useful whether the actual production pipeline is XSLT, Java, Python, PHP, or Rust.

# MVP surface

- Minimal types: `ArticleRecord`, `JatsSnapshot`, `CrossrefSnapshot`, `DepositProfile`, `DepositReport`
- Minimal functions:
  - `load_jats()`
  - `to_article_ir()`
  - `to_crossref_xml()`
  - `verify_deposit()`
  - `diff_records()`
  - `write_bundle()`
- Feature flags:
  - `jats`
  - `crossref`
  - `serde`
  - `redaction`
  - `schematron` 

# Compatibility story

- MVP should target **JATS 1.4** inputs and **Crossref 5.4.0** outputs first.
- It should ingest legacy XML when practical through adapters, but only promise stable semantics for pinned profiles.
- It should complement, not replace, existing Crossref upload tools or manuscript platforms.
- MVP should intentionally avoid becoming a full journal-production system.

# Conformance & fixtures

- Minimal journal-article fixtures covering titles, contributors, affiliations, ORCIDs, abstracts, references, funding, relations, and licenses.
- Positive/negative examples for multilingual titles, abstract markup, reference edge cases, and relation metadata.
- JATS-to-Crossref fixture packs with expected semantic verdicts and normalized output diffs.
- Optional adapters for Crossref validation responses and legacy local-validation logs.

# Path to boring stability

- First stabilize the IR and semantic verdict vocabulary.
- Then prove that bundle outputs stay useful across several fixture classes and one real-world, redacted publisher corpus.
- Freeze bundle layout only after replay + redaction + diff remain stable across multiple schema versions.
- Keep new schema versions additive through versioned profile packs.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that ingest one JATS 1.4 article, transform it into pinned Crossref 5.4.0 XML, validate the output locally, explain any failures semantically, diff it against a previous good deposit, and emit a redactable `*.depositbundle.zip`.

# De-risk plan

1. Start with journal articles only.
2. Keep the IR intentionally narrow and article-centric before covering more record classes.
3. Treat local schema validation and semantic transforms as the core; leave real submission transport out of core MVP.
4. Prove value on redacted regression fixtures before adding live platform adapters.

# Non-goals

- Not a manuscript submission platform.
- Not a full JATS editor or WYSIWYG authoring system.
- Not a replacement for Crossref’s own submission services.

# Architecture & API sketch

```rust
pub struct DepositReport {
    pub profile_id: String,
    pub transform_findings: Vec<TransformFinding>,
    pub validation_findings: Vec<ValidationFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn to_crossref(profile: &DepositProfile, article: &ArticleRecord) -> Result<CrossrefSnapshot>;
pub fn verify_deposit(profile: &DepositProfile, xml: &CrossrefSnapshot) -> DepositReport;
```

Bundle draft: `profile.toml`, `input/jats.xml`, `normalized/article.json`, `output/crossref.xml`, `validation/report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact depositor credentials, email addresses, internal submission IDs, and embargo-sensitive URLs.
- Bound XML expansion and external-entity behavior by default.
- Preserve enough provenance for semantic diffs after redaction.
- Record exact profile and validator hashes for reproducibility.

# Maintenance & governance plan

- Ship schema/profile packs as explicit versioned data.
- Keep IR additive and conservative.
- Test against official JATS/Crossref examples and community-donated redacted fixtures.
- Separate transformation logic from transport adapters so maintenance stays tractable.

# Milestones

## 0.1
- JATS 1.4 ingest subset
- Crossref 5.4.0 output subset
- Semantic validation and bundle draft

## 0.2
- Semantic diffs
- Redaction support
- Validation-response adapters

## 1.0
- Stable `*.depositbundle.zip`
- Regression corpus across multiple issue/article shapes
- CI-ready workflow for scholarly XML pipelines

# Open questions

- Should Crossref helper-tool quirks live in profiles or adapters?
- How much of JATS should be modeled natively versus normalized away?
- Should resource-only deposit support land before broader record classes, or after the core article path is boring?

# Sources

- JATS 1.4 publishing tag set: https://jats.nlm.nih.gov/publishing/1.4/
- Crossref metadata deposit schema 5.4.0: https://www.crossref.org/documentation/schema-library/metadata-deposit-schema-5-4-0/
- Crossref testing guidance: https://www.crossref.org/documentation/register-maintain-records/direct-deposit-xml/testing-your-xml/
- Crossref JATS XML guidance: https://www.crossref.org/documentation/register-maintain-records/direct-deposit-xml/jats-xml/
- `crossref-xml`: https://crates.io/crates/crossref-xml
