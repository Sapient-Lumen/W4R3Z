---
id: P-0420
title: GS1 Digital Link + EPC URI Translation Workbench Kit — barcode/web locks, resolver receipts, and explainable identifier transforms
status: idea
domains: [commerce, identifiers, barcodes, supply-chain, interoperability, web, validation]
last_reviewed: 2026-03-06
evidence:
  - https://www.gs1.org/standards/gs1-digital-link
  - https://ref.gs1.org/standards/digital-link/uri-syntax/
  - https://www.gs1.org/standards/tds
  - https://ref.gs1.org/standards/resolver/
  - https://crates.io/crates/gs1
---

# Problem

GS1 Digital Link is no longer just a standards-side experiment. GS1 now maintains current Digital Link materials, resolver guidance, and EPC/Tag Data standards that explicitly connect barcodes, EPC identity forms, and web-native resolution.

But real implementations still fail at the seam between:

- **a barcode or EPC identifier as scanned and the canonical identity form another system expects**,
- **GS1 key syntax, EPC URI syntax, and Digital Link URI forms that are related but not interchangeable**,
- **resolver behavior and the exact redirects, link types, and query semantics clients actually encountered**,
- **web-enabled product journeys and the supply-chain traceability identifiers behind them**,
- and **identifier-conversion code that silently normalizes, drops, or invents information.**

The missing Rust contribution is not another barcode generator. It is a **translation workbench** that pins source identifier form, Digital Link revision, EPC/GS1 assumptions, resolver interactions, and transform receipts into one boring artifact.

# What it provides

- `gs1.lock` — pins source identifier family, application identifier assumptions, Digital Link revision, resolver policy, and normalization rules.
- `translation-receipt` — records every step from barcode payload or EPC form to target URI / key / identity form.
- `resolver-replay` — compact receipt of redirects, linkset responses, and content negotiation.
- `loss-report` — explicit statement of what data was preserved, normalized, or dropped during translation.
- `cargo gs1-workbench` — emits `*.gs1bundle.zip` with fixtures, receipts, and resolver-safe evidence.

# What the crate should provide other people

1. **A boring identifier-conversion artifact** for commerce and traceability systems.
2. **An honest translation layer** between GS1 keys, EPC URIs, and Digital Link URIs.
3. **Replayable resolver evidence** for debugging client/partner disagreements.
4. **Loss-aware normalization** instead of magical “parse and stringify” behavior.
5. **A Rust-native validation core** that barcode, EPCIS, and web teams can share.

# Persona / who it’s for

- retail / supply-chain platform engineers
- traceability and EPCIS integrators
- barcode and resolver tool builders
- digital-product-link / consumer-engagement teams

# Users & user stories

- **Integrator**: “Show me exactly how this scan became that Digital Link URL.”
- **Resolver operator**: “Package the redirect and linkset behavior another partner is failing against.”
- **Traceability engineer**: “Prove whether this EPC URI and this Digital Link URI identify the same object under the pinned rules.”
- **SDK author**: “Reuse one lock/diff core rather than writing ad hoc translators.”

# Prior art (and why it’s insufficient)

- GS1 standards define Digital Link, resolver behavior, and EPC/Tag Data mappings.
- GS1 tooling exists for interactive translation and education.
- Rust has at least early GS1 identifier crates.

What Rust still lacks is a **portable transform/evidence layer** that pins the exact identifier form, mapping rule, resolver interaction, and loss surface together.

# Design goals

1. **Transform-explicit** — every identifier conversion step must be inspectable.
2. **Resolver-aware** — HTTP behavior is part of the interoperability surface.
3. **Loss-honest** — report normalization and dropped detail explicitly.
4. **Family-aware** — do not flatten GS1 keys, EPC URIs, and Digital Link URIs into one pretend-identical string type.
5. **CI-friendly** — fixture packs should be easy to run in automation.

# MVP surface

- Minimal types: `Gs1Lock`, `SourceIdentifier`, `TranslationReceipt`, `ResolverReplay`, `LossReport`, `Gs1Bundle`
- Minimal functions:
  - `parse_identifier()`
  - `translate_identifier()`
  - `replay_resolver()`
  - `diff_translations()`
  - `write_bundle()`
