# Epic crate package-topology doctrine — 2026-03-25

This note answers a practical archive question:

**If a worthy missing Rust contribution is real, what package shape should it have in theory and practice?**

The answer should still be conservative.
The goal is not to turn every idea into a federation of microcrates.
The goal is to split packages where the **receiver**, **stability level**, or **substrate churn** genuinely differ.

## Main doctrine

A worthy crate contribution is often best shipped as a small suite with distinct package roles:

### 1. `*-core`
What it is for:
- pure semantics,
- packet production logic,
- diff/recheck logic,
- receiver-facing meaning.

What it should avoid:
- unnecessary network access,
- live service coupling,
- volatile substrate assumptions,
- giant optional dependency piles.

### 2. `*-schemas`
What it is for:
- stable serde types,
- JSON schema generation or checked definitions,
- packet versioning,
- cross-tool interoperability.

Why it matters:
If another team is meant to review and diff packets, the packet types should not be buried in a CLI crate.

### 3. `cargo-*` or `*-cli`
What it is for:
- one-shot operator workflows,
- CI entry points,
- report generation,
- rechecks and exports.

Why it matters:
A worthy contribution should be runnable by ordinary teams without embedding it first.

### 4. `*-adapter-*` or `*-import-*`
What it is for:
- crates.io imports,
- docs.rs imports,
- Cargo output imports,
- local-environment probes,
- other fast-moving substrate bridges.

Why it matters:
The archive already depends on surfaces that can change:
- docs.rs metadata and target defaults,
- crates.io trust/publishing/security surfaces,
- Cargo report/build-analysis work,
- eventual namespace/boundary/tooling changes.

Adapter churn should not destabilize packet meaning.

### 5. `*-corpus` or fixtures tree
What it is for:
- scenario packs,
- golden examples,
- regression corpora,
- matrix-preservation.

Why it matters:
A worthy crate should not rely on oral tradition to explain what its packets mean.

## What a worthy crate should provide other people

A strong contribution should usually provide at least four things:

### A. One easy command surface
For example:
- `cargo pathfinder explain`
- `cargo support-envelope inspect`
- `cargo debug-support matrix`

This is the adoption surface.

### B. One embeddable library API
For example:
- construct packets programmatically,
- import workspace/project state,
- diff and reopen old packets,
- integrate into org-specific workflows.

This is the automation surface.

### C. One stable packet vocabulary
For example:
- typed receipts and reports,
- stable field meaning,
- versioned schemas,
- migration notes.

This is the review surface.

### D. One reproducible corpus
For example:
- known tricky scenarios,
- matrix fixtures,
- failure examples,
- support-ceiling examples.

This is the honesty surface.

## Release doctrine

### Honest `0.1`
Usually ship:
- `*-core`
- `*-schemas`
- one `cargo-*` or CLI front door

Avoid at `0.1`:
- too many adapters,
- remote services,
- policy sprawl,
- fake cross-domain universality.

### Strong `0.3`
Usually add:
- adapter crates,
- richer corpus,
- policy overlays or reusable presets,
- stronger diff/recheck flows.

### Real `1.0`
Usually means:
- packet semantics stable,
- schema evolution policy explicit,
- adapter churn isolated,
- corpus strong enough to defend handoff semantics.

## Anti-patterns

### Anti-pattern 1 — the one-crate blob
Symptoms:
- CLI, library, schemas, probes, fixtures, and policy all in one package;
- difficult to embed;
- difficult to version packet semantics separately;
- heavy dependency footprint for every receiver.

### Anti-pattern 2 — unprincipled microcrates
Symptoms:
- splits that reflect maintainer taste rather than contract boundaries;
- extra package names without extra receiver clarity;
- workspace sprawl that makes adoption harder.

### Anti-pattern 3 — stable packets coupled to unstable imports
Symptoms:
- docs.rs / crates.io / Cargo quirks leak directly into packet meaning;
- every substrate change becomes a packet-breaking event.

## Practical archive rule after this pass

When planning a top-lane crate, the archive should now answer:
1. what is the smallest honest package family,
2. what surface each package serves,
3. what can stay unstable behind adapters,
4. what packet/schema meaning must stabilize,
5. and what corpus defends that meaning.

If the pass cannot answer those questions, the lane is still not fully planned.
