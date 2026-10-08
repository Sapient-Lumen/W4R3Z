---
id: P-0316
title: STIX 2.1 + TAXII 2.1 Interop & Evidence Kit — threat-intel profile packs, collection replay, and explainable CTI bundle diffs
status: idea
domains: [security, threat-intelligence, stix, taxii, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://oasis-open.github.io/cti-documentation/
  - https://oasis-open.github.io/cti-documentation/taxii/intro.html
  - https://oasis-open.github.io/cti-documentation/resources.html
  - https://crates.io/crates/stix2
---

# Problem

Cyber-threat intelligence exchange is a classic interoperability trap:

- syntax validity is not enough if collections, filtering, object versioning, markings, or pattern behavior diverge,
- TAXII and STIX are related but distinct layers, so “we support CTI exchange” often hides boundary failures,
- incident response teams need small, replayable bundles rather than full production servers or giant JSON dumps,
- Rust has some STIX substrate, but no obvious default for **interop rehearsal, semantic diffing, and evidence shipping**.

A worthy crate contribution would be a **STIX/TAXII interop and evidence kit** that turns CTI-exchange failures into portable, policy-aware artifacts.

# What it provides

- `cti-profile` — lockfiles for STIX version/features, TAXII API assumptions, markings rules, object-size policies, and supported filter/query behavior.
- `stix-canon` — canonical IR for bundles, objects, relationships, markings, and object versions.
- `taxii-replay` — deterministic replay of collection operations, filtering, pagination, auth/header assumptions, and sync workflows.
- `cti-diff` — semantic diffs for “which threat-intel meaning changed”, not just JSON text.
- `cti-verify` — checks collection behavior, required STIX/TAXII semantics, and interoperability-test expectations.
- `cargo cti` — emit `*.ctibundle.zip` for vendor support, SOC integration testing, and sharing-lab regression CI.

# What the crate should provide other people

1. **A profile-aware CTI exchange artifact** that multiple tools can replay.
2. **Semantic diffs for intelligence objects** so analysts and engineers can separate meaningful changes from format noise.
3. **Collection/workflow replay** without standing up full production infrastructure.
4. **A Rust-native path into standards-based threat-intel interoperability testing**.
5. **A reusable evidence format** for blue-team vendors, integrators, and large enterprises.

# Users & user stories

- **Threat-intel platform teams**: “Replay the failing TAXII collection sync against a patched server.”
- **SOC integration engineers**: “Prove whether the failure is auth, pagination, filtering, or STIX object semantics.”
- **Vendors**: “Ship a conformance bundle with releases instead of a marketing claim.”
- **Analysts**: “Explain what threat-intel meaning changed between two feeds or two toolchains.”

# Prior art (and why it’s insufficient)

- OASIS provides strong public STIX/TAXII explanations and interoperability test resources.
- Rust has STIX crates and OASIS-hosted Rust API work, which means this is not pure greenfield.
- The missing leverage is the boring layer: **profile packs, replay, semantic diffs, and small evidence bundles**.

# Design goals

1. **Meaning over raw JSON** — relationships, markings, and versions matter.
2. **Transport + content together** — TAXII and STIX must be debugged as a coupled boundary.
3. **Policy-aware** — size limits, markings, and filter support belong in profiles.
4. **Portable and safe** — enough redaction to share failures outside a single organization.
5. **Works with existing substrate** — complement, do not replace, evolving STIX crates.

# Non-goals

- Not a full TIP/TI platform.
- Not a SIEM.
- Not a substitute for broader detection/content engineering workflows.

# Architecture & API sketch

```rust
pub struct CtiInteropReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub collection_findings: Vec<CollectionFinding>,
    pub semantic_diffs: Vec<SemanticDiff>,
}

pub fn verify_exchange(profile: &Profile, exchange: &CtiExchange) -> CtiInteropReport;
```

Bundle draft: `profile.toml`, `requests.jsonl`, `responses/`, `objects.jsonl`, `markings.json`, `verdicts.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support removal or hashing of sensitive indicators, identity objects, and internal collection names.
- Preserve object IDs/version ordering and markings provenance across redaction.
- Bound replay resource usage for large bundle histories.
- Make auth and trust assumptions explicit but pluggable.

# Maintenance & governance plan

- Pin exact STIX 2.1 / TAXII 2.1 expectations and interoperability-test references.
- Publish fixture packs for collection listing, object add/update/delete, filtering, pagination, and markings cases.
- Keep semantic-object modeling separate from HTTP/TAXII capture logic.
- Encourage vendor-neutral failing bundles and “known divergence” catalogs.

# Milestones

## 0.1
- Canonical STIX IR
- TAXII transcript replay
- Profile packs + draft bundle format

## 0.2
- Semantic diffing and markings diagnostics
- Interoperability-test adapters
- Redaction presets and fixture corpus

## 1.0
- Stable `*.ctibundle.zip`
- CI-ready conformance workflows
- Multi-tool interoperability lab support

# Open questions

- Which STIX patterning checks belong in MVP versus later overlays?
- How should authentication assumptions be encoded without overfitting vendors?
- Should the core canonical model be useful outside TAXII, e.g. file-based exchange or offline curation?

# Sources

- OASIS CTI documentation hub: https://oasis-open.github.io/cti-documentation/
- TAXII introduction: https://oasis-open.github.io/cti-documentation/taxii/intro.html
- STIX/TAXII interoperability resources: https://oasis-open.github.io/cti-documentation/resources.html
- `stix2`: https://crates.io/crates/stix2
