---
id: P-0152
title: WebRTC SFU & Media Router Kit
status: idea
domains: [networking, realtime, media, devtools, interop, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/webrtc
  - https://github.com/webrtc-rs/webrtc
  - https://medium.com/@h3poteto/developing-a-webrtc-sfu-library-in-rust-019d467ab6c1
---
# Problem

Rust has an increasingly capable **WebRTC stack** (`webrtc-rs`) but the “last mile” for real deployments is still fragmented:

- App teams want an **SFU (Selective Forwarding Unit)** or media router, but they end up re-learning congestion control, simulcast/SVC policy, track forwarding, and operational guardrails.
- Most projects get stuck in bespoke signaling + bespoke room state + bespoke metrics, and interoperability breakage is hard to triage.

What’s missing is a **deployment-grade, testable SFU/router core** with a stable artifact model for *reproducible* debugging.

# What it should provide

## 1) A runtime-agnostic SFU core
A crate (or workspace) offering:

- Track ingest/egress plumbing (RTP/RTCP), relaying, and media routing primitives
- Subscriber policies (layer selection, bitrate caps, priority scheduling)
- Simulcast + basic SVC strategies (policy-first, customizable)
- Congestion-control hooks and “safe defaults” (no footguns by default)

Non-goals: a full “product” (auth, billing, dashboards). This kit is the “engine room”.

## 2) A standard evidence bundle for bug reports and CI
A portable `webrtcbundle.zip` with:

- `manifest.json` (kit version, dependency fingerprints, feature flags)
- `sdp/` offers/answers (redactable)
- `rtp/` optional pcap/qlog/qlog-like stream summaries
- `events.jsonl` (normalized: ICE, DTLS, SRTP, RTCP, CC events, key transitions)
- `metrics.json` (bitrate, RTT, loss, jitter, layer switches)
- `logs/` normalized logs
- `repro/` deterministic scenario spec (seeded timing + packet impairment profile)

This turns “it broke in production” into “here is the artifact; anyone can replay”.

## 3) A conformance/interoperability harness
- “Known-good” scenario suites (Chrome/Firefox/Safari; headless where possible)
- Interop matrices: codecs, DTLS versions, ICE edge cases, mid-session renegotiation
- CI sharding + failure clustering (minimize similar failures)

## 4) A `cargo` UX layer
A `cargo webrtc-sfu` plugin that can:
- `bundle` (capture), `replay`, `doctor`, `interop` (run scenario sets)
- produce a stable HTML report from the bundle

# MVP plan (shippable in ~3 layers)

1) **MVP (0.x)**: SFU core for DataChannel + audio, plus `webrtcbundle.zip` capture + replay for a small scenario set.
2) **v0.5**: simulcast policy + RTCP feedback + impairment profiles + CI clustering.
3) **v1.0**: interop harness + long-term maintenance policy + “profile packs” for common deployments.

# Design notes

- Prefer *Sans-I/O-ish* cores where feasible (testability), with adapters for Tokio/async-std/etc.
- Make policy explicit and typed: if a deployment chooses “aggressive layer-switching”, that’s a configuration profile with documented tradeoffs.
- Provide “escape hatches”, but keep the golden path simple.

# Why this is worthy

A reliable SFU kit would unlock:
- P2P + small-group calls for Rust apps without reimplementing a media server.
- Consistent evidence for hard WebRTC bugs (interop, NAT, timing).
- A shared place for Rust WebRTC operational best practices to accumulate.
