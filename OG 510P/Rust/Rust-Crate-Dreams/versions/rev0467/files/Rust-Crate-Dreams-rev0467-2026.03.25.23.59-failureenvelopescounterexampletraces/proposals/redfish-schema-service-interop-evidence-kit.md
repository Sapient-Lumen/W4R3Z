---
id: P-0260
title: Redfish Schema + Service Interop & Evidence Kit
status: idea
domains: [datacenter, management, schemas, interop, conformance, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://redfish.dmtf.org/redfish/schema_index
  - https://www.dmtf.org/sites/default/files/standards/documents/DSP0268_2024.3.pdf
  - https://www.dmtf.org/sites/default/files/standards/documents/DSP2046_2025.1.pdf
---

# Problem

Redfish is a widely adopted, web-friendly management interface for datacenter hardware and infrastructure. In practice, teams struggle with:

- **Schema drift** across versions and vendors
- inconsistent service behavior under optional/conditional properties
- fragile client generators and tests due to non-canonical payloads and incomplete schema/registry alignment

The ecosystem lacks a **portable, reproducible** way to capture “this service behaves like X” as an artifact that can be diffed, shared, and replayed.

# What it provides

A Rust toolchain and evidence format:

- **`redfish-schema`**: schema index ingestion (JSON Schema and CSDL), with version pinning and normalization.
- **`redfish-svc-scan`**: safe crawling and capability discovery (respecting rate limits/auth) that produces canonical snapshots.
- **`redfish-conformance`**: a test runner against a service with:
  - structural validation (schema + message registries)
  - behavior probes (ETag, pagination, action invocation patterns, error payload shapes)
- **`redfish-diff`**: semantic diffing between service snapshots and between schema versions.
- **`redfishbundle`** (`*.redfishbundle.zip`): a signed, redactable evidence bundle (Evidence Bundle Core) containing:
  - pinned schema version + hash
  - canonical service snapshot (redacted)
  - conformance results + repro recipe
  - semantic diffs

# Users & user stories

- **Infra / SRE**: “Tell me what changed in this vendor firmware update and why my automation broke.”
- **Vendors**: “Run the same conformance probes and share a bundle with the community/test lab.”
- **Client authors**: “Generate stable, tested bindings from pinned schema versions.”

# Prior art (and why it’s insufficient)

- DMTF provides schema distributions and documentation, but not a Rust-first conformance harness with evidence artifacts.
- Many client SDKs exist, but they rarely produce **diffable service snapshots** and **shareable repro bundles**.

# Design goals

- **Schema-true**: treat schema versions as first-class inputs; pin everything.
- **Canonicalization**: stable ordering, normalized URIs, and controlled redaction.
- **Safe crawling**: avoid dangerous actions by default; explicit “active mode” for action probes.
- **Interop**: support multiple auth styles and vendor quirks via adapters.

# Non-goals

- Replace vendor certification programs.
- Become a full Redfish service implementation.

# Architecture & API sketch

CLI:

```bash
redfishkit scan --base https://bmc.example/redfish/v1 --auth bearer:... --out snapshot.redfishbundle.zip
redfishkit diff snapshotA.redfishbundle.zip snapshotB.redfishbundle.zip
redfishkit conformance --bundle snapshot.redfishbundle.zip --profile baseline
```

Crates:

- `redfish_schema` (schema ingestion + normalization)
- `redfish_client` (auth, paging, retry, backoff)
- `redfish_scan` (snapshot builder + redaction)
- `redfish_conformance` (profiles + probes)
- `redfishbundle` (bundle schema)

# Security / safety model

- Redaction presets: remove secrets, credentials, unique serials by default.
- Active probes (Actions) require explicit flags and allowlists.

# Maintenance & governance plan

- Track DMTF schema releases; keep fixture packs pinned.
- Maintain a public corpus of anonymized service snapshots for regression.

# Milestones

## MVP (4–8 weeks)
1. Schema ingestion + normalization for a pinned release
2. Service snapshotter (GET-only) + canonicalization
3. Baseline conformance profile (schema validation + a few behavior probes)
4. Bundle format + diff tool

## Next
- Message registry validation
- Action probes with safe allowlists
- Generator integration for typed clients

# Sources

- Redfish schema index and distributions.
- Redfish Data Model specification (DSP0268).
- Redfish Resource and Schema Guide (DSP2046).
