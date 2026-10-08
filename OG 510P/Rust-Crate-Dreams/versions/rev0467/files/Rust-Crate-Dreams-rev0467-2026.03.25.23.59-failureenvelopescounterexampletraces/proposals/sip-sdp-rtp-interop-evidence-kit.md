---
id: P-0311
title: SIP + SDP + RTP Interop & Evidence Kit — profile-aware call flows, media-negotiation diagnostics, and replayable VoIP bundles
status: idea
domains: [telephony, realtime, networking, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://datatracker.ietf.org/doc/html/rfc3261
  - https://www.sipforum.org/news-events/test-event-wg-overview-and-charter-sipit/upcoming-sipit-events/
  - https://crates.io/crates/rsipstack
---

# Problem

SIP is old, huge, and still expensive to debug. The failure modes that hurt operators are rarely “can I parse the header?” They are:

- route-set and DNS resolution surprises,
- auth/TLS and policy mismatches,
- early-media and forked-call edge cases,
- SDP/media negotiation drift,
- RTP symptoms that are impossible to explain from signaling logs alone.

Rust now has credible SIP substrate again (`rsip`, `rsip-dns`, `rsipstack`, SIP bot/test tooling), but it still lacks a default **interop-evidence layer** that can turn real call failures into portable and replayable artifacts.

# What it provides

- `sip-profile` — operator/vendor profile packs for transports, DNS, auth, extensions, timers, and tolerated deviations.
- `sip-canon` — canonical IR for dialogs, transactions, route decisions, auth events, and media negotiation state.
- `sdp-check` — semantic comparison of codec/transport/media-attribute negotiation.
- `rtp-summary` — media-path evidence summaries tied back to signaling decisions.
- `sip-replay` — deterministic replay for registration, call setup, fork, transfer, and failure scenarios.
- `cargo sip-interop` — emit `*.sipbundle.zip` for lab repro, carrier/vendor escalation, and regression suites.

# What the crate should provide other people

1. **A stable call-failure artifact** that spans SIP signaling and enough media evidence to be useful.
2. **Profile pinning** for operator/counterparty behavior instead of vague “SIP compliant” claims.
3. **Replayable interop scenarios** aligned with the kinds of issues that surface at SIPit-style events and real deployments.
4. **Explainable negotiation diffs** for route, auth, SDP, and codec mismatches.
5. **Composable adapters** for Rust SIP stacks and network test harnesses.

# Users & user stories

- **PBX / SBC / softphone teams**: “Replay the exact failing call flow against the new build before shipping.”
- **Carrier interop engineers**: “Compare our profile pack with the counterparty’s and pinpoint the first semantic divergence.”
- **QA labs**: “Generate portable bundles from registration, re-INVITE, and forked-call scenarios.”
- **Support/SRE teams**: “Share one evidence artifact instead of SIP logs plus separate RTP notes.”

# Prior art (and why it’s insufficient)

- RFC 3261 and the surrounding SIP ecosystem are mature, and SIP Forum’s SIPit events still exist because interoperability remains stubbornly hard.
- Rust substrate is better than it used to be, but still mostly oriented around stack implementation rather than **canonical evidence and scenario replay**.
- Existing support practice still leans heavily on ad hoc packet captures and manually annotated ladder diagrams.

# Design goals

1. **Dialog- and transaction-aware** — the canonical model must explain call state, not just messages.
2. **Media-linked** — SDP and RTP evidence should connect back to signaling verdicts.
3. **Profile-driven** — operator/vendor assumptions are explicit and versioned.
4. **Carrier-realistic** — support forks, early media, transfers, timers, retransmits, and TLS/DNS policy quirks.
5. **Privacy-preserving** — redact phone numbers, user identities, and payload content by default.

# Non-goals

- Not a turnkey softswitch.
- Not a full media server or transcoder.
- Not a replacement for packet-capture tools.

# Architecture & API sketch

```rust
pub struct SipInteropReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub negotiation_diffs: Vec<Divergence>,
    pub media_findings: Vec<MediaFinding>,
}

pub trait SipAdapter {
    fn transact(&mut self, event: CanonicalSipEvent) -> Result<Vec<CanonicalSipEvent>, Error>;
}
```

Bundle draft: `profile.toml`, `dialogs.json`, `transactions.jsonl`, `sdp.json`, `rtp-summary.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Default tokenization for numbers, domains, and user identities.
- No default storage of raw media payloads.
- Time-bound replay and fuzz-resistant parsing boundaries.
- Support separate operator-internal and vendor-shareable bundle views.

# Maintenance & governance plan

- Keep canonical IR narrow and aligned to widely deployed flows first.
- Publish scenario packs for registration, INVITE, re-INVITE, REFER, cancel, fork, and auth/DNS cases.
- Maintain adapters for the most active Rust SIP crates before broader integrations.
- Record exact RFC/profile assumptions and extension support in every profile pack.

# Milestones

## 0.1
- Canonical dialog/transaction IR
- SDP diff model
- Redacted bundle writer

## 0.2
- Replay harness
- Registration/INVITE/fork scenarios
- `cargo sip-interop doctor`

## 1.0
- Stable `*.sipbundle.zip`
- Profile packs for common operator/counterparty setups
- RTP summary integration tied to signaling verdicts

# Open questions

- How much RTP evidence is enough without becoming a media analyzer?
- Which SIP extensions belong in the MVP profile model?
- Should DNS resolution evidence live in core or a companion crate?

# Sources

- RFC 3261 (SIP): https://datatracker.ietf.org/doc/html/rfc3261
- SIP Forum SIPit page: https://www.sipforum.org/news-events/test-event-wg-overview-and-charter-sipit/upcoming-sipit-events/
- `rsip` crate: https://crates.io/crates/rsip
- `rsipstack` crate: https://crates.io/crates/rsipstack
- `rsip-dns` crate: https://crates.io/crates/rsip-dns
