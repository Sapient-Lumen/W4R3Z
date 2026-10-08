---
id: P-0308
title: GS1 EPCIS 2.0 + CBV Conformance & Evidence Kit — canonical supply-chain events, vocabulary-aware validation, and recall-ready trace bundles
status: idea
domains: [supply-chain, logistics, traceability, standards, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.gs1.org/standards/epcis
  - https://ref.gs1.org/standards/epcis/
  - https://crates.io/crates/gs1
---

# Problem

EPCIS 2.0 is increasingly the shared language for **traceability, provenance, recalls, and multi-party supply-chain visibility**, but Rust lacks a strong default for the hard operational layer:

- validating event streams against EPCIS 2.0 and CBV assumptions,
- canonicalizing events for semantic diffing across partners,
- pinning business vocabulary/profile choices,
- reproducing “why did this traceability chain fail?” without passing around giant raw payload dumps.

The missing epic crate is not merely “parse some JSON-LD.” It is an **event-conformance and evidence kit** that makes supply-chain debugging, audits, and onboarding tractable.

# What it provides

- `epcis-canon` — canonical IR for object/aggregation/transformation/transaction/association events.
- `cbv-profile` — versioned vocab/profile packs for business steps, dispositions, identifiers, and partner constraints.
- `epcis-validate` — schema + semantic validation, including identifier hygiene and vocabulary-aware checks.
- `epcis-replay` — deterministic replay of event chains and query responses.
- `epcis-diff` — semantic diffs for event meaning, chronology, lineage, and vocabulary mismatches.
- `cargo epcis` — emit `*.epcisbundle.zip` for recalls, partner onboarding, and regulator/customer support.

# What the crate should provide other people

1. **A canonical event artifact** that can travel between manufacturers, logistics providers, retailers, and auditors.
2. **Vocabulary lockfiles** so teams can pin “our traceability dialect” instead of hand-waving about EPCIS support.
3. **Explainable lineage diffs** when two systems disagree about aggregation, transformation, or shipping history.
4. **Redactable evidence bundles** that preserve identifiers and timings without exposing unnecessary commercial detail.
5. **A path from today’s Rust GS1 utilities to tomorrow’s traceability workbench**.

# Users & user stories

- **Supply-chain platform teams**: “Show the first event where our partner’s vocabulary/profile diverged from ours.”
- **Recall / compliance teams**: “Package a verifiable trace bundle for affected lots without dumping the whole data lake.”
- **System integrators**: “Replay last week’s failed event-import chain against new validation rules.”
- **Retail / food / pharma operators**: “Prove lineage across transformation and aggregation steps.”

# Prior art (and why it’s insufficient)

- GS1 provides a mature standard and web-based references, which sharply reduces guesswork about what “correct enough” should mean.
- Rust has GS1-related substrate, but not a common **canonicalization + validation + replay + evidence** layer for EPCIS workflows.
- Most existing operational debugging still collapses into hand-comparing JSON/XML payloads and spreadsheets.

# Design goals

1. **Semantics before syntax** — event meaning and lineage matter more than original serialization.
2. **Vocabulary-aware** — CBV/business-step/disposition assumptions are explicit and versioned.
3. **Query-friendly** — support both event ingestion and query-response evidence.
4. **Partner-exchange ready** — bundles must be small enough and safe enough to share.
5. **Schema-neutral at the edges** — support JSON-LD/XML adapters without tying core logic to one wire form.

# Non-goals

- Not a full supply-chain visibility platform.
- Not a blockchain/provenance marketing layer.
- Not a warehouse-management system.

# Architecture & API sketch

```rust
pub struct EpcisReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub lineage_findings: Vec<LineageFinding>,
    pub divergences: Vec<Divergence>,
}

pub fn verify_events(profile: &CbvProfile, events: &[CanonicalEvent]) -> EpcisReport;
```

Bundle draft: `profile.toml`, `events.jsonl`, `queries.json`, `lineage.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Tokenize or hash business identifiers where full cleartext is not required.
- Support selective disclosure for lot/batch/item identity.
- Bound replay resource use for large event sets.
- Preserve provenance of profile versions and transformation steps.

# Maintenance & governance plan

- Keep the canonical event model additive and GS1-aligned.
- Publish fixture packs for common traceability stories: shipping, aggregation, transformation, return, recall.
- Separate core EPCIS/CBV logic from industry overlays (food, pharma, apparel, etc.).
- Record exact GS1 spec snapshot dates in bundles and profiles.

# Milestones

## 0.1
- Canonical event IR
- Profile/vocabulary lockfiles
- Validation + verdict model

## 0.2
- Replay/diff engine
- Lineage and recall fixture packs
- `cargo epcis diff`

## 1.0
- Stable `*.epcisbundle.zip`
- Query-response evidence support
- Industry overlay packs

# Open questions

- How much JSON-LD processing belongs in core versus adapters?
- Which query patterns deserve first-class replay in the MVP?
- How should partner-private vocab extensions be represented without breaking portability?

# Sources

- GS1 EPCIS overview: https://www.gs1.org/standards/epcis
- GS1 EPCIS reference portal: https://ref.gs1.org/standards/epcis/
- `gs1` crate: https://crates.io/crates/gs1
