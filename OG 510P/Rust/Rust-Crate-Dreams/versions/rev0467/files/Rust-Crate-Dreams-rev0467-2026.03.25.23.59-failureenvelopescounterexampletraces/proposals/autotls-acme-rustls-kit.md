---
id: P-0147
title: Autotls (ACME + rustls) Kit
status: idea
domains: [security, tls, ops, devtools, http, networking]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/rustls-acme/latest/rustls_acme/
  - https://letsencrypt.org/docs/client-options/
  - https://www.shuttle.dev/blog/2025/02/06/provisioning-tls-certificates-with-acme-in-rust
  - https://github.com/ctz/rustls/issues/364
---

# Problem

Rust web services frequently want a “Go autocert”-style experience: **one-line HTTPS** with automatic certificate
provisioning/renewal. The ecosystem has building blocks (notably `rustls-acme`), but the common operational tasks
still get reimplemented: DNS-01 integrations, multi-tenant SNI, staging vs prod, ACME rate-limit safety,
hot-reload across servers, and incident artifacts.

# What it provides

A pragmatic crate + cargo subcommand that turns ACME+rustrls into a production-ready workflow:

- `autotls::Manager` that yields `rustls::ServerConfig` updates (hot-rotated)
- Challenge support:
  - **HTTP-01** (built-in)
  - **DNS-01** via a provider trait + adapters for common DNS APIs (feature-gated)
- Multi-domain + multi-tenant SNI routing with safe caching and renewal scheduling
- A stable evidence bundle: `*.acmebundle.zip`
  - redacted ACME order timeline, challenge type, renewal schedule
  - endpoint reachability checks + errors
  - cert chain fingerprint + notAfter
- `cargo autotls doctor`:
  - validates ports, DNS, ALPN, clock skew, storage permissions
  - detects likely Let’s Encrypt rate-limit risk patterns

# Users & user stories

- **Small services**: “Turn on HTTPS without running a full PKI pipeline.”
- **Platform teams**: “Standardize certificate automation across many Rust services.”
- **Maintainers**: “Get reproducible evidence bundles for bug reports.”

# Prior art (and why it’s insufficient)

- `rustls-acme`: strong library, but leaves many ops decisions to each application.
- `acme-client` style crates: varied completeness; operational UX is fragmented.
- General ACME client lists show breadth, not a Rust cargo-native, auditable workflow.

# Design goals

- Zero background tasks by default (align with `rustls-acme` philosophy).
- “Evidence bundle first” for supportability and safe diagnostics.
- Provider adapters should be **optional** and auditable.

# Non-goals

- Not a reverse proxy.
- Not a full secret-management system (but must support external keystore hooks).

# Architecture & API sketch

- `autotls::store::{CertStore}` (pluggable persistence)
- `autotls::dns::{DnsProvider}` (DNS-01)
- `autotls::manager::Manager` (state machine + renewal)
- `autotls::bundle::{AcmeBundle}` (zip schema + redaction rules)
- `cargo-autotls` front-end

# Security / safety model

- Never store private keys unencrypted unless user explicitly chooses.
- Redaction rules ensure bundles are safe to share publicly by default.

# Maintenance & governance plan

- Keep minimal runtime assumptions (tokio optional).
- Maintain a small set of “officially supported” DNS providers; accept community adapters.

# Milestones

- **MVP**: HTTP-01 + file store + hot-rotating rustls config + doctor.
- **v0.5**: DNS-01 provider trait + 2–3 providers + `acmebundle.zip`.
- **v1.0**: multi-tenant SNI + hardening (rate-limit guardrails, backoff policies).

# Sources

- `rustls-acme` docs: https://docs.rs/rustls-acme/latest/rustls_acme/
- Let’s Encrypt ACME client overview: https://letsencrypt.org/docs/client-options/
- Real-world Rust ACME provisioning write-up: https://www.shuttle.dev/blog/2025/02/06/provisioning-tls-certificates-with-acme-in-rust
- rustls issue referencing need for OpenSSL-free ACME examples: https://github.com/ctz/rustls/issues/364
