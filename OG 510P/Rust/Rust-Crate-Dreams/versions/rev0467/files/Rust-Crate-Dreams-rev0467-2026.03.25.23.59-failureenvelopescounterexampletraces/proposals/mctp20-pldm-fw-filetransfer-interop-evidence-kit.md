---
id: P-0386
title: MCTP 2.0 Host Interface + PLDM Firmware/File Transfer Interop & Evidence Kit — endpoint-discovery locks, package replay, and transport-binding debug bundles
status: idea
domains: [systems, firmware, hardware-management, interoperability, embedded, datacenter, transport]
last_reviewed: 2026-03-06
evidence:
  - https://www.dmtf.org/standards/pmci
  - https://www.dmtf.org/sites/default/files/standards/documents/DSP2015_2.3.0.pdf
  - https://www.dmtf.org/standards/published_documents
  - https://github.com/CodeConstruct/mctp-rs
  - https://crates.io/crates/pldm
  - https://crates.io/crates/pldm-fw
---

# Problem

Rust now has a meaningful foothold in platform-management transport stacks: there is a Rust MCTP workspace, a PLDM base crate, and a PLDM firmware-update crate. Meanwhile the DMTF PMCI family keeps growing: MCTP 2.0 host-interface work, PLDM base/monitoring/file-transfer/firmware specifications, new bindings, and adjacent Redfish/SPDM relationships.

But painful failures still happen at the seam between:

- **endpoint discovery / EID assignment and higher-level PLDM expectations**,
- **transport binding behavior and what firmware-update tools assume about flow, fragmentation, and timing**,
- **PLDM package metadata and what a device actually accepts or activates**,
- **file-transfer or firmware-update traces that are too low-level to explain but too high-stakes to ignore**,
- and **lab/vendor evidence that still depends on bus captures and custom scripts with no stable schema**.

The missing Rust contribution is not another management controller stack. It is an **interop and evidence kit** that captures binding assumptions, endpoint topology, package/replay semantics, and firmware/file-transfer findings in a shareable bundle.

# What it provides

- `pmci-profile.lock` — pins MCTP host/binding assumptions, endpoint topology, PLDM type set, package constraints, and timing policy.
- `pmci-irx` — neutral IR for discovery, endpoint IDs, transport fragments, PLDM commands, file-transfer state, and firmware-update phases.
- `pkg-summarizer` — extracts stable summaries from PLDM firmware packages without requiring device access.
- `replay-lab` — replays or checks narrow MCTP/PLDM sequences against fixtures and adapters.
- `cargo pmci-evidence` — emits `*.pmcibundle.zip` with topology, traces, package notes, and findings.

# What the crate should provide other people

1. **A boring incident bundle for MCTP/PLDM problems**.
2. **Transport-binding and endpoint-topology locks** instead of hidden platform assumptions.
3. **Package and phase summaries** for firmware/file-transfer debugging.
4. **Replayable traces** that survive vendor handoff.
5. **A bridge between raw bus-level events and human-readable failure explanations.**

# Persona / who it’s for

- Firmware and platform-management engineers
- BMC/MC developers and integrators
- Datacenter hardware teams debugging updates
- Rust maintainers building PMCI tooling

# Users & user stories

- **Firmware engineer**: “Tell me whether the update failed because of package contents, activation state, endpoint discovery, or transport behavior.”
- **Platform integrator**: “Capture a bundle I can send to a vendor without requiring their exact lab setup.”
- **Maintainer**: “Compare the same PLDM update flow over different MCTP bindings or host-interface assumptions.”
- **Operator**: “Summarize the package and update phases before I risk a rollout.”

# Prior art (and why it’s insufficient)

- DMTF PMCI publishes the MCTP and PLDM families, including recent host-interface and file-transfer work.
- Rust now has `mctp-rs`, `pldm`, and `pldm-fw` substrate.
- There are lab tools and scripts for specific deployments.

What Rust still lacks is a **boring cross-layer evidence format** for topology locks, package summaries, discovery traces, and replayable firmware/file-transfer incidents.

# Design goals

