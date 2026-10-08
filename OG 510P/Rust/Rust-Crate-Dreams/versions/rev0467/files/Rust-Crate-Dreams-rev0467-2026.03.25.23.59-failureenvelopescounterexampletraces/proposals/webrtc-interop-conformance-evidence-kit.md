---
id: P-0222
title: WebRTC Interop & Evidence Lab Kit — JSEP scenarios, canonical traces, and repro bundles
status: idea
domains: [networking, webrtc, media, realtime, interop, conformance, observability]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/webrtc/
  - https://datatracker.ietf.org/doc/html/rfc8829
  - https://www.rfc-editor.org/rfc/rfc5764.html
  - https://github.com/webrtc-rs/webrtc
  - https://crates.io/crates/webrtc
needs:
  - A Rust-native way to share and replay WebRTC failures across stacks (Rust↔browser, Rust↔Rust, Rust↔SFU).
  - Canonical, safe-to-share evidence artifacts (SDP/ICE/DTLS/SRTP summaries, timing, stats) with privacy redaction.
risks:
  - WebRTC interop is huge; must scope to scenario-driven harness + evidence, not “yet another full stack”.
  - Privacy: bundles must avoid leaking IPs, candidate info, media payloads by default.
---

## Problem
WebRTC failures are often “works on Chrome but not Safari” or “fails behind NAT type X”. Debugging requires:
- capturing negotiation state (JSEP/SDP), ICE behavior, DTLS-SRTP setup, RTP/RTCP timing,
- replaying comparable scenarios across implementations,
- and doing it with **redaction defaults** suitable for tickets/CI.

## What this crate provides (sharp idea)
A **scenario runner + evidence bundle standard** for WebRTC, so interop bugs become *portable artifacts*, not folklore.

## Users
- Rust WebRTC stacks (`webrtc-rs`) and SFUs.
- Teams integrating browser clients with Rust backends.
- QA/CI: regression detection on negotiation and network edge cases.

## Prior art (insufficient)
- Existing Rust WebRTC stacks provide protocol functionality, not a shared **interop harness + canonical evidence bundles**.
- Browser tooling (webrtc-internals) is useful, but not structured for CI diffs or cross-stack replay.

## Design goals
- **Scenario-first:** describe tests as small JSEP + network scenarios (offer/answer patterns, renegotiation, data channels).
- **Canonical evidence:** produce `*.webrtcbundle.zip` with stable diff semantics.
- **Redaction-first:** scrub IPs/candidates, device IDs, and media payloads by default.
- **Cross-stack adapters:** browser (via WebDriver/CDP where possible), Rust endpoints, SFU endpoints.

Non-goals:
- Replacing existing WebRTC stacks.
- Capturing raw media by default.

## Architecture sketch
Workspace:
- `webrtclab-core` — scenario DSL, canonical evidence schema, redaction, diff.
- `webrtclab-adapter-webrtc-rs` — endpoint adapter for `webrtc-rs`.
- `webrtclab-adapter-browser` — harness for headless Chrome/Firefox (where feasible) to run minimal scenarios.
- `webrtclab-net` — optional network impairment integration (netem, tc, tun).
- `webrtclab-cli` — `run`, `bundle`, `diff`, `report`.

### Bundle format: `*.webrtcbundle.zip`
- `manifest.json` (browser/build, rust crate versions, OS, scenario)
- `signaling/` (redacted SDP offer/answer, JSEP state transitions)
- `ice/` (candidate types summarized; timings; failure reasons)
- `dtls/` (handshake transcript hash, ciphers, fingerprints; no key material)
- `srtp/` (SRTP profile, packet counters, replay stats)
- `rtp/rtcp/` (timing stats, jitter, loss; optional PCAP reference by hash)
- `stats.json` (canonicalized getStats snapshots)
- `verdict.json` (normalized outcomes)

## MVP (4–8 weeks)
1. Scenario DSL for: simple audio/video call + data channel.
2. Adapter for `webrtc-rs` endpoint + evidence bundle emission.
3. Canonical diff tool that highlights: SDP differences, ICE timing, DTLS failure class.

## De-risk plan
- Start Rust↔Rust (two endpoints) with deterministic seeds and controlled network.
- Add browser adapter second; keep it optional behind feature flags.

## Maintenance
- Treat scenarios and evidence schema as “semi-stable”: versioned with explicit migrations.
- Encourage community submissions of bundles for real-world failures (with redaction).

## Open questions
- Best browser automation path for stable CI (WebDriver vs CDP)?
- How to standardize stats across browsers?

## Sources
- W3C WebRTC API.
- IETF JSEP (RFC 8829) and DTLS-SRTP (RFC 5764).
- Rust ecosystem: `webrtc-rs` (`webrtc` crate).
