---
id: P-0317
title: Asset Administration Shell (AAS) + AASX Conformance & Evidence Kit — profile-pinned digital-twin payloads, semantic diffs, and portable exchange bundles
status: idea
domains: [industrial, digital-twins, aas, aasx, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://industrialdigitaltwin.org/en/content-hub/aasspecifications
  - https://industrialdigitaltwin.io/aas-specifications/index/home/index.html
  - https://github.com/admin-shell-io/aas-specs-api
  - https://github.com/eclipse-basyx/basyx-rust-sdk
  - https://crates.io/crates/aas
---

# Problem

Rust now has real AAS movement, but the expensive failures are no longer at the level of “can I deserialize JSON at all?” They sit in the missing middle:

- metamodel version drift,
- API/profile mismatches,
- shell/submodel semantic changes that are hard to explain,
- package-file (`.aasx`) exchange differences,
- and partner or plant handoffs that still travel as screenshots, giant ZIPs, or vague bug reports.

The worthy crate contribution here is not a giant Industry 4.0 platform. It is a **conformance and evidence workbench** that turns AAS payloads and exchanges into deterministic, diffable, portable artifacts.

# What it provides

- `aas-ir` — canonical IR for shells, submodels, references, concept descriptions, qualifiers, and package manifests.
- `aas-profile` — lockfiles that pin exact spec release assumptions (e.g. metamodel/API/package format snapshots, extension policies, namespace expectations).
- `aas-verify` — semantic checks for referential integrity, required surfaces, API/profile compliance, and package/extract consistency.
- `aas-diff` — explainable diffs: “reference target changed”, “semanticId moved”, “submodel element cardinality violated”, “package contains stale serialized copy”.
- `aasx-replay` — deterministic round-trip and exchange replay for JSON/API/package workflows.
- `cargo aasx` — emit `*.aasbundle.zip` for interop labs, supplier onboarding, and long-lived industrial evidence.

# What the crate should provide other people

1. **A boring-default artifact for industrial exchange debugging** instead of giant proprietary handoff bundles.
2. **Version/profile pinning** for exact AAS assumptions so vendors and integrators stop arguing from different snapshots.
3. **Semantic diffs** that speak in AAS terms, not raw JSON patch.
4. **AASX-aware round-trip checks** that make packaging errors reproducible in CI.
5. **A practical bridge from today’s Rust AAS crates to conformance-grade digital-twin workflows**.

# Users & user stories

- **Industrial platform teams**: “Tell me whether this break is a metamodel issue, an API issue, or a packaging issue.”
- **Suppliers / OEMs**: “Ship an AAS evidence bundle with the release so customers can diff against last quarter’s payload.”
- **Plant integrators**: “Verify the package we received actually matches the API payload we validated.”
- **Tool vendors**: “Replay edge-case shells and package files across versions before shipping.”

# Prior art (and why it’s insufficient)

- IDTA now publishes current AAS releases, including metamodel, APIs, security, and package-file format specifications.
- Machine-readable API artifacts exist, which means a Rust workbench can be spec-pinned instead of hand-wavy.
- Rust substrate exists in the `aas` crate and in the BaSyx Rust SDK.
- But those pieces do not yet yield a **portable conformance artifact, semantic diff workflow, or AASX-centered replay story**.

# Design goals

1. **Spec-pinned** — every fixture pack states the exact AAS release and API assumptions.
2. **Semantic, not textual** — diffs must speak in shells/submodels/references/semantics, not just bytes.
3. **Package-aware** — `.aasx` is first-class, not an afterthought.
4. **Industrial portability** — results must survive ticket systems, supplier handoffs, and CI archives.
5. **Adapter-first** — wrap existing Rust SDKs instead of replacing them.

# Non-goals

- Not a full digital-twin platform.
- Not a proprietary PLM/MES/SCADA integration suite.
- Not a general GUI modeling environment.

# Architecture & API sketch

```rust
pub struct AasReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub semantic_findings: Vec<SemanticFinding>,
    pub package_findings: Vec<PackageFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_exchange(profile: &AasProfile, exchange: &AasExchange) -> AasReport;
```

Bundle draft: `profile.toml`, `shells/*.json`, `submodels/*.json`, `package/manifest.json`, `package/original.aasx`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support redaction or hashing of internal asset identifiers, URLs, vendor names, and proprietary strings.
- Bound unpacking behavior for `.aasx` inputs.
- Keep raw package bytes optional when policy forbids redistribution.
- Preserve exact verifier version and profile hash for long-lived evidence.

# Maintenance & governance plan

- Pin exact IDTA release assumptions in fixture packs.
- Keep IR additive and transport-neutral.
- Publish scenario packs for broken references, stale package payloads, profile drift, and cross-version round trips.
- Encourage public synthetic fixtures to avoid leaking plant data.

# Milestones

## 0.1
- Canonical AAS IR
- Profile lockfiles
- Basic semantic verification and bundle format

## 0.2
- AASX unpack/round-trip checks
- Semantic diff engine
- API/profile scenario corpus

## 1.0
- Stable `*.aasbundle.zip`
- Adapters for multiple Rust AAS implementations
- CI-ready supplier/onboarding workflows

# Open questions

- How much package-file logic belongs in core versus adapters?
- Should API conformance and payload semantics remain one crate family or split later?
- Which extension/customization points can be normalized without hiding important differences?

# Sources

- IDTA AAS specifications hub: https://industrialdigitaltwin.org/en/content-hub/aasspecifications
- AAS release index (Release 25-01, current part versions): https://industrialdigitaltwin.io/aas-specifications/index/home/index.html
- AAS API specifications repo: https://github.com/admin-shell-io/aas-specs-api
- Eclipse BaSyx Rust SDK: https://github.com/eclipse-basyx/basyx-rust-sdk
- `aas` crate: https://crates.io/crates/aas