1. **Cross-layer honest** — keep transport, discovery, and PLDM semantics separate but linked.
2. **Package-aware** — firmware bundles and their metadata are first-class.
3. **Binding-aware** — host-interface and transport-binding assumptions must be pinned.
4. **Lab-friendly** — usable with synthetic fixtures and partial captures.
5. **Implementation-neutral** — complement existing Rust substrate and vendor stacks.

# MVP surface

- Minimal types: `PmciProfileLock`, `EndpointTopology`, `FirmwarePackageSummary`, `PmciBundle`
- Minimal functions:
  - `inspect_package()`
  - `normalize_trace()`
  - `replay_sequence()`
  - `write_bundle()`
- Feature flags:
  - `mctp`
  - `pldm-fw`
  - `pldm-file-transfer`
  - `topology`
  - `redaction`

# Compatibility story

- Works above Linux or embedded Rust MCTP substrate.
- Can ingest device traces, synthetic fixtures, or package files independently.
- Keeps binding-specific quirks in overlays instead of hidden heuristics.
- Lets vendors ship private adapters without fracturing the core bundle format.

# Conformance & fixtures

- Tiny fixtures for EID assignment drift, message-fragment issues, package incompatibility, transfer interruption, and activation failure.
- Goldens for “same package, different endpoint/binding behavior”.
- Public synthetic packages and sequence traces.
- Replays that compare expected phases against observed device/device-manager behavior.

# Path to boring stability

- Stabilize lockfile, topology schema, and package-summary format before more adapters.
- Start with firmware update and file transfer, where evidence value is highest.
- Keep raw captures optional and bounded.
- Make timing/binding assumptions explicit everywhere.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that summarize PLDM firmware packages, normalize MCTP/PLDM traces, pin topology and binding assumptions, and emit compact `*.pmcibundle.zip` artifacts.

# De-risk plan

1. Start with package inspection and replay helpers rather than a full device stack.
2. Keep transport-binding quirks in explicit overlays.
3. Use synthetic public fixtures before vendor-private captures.
4. Separate discovery/topology findings from package/activation findings.

# Non-goals

- Not a replacement for BMC firmware.
- Not a generic logic analyzer or bus sniffer.
- Not a full Redfish or SPDM implementation.
- Not a firmware rollout orchestration platform.

# Architecture & API sketch

```rust
pub struct PmciProfileLock {
    pub mctp_profile: String,
    pub bindings: Vec<String>,
    pub pldm_types: Vec<String>,
    pub timing_policy: String,
}

pub fn inspect_package(path: &std::path::Path) -> Result<FirmwarePackageSummary>;
pub fn normalize_trace(input: &[u8]) -> Result<PmciTrace>;
pub fn replay_sequence(trace: &PmciTrace, lock: &PmciProfileLock) -> ReplayResult;
```

Bundle draft: `pmci-profile.lock`, `topology.json`, `trace.json`, `package-summary.json`, `findings.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat captures, package manifests, and endpoint identities as sensitive until redacted.
- Support structural summaries without raw payload retention.
- Record exact spec/binding/profile versions in every bundle.
- Make missing captures explicit so partial evidence is not mistaken for negative evidence.

# Maintenance & governance plan

- Keep the core about locks, traces, package summaries, replay, and bundle format.
- Version binding-specific adapters separately if needed.
- Publish small public fixture corpora.
- Resist scope creep into full controller stacks.

# Milestones

## 0.1
- package summarizer
- trace normalization
- topology lockfile

## 0.2
- replay lab
- file-transfer fixtures
- synthetic endpoint corpora

## 1.0
- stable `*.pmcibundle.zip`
- documented compatibility policy
- broader adapter coverage

# Open questions

- Which MCTP bindings deserve first-class overlays in MVP?
- How much timing/fragmentation detail should be retained in the stable IR?
- What is the safest public fixture strategy for package and activation scenarios?

# Sources

- DMTF PMCI overview: https://www.dmtf.org/standards/pmci
- PMCI architecture white paper: https://www.dmtf.org/sites/default/files/standards/documents/DSP2015_2.3.0.pdf
- DMTF published documents: https://www.dmtf.org/standards/published_documents
- `mctp-rs`: https://github.com/CodeConstruct/mctp-rs
- `pldm`: https://crates.io/crates/pldm
- `pldm-fw`: https://crates.io/crates/pldm-fw
