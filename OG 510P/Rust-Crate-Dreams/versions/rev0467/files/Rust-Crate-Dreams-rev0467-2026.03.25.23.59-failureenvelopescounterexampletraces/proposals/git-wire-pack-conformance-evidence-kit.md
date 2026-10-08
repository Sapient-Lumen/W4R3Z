---
id: P-0253
title: Git Wire/Pack Conformance & Evidence Kit — protocol-v2 + pack-format corpora, canonical traces, and repro bundles
status: idea
domains: [developer-tools, networking, storage, interop, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://git-scm.com/docs/protocol-v2
  - https://git-scm.com/docs/pack-format
  - https://opensource.googleblog.com/2018/05/introducing-git-protocol-version-2.html
---

## Why this is missing
Rust Git implementations and Git-adjacent tooling (mirrors, partial clones, CI optimizations) often need:
- correct protocol-v2 negotiation,
- correct pack parsing/production,
- compatibility across servers with subtle capability differences.

Git’s official docs define protocol v2 and pack format, but Rust lacks a **portable “wire+pack evidence bundle”** for reproducible debugging and conformance testing.

## What the crate provides
A workspace that produces **`*.gitbundle.zip`** artifacts and a conformance harness:

- Canonical traces of protocol-v2 sessions (pkt-line transcripts, capabilities, commands, server options).
- Packfile corpora with normalized metadata and deterministic parsing checks.
- A replay runner that can execute sessions against multiple servers (git-daemon, HTTP smart, SSH) and diff results.

### Core crates/modules
- `pktline`: strict pkt-line parsing/rendering.
- `gitproto-v2`: protocol-v2 state machine and canonical transcript IR.
- `pack-canon`: pack parsing + canonicalization views (object graph summary, deltification stats).
- `gitbundle`: evidence schema + redaction + deterministic ordering.
- `matrix`: adapter runner to compare multiple backends.

## Bundle format sketch
`gitbundle/`
- `meta.json`
- `wire/`:
  - `session.pkt` (canonical pkt-line transcript)
  - `parsed.json` (semantic view)
- `pack/`:
  - `pack.pack` (binary)
  - `pack.index` (optional)
  - `summary.json` (object counts/types, delta chains, checksums)
- `verdict.json` + `diff.md`

## MVP plan (6–8 weeks)
1. `pktline` + transcript IR with stable formatting.
2. Parse protocol-v2 handshakes and `ls-refs` (minimal but real).
3. Parse pack headers, object entries, checksums; emit deterministic summary.
4. Generate “golden bundles” from real servers and diff across implementations.

## De-risking
- Start with **read-only** fetch flows and conformance corpora; push can come later.
- Bundle-based fuzzing: any parser failure yields a minimized `gitbundle` repro.

## What users get
- A shareable “wire+pack” repro artifact that makes Git interoperability bugs actionable.
