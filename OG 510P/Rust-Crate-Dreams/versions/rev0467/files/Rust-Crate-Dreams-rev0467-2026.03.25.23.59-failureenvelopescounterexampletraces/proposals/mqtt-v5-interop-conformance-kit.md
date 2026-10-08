---
id: P-0238
title: MQTT v5 Interop & Conformance Evidence Kit
status: idea
domains: [iot, messaging, protocols, networking, interop, testing, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://www.oasis-open.org/standard/mqtt-v5-0-os/
  - https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
  - https://mqtt.org/mqtt-specification/
---

# Problem

MQTT is ubiquitous in IoT, but production failures often hinge on subtle protocol details: session expiry, shared subscriptions, retained messages, QoS flows, reason codes, and property handling. Rust has clients/brokers, but lacks a **default conformance + interop harness** that produces **portable, redactable evidence bundles** for client↔broker behavior. citeturn0search2turn0search6turn0search14

# What it provides

1. `mqttlab` workspace (crates):
   - `mqttlab-wire`: MQTT v5 codec with strict/lenient parsing toggles + canonicalization.
   - `mqttlab-scenarios`: scenario DSL (connect/auth/session, retain, QoS1/2, will, shared subs, disconnect reason codes).
   - `mqttlab-runner`: adapter traits + orchestrator (run against a broker, or against a client with a harness broker).
   - `mqttlab-evidence`: capture/replay/diff with redaction presets.

2. Evidence bundle format: `*.mqttbundle.zip`
   - `manifest.json`: broker/client versions, features enabled, scenario seed
   - `trace.ndjson`: canonical frames + timestamps + derived state transitions
   - `assertions.json`: expected invariants + failure explanations
   - `redaction.toml`: topic/payload redaction rules + hashing modes
   - `compat.csv`: feature matrix output (what passed/failed)

3. CLI: `mqttlab`
   - `mqttlab run --broker <url> --scenario retain-qos2`
   - `mqttlab matrix --brokers ... --clients ...`
   - `mqttlab diff a.mqttbundle.zip b.mqttbundle.zip`

# Minimum lovable MVP (4–8 weeks)

- Codec + canonical trace representation (stable, diffable).
- 10–15 high-value scenarios (connect/session expiry, retain, QoS2, reason codes).
- One broker adapter + one client adapter (choose the most widely used Rust ones).
- Bundle emit + diff + compatibility table.

# De-risk plan

- Start with a strict codec and a small scenario set; expand only after deterministic evidence is rock-solid.
- Make redaction a first-class requirement (topic/payload) from day 1.

# Non-goals

- Not a new broker.
- Not a general fuzzing framework (though it should plug into fuzzers).