- Feature flags:
  - `digital-link`
  - `epc-uri`
  - `resolver`
  - `barcode-ai`
  - `redaction`

# Compatibility story

- Sits above barcode scanners, EPCIS stacks, and resolver clients.
- Supports offline transform validation and optional live resolver capture.
- Treats resolver behavior as an overlay above the core identifier model.
- Leaves label rendering and symbology image generation out of the core.

# Conformance & fixtures

- Goldens for GTIN/GLN/SSCC/EPC conversions, AI ordering, percent-encoding, path-vs-query normalization, and resolver redirect chains.
- Tiny corpora for multiple identifier families and serial/batch/expiry variants.
- Fixtures showing when two URIs are semantically equivalent versus textually different.
- Redacted bundles safe for partner bug reports.

# Path to boring stability

- Stabilize `gs1.lock`, translation receipts, and loss reports before broad scanner integration.
- Start with offline identity-form conversion and equivalence checks.
- Add resolver replay as an overlay.
- Resist drift into becoming a full commerce platform.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin a GS1 identifier family and Digital Link revision, record translation steps and loss reports, optionally capture resolver behavior, and package everything into `*.gs1bundle.zip`.

# De-risk plan

1. Start with offline identifier translations and equivalence checks.
2. Ship tiny public fixtures covering the most common GS1 key families.
3. Add live resolver capture only after the transform core is stable.
4. Pilot with EPCIS-adjacent teams that already need cross-form translation.

# Non-goals

- Not a barcode image rendering library.
- Not a resolver server.
- Not an EPCIS event store.
- Not a retail engagement platform.

# Architecture & API sketch

```rust
pub struct Gs1Lock {
    pub digital_link_version: String,
    pub source_family: String,
    pub target_family: String,
    pub resolver_policy: Option<String>,
}

pub fn parse_identifier(input: &str) -> Result<SourceIdentifier>;
pub fn translate_identifier(id: &SourceIdentifier, lock: &Gs1Lock) -> Result<TranslationReceipt>;
pub fn replay_resolver(url: &str) -> Result<ResolverReplay>;
pub fn diff_translations(a: &TranslationReceipt, b: &TranslationReceipt) -> LossReport;
```

Bundle draft: `gs1.lock`, `source.txt`, `translation-receipt.json`, `resolver-replay.json`, `loss-report.json`, `notes.md`.

# Security / safety model

- Support redaction of serial numbers, batch/lot numbers, and private resolver domains.
- Keep live resolver responses separate from normative transform receipts.
- Distinguish canonical equivalence from heuristic matching.
- Mark proprietary/private application identifiers and partner-specific rules explicitly.

# Maintenance & governance plan

- Track Digital Link, resolver, and EPC family revisions explicitly.
- Keep family-specific rules in data packs, not hard-coded branches everywhere.
- Publish a tiny fixture corpus for regression testing.
- Avoid turning the core into a commerce-stack monolith.

# Milestones

## 0.1
- `gs1.lock`
- offline identifier parser/translator
- loss-report schema

## 0.2
- resolver replay receipts
- equivalence diff engine
- redacted public fixtures

## 1.0
- stable `*.gs1bundle.zip`
- compatibility policy for GS1 family revisions
- CI-friendly transform approval gates

# Open questions

- What is the right portable representation for “same identity, different URI family” assertions?
- Which resolver behaviors belong in the portable core versus optional overlays?
- How should the workbench encode partner/private rules without pretending they are part of GS1 normative behavior?

# Sources

- GS1 Digital Link overview: https://www.gs1.org/standards/gs1-digital-link
- GS1 Digital Link URI Syntax: https://ref.gs1.org/standards/digital-link/uri-syntax/
- GS1 EPC Tag Data Standard overview: https://www.gs1.org/standards/tds
- GS1-Conformant Resolver Standard: https://ref.gs1.org/standards/resolver/
- `gs1` crate: https://crates.io/crates/gs1
