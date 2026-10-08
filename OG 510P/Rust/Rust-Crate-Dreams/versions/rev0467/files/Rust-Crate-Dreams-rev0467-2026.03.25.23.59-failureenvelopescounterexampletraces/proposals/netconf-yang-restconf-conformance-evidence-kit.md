---
id: P-0339
title: NETCONF + YANG + RESTCONF Conformance & Evidence Kit — model-driven network-management lockfiles, explainable capability drift, and replayable device bundles
status: idea
domains: [networking, netconf, restconf, yang, automation, interoperability, conformance]
last_reviewed: 2026-03-06
evidence:
  - https://www.rfc-editor.org/rfc/rfc6241.html
  - https://datatracker.ietf.org/doc/html/rfc7950
  - https://www.rfc-editor.org/rfc/rfc8040.html
  - https://docs.rs/netgauze-netconf-proto
  - https://crates.io/crates/netconf-rs
  - https://crates.io/crates/serde_yang
---

# Problem

Rust has credible low-level substrate for model-driven network management, but the operational pain still sits above raw protocol parsing:

- device capabilities and YANG module sets drift between firmware versions,
- NETCONF and RESTCONF surfaces disagree on what a device actually supports,
- payloads are syntactically valid but semantically wrong for a pinned model revision,
- replaying a failing config push often requires a whole lab environment instead of a small deterministic artifact,
- and support escalations still circulate as sanitized XML/JSON fragments with missing capability context.

The worthy crate contribution is a **conformance and evidence kit** that pins YANG/model assumptions, captures protocol capabilities and transactions, and emits replayable bundles that make device or controller drift explainable.

# What it provides

- `yang-lock` — lockfiles pinning YANG module sets, revisions, features, deviations, and capability expectations.
- `netconf-restconf-ir` — canonical Rust IR for capabilities, datastores, RPCs, notifications, YANG-JSON/YANG-XML payloads, and error surfaces.
- `capability-diff` — semantic diffs such as “same module name, different revision/features”, “RESTCONF advertises data path that NETCONF cannot serve”, or “payload valid against old revision but not current lock”.
- `transaction-replay` — deterministic replay of config and read flows across NETCONF and RESTCONF endpoints.
- `bundle-redactor` — scrub credentials, secrets, and device-specific identifiers while preserving enough structure to reproduce model and protocol errors.
- `cargo yang-evidence` — emit `*.yangbundle.zip` for CI, vendor support, or firmware-upgrade regression testing.

# What the crate should provide other people

1. **A boring default for model-driven network interop work** instead of one-off scripts and hand-curated captures.
2. **One place to pin YANG expectations** across controller code, CI fixtures, and hardware labs.
3. **Explainable capability drift** when firmware or module sets change.
4. **Cross-surface debugging** so NETCONF and RESTCONF behavior can be compared in the same artifact.
5. **Replayable, redactable bundles** that travel between operator and vendor without requiring a whole network lab.

# Persona / who it’s for

- Network automation engineers
- NMS/controller authors
- Device-vendor QA teams
- Rust developers building on NetGauze or NETCONF client crates
- Operators validating firmware or schema upgrades

# Users & user stories

- **Controller author**: “Diff this device’s current YANG capability set against the one our automation expects.”
- **Vendor QA team**: “Replay the same edit-config or RESTCONF patch against two firmware builds and compare semantic results.”
- **Operator**: “Capture a failing transaction with enough model metadata that support can reproduce it.”
- **CI maintainer**: “Pin model revisions and fail fast when device capabilities drift.”

# Prior art (and why it’s insufficient)

- RFC 6241, RFC 7950, and RFC 8040 already define the core model-driven management stack.
- Rust substrate exists in `netgauze-netconf-proto`, `netconf-rs`, and `serde_yang`/YANG parsers.
- But there is still no boring-default Rust crate family for **YANG lockfiles + capability diffs + cross-protocol replay + redactable interop bundles**.

# Design goals

1. **Model-first** — protocol success should always be judged relative to pinned YANG expectations.
2. **Capability-aware** — device support and deviations must be captured explicitly.
3. **Cross-surface comparisons** — NETCONF and RESTCONF should be diffable as different faces of the same modeled system.
4. **Lab-portable evidence** — bundles should shrink failing cases into shareable artifacts.
5. **Implementation neutrality** — useful across vendors and controller stacks.

