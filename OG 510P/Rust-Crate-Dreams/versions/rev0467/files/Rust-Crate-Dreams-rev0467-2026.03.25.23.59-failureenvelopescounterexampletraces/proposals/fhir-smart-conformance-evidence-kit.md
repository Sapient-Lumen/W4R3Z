---
id: P-0303
title: FHIR + SMART App Launch Conformance & Evidence Kit — IG-pinned validation, launch replay, and redactable health API bundles
status: idea
domains: [healthcare, apis, security, interoperability, compliance]
last_reviewed: 2026-03-06
evidence:
  - https://hl7.org/fhir/R4/
  - https://projectlifedashboard.hl7.org/specifications/hl7-fhir-uv-smart-app-launch-v2-1-0/
  - https://inferno.healthit.gov/
---

# Problem

Rust FHIR substrate is improving — `helios-fhir`, `helios-fhirpath`, `fhir-rs`, and related crates are real signals — but the hard part for implementers is rarely “deserialize a Patient resource.” The hard part is **conformance to implementation guides, profile constraints, SMART launch behavior, and reproducible evidence** when systems disagree.

That matters even more because FHIR adoption is coupled to implementation guides, formal validation, and public testing infrastructure such as Inferno. The missing Rust opportunity is therefore not just a codec or model generator; it is a **guide-pinned conformance and incident workbench**.

# What it provides

- `fhir-ig-lock` — pin StructureDefinitions, ValueSets, CapabilityStatements, and guide versions.
- `smart-launch-replay` — deterministic SMART App Launch flow replay with PKCE, scopes, token exchange, and resource-access checks.
- `fhir-evidence` — canonical IR for request/response exchanges, validation outcomes, and profile mismatches.
- `fhir-fixtures` — scenario packs for read/search/create/update, profile validation, SMART scopes, and versioned guide regressions.
- `fhir-diff` — semantic diffs for resource meaning, profile violations, search-parameter behavior, and auth-scope mismatches.
- `cargo fhir-interop` — emit `*.fhirbundle.zip` bundles for vendor support, certification rehearsal, and CI regression.

# What the crate should provide other people

1. **Guide-pinned reproducibility** — the same resource can validate differently under different guides or guide versions; that must be explicit.
2. **Launch-and-data evidence in one place** — auth failures and resource failures belong in the same bundle.
3. **Redactable incident sharing** — enough structure for debugging without casually shipping PHI.
4. **Validator pluralism** — compare Rust-native validation with external/reference validators instead of pretending one engine is always enough.
5. **Framework-neutral integration** — libraries and services using Axum, Actix, tonic, or custom stacks should all be able to plug in.

# Users & user stories

- **EHR / payer / provider API teams**: “Which exact guide rule or SMART scope caused this flow to fail?”
- **Integrator teams**: “Replay the failing launch + API sequence against today’s build.”
- **SDK/tool authors**: “Pin one guide snapshot and compare outputs across validators.”
- **Compliance / certification teams**: “Rehearse public test scenarios locally with artifacted results.”

# Prior art (and why it’s insufficient)

- The HL7 FHIR specification and SMART App Launch guide define the target behavior.
- Inferno and the HL7 validator ecosystem prove that conformance tooling matters and that testable IG behavior is the real problem.
- Existing Rust crates provide type models and FHIRPath substrate, but not a cohesive **IG lockfile + auth replay + evidence bundle** story.

# Design goals

1. **Implementation-guide first** — raw FHIR resources are not enough.
2. **Auth + resource unification** — SMART launch and FHIR API behavior must be testable together.
3. **PHI-minimizing bundles** — aggressive redaction/tokenization with provenance preserved.
4. **Explainable verdicts** — map failures back to specific guide rules, scopes, searches, or resource constraints.
5. **Version realism** — R4, R4B, and R5 drift should be explicit, not implicit.

# Non-goals

- Not a full EHR.
- Not an end-user health portal.
- Not a replacement for all official validator services.

# Architecture & API sketch

```rust
pub struct FhirInteropReport {
    pub guide_id: String,
    pub launch_profile: String,
    pub verdicts: Vec<Verdict>,
    pub validation_results: Vec<ValidationResult>,
}

pub trait FhirEndpoint {
    fn request(&mut self, req: CanonicalHttpRequest) -> Result<CanonicalHttpResponse, Error>;
}

pub fn replay(bundle: &FhirBundle, endpoint: &mut dyn FhirEndpoint) -> Result<FhirInteropReport, Error>;
```

Bundle draft: `ig.lock`, `launch-flow.json`, `http.jsonl`, `resources.ndjson`, `validator-results.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default redaction for direct identifiers, access tokens, patient references, addresses, and narrative text.
- Keep token handling and launch-state secrets out of bundles.
- Support tokenization/pseudonymization so behavior survives while identities do not.
- Explicit PHI-handling modes with hard warnings before raw export.

# Maintenance & governance plan

- Keep guide pinning and replay core separate from validator adapters.
- Ship public scenario packs first for open guides and generic SMART flows.
- Record exact HL7/guide publication versions in lockfiles.
- Encourage adapters around official/public testing tools rather than re-implementing everything.

# Milestones

## 0.1
- Guide lockfile format
- Canonical HTTP/resource IR
- SMART launch capture + replay basics

## 0.2
- Validator adapters
- Search/profile diffing
- `cargo fhir-interop replay`

## 1.0
- Stable `*.fhirbundle.zip`
- Public guide packs for common interoperability surfaces
- Explainable verdict mapping to guide/scope/validator failures

# Open questions

- Which official/public guides should be first-class in the MVP?
- How much FHIRPath / invariant evaluation belongs in core versus adapters?
- Can bundles preserve enough context for debugging while staying PHI-safe by default?

# Sources

- HL7 FHIR R4: https://hl7.org/fhir/R4/
- SMART App Launch guide: https://projectlifedashboard.hl7.org/specifications/hl7-fhir-uv-smart-app-launch-v2-1-0/
- Inferno public testing service: https://inferno.healthit.gov/
- Inferno docs / validator dependency notes: https://inferno-framework.github.io/docs/
- ONC/CMS references to Inferno and FHIR testing: https://www.cms.gov/priorities/burden-reduction/overview/interoperability/frequently-asked-questions/standards-and-implementation-guides
- Rust crates: https://crates.io/crates/helios-fhir ; https://crates.io/crates/helios-fhirpath ; https://crates.io/crates/fhir-rs ; https://crates.io/crates/fhir
