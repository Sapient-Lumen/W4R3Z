---
id: P-0393
title: Sigma + OCSF Detection Interop Workbench Kit — rule locks, mapping receipts, and backend-portable evidence bundles
status: idea
domains: [security, detections, schemas, interoperability, siem, validation]
last_reviewed: 2026-03-06
evidence:
  - https://sigmahq.io/sigma-specification/
  - https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html
  - https://sigmahq.io/docs/meta/correlations.html
  - https://ocsf.io/
  - https://schema.ocsf.io/classes/authentication
  - https://github.com/timescale/rsigma
---

# Problem

Sigma has matured from a generic detection idea into a richer rule ecosystem with a formal specification, taxonomy, modifiers, and first-party correlation concepts. In parallel, OCSF now gives defenders a vendor-neutral schema framework and a normative event taxonomy that many pipelines increasingly normalize into.

Rust also has meaningful substrate now: multiple Sigma parsers/evaluators exist, and OCSF Rust type-generation efforts already exist.

But the painful failures still happen at the seam between:

- **what a Sigma rule claims to match and what an OCSF-normalized event actually exposes**,
- **Sigma taxonomy/logsource assumptions and backend-specific field availability**,
- **rule/correlation evolution and whether an engine or SIEM can faithfully implement it**,
- **sample-event sharing and redaction in real incident or tuning workflows**,
- and **“this rule didn’t translate cleanly” explanations that are currently scattered across ad hoc scripts and spreadsheets**.

The missing Rust contribution is not yet another SIEM. It is a **rule-lock, mapping, and evidence workbench** that makes Sigma↔OCSF↔backend compatibility portable and explainable.

# What it provides

- `sigma.lock` — pins Sigma spec surface, taxonomy version, correlation support, target backend pack, and OCSF schema/profile version.
- `detect-ir` — neutral IR connecting Sigma AST, correlation intent, field modifiers, normalized event shape, and backend query targets.
- `mapping-receipt` — explicit evidence for how Sigma fields/modifiers mapped into OCSF classes/attributes and where semantics were lost.
- `sample-pack` — small, redactable event corpora stored in raw and OCSF-normalized form.
- `cargo detection-evidence` — emits `*.detbundle.zip` with lockfile, rules, mappings, samples, findings, and suppressions.

# What the crate should provide other people

1. **A boring artifact for detection-rule portability bugs**.
2. **Rule and taxonomy pinning** across Sigma and OCSF versions.
3. **Explainable mapping receipts** instead of opaque conversion output.
4. **Small redacted corpora** for regression tests and handoffs.
5. **A shared basis for linting, testing, and tuning** across backends.

# Persona / who it’s for

- Rust maintainers building detection pipelines or security data processors
- Detection engineers who need vendor-neutral rules and sample corpora
- Backend authors translating or evaluating Sigma rules over normalized event streams
- Security operations teams debugging rule drift and false positives

# Users & user stories

- **Detection engineer**: “Tell me exactly which part of my Sigma rule cannot be represented in the target OCSF-backed pipeline.”
- **Backend maintainer**: “Pin the Sigma and OCSF surfaces I support, then diff the next release safely.”
- **SOC team**: “Share a minimal corpus that reproduces the false positive without shipping production logs.”
- **Standards integrator**: “Show whether the mismatch is in taxonomy, field availability, correlation semantics, or backend policy.”

# Prior art (and why it’s insufficient)

- Sigma now has official specifications for rules, correlations, filters, taxonomy, and modifiers.
- OCSF provides an extensible, vendor-agnostic core security schema and a browsable normative schema surface.
- Rust has active Sigma and OCSF ecosystem pieces.

What Rust still lacks is a **single coordination artifact** for pinning versions, preserving semantic mapping decisions, shipping redactable corpora, and computing compatibility diffs.

# Design goals

1. **Semantic honesty** — clearly separate exact mappings, lossy mappings, and unsupported constructs.
2. **Version-pinned** — Sigma and OCSF versions must be explicit in every bundle.
3. **Backend-neutral** — the core must sit above specific SIEMs or query engines.
4. **Redaction-first** — corpora must be safe to share.
5. **Tuning-friendly** — allow documented suppressions and environment overlays without mutating source rules.

