---
id: P-0232
title: Nostr Relay/Client Interop & Compliance Kit
status: idea
domains: [p2p, protocols, messaging, interop, testing, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://nips.nostr.com/1
  - https://github.com/nostr-protocol/nips
  - https://crates.io/crates/nostr
  - https://crates.io/crates/nostr-relay
---

# Problem

Nostr is a fast-moving protocol ecosystem defined by “NIPs” (Nostr Implementation Possibilities). Even with Rust implementations, developers still lack:

- an interop-grade harness to check relay/client behavior against pinned NIPs,
- canonicalization for event validation and subscription/filter semantics,
- safe, shareable repro artifacts for bugs (privacy and key material concerns),
- a “compliance surface” report (what NIPs/features a relay claims vs actually supports).

The base protocol flow is described in NIP-01 and evolves through additional NIPs; teams need a kit that can pin a NIP set and produce reproducible evidence bundles when behavior diverges. citeturn0search2turn0search5

# What it provides

1. `nostr-interop` workspace:
   - `nostr-nips`: pinned NIP schema snapshots + validation rules.
   - `nostr-canon`: canonical event representation (stable serialization, signature checks, tag normalization).
   - `nostr-harness`: scenario DSL (client ↔ relay) with controllable clocks and injected faults.
   - `nostr-evidence`: capture/redact/bundle/replay/diff.
   - `nostr-matrix`: “supported NIPs/features” probing + report.

2. Evidence bundle format: `*.nostrbundle.zip`
   - `manifest.json` (relay version, config hints, pinned NIP set)
   - `events.ndjson` (canonicalized events; signatures preserved but keys not leaked)
   - `session.ndjson` (client↔relay frames: REQ/EVENT/EOSE/CLOSE/NOTICE etc.)
   - `assertions.json` (expected semantics and observed deltas)
   - `redaction.toml` (pubkeys optionally hashed; content redaction presets)

3. CLI:
   - `nostr-interop probe` (discover capability surface)
   - `nostr-interop run` (scenario runner)
   - `nostr-interop diff` (semantic diffs across bundles)
   - `nostr-interop fuzz` (structured fuzzing around filters/tags/kinds)

# Design notes

## Canonicalization and privacy

Nostr events contain content and public keys. The kit should default to:

- content redaction presets (or content hashing),
- pubkey hashing with a bundle-local salt when needed,
- strict separation: bundles never contain private keys.

## Leverage existing Rust ecosystem

Rust already has protocol and relay crates (e.g., `nostr`, `nostr-relay`). The missing piece is a *standard interop harness* and evidence format that makes failures actionable across implementations. citeturn1search11turn1search2

# Minimum lovable MVP (4–8 weeks)

1. NIP-01 compliance harness:
   - event verification, basic REQ/subscription flow, EOSE semantics
2. Bundle capture + replay:
   - capture WebSocket frames and canonicalized events
3. `diff`:
   - highlight semantic mismatches (filter matching, tag/kind handling, EOSE timing)

# De-risk plan

- Begin with a tiny pinned NIP set: NIP-01 plus a small, widely-used subset.
- Build fixture corpus from real public relays (with aggressive redaction).
- Keep the harness modular so new NIPs can be added as plugins, not rewrites.

# Scorecard (0–5)

- Impact: 3
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4 (interop + evidence bundles, not “another client SDK”)

# Prior art / adjacent

- NIP-01 (base protocol) and the NIPs repository. citeturn0search2turn0search5
- Rust protocol/relay crates (building blocks). citeturn1search11turn1search2
