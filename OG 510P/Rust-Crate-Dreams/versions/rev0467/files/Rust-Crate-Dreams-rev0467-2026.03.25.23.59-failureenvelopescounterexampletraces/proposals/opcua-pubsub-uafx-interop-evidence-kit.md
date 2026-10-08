---
id: P-0312
title: OPC UA PubSub + UAFX Interop & Evidence Kit — deterministic industrial PubSub traces, profile pinning, and explainable divergence reports
status: idea
domains: [industrial, opcua, pubsub, industrial-automation, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://reference.opcfoundation.org/Core/Part14/v105/docs/
  - https://reference.opcfoundation.org/UAFX/Part81/v100/docs/
  - https://crates.io/crates/async-opcua
  - https://crates.io/crates/async-opcua-types
---

# Problem

General OPC UA client/server work already has meaningful Rust substrate, but **industrial PubSub** remains a harder and more operationally painful layer:

- UADP / JSON mappings and field layouts are easy to misread,
- Publisher / Subscriber / ReaderGroup / WriterGroup configuration drift is hard to explain,
- UAFX deployments raise the cost of “almost interoperable” behavior,
- teams still fall back to Wireshark captures and vendor screenshots instead of portable, replayable artifacts.

The worthy crate contribution here is not “yet another generic OPC UA stack.” It is a **PubSub/UAFX interop and evidence workbench** that makes failures deterministic, diffable, and small enough to share.

# What it provides

- `ua-pubsub-ir` — canonical IR for NetworkMessages, DataSetMessages, fields, headers, timings, and config snapshots.
- `ua-pubsub-profile` — lockfiles for transport, encoding, security, field metadata, and UAFX assumptions.
- `ua-pubsub-verify` — semantic checks for sequence numbers, metadata compatibility, key/frame settings, timestamps, and decoding expectations.
- `ua-pubsub-replay` — deterministic replay of publish/subscribe transcripts and impairment scenarios.
- `ua-pubsub-diff` — explainable diffs: “metadata version changed”, “field promoted from Variant to DataValue”, “WriterGroup timing drift exceeded profile budget”.
- `cargo ua-pubsub` — emit `*.uapubsubbundle.zip` for field incidents, factory acceptance tests, and vendor escalation.

# What the crate should provide other people

1. **A portable industrial incident artifact** instead of ad hoc packet dumps.
2. **Config/profile lockfiles** so system integrators can pin the exact interoperability contract they think they bought.
3. **Replayable PubSub evidence** for CI, lab bring-up, and regression testing.
4. **Vendor-neutral explanations** when two stacks disagree on message or metadata semantics.
5. **A practical bridge from today’s OPC UA Rust crates to tomorrow’s UAFX deployment tooling**.

# Users & user stories

- **Controls / OT integrators**: “Show the first published frame where the subscriber’s expectation diverged.”
- **Gateway vendors**: “Replay a failing broker or UDP multicast trace against the patched decoder.”
- **Factory acceptance teams**: “Archive a passing conformance bundle and compare every firmware update against it.”
- **Operations engineers**: “Prove whether the issue is network timing, metadata drift, or security/config mismatch.”

# Prior art (and why it’s insufficient)

- OPC Foundation references already define the normative PubSub and UAFX world well enough that Rust should not guess blindly.
- Rust now has more serious OPC UA substrate than a year ago, including active `async-opcua` crates and generated types.
- But a stack alone does not solve **incident portability, config pinning, semantic diffing, or evidence shipping**.

# Design goals

1. **PubSub-first** — focus on the painful edge, not generic node browsing.
2. **Industrial realism** — timing, message loss, and metadata-version behavior must be first-class.
3. **Profile-aware** — UAFX and deployment-specific assumptions must be explicit.
4. **Small portable bundles** — useful over email/ticket systems and safe for long retention.
5. **Adapter-friendly** — wrap existing pure-Rust or bound stacks instead of forcing one implementation.

# Non-goals

- Not a full MES/SCADA platform.
- Not a complete replacement for vendor certification labs.
- Not a monolithic OPC UA IDE.

# Architecture & API sketch

```rust
pub struct UaPubSubReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub timing_findings: Vec<TimingFinding>,
    pub metadata_findings: Vec<MetadataFinding>,
    pub divergences: Vec<Divergence>,
}

pub fn verify_trace(profile: &Profile, trace: &PubSubTrace) -> UaPubSubReport;
```

Bundle draft: `profile.toml`, `config.json`, `messages.bin`, `trace.jsonl`, `timing.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Support redaction or hashing of endpoint URLs, certificates, and asset identifiers.
- Bound bundle sizes for long-running captures.
- Separate semantic summaries from raw packet material.
- Preserve enough provenance to prove which profile and decoder versions were used.

# Maintenance & governance plan

- Pin exact OPC UA Part 14 and UAFX snapshot versions in every fixture pack.
- Keep IR additive and transport-neutral where possible.
- Publish scenario packs for brokered PubSub, UDP multicast, late joiners, metadata changes, and security-key rollover.
- Encourage cross-vendor fixture contributions without shipping proprietary payload meaning.

# Milestones

## 0.1
- Canonical PubSub IR
- Profile lockfiles
- Basic trace verification + bundle format

## 0.2
- Replay engine
- Timing / sequence / metadata diffing
- UAFX-oriented scenario fixtures

## 1.0
- Stable `*.uapubsubbundle.zip`
- Adapter layer for multiple OPC UA stacks
- CI-ready conformance and incident workflows

# Open questions

- How much broker/MQTT detail belongs in core versus transport adapters?
- Which timing abstractions are stable enough to compare across vendors?
- Should UAFX-specific checks live as overlays on a smaller PubSub core?

# Sources

- OPC UA Part 14 PubSub: https://reference.opcfoundation.org/Core/Part14/v105/docs/
- OPC UA FX Part 81: https://reference.opcfoundation.org/UAFX/Part81/v100/docs/
- `async-opcua`: https://crates.io/crates/async-opcua
- `async-opcua-types`: https://crates.io/crates/async-opcua-types
