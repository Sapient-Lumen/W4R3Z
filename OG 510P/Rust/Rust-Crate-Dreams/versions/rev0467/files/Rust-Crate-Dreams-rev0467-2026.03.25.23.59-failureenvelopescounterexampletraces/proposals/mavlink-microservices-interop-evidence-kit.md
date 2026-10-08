---
id: P-0293
title: MAVLink Microservices Interop & Evidence Kit — canonical mission/parameter/file traces + signing-aware replay
status: idea
domains: [robotics, drones, embedded, protocols, testing]
last_reviewed: 2026-03-06
evidence:
  - https://mavlink.io/en/
  - https://mavlink.io/en/services/index.html
  - https://mavlink.io/en/guide/message_signing.html
---

# Problem

Rust has credible MAVLink protocol crates, but the hard part in practice is not packet framing — it is **microservice behavior** across autopilots, radios, SDKs, and ground stations. Mission upload/download, parameter sync, file transfer, command acknowledgment, retries, and signing behavior often fail in ways that are painful to reproduce.

That makes the real missing crate less “another MAVLink parser” and more a **portable microservice evidence lab**.

# What it provides

- `mav-evidence` — canonical MAVLink microservice IR with timing, retransmission, and signing metadata.
- `mav-scenario` — scenario DSL for missions, parameters, FTP transfers, and command/ack flows.
- `mav-replay` — deterministic trace replay with packet loss, latency, and reordering profiles.
- `mav-fixtures` — known-good corpora for PX4/ArduPilot/GCS interoperability.
- `cargo mav` — capture, replay, diff, and package `*.mavbundle.zip` evidence bundles.

# Users & user stories

- **Autopilot teams**: “Why does this GCS stall during mission upload only over a lossy link?”
- **Ground-control / SDK teams**: “Did we break parameter sync semantics or just timing tolerance?”
- **Drone OEMs / integrators**: “Certify our stack against fixed scenario packs before flight tests.”
- **Researchers / labs**: “Share one replayable artifact instead of a pile of logs and radio captures.”

# Prior art (and why it’s insufficient)

- `mavlink`, `mavio`, `maviola`, and the newer `mavspec` family are valuable protocol building blocks, but they are not a standard interop bundle or scenario runner.
- The MAVLink Developer Guide documents the microservices, mission protocol, and signing, but it is not itself an executable conformance harness.
- PX4 and ArduPilot docs explain behavior from their perspective, but cross-stack reproducibility remains ad hoc.

# Design goals

1. **Microservice-first** — parameters, missions, FTP, commands, and heartbeats before exotic dialect coverage.
2. **Transport-agnostic** — serial, UDP, TCP, and log-derived traces.
3. **Signing-aware** — bundle enough metadata to debug MAVLink 2 signing issues without leaking keys.
4. **Field-realistic** — simulate loss, jitter, radio stalls, and reboot windows.
5. **no_std-friendly adapters where possible** — collection on constrained devices should be possible.

# Non-goals

- Not a new flight stack.
- Not a full GCS UI.
- Not a simulator replacement.

# Architecture & API sketch

```rust
pub enum ScenarioStep {
    UploadMission(MissionPlan),
    FetchParameters,
    CommandLong(Command),
    FtpPut(RemotePath, Vec<u8>),
}

pub struct ReplayProfile {
    pub latency_ms: u32,
    pub drop_rate: f32,
    pub reorder_window: u16,
}

pub trait EndpointAdapter {
    fn send_frame(&mut self, frame: FrameIr) -> Result<(), IoError>;
    fn recv_event(&mut self) -> Result<EventIr, IoError>;
}
```

Bundle draft: `scenario.toml`, `events.jsonl`, `transport.json`, `signing.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Never store signing keys in bundles.
- Redact GPS and operator identifiers by default.
- Separate wire authenticity verdicts from confidentiality assumptions (MAVLink signing authenticates; it does not encrypt).
- Bound replay resources to protect CI and fuzz environments.

# Maintenance & governance plan

- Keep dialect support modular and generated.
- Focus first on common microservices that create most integration pain.
- Maintain open fixture packs for at least PX4 and ArduPilot-adjacent workflows.
- Use golden traces plus property tests for retransmission/state-machine invariants.

# Milestones

## 0.1
- Canonical event model
- Mission upload/download scenario runner
- Parameter sync diff

## 0.2
- Packet-loss/jitter replay profiles
- Signing-aware capture metadata
- FTP and command/ack scenarios

## 1.0
- Stable `*.mavbundle.zip`
- Compatibility matrix across common endpoints
- Flight-lab-ready fixture corpus

# Open questions

- Which minimum set of microservices yields the highest ecosystem leverage?
- Should scenario files be purely declarative, or allow embedded assertions in Rust?
- How much dialect-specific behavior belongs in core versus adapters?

# Sources

- MAVLink Developer Guide: https://mavlink.io/en/
- MAVLink microservices overview: https://mavlink.io/en/services/index.html
- Mission protocol: https://mavlink.io/en/services/mission.html
- Message signing: https://mavlink.io/en/guide/message_signing.html
- PX4 MAVLink microservices overview: https://docs.px4.io/main/en/mavlink/protocols
- Rust crates: https://crates.io/crates/mavlink ; https://crates.io/crates/mavio ; https://crates.io/crates/maviola ; https://crates.io/crates/mavspec
