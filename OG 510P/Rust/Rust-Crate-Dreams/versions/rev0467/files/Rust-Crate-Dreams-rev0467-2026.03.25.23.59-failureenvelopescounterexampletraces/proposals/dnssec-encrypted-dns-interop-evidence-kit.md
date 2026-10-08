---
id: P-0251
title: DNSSEC + Encrypted DNS (DoH/DoQ/DoT) Interop & Evidence Kit — canonical traces, policy explainers, and repro bundles
status: idea
domains: [networking, dns, privacy, security, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc4033
  - https://datatracker.ietf.org/doc/html/rfc8484
  - https://www.rfc-editor.org/rfc/rfc9250.html
---

## Why this is missing
Rust has good *pieces* (DNS message parsing, resolvers, TLS stacks), but operators and client authors still lack a **portable, reproducible “what happened?” artifact** when DNSSEC validation fails, when encrypted DNS transports misbehave, or when policy decisions differ across implementations.

This crate proposal is not “yet another resolver”. It’s the **interop + evidence layer**: *capture → canonicalize → diff → explain → replay*.

## What the crate provides
A workspace that produces and consumes **`*.dnsbundle.zip`** artifacts (redaction-first) containing:

- Raw request/response wire messages (classic DNS UDP/TCP), plus DNSSEC material (RRSIG/DNSKEY/DS/NSEC/NSEC3) and validation outcomes (based on DNSSEC’s origin authentication/integrity model).  
- Encrypted DNS transport transcripts:
  - DoH request/response mapping (DNS messages in HTTP exchanges).  
  - DoQ connection + stream transcript (DNS over QUIC).  
- A “policy snapshot” (trust anchors, permitted algorithms, NTP offset tolerance, max chain length, etc.) and a **verifiable decision log**: which record validated, which didn’t, and why.

Spec anchors: DNSSEC overview and capability/limits in RFC 4033; DoH in RFC 8484; DoQ in RFC 9250.  
(See evidence links above.)

### Core crates/modules
- `dnsbundle`: bundle schema + redaction + signing + deterministic ordering.
- `dns-wire`: strict DNS message roundtrip + canonicalization (no “helpful” normalization without explicit mode).
- `dnssec-explain`: validation trace IR (“why validated / why failed”).
- `doh-transcript`: HTTP capture + canonicalization for DoH semantics.
- `doq-transcript`: QUIC transcript capture + canonicalization for DoQ.
- `matrix`: runner that executes the same scenario against multiple backends (adapters) and produces a diff report.

### Adapter targets (initial)
- “Local” resolvers (running process) via a loopback harness.
- External resolvers via UDP/TCP/DoH/DoQ endpoints (network cassette style).
- Existing Rust DNS crates as backends where feasible (explicitly non-goal to replace them).

## Bundle format sketch
`dnsbundle/`
- `meta.json` (schema version, platform, clocks, redaction profile)
- `policy.json` (trust anchors, algorithm allowlist, limits)
- `queries/` + `responses/` as canonicalized binary + JSON view
- `transports/`:
  - `doh/` HTTP exchanges (headers redacted) + binary DNS messages
  - `doq/` QUIC connection summary + streams
- `validation.jsonl` (step-by-step validation events)
- `verdict.json` (machine summary + human-friendly “why”)

## MVP plan (6–8 weeks)
1. `dnsbundle` schema + deterministic pack/unpack + redaction presets.
2. Canonical DNS message capture + replay harness (UDP/TCP).
3. Minimal DNSSEC explain trace for common failures (bad sig, missing DS, expired, alg mismatch).
4. DoH transcript capture and mapping (RFC 8484 constraints) and DoQ transcript capture (RFC 9250).
5. “Diff view” report: same query scenario across two backends.

## De-risking
- Start with **evidence** (capture/canon/diff) before “full validation engine”.
- Use a compatibility matrix driven by bundles, not integration tests that are hard to reproduce.
- Treat “canonicalization” as versioned and testable: every change requires golden bundle updates.

## What users get
- A single zip they can attach to a bug report that lets others reproduce and compare behavior.
- A tool to answer: “is this DNSSEC failure due to policy, clocks, transport, or data?”