# MVP surface

- Minimal types: `SigmaLock`, `DetectionIr`, `MappingReceipt`, `SamplePack`, `DetBundle`
- Minimal functions:
  - `parse_rule_set()`
  - `normalize_events()`
  - `map_rule_to_ocsf()`
  - `write_bundle()`
- Feature flags:
  - `sigma-rules`
  - `correlations`
  - `ocsf`
  - `samples`
  - `redaction`

# Compatibility story

- Adapts existing Sigma parsers/evaluators rather than replacing them.
- Treats OCSF as a normalized target surface, not the only possible runtime schema.
- Keeps backend-specific query generation in adapters around one stable evidence format.
- Distinguishes strict conformance, advisory mapping, and local suppressions.

# Conformance & fixtures

- Tiny corpora for authentication, process, file, and network events with raw + normalized OCSF forms.
- Goldens for modifier handling, taxonomy mismatches, correlation rules, and lossy mappings.
- Fixture packs that demonstrate exact-match, partial-match, and unsupported semantics.
- Public regression corpus for sample false-positive and false-negative cases.

# Path to boring stability

- Stabilize the lockfile, mapping receipt schema, and corpus format first.
- Keep backend adapters thin and versioned separately.
- Start with explainability and reproducibility rather than real-time detection performance.
- Model suppressions as overlays, not silent edits to rules.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that pin Sigma and OCSF versions, parse rules, normalize a small event corpus, produce explainable mapping receipts, and emit compact `*.detbundle.zip` artifacts.

# De-risk plan

1. Start with read-only mapping receipts and sample packs.
2. Delay broad backend-query generation until the neutral IR is stable.
3. Keep corpus tooling tiny and redactable.
4. Treat correlations as a separately versioned capability pack.

# Non-goals

- Not a SIEM.
- Not a full event-ingestion platform.
- Not a replacement for Sigma authoring tools.
- Not a giant threat-intelligence ontology.

# Architecture & API sketch

```rust
pub struct SigmaLock {
    pub sigma_spec: String,
    pub taxonomy_version: String,
    pub ocsf_version: String,
    pub backend_profile: String,
}

pub fn parse_rule_set(input: &str) -> Result<Vec<DetectionIr>>;
pub fn normalize_events(raw: &[u8], ocsf_version: &str) -> Result<SamplePack>;
pub fn map_rule_to_ocsf(rule: &DetectionIr, pack: &SamplePack) -> MappingReceipt;
```

Bundle draft: `sigma.lock`, `rules/`, `samples/`, `mappings.json`, `findings.json`, `suppressions.json`, `notes.md`.

# Security / safety model

- Default to structural normalization and sampled payloads rather than full raw-log export.
- Support field hashing, truncation, and tokenization for sensitive values.
- Record what mappings were guessed or environment-specific.
- Keep sample packs bounded and deterministic for CI usage.

# Maintenance & governance plan

- Keep the core centered on locks, mapping receipts, samples, and diffs.
- Version Sigma and OCSF overlays independently.
- Publish a small public corpus with representative, legally shareable events.
- Resist product creep into “security data platform” scope.

# Milestones

## 0.1
- Sigma parsing adapter
- OCSF normalization basics
- mapping receipts

## 0.2
- correlation overlays
- redacted sample packs
- compatibility diffs

## 1.0
- stable `*.detbundle.zip`
- documented version policy across Sigma and OCSF changes
- public regression corpus

# Open questions

- Which backend traits belong in the neutral IR versus adapters?
- How much of Sigma correlation semantics should be first-class in MVP?
- What is the cleanest way to express environment-specific suppressions without corrupting shareable bundles?

# Sources

- Sigma specification landing page: https://sigmahq.io/sigma-specification/
- Sigma rules specification: https://sigmahq.io/sigma-specification/specification/sigma-rules-specification.html
- Sigma correlations: https://sigmahq.io/docs/meta/correlations.html
- OCSF overview: https://ocsf.io/
- OCSF schema browser example class: https://schema.ocsf.io/classes/authentication
- `rsigma` Rust toolkit: https://github.com/timescale/rsigma
