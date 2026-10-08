---
id: P-0277
title: SSH Interop & Evidence Kit — canonical transcripts, redaction, and replay bundles across SSH implementations
status: idea
domains: [networking, security, ssh, interoperability, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc4253
  - https://datatracker.ietf.org/doc/html/rfc4254
  - https://www.rfc-editor.org/info/rfc4253
  - https://crates.io/crates/russh
  - https://crates.io/crates/thrussh
---

## What it should provide others

A **portable, redactable evidence workflow** for diagnosing “works with OpenSSH but fails with X” problems, and for building **conformance/interop CI** for Rust SSH clients/servers.

The gap is not “yet another SSH client library”; it is:
- a **canonical transcript IR** (handshake → auth → channels → subsystems) that can be compared across stacks
- **privacy-safe bundles** for bug reports and CI artifacts
- a runner that can produce **capability matrices** and reproducible “minimal failing scenarios”

## Why now (ecosystem gap)

Rust has capable SSH implementations (e.g., `russh`, `thrussh`) but interop debugging is still mostly ad‑hoc packet logs and “try a different cipher/KEX”. A kit that standardizes capture/replay/diff would unlock:
- faster upstreaming of interop fixes
- safer defaults via *measured* compatibility data
- regression protection across OpenSSH releases and embedded SSH stacks

## Proposed crate shape (workspace)

- `sshkit-core` — canonical event model, normalization, redaction framework
- `sshkit-capture` — adapters: `russh`, OpenSSH `ssh -vvv` log parser, (optional) pcap decoder hooks
- `sshkit-runner` — scenario DSL + orchestration (client/server matrix)
- `sshkit-diff` — semantic diff + “explain” (where the divergence begins)
- `sshkit-bundle` — `*.sshbundle.zip` IO, schema, signing hooks (optional DSSE)
- `cargo-sshkit` — CLI for CI use

### Canonical IR sketch

Events (example): `kex.proposal`, `kex.choice`, `hostkey`, `newkeys`, `auth.request`, `auth.success`, `channel.open`, `channel.request(pty)`, `subsystem(sftp)`, `global.request`.

Normalization rules:
- canonical algorithm naming and ordering
- stable timestamp bucketing
- redact user identifiers and payload bytes via policies

## Minimum lovable MVP (4–8 weeks)

1. `sshkit-bundle` + schema + `sshkit-diff` for transport/KEX/auth events
2. `sshkit-capture` adapters: OpenSSH verbose log → IR; `russh` handler hooks → IR
3. `sshkit-runner` matrix runner for a small set of scenarios:
   - password auth, pubkey auth
   - exec channel and PTY channel
   - SFTP subsystem “smoke” (optional)

Deliverable: `cargo sshkit matrix --clients ... --servers ... --out results.sshbundle.zip` and a diff report.

## De-risk plan

- Start with **log-level capture** (OpenSSH verbose logs, `russh` hooks) before full packet decoding.
- Use **golden fixtures** that pin known-good transcripts for common OpenSSH versions.
- Add pcap decoding only after IR+diff stabilize.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (canonical transcript + bundles + semantic diff)
