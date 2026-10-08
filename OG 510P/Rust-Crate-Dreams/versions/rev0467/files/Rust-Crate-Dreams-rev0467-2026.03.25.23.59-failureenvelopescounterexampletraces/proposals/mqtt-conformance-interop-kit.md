---
id: P-0167
title: MQTT Conformance & Interop Kit — artifacts + harness to make MQTT correctness reproducible
status: idea
domains: [iot, networking, conformance, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/rumqttc
  - https://github.com/bytebeamio/rumqtt
  - https://iottestware.readthedocs.io/en/master/mqtt_test_suite.html
  - https://www.etsi.org/committee?id=1943
---

## What it should provide others

A **standard way to prove and debug MQTT correctness** across clients/brokers/bridges:

- A portable **evidence bundle** format: `mqttbundle.zip`
  - pcap-like captures (where available), normalized packet transcript, timing + session metadata
  - a *redaction* layer for credentials/tokens
  - a single `report.json` with normative coverage, failures, and deltas vs baseline
- A reusable **scenario harness**:
  - client↔broker permutations, clean-session semantics, retained messages, QoS 0/1/2, will messages
  - reconnect storms, slow consumer, out-of-order delivery, packet loss, duplicate publish, half-open TCP
- A conformance mapping layer that links test cases to **normative statements** (spec mapping is the product).

## Why this is still missing

Rust has solid MQTT building blocks, but the ecosystem lacks a **shared correctness contract**:
everyone re-discovers the same edge cases (QoS2 state machines, retries, session expiry, inflight limits, etc.),
and bug reports arrive without enough evidence to reproduce.

## Design principles

- **Artifacts-first debugging**: every failure produces a bundle that can be replayed on another machine.
- **Matrix-friendly**: run scenarios against multiple brokers/clients and diff results.
- **Protocol-accurate core**: keep parsing/transcript normalization strict and well-tested.
- **Redaction by default**: safe to upload bundles to OSS issues.

## MVP

- `mqttbundle` spec + validator
- `cargo mqtt {run,replay,doctor}` (cargo-subcommand optional but preferred)
- 10–15 high value scenarios (QoS2 handshake, retained, session persistence, reconnect, will)
- Transcript normalizer + minimal replay engine (at least for client-side deterministic replay)

## v1

- Normative mapping coverage report (statement IDs → test coverage)
- Broker harness runner + multi-impl matrix (Docker profiles)
- Fuzzing adapters: turn `mqttbundle` transcripts into fuzz corpora
- Performance profiles (latency/throughput under stress) as optional lanes

## Compatibility strategy

- Support v3.1.1 and v5 with feature flags.
- Keep `mqttbundle` stable and versioned; allow extensions but require a strict “core” subset.

## Risks / open questions

- How to standardize timing without flakiness: prefer deterministic “virtual time” replay where possible.
- Avoid re-implementing a broker: integrate existing brokers via adapters and focus on *interop evidence*.
