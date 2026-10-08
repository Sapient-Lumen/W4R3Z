---
id: P-0259
title: SPDM + Secured Messages Interop & Evidence Kit
status: idea
domains: [security, firmware, datacenter, interop, conformance, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://www.dmtf.org/sites/default/files/standards/documents/DSP0274_1.2.2.pdf
  - https://www.dmtf.org/sites/default/files/standards/documents/DSP0277_1.2.0.pdf
---

# Problem

SPDM is becoming a key building block for device-to-device and firmware security sessions in datacenter and platform security stacks, but *practical interoperability* across implementations is hard to validate and share. When sessions fail, teams need **reproducible** artifacts that capture: negotiation parameters, transcript state, selected algorithms, certificate slot handling, and secured messaging behavior—without leaking secrets.

Today, debugging often relies on bespoke logs or proprietary hardware traces, making interop fixes slow and non-portable.

# What it provides

A Rust workspace that delivers:

- **`spdm-ir`**: a canonical, diffable intermediate representation (IR) for SPDM handshakes and secured messaging transcripts.
- **`spdm-capture`**: adapters to ingest traces from:
  - in-process Rust SPDM implementations (feature-gated hooks)
  - external logs / packet-like transcripts (JSON/CBOR)
- **`spdm-runner`**: a scenario runner that replays a captured session against a target implementation and records divergences.
- **`spdm-explain`**: “why did it fail?” reports (policy/parameter mismatch, certificate slot mismatch, retry timing, session policy mismatch).
- **`spdmbundle`** format (`*.spdmbundle.zip`): a signed, redactable evidence bundle using **Evidence Bundle Core (P-0256)**:
  - transcript (redacted)
  - algorithm/capability snapshot
  - verifier policy snapshot
  - normalized divergences + reproduction recipe

# Users & user stories

- **Firmware / platform security engineers**: “Reproduce this SPDM failure on your stack using the same scenario and policy.”
- **Datacenter operators**: “Verify a vendor’s BMC/host stack interop across a matrix of settings and certificate configurations.”
- **Security auditors**: “Show evidence that SPDM secured messaging was negotiated as expected, without exposing secrets.”

# Prior art (and why it’s insufficient)

- SPDM specs define wire behavior but do not provide a portable evidence artifact format or interop harness.
- Existing implementations and vendor tools typically produce logs that are **not canonicalized**, **not diffable**, and **not shareable** across organizations.

# Design goals

- **Interop-first**: multiple implementation adapters; never tied to one stack.
- **Evidence-first**: bundles are the primary unit of collaboration.
- **Secret-minimizing**: bundle defaults to redaction; explicit “unsafe mode” only for local debugging.
- **Deterministic replay**: scenarios replayed with controlled randomness/time.

# Non-goals

- Building a full SPDM implementation from scratch.
- Competing with vendor certification programs; instead provide tooling that can complement them.

# Architecture & API sketch

```rust
// Build a scenario and run against a target, producing a bundle.
let scenario = spdm_runner::Scenario::from_yaml("scenarios/basic-mutual-auth.yaml")?;
let verdict = spdm_runner::run(&scenario, spdm_runner::Target::Tcp("127.0.0.1:2323"))?;
let bundle_path = spdmbundle::emit(verdict, "out/failure.spdmbundle.zip")?;
```

Core crates:

- `spdm_ir` (canonical transcript + capability model)
- `spdm_capture` (ingest/export)
- `spdm_runner` (scenario engine; target adapters)
- `spdm_explain` (diagnostics; policy diffs)
- `spdmbundle` (bundle schema + signing + redaction profiles)

# Security / safety model

- Redaction is **on by default**.
- Bundles may include **cryptographic commitments** (hashes) to support auditability without revealing keys.
- Support DSSE envelopes via Evidence Bundle Core; allow verifying integrity without trusting transport.

# Maintenance & governance plan

- Start with a small “interop council” model: maintainers from 2–3 independent SPDM stacks.
- Require fixture additions for behavior changes; prefer spec-anchored corpus.

# Milestones

## MVP (4–8 weeks)
1. `spdm_ir` + minimal `spdmbundle` schema + CLI (`spdmkit bundle validate|diff`)
2. Adapter for one Rust implementation + one “log transcript” format
3. Scenario runner for handshake negotiation + 1 secured message exchange
4. Explain reports for 5 common divergence classes

## Next
- Matrix runner across multiple targets
- Wireshark-compatible export helpers (optional)
- Fuzz/minimize for transcript divergence

# Open questions

- Best minimal secret-free transcript representation for secured messaging (commitments vs. encrypted payload omission)?
- How to standardize “time/RTD” handling for deterministic reproduction?

# Sources

- DMTF **SPDM** specification (DSP0274 v1.2.2). 
- DMTF **Secured Messages using SPDM** specification (DSP0277 v1.2.0).
