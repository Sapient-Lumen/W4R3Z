---
id: P-0322
title: AMWA NMOS Interop & Evidence Kit — IS-04/05 profile lockfiles, topology diffs, and replayable broadcast-control bug bundles
status: idea
domains: [media, broadcast, amwa, nmos, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://specs.amwa.tv/nmos/
  - https://specs.amwa.tv/nmos/branches/main/docs/Technical_Overview.html
  - https://specs.amwa.tv/nmos-testing/
  - https://github.com/AMWA-TV/nmos-testing
  - https://github.com/rufusutt/nmos-rs
---

# Problem

Rust is now close enough to real NMOS work that the missing contribution is no longer “yet another REST client.” The hard failures in the field happen in the seam between discovery, registration, connection management, and the live topology people *think* they have:

- IS-04 resources drifting from reality,
- IS-05 activations that look valid but fail operationally,
- sender/receiver capability mismatches,
- DNS-SD and registry assumptions that differ across facilities,
- and incident reports that still move around as screenshots, packet captures, and hand-written timeline notes.

The worthy crate contribution is a **NMOS interop and evidence kit** that turns facility state, API behavior, and connection attempts into deterministic, diffable, replayable artifacts.

# What it provides

- `nmos-ir` — canonical IR for Nodes, Devices, Sources, Flows, Senders, Receivers, clocks, transport params, staged/active connection state, and registry snapshots.
- `nmos-profile` — lockfiles pinning exact spec/version assumptions, facility policies, IPMX-adjacent expectations, optional auth surfaces, and accepted API versions.
- `nmos-verify` — semantic checks for topology integrity, resource consistency, connection compatibility, and activation workflow correctness.
- `nmos-replay` — deterministic replay of registration changes, discovery snapshots, staged/active activation sequences, and failing control interactions.
- `nmos-diff` — explainable diffs: “receiver caps narrowed”, “sender transport params changed”, “registry snapshot lost resource”, “activation succeeded but active state diverged”.
- `cargo nmos` — emit `*.nmosbundle.zip` for vendor escalations, workshop prep, regression CI, and field incident archives.

# What the crate should provide other people

1. **A boring-default artifact for NMOS incidents** instead of vague screenshots and partial API dumps.
2. **Profile pinning** for the exact NMOS assumptions a plant or product expects.
3. **Topology-aware diffs** that speak in NMOS terms rather than raw JSON patches.
4. **Replayable control flows** for discovery/registration/connection regressions.
5. **A neutral layer above existing Rust and non-Rust NMOS implementations**.

# Persona / who it’s for

- Broadcast-control developers
- Pro AV / IPMX implementers
- Device vendors shipping NMOS-capable products
- Integration labs and interoperability workshop teams
- Operators debugging “works in one facility, breaks in another” failures

# Users & user stories

- **Vendor engineer**: “Show me exactly when the receiver capabilities diverged from the sender’s advertised transport parameters.”
- **Systems integrator**: “Diff this facility snapshot against the last working one semantically, not by line order.”
- **Interop lab**: “Replay the exact discovery and activation sequence that failed during the workshop.”
- **Operations team**: “Redact hostnames and addresses but keep the failure reproducible.”

# Prior art (and why it’s insufficient)

- AMWA publishes a broad and evolving NMOS family with a live technical overview.
- AMWA also publishes the NMOS Testing Tool, which already proves conformance and behavioral checking matter operationally.
- Rust substrate exists in `nmos-rs`, and adjacent media/network crates can handle HTTP, mDNS, RTP, and JSON concerns.
- But there is still no boring-default Rust crate family for **profile pinning + snapshot diffing + replayable evidence bundles** around NMOS workflows.

# Design goals

1. **Topology-first** — the graph of resources is the unit of meaning.
2. **Workflow-aware** — discovery, registration, and connection changes must be replayable as timelines.
3. **Version/profile explicit** — every finding must be tied to a pinned expectation set.
4. **Redaction-first** — facility-sensitive details must be scrub-able without destroying semantics.
5. **Implementation-neutral** — useful whether the product under test is Rust, C++, Python, or mixed.

# MVP surface

- Minimal types: `NodeSnapshot`, `RegistrySnapshot`, `ConnectionAttempt`, `NmosProfile`, `NmosReport`
- Minimal functions:
  - `load_snapshot()`
  - `verify_topology()`
  - `verify_connection()`
  - `diff_snapshots()`
  - `write_bundle()`
- Feature flags:
  - `is04`
  - `is05`
  - `dns-sd`
  - `redaction`
  - `serde`

# Compatibility story

- Interoperates with AMWA API resources and test-tool outputs first.
- Adapters should accept captures from Rust and non-Rust implementations.
- MVP should intentionally avoid becoming a full controller UI or media router.

# Conformance & fixtures

- Synthetic facilities with known-good and known-bad IS-04 graphs.
- IS-05 activation scenario packs (staged vs active, transport-parameter mismatch, rollback behavior).
- Registry drift fixtures and redacted workshop captures.
- Optional adapter layer for NMOS Testing Tool outputs.

# Path to boring stability

- First prove stable IR and diff semantics on synthetic fixtures.
- Then prove replay against real captures from at least two independent implementations.
- Freeze bundle format only after redaction and replay survive actual escalations.
- Deprecate profile rules additively with explicit version hashes.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A CLI and library that ingest IS-04 resource snapshots plus one IS-05 activation attempt, verify compatibility and topology integrity, produce an explainable diff against a prior snapshot, and emit a redactable `*.nmosbundle.zip`.

# De-risk plan

1. Start with offline snapshots only; do not require live controller behavior.
2. Define the IR around a narrow IS-04/05 subset that covers the most common failure modes.
3. Validate output quality against AMWA Testing Tool findings and one real capture corpus.
4. Add live-capture and DNS-SD adapters later.

# Non-goals

- Not a real-time media transport stack.
- Not a full broadcast controller or orchestration UI.
- Not a replacement for the AMWA Testing Tool.

# Architecture & API sketch

```rust
pub struct NmosReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub topology_findings: Vec<TopologyFinding>,
    pub connection_findings: Vec<ConnectionFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_snapshot(profile: &NmosProfile, snap: &RegistrySnapshot) -> NmosReport;
pub fn verify_connection(profile: &NmosProfile, attempt: &ConnectionAttempt) -> NmosReport;
```

Bundle draft: `profile.toml`, `snapshots/*.json`, `connection/*.json`, `timeline.jsonl`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact IPs, hostnames, labels, facility names, auth tokens, and controller identifiers.
- Bound capture sizes and forbid accidental media essence inclusion.
- Preserve enough identifiers for graph integrity after redaction.
- Record verifier/profile hashes for reproducibility.

# Maintenance & governance plan

- Pin exact AMWA version assumptions in every fixture pack.
- Keep IR additive so new specs/profiles do not break old bundles.
- Publish small synthetic facilities and activation scenarios first.
- Encourage cross-vendor scenario donations in redacted form.

# Milestones

## 0.1
- Canonical IS-04/05 IR
- Topology verification
- Bundle format draft

## 0.2
- Activation replay
- Topology and connection diffs
- Test-tool adapter

## 1.0
- Stable `*.nmosbundle.zip`
- Cross-implementation replay corpus
- CI-ready interop regression workflows

# Open questions

- How much DNS-SD and registry-discovery logic belongs in core versus adapters?
- Should auth and BCP-003-like constraints stay out of MVP or be modeled from day one?
- Is IPMX-specific policy best represented as profiles or a companion crate?

# Sources

- NMOS overview index: https://specs.amwa.tv/nmos/
- NMOS technical overview: https://specs.amwa.tv/nmos/branches/main/docs/Technical_Overview.html
- NMOS Testing Tool docs: https://specs.amwa.tv/nmos-testing/
- NMOS Testing Tool repo: https://github.com/AMWA-TV/nmos-testing
- `nmos-rs`: https://github.com/rufusutt/nmos-rs
