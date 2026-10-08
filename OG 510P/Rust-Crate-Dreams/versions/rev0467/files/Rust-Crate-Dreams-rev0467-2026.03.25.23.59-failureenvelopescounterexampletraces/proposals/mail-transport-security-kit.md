---
id: P-0069
title: mail-transport-security-kit — MTA-STS/TLS-RPT/DANE “doctor” + evaluation engine
status: idea
domains: [email, security, dns, transport, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/kravietz/tlsrpt-rs
  - https://crates.io/crates/mhost
  - https://stalw.art/docs/mta/transport-security/mta-sts/
  - https://github.com/stalwartlabs/mail-auth
---
# Problem
Modern email security is no longer just SPF/DKIM/DMARC. Transport-layer protections (MTA-STS, TLS-RPT, DANE/TLSA) require correct DNS + HTTPS policy hosting + TLS validation, and failure modes are subtle (stale policies, mismatched MX, TLS downgrade behavior, report parsing). Rust has building blocks (auth libraries, TLS-RPT parsers, probing tools), but operators and application developers still stitch together bespoke checks and policy evaluators.

# Users & user stories
- **Mail server developers** want to evaluate remote domains’ transport security policies during delivery and emit correct TLS-RPT reports.
- **Operators** want a single “doctor” command to validate their domain setup (DNS + policy hosting) and explain deliverability failures.
- **Security teams** want CI checks and periodic monitoring with reproducible reports.

# Prior art (and why it’s insufficient)
- `tlsrpt-rs` parses TLS-RPT reports but does not provide full policy evaluation or setup validation. https://github.com/kravietz/tlsrpt-rs
- `mhost` queries many well-known subdomains and records; it’s great as a probe, but not a reusable policy engine with fixtures and evaluation APIs. https://crates.io/crates/mhost
- Stalwart’s docs and server show the feature set exists in a larger product, but the ecosystem lacks a crate-level “golden path” kit. https://stalw.art/docs/mta/transport-security/mta-sts/
- `mail-auth` covers DKIM/ARC/SPF/DMARC; transport-security needs a parallel kit (and should interoperate, not reimplement). https://github.com/stalwartlabs/mail-auth

# Design goals
- **Reusable evaluation core**: fetch, parse, and evaluate MTA-STS policies and DANE/TLSA records against observed MX/TLS sessions.
- **Explainability first**: every “fail” should come with a structured reason tree (“policy missing”, “policy expired”, “MX mismatch”, “TLSA mismatch”, etc.).
- **Test vectors + fixtures**: include a small conformance suite and fixtures for tricky cases (policy rollover, stale id, mixed MX).
- **Operational UX**: a `doctor` CLI that validates a domain’s DNS + HTTPS policy hosting, plus a machine-readable JSON report.
- **Composable**: can be embedded into MTAs, scanners, or monitoring agents.

# Non-goals
- Implementing SMTP or a full mail server.
- Re-implementing DKIM/DMARC (interop with existing crates is preferred).

# Architecture & API sketch
## Core crates
- `transport-security-core`:
  - `Resolver` trait (DNS + HTTPS fetch abstraction; caller supplies caching).
  - `MtaStsPolicy`, `TlsRptPolicy`, `DanePolicy` parsers.
  - `Evaluator` that consumes:
    - domain name
    - observed MX hostnames
    - observed TLS session metadata (cert chain, SNI, protocol versions)
    - returns `TransportSecurityResult { verdict, reasons, evidence }`
- `mail-transport-security-kit` (public facade + CLI):
  - `doctor domain.example`
  - `evaluate --mx mx.example --cert-chain ...` (for embedding/testing)

## Example API (sketch)
- `let policy = fetch_mta_sts(&resolver, "example.com").await?;`
- `let res = evaluate_mta_sts(&policy, observed_mx, observed_tls);`
- `println!("{}", res.explain_tree());` / `serde_json::to_value(res)`

# Security / safety model
- Treat DNS and HTTPS inputs as **untrusted**; enforce strict bounds (max TXT size, max redirects, max policy length).
- Provide **timeout + budget knobs** (DNS query count, HTTPS fetch size).
- Default to **fail-closed only when explicitly configured** (operators may prefer fail-open in early deployment).

# Maintenance & governance plan
- Keep `transport-security-core` dependency-minimal; isolate heavy dependencies (TLS stacks, HTTP clients) behind feature flags.
- Publish fixtures and a “compatibility ledger” documenting real-world deviations observed.

# Milestones
- **0.1**: MTA-STS fetch/parse/evaluate + `doctor` report (DNS + policy hosting sanity checks).
- **0.2**: TLS-RPT policy parsing + report parsing helpers (interop with `tlsrpt-rs`).
- **0.3**: DANE/TLSA evaluation + cross-checking with MTA-STS (explainable combined verdict).
- **0.4**: Monitoring mode (periodic checks + diff reports).

# Open questions
- How to model “observed TLS” generically across rustls/native-tls backends?
- What fixture corpus can be redistributed safely (avoid collecting sensitive production configs)?

# Sources
- https://github.com/kravietz/tlsrpt-rs
- https://crates.io/crates/mhost
- https://stalw.art/docs/mta/transport-security/mta-sts/
- https://github.com/stalwartlabs/mail-auth
