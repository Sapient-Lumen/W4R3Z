---
id: P-0275
title: DID Resolution Interop & Evidence Kit — resolver conformance packs + didbundle.zip
status: idea
domains: [identity, web, standards, interoperability, testing, security]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/did-1.1/
  - https://www.w3.org/TR/did-resolution/
  - https://www.w3.org/TR/did-resolution/all/
---

## What it should provide others

A practical way to make Decentralized Identifier (DID) resolvers **predictable and interoperable** by shipping:

- **Conformance packs** (method-agnostic and method-specific fixtures) that can run in CI.
- A canonical **resolution result IR** (document + metadata + error handling) with stable diffs.
- **Evidence bundles** (`*.didbundle.zip`) that capture inputs, resolver config, and outputs in a redactable, replayable form.

## Why it is missing / worth building

The DID Core spec describes resolution at a high level and points to the DID Resolution spec for algorithms and result formats; in practice, resolver behavior varies widely across methods and implementations. Teams debugging “my DID resolves in stack A but not B” lack portable repro artifacts.

Rust has identity primitives, but the missing piece is a **standards-anchored harness**: fixtures + canonicalization + explainable diffs.

## Non-goals

- Not defining new DID methods.
- Not replacing universal resolvers; it should wrap and test them.

## Proposed design

### Workspace layout

- `did-evidence-core`
  - resolution result IR + canonicalization + bundle I/O (`didbundle.zip`)
- `did-fixtures`
  - method-agnostic corpora (syntax edges, DID URL deref, metadata combinations)
  - optional method packs (sidetree-like, did:web, etc.) as separate crates/repos
- `did-runner`
  - run resolvers via:
    - in-process Rust trait (native)
    - HTTP resolver API adapter
    - CLI adapter
- `did-report`
  - semantic diffs + “explain” layer (where did it deviate from expectations?)

### Canonical IR sketch

- `ResolveRequest { did, did_url?, accept, options }`
- `ResolveResult { did_document_ref, did_resolution_metadata, did_document_metadata }`
- `DerefResult { content_stream_ref, content_metadata, deref_metadata }`

### Evidence bundle (`*.didbundle.zip`)

- `request.json`
- `expected.json` (optional, per fixture)
- `observed.json`
- `resolver_fingerprint.json` (version, method modules enabled, network/dns mode)
- `diff.md` (human report)

## Minimum lovable MVP (4–8 weeks)

1. Implement IR + canonical JSON normalization and a diff reporter.
2. Add a small “core” fixture set (syntax + basic resolution metadata rules).
3. Provide HTTP-resolver adapter + CLI entrypoint (`didlab run`).

## De-risk plan

- Start with **method-agnostic invariants** (syntax, metadata rules, error classes).
- Make method packs opt-in to avoid political/maintenance churn.
- Ensure bundles work offline by allowing pinned resolver caches.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 3
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
