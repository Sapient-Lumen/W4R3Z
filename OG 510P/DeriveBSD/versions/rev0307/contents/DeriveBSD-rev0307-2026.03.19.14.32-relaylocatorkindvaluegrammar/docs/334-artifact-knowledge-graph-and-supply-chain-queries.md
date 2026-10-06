# Artifact knowledge graph (GUAC-style) + supply-chain queries

DeriveBSD’s evidence spine and `causality.graph` make incidents explainable.
But modern supply-chain practice produces *a lot* of metadata:
SBOMs, VEX, provenance, test receipts, scorecards, transparency proofs, identity receipts.

A greenfield OS can bake in something most systems bolt on late:

**a queryable, normalized knowledge graph of “what do we know about the artifacts we run?”**

This is not primarily a security feature; it is an operability feature.
If an operator can’t answer “where is this vulnerable thing deployed?” quickly, the rest is theatre.

Prior art worth stealing:
- GUAC (Graph for Understanding Artifact Composition) vision + ingestion model: https://guac.sh/guac/
- GUAC discussion of “known/unknown” gaps in supply chain metadata: https://docs.guac.sh/guac/known-and-unknown/


## 1) What problem this solves for DeriveBSD

Examples that should be first-class queries:
- “Which host generations include `openssl@3.0.x`?”
- “Which running jails/microVMs were built from a closure that depends on `libfoo`?”
- “Show all artifacts missing provenance or missing an SBOM.”
- “Show artifacts where SBOM says X, but VEX says ‘not affected’ and explain why.”
- “Show changes that introduced a new network egress destination.”

Today, ecosystems often solve this with a central scanning product.
DeriveBSD can instead make it a **derived, local-first capability**:
- ingest evidence objects that already exist (SBOM/VEX/provenance/identity)
- normalize into a compact “facts” graph
- enable queries locally and optionally sync summaries centrally


## 2) How this fits existing DeriveBSD artifacts

We already have the right primitives:
- closure manifests (`spec/closure.manifest.schema.json`) link outputs to inputs
- evidence objects are digested and typed (`docs/229-evidence-spine-overview.md`)
- `causality.graph` provides a minimal “bundle-min” index for incidents (`docs/246-causality-graphs-and-minimal-evidence-bundles.md`)

The knowledge graph is a *different projection*:
- causality graph: “what caused what” for a particular system/change
- knowledge graph: “what do we know about this artifact set” across time


## 3) Proposed shape: derived facts + local query engine

### A) Fact extraction is deterministic

Define a compiler:
- input: evidence objects (SBOM, VEX, provenance, publisher identity, test receipts)
- output: a normalized set of **fact records**

Rules:
- facts are derived only from verified evidence objects
- every fact record points back to the originating evidence digest(s)
- facts are recomputable (no hidden state)

### B) Storage can be implementation-defined

The conceptual interface is a query engine (CLI and API):
- `derive query depends-on <purl or digest>`
- `derive query affected-by <cve>`
- `derive query missing-attestation <predicate>`

Backend choices (not decided here):
- embedded SQLite with adjacency tables
- a local graph DB
- exportable summaries for fleet services


## 4) “Bake-in now” recommendation

- Treat “facts extraction” as a **first-class derived operation** with receipts.
- Ensure SBOM/VEX/provenance lanes always produce machine-queryable identifiers:
  - purl/cpe where applicable
  - digest linkage (closure → subject)
- Add a small stable query surface early (even if implementation is primitive).

See: `docs/168-sboms-and-vex-as-evidence.md`, `docs/246-causality-graphs-and-minimal-evidence-bundles.md`.

Last updated: 2026-02-26r92
