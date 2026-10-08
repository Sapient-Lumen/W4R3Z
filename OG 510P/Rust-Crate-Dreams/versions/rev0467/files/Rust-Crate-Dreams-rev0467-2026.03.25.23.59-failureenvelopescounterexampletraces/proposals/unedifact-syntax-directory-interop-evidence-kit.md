---
id: P-0365
title: UN/EDIFACT Syntax + Directory Interop & Evidence Kit — release locks, code-list diffs, and replayable B2B document bug bundles
status: idea
domains: [b2b, edi, supply-chain, trade, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://unece.org/trade/uncefact/unedifact-introduction-and-rules
  - https://service.unece.org/trade/untdid/d24a/trsd/trsdind.htm
  - https://unece.org/uncefact/unedifact/2021-2024
  - https://service.unece.org/trade/untdid/d00b/tred/tred2025.htm
  - https://crates.io/crates/edifact-types
  - https://crates.io/crates/edi-format
---

# Problem

Rust now has early substrate for working with EDI structures, but the painful failures in UN/EDIFACT workflows still happen at the seam between:

- syntax-version assumptions,
- directory-release drift,
- message implementation guidelines and code-list overlays,
- partner-specific segment/cardinality interpretations,
- and support cases that arrive as “their INVOIC fails ours” with no normalized, portable artifact.

The missing Rust contribution is not another generic EDI parser. It is a **release-and-evidence workbench** that makes EDIFACT bugs reproducible, comparable, and small enough to ship between trading partners.

# What it provides

- `edi-lock` — lockfiles pinning syntax version, directory release, message type, partner profile, separators/service-string assumptions, and code-list overlays.
- `edifact-ir` — a neutral IR for segments, composites, validation findings, code-list references, and directory metadata.
- `message-check` — validate a message against locked release/profile expectations and normalize the findings.
- `edi-diff` — semantic diffs such as “same segment path, different release meaning” or “same message, different cardinality acceptance”.
- `cargo edi-evidence` — emits `*.edibundle.zip` with redacted interchange samples, release/profile locks, normalized validation findings, and notes.

# What the crate should provide other people

1. **A boring default artifact for EDIFACT interoperability bugs**.
2. **Pinned release/profile expectations** that survive directory upgrades and trading-partner changes.
3. **Explainable code-list and segment diagnostics** instead of free-form rejection emails.
4. **Replayable message-validation cases** for CI, onboarding, and partner support.
5. **A bridge from Rust EDI parsers/types to evidence-grade partner debugging workflows**.

# Persona / who it’s for

- B2B integration teams
- Logistics, customs, and trade-document platform maintainers
- Partner-onboarding and message-validation teams
- Rust developers building EDI tooling or adapters

# Users & user stories

- **Integrator**: “Tell me whether the failure is syntax, directory release, code-list, or partner-profile drift.”
- **Partner-onboarding engineer**: “Lock exactly which message release and MIG-like assumptions this connection uses.”
- **Support engineer**: “Produce a redacted evidence bundle instead of a long rejection email thread.”
- **Tool maintainer**: “Diff the same interchange against two directory releases and show only the semantic differences.”

# Prior art (and why it’s insufficient)

- UNECE publishes the EDIFACT syntax rules and directory material, including current directory windows.
- Rust has early substrate in `edifact-types` and formatting/parsing helpers.
- But Rust still lacks a boring-default crate for **release/profile lockfiles + normalized validation + semantic diffs + portable evidence bundles**.

# Design goals

1. **Release-aware** — directory version and syntax assumptions must be explicit.
2. **Profile-aware** — partner overlays matter as much as raw syntax.
3. **Message-small** — diagnostics should get sharper as the failing case gets smaller.
4. **Redaction-first** — safe partner sharing must be possible.
5. **Directory-neutral** — do not hardwire the crate to one industry subset.

# MVP surface

- Minimal types: `EdiLock`, `DirectoryPin`, `EdiBundle`, `ValidationFinding`, `SegmentDiffFinding`
- Minimal functions:
  - `normalize_interchange()`
  - `validate_message()`
  - `diff_release_reports()`
  - `write_bundle()`
- Feature flags:
  - `syntax`
  - `directories`
  - `profiles`
  - `redaction`

# Compatibility story

- MVP should target UN/EDIFACT syntax and selected directory-release aware validation.
- The crate should complement parser/type crates rather than replace them.
- Industry or partner profile packs can live outside the stable core schemas.
- Separator/service-string handling must remain deterministic and explicit.

# Conformance & fixtures

- Tiny interchange fixtures for common message families with deliberate release/profile drift.
- Cases for UNA/service-string mismatch, bad segment counts, invalid code values, and release-specific field meaning changes.
- Goldens for “same business meaning, different release path” and “same path, different validation outcome due to profile”.
- Redaction tests for identifiers, addresses, references, and monetary fields.

# Path to boring stability

- Stabilize the lockfile and validation-report schemas before broadening message-family coverage.
- Start with directory-aware validation and semantic diffs, not partner-portal automation.
- Keep findings grounded in release/profile language that B2B teams actually use.
- Build a public corpus from tiny interchanges and synthetic partner profiles.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that lock a message to a directory release and partner profile, validate a tiny interchange, and emit a compact `*.edibundle.zip` with normalized findings and semantic diffs.

# De-risk plan

1. Start with one or two message families and a narrow set of release-aware checks.
2. Treat directory/code-list version pinning as the hardest early design problem.
3. Keep partner-profile overlays optional in the first release.
4. Use tiny interchanges before tackling giant production messages.

# Non-goals

- Not a universal EDI gateway.
- Not a business-process orchestration platform.
- Not a replacement for industry-specific partner agreements.
- Not a complete implementation of every EDI family beyond the EDIFACT seam in scope.

# Architecture & API sketch

```rust
pub struct EdiLock {
    pub syntax_version: String,
    pub directory_release: String,
    pub message_type: String,
}

pub fn validate_message(lock: &EdiLock, message: &NormalizedInterchange) -> Result<EdiReport>;
pub fn diff_release_reports(a: &EdiReport, b: &EdiReport) -> SegmentDiff;
```

Bundle draft: `profile.toml`, `message.edi`, `directory.json`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat interchange files and partner profiles as untrusted input.
- Support redaction of party identifiers, references, and monetary details.
- Record exact syntax, directory, and profile assumptions.
- Keep bundle outputs deterministic enough for partner debugging and regression testing.

# Maintenance & governance plan

- Keep the core centered on release/profile locks, normalized findings, diffs, and bundle format.
- Version industry/partner overlays separately.
- Publish a small public fixture corpus organized around release and code-list seams.
- Avoid coupling the workbench to one sector’s implementation guidelines.

# Milestones

## 0.1
- syntax/release lockfile
- normalized interchange report
- bundle writer

## 0.2
- semantic diffs
- optional partner-profile overlays
- redaction support

## 1.0
- stable `*.edibundle.zip`
- public fixture corpus
- documented compatibility policy for supported releases and profiles

# Open questions

- Which minimum directory-release set is enough to make the crate obviously useful?
- How much partner-profile semantics belongs in the stable core schema versus extension packs?
- What is the clearest way to present code-list drift without overwhelming maintainers?

# Sources

- UN/EDIFACT introduction and rules: https://unece.org/trade/uncefact/unedifact-introduction-and-rules
- UN/EDIFACT D.24A segment directory example: https://service.unece.org/trade/untdid/d24a/trsd/trsdind.htm
- UNECE directories 2021–2024 index: https://unece.org/uncefact/unedifact/2021-2024
- UN/EDIFACT data element directory page: https://service.unece.org/trade/untdid/d00b/tred/tred2025.htm
- `edifact-types`: https://crates.io/crates/edifact-types
- `edi-format`: https://crates.io/crates/edi-format
