---
id: P-0198
title: Network Cassette & Impairment Kit — pcap/pcapng capture→replay + tc/netem profiles + redacted evidence bundles
status: idea
domains: [networking, testing, observability, devtools, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/draft-ietf-opsawg-pcapng/
  - https://ietf-opsawg-wg.github.io/draft-ietf-opsawg-pcap/draft-ietf-opsawg-pcap.html
  - https://man7.org/linux/man-pages/man8/tc-netem.8.html
  - https://crates.io/crates/pcap_replay
  - https://crates.io/crates/net-replay
needs:
  - Rust teams routinely need reproducible network bug reports (timeouts, retransmits, QUIC weirdness, proxies), but there’s no “one right way” to capture, redact, replay, and *impair* networks in CI.
  - Existing crates/tools tend to cover one slice (pcap parsing, tcpreplay-like senders, ad-hoc netem scripts) without a shared artifact format and a first-class redaction story.
risks:
  - Privileged operations (raw sockets, capture) vary by OS; must offer “unprivileged mode” fallbacks and clear capability boundaries.
  - Replaying packet captures is easy to misuse (privacy); the kit must default to redaction + consent-friendly bundles.
---

# Problem

Distributed systems fail in ways that unit tests can’t reach:

- packet loss / reordering / jitter
- MTU and fragmentation edge cases
- proxy/NAT behavior
- DNS weirdness
- QUIC handshake and path migration bugs

Today, teams capture traffic (pcap/pcapng), maybe replay it with a one-off tool, and manually script impairment with `tc netem`. The results are rarely portable, reproducible, or safe to share.

# What it provides

A “cassette” concept for network behavior, with **artifact-first** workflows:

1) **Capture formats & normalization**
- parse/read/write PCAP and PCAPNG (normalize timestamps, linktypes, metadata)
- canonical JSON summaries (flows, RTT estimates, retransmits, DNS timing)

2) **Replay primitives (safe-by-default)**
- L7-first replay: HTTP/2/3, DNS, gRPC, WebSocket (prefer *semantic* replay)
- L4 replay (TCP/UDP) when needed
- strict redaction: PII fields, auth headers, IP anonymization, payload hashing

3) **Impairment profiles**
- portable impairment schema: loss, delay, jitter, duplication, corruption, bandwidth
- backends:
  - Linux `tc netem`
  - user-space shims where possible (tokio socket wrappers, QUIC hooks)

4) **Evidence bundle: `*.netbundle.zip`**
- `capture/` (pcap/pcapng or normalized slices)
- `impairment.toml` (profile)
- `redaction.toml` (policy)
- `scenarios/` (what to replay, endpoints, expectations)
- `report.json` (environment, hashes, verdicts, metrics)

5) **Cargo/CLI UX**
- `cargo net doctor` — check permissions/caps, validate netem availability
- `cargo net capture` — record with redaction rules applied
- `cargo net replay` — replay bundle and emit deterministic report
- `cargo net diff` — compare two captures/replays (regression triage)

# Users & user stories

- **Service teams**: “Reproduce a flaky network incident locally and in CI from a shareable bundle.”
- **Protocol implementers**: “Run regression suites for QUIC/TLS/HTTP changes under controlled impairment.”
- **SRE/security**: “Share failure evidence without leaking payloads or secrets.”

# Design goals / non-goals

**Goals**
- Redaction-first artifacts (`*.netbundle.zip`) that are safe to share by default.
- Prefer semantic (L7) replay; fall back to lower layers only when necessary.
- Make impairments declarative and portable (backend adapters).

**Non-goals**
- A full packet crafting toolkit for offensive security.
- Replacing Wireshark/tcpdump; integrate with them via standard formats.

# Prior art (and why it’s insufficient)

- PCAP/PCAPNG are widely used capture formats and are being standardized, but they are *files*, not a reproducible test workflow.
- Tools like `tc netem` can emulate delay/loss, but aren’t integrated with Rust test harnesses or portable artifacts.
- Rust crates exist for replaying traffic (e.g., tcpreplay-like senders, TCP replay utilities), but there’s no shared cassette/bundle format or redaction-default UX.

# Architecture & API sketch

Crates:
- `netcassette-core`: canonical flow model, timestamps, hashing, redaction primitives
- `netcassette-pcap`: pcap/pcapng adapters
- `netcassette-impair`: impairment schema + backends (netem, user-space)
- `netcassette-replay`: replay engines (L7 adapters first)
- `netcassette-bundle`: `*.netbundle.zip` IO
- `cargo-netcassette`: CLI

Key traits:
- `CaptureSource` (live, file)
- `Redactor` (policy-driven)
- `ReplayEngine` (HTTP, DNS, QUIC, raw)
- `ImpairmentBackend` (netem, shim)

# Minimum lovable MVP

- PCAP/PCAPNG read → normalized “flows + timing” summary
- A minimal `*.netbundle.zip` writer/reader
- `cargo net replay` for HTTP (reqwest/hyper adapter) with:
  - deterministic timing model (wall clock not required)
  - strict redaction presets
- Linux-only netem backend (delay/loss/jitter)

# De-risk plan

1) Start with **L7 replay** and redaction-first bundles; add L4 only if needed.
2) Make “no raw payload” the default: hash bodies, keep headers allowlisted.
3) Ensure bundles can be created from integration tests without root (capture via proxies or app-level instrumentation).

# Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
