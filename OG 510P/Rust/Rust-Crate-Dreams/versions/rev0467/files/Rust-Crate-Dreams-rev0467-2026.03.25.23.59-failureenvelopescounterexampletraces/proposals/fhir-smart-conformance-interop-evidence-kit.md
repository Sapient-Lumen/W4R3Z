---
id: P-0229
title: FHIR + SMART on FHIR Conformance & Interop Evidence Kit
status: idea
domains: [healthcare, apis, security, interop, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://www.hl7.org/fhir/http.html
  - https://build.fhir.org/ig/HL7/smart-app-launch/
---

# Problem

FHIR adoption is broad, but implementers still struggle with **real interoperability**:

- subtle REST behavior differences across servers (search, conditional operations, patch/version sensitivity),
- conformance to profiles/IGs (StructureDefinitions, ValueSets) and “what broke” explanations,
- SMART on FHIR authorization edge cases in OAuth-based launches.

Rust has building blocks (HTTP clients, JSON, OAuth libraries), and some FHIR parsers, but lacks a cohesive, *profile-first* **conformance & evidence kit** that teams can plug into CI to verify “we interoperate” and produce a shareable, redactable repro.

# What it provides

1. Workspace crates:
   - `fhir-ir`: minimal stable IR for resources + meta, with lossless JSON preservation.
   - `fhir-validate`: profile/terminology validation surface (StructureDefinition/ValueSet hooks).
   - `fhir-rest-harness`: scenario DSL for REST interactions + canonical request/response capture.
   - `smart-launch-harness`: SMART launch flows (EHR launch/standalone), token exchange helpers, scope checks.
   - `fhir-diff`: semantic diffs (resources, bundles, search result sets).
   - `fhir-cli`: `run|validate|canon|diff|bundle`.

2. Evidence bundle format: `*.fhirbundle.zip`
   - `scenarios/` (declarative scenarios)
   - `http/` (canonicalized transcripts)
   - `resources/` (redacted payloads or hashes)
   - `reports/` (validation + conformance results)
   - `policy/redaction.json`

3. Conformance pack workflow
   - per-IG packs: pinned definitions + test scenarios + expected behaviors.

# Users & user stories

- **FHIR server operators**: “We want CI that proves our REST behavior and profile conformance didn’t regress.”
- **App developers**: “We want a simulator harness for SMART launch flows and scope behavior across environments.”
- **Integration teams**: “We need a repro bundle to share with partners without leaking PHI.”

# Prior art (and why it’s insufficient)

- The FHIR RESTful API spec includes behavior that is *version sensitive* (e.g., PATCH guidance), and implementers need tooling to surface these differences consistently.
- SMART App Launch specifies OAuth-based patterns for authorization against FHIR systems; real deployments vary and require interop harnessing.
- Existing tools exist in other ecosystems, but Rust lacks an opinionated, reusable kit centered on reproducible evidence bundles.

# Design goals

- **Profile-first**: conformance packs are first-class, not afterthought.
- **Deterministic transcripts**: stable canonicalization for diffs and review.
- **Redaction-by-default**: PHI-safe sharing with explicit policies.
- **Composable**: use crates as libraries or via CLI.

# Non-goals

- Becoming a full EHR/FHIR server implementation.
- Encoding every national IG by default (packs are modular).

# Architecture & API sketch

```rust
pub struct Scenario { /* steps */ }

pub fn run_scenario(cfg: RunCfg, s: &Scenario) -> Result<RunReport>;

pub fn validate_resources(pack: &ConformancePack, docs: &[ResourceDoc]) -> ValidationReport;

pub fn smart_launch(flow: SmartFlowCfg) -> Result<SmartTranscript>;

pub fn write_fhirbundle(inputs: BundleInputs) -> Result<PathBuf>;
```

# Security / safety model

- Default redaction policy:
  - remove/replace identifiers, names, addresses, free text,
  - allow hash-only mode for payloads,
  - size caps + explicit “unsafe fields present” warnings.

# Maintenance & governance plan

- Start with a *small* set of common scenarios and a pack format; grow via community packs.
- Strong versioning: pin FHIR version + IG versions per pack.

# Milestones

1. **MVP (4–8 weeks)**
   - scenario runner with canonical HTTP transcripts
   - bundle writer + minimal schema
   - basic diff and report generation
   - SMART auth helper (authorization code flow, token parsing)

2. **Conformance expansion (next)**
   - pack format for StructureDefinitions/ValueSets
   - validator hooks (terminology adapters)

# Open questions

- Which “minimum useful” validation surface can ship without embedding a full terminology server?
- How to best structure pack distribution and caching.

# Sources

- HL7 FHIR RESTful API specification (noting version sensitivity and REST behaviors). https://www.hl7.org/fhir/http.html
- SMART App Launch implementation guide (OAuth-based patterns for apps integrating with FHIR systems). https://build.fhir.org/ig/HL7/smart-app-launch/