# MVP surface

- Minimal types: `YangLock`, `CapabilitySnapshot`, `OperationTrace`, `ValidationFinding`, `ReplayReport`, `CapabilityDiff`
- Minimal functions:
  - `load_capabilities()`
  - `verify_yang_lock()`
  - `replay_trace()`
  - `diff_capabilities()`
  - `write_bundle()`
- Feature flags:
  - `netconf`
  - `restconf`
  - `yang`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target base **NETCONF**, **YANG 1.1**, and **RESTCONF** behavior first.
- Module-specific support should be opt-in via explicit lockfiles and fixture packs.
- The crate should complement device/controller implementations rather than become a new NMS.
- MVP should avoid trying to be a universal YANG compiler or telemetry platform.

# Conformance & fixtures

- Tiny capability snapshots for module/revision/feature combinations.
- Golden fixtures for YANG-XML/YANG-JSON translation drift, lock mismatch, and error-tag normalization.
- Replay traces for get-config, edit-config, patch, and datastore-sensitive operations.
- Optional fixture packs for widely used base modules and vendor-neutral labs.

# Path to boring stability

- First stabilize lockfile and findings vocabulary.
- Then prove capability diffs remain meaningful across multiple device families.
- Freeze bundle layout only after redaction retains useful protocol/model evidence.
- Add richer module ecosystems only after the core base stack is boring and trusted.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 21/30**

# Minimum lovable MVP

A CLI and library that collect a device’s NETCONF/RESTCONF capabilities, compare them to a pinned YANG lockfile, replay one or two representative operations, and emit a redactable `*.yangbundle.zip` with semantic diffs and normalized findings.

# De-risk plan

1. Start with capability discovery and read-only checks before write-path complexity.
2. Treat vendor-specific modules as opt-in profile packs.
3. Keep redaction explicit so bundles can travel outside the operator environment.
4. Normalize only a narrow, high-value subset of error and capability semantics first.

# Non-goals

- Not a full network controller.
- Not a generic telemetry backend.
- Not a replacement for vendor labs or formal certification programs.

# Architecture & API sketch

```rust
pub struct ReplayReport {
    pub lock_id: String,
    pub capability_findings: Vec<Finding>,
    pub operation_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_yang_lock(lock: &YangLock, device: &CapabilitySnapshot) -> ReplayReport;
pub fn replay_trace(lock: &YangLock, trace: &OperationTrace) -> Result<ReplayReport>;
```

Bundle draft: `lock.toml`, `capabilities/`, `operations.ndjson`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact credentials, hostnames, secrets, and sensitive path values by default.
- Preserve capability URIs, module revisions, and error tags where possible.
- Bound operation capture to explicit scopes; no silent full-device scraping.
- Record exact YANG lock and crate versions used.

# Maintenance & governance plan

- Keep core focused on lockfiles, IRs, replay, and finding vocabularies.
- Version fixture/module packs separately from bundle schema.
- Favor vendor-neutral fixtures first.
- Document how new RFCs/extensions are incorporated without destabilizing old bundles.

# Milestones

## 0.1
- capability discovery
- YANG lockfile format
- bundle writer

## 0.2
- operation replay
- semantic diffs
- redaction support

## 1.0
- stable `*.yangbundle.zip`
- CI-ready compatibility corpus
- documented extension policy

# Open questions

- How far should the core go into YANG schema compilation versus relying on existing parsers?
- Should RESTCONF and NETCONF traces share a single normalized operation model or parallel ones?
- Which vendor-neutral module sets deserve first-class fixture packs?

# Sources

- RFC 6241 NETCONF: https://www.rfc-editor.org/rfc/rfc6241.html
- RFC 7950 YANG 1.1: https://datatracker.ietf.org/doc/html/rfc7950
- RFC 8040 RESTCONF: https://www.rfc-editor.org/rfc/rfc8040.html
- `netgauze-netconf-proto`: https://docs.rs/netgauze-netconf-proto
- `netconf-rs`: https://crates.io/crates/netconf-rs
- `serde_yang`: https://crates.io/crates/serde_yang
