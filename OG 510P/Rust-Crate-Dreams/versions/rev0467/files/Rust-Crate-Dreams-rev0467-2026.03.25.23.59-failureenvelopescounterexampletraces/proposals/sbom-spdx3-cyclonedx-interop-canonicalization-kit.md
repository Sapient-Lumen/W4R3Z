---
id: P-0218
title: SBOM Interop & Canonicalization Kit (SPDX 3.x + CycloneDX 1.x) — normalize, diff, validate, and ship evidence bundles
status: idea
domains: [supply-chain, sbom, spdx, cyclonedx, conformance, tooling, security]
last_reviewed: 2026-03-05
evidence:
  - https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf
  - https://www.omg.org/spec/SPDX/3.0/About-SPDX
  - https://github.com/CycloneDX/specification  - https://ferrous-systems.com/blog/stackable-client/
needs:
  - Rust teams can *generate* SBOMs, but the missing middle is **interop-quality parsing, canonicalization, semantic diffs, and explainable validation** across *multiple* SBOM standards.
  - A stable, redactable, shareable artifact format so SBOM issues are reproducible (schema drift, component identity mismatch, dependency graph disagreements).
  - A “policy boundary” API that downstream tools (VEX, signing, attestation, compliance) can rely on.
risks:
  - Specs evolve (SPDX 3.x, CycloneDX 1.x). Must pin versions, support multi-version decoding, and be explicit about lossiness.
  - Identity semantics differ across formats; need a carefully designed internal IR with provenance metadata.
---

## Problem

SBOM adoption is being driven by policy/compliance and supply-chain security, but real-world pipelines frequently need to **round-trip** between formats and compare outputs from different generators. SPDX defines an underlying data model with multiple serializations, and SPDX 3.x broadens use-cases and profiles.
Source: https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf
Source: https://www.omg.org/spec/SPDX/3.0/About-SPDX

CycloneDX is another widely used BOM standard with an actively maintained specification and frequent releases.
Source: https://github.com/CycloneDX/specification

Rust has pieces (e.g., CycloneDX parsing crates), but the ecosystem lacks a **single, high-quality “SBOM interop workbench” crate** that provides:
- deterministic canonical forms,
- semantic diffs,
- strict/lenient validators with clear diagnostics,
- and portable evidence bundles for CI triage.

## What this crate should provide

### 1) Multi-format decode → internal IR (“SBOM-IR”)
- Parse and validate:
  - SPDX 3.x (at least JSON-LD/JSON if present in toolchains; support the most common serializations used in practice)
  - CycloneDX 1.x (JSON/XML)
- Convert into an internal, loss-aware IR:
  - `Component`, `Relationship`, `License`, `Evidence`, `Provenance`, `Pedigree`
  - explicit `LossNote` records when a field cannot be represented

### 2) Canonicalization (“stable, diffable SBOMs”)
- Deterministic ordering and normalization:
  - stable component keys (with explainable identity rules)
  - normalized timestamps and tool metadata
  - normalized PURLs/CPEs/URLs when possible
- Output:
  - `sbomir.json` (canonical IR)
  - `canon.spdx.json` / `canon.cdx.json` (best-effort canonical re-serialization)

### 3) Semantic diff + “explain why different”
- Compare two SBOMs (any format) and emit:
  - added/removed components
  - relationship graph diffs
  - identity collisions / suspicious merges
  - license field diffs (expression normalization)
  - “likely generator causes” heuristics (e.g., workspace dependency flattening)

### 4) Evidence bundles: `*.sbombundle.zip`
Bundle structure:
- `input/a.(spdx|cdx).json` / `input/b...`
- `ir/a.sbomir.json`, `ir/b.sbomir.json`
- `canon/a.json`, `canon/b.json`
- `diff/report.md`, `diff/report.json`
- `env/tooling.json` (generator versions, cargo metadata)
- `redaction/policy.json` (what was removed)

### 5) Cargo UX and CI affordances
- `cargo sbom diff a.json b.xml`
- `cargo sbom normalize --in foo.cdx.json --out canon.json`
- `cargo sbom validate --profile strict --explain`
- GitHub Actions helper: upload `*.sbombundle.zip` on failure

## Crate design (workspace layout)

- `sbom-ir` — internal types + identity rules + loss tracking
- `sbom-spdx3` — SPDX 3.x decode/encode adapters
- `sbom-cyclonedx` — CycloneDX decode/encode adapters
- `sbom-canon` — canonicalization engine
- `sbom-diff` — semantic diff engine + explainers
- `sbom-bundle` — bundle writer/reader + redaction plumbing
- `cargo-sbom` — CLI (thin wrapper)

## Minimum lovable MVP (4–8 weeks)

1. CycloneDX 1.6/1.7 JSON parse → IR → canonical IR output.
   - CycloneDX release history is explicit in the spec repo.
   Source: https://github.com/CycloneDX/specification
2. SPDX 3.x: implement **enough** parsing to support common fields (creation info, elements, relationships) with version pinning and “unsupported field” reporting.
   Source: https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf
3. `sbom-diff` for components + relationships.
4. Evidence bundles + `cargo sbom diff`.

## De-risk plan

- Start by supporting 2–3 well-known SBOM generators in fixtures, and lock golden outputs.
- Build a corpus of “real-world messy SBOMs” (with redaction policy) to drive lenient parsing.
- Publish “identity rules” as a spec in-repo and add fuzz tests to detect collisions.

## Scorecard (0–5)

- Impact: 5
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 5
- Sustainability: 3
- Differentiation: 4

## Prior art (and why it’s insufficient)

- CycloneDX parsing exists in Rust toolchains, but pipelines still struggle with canonical diffs and reproducible interop artifacts.
  Source: https://ferrous-systems.com/blog/stackable-client/
- SPDX-focused Rust crates often emphasize license expressions or older document models; SPDX 3.x pushes toward a broader data model with multiple serializations.
  Source: https://www.omg.org/spec/SPDX/3.0/About-SPDX

## Notes

This proposal pairs naturally with supply-chain signing/attestation crates, but should remain **format-interop + evidence** focused to avoid ballooning into a full policy engine.
