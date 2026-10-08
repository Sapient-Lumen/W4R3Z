---
id: P-0201
title: Secure Email Interop ShipKit
status: idea
domains: [security, email, crypto, interoperability, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc5322
  - https://datatracker.ietf.org/doc/html/rfc6376
  - https://datatracker.ietf.org/doc/html/rfc7489
  - https://datatracker.ietf.org/doc/html/rfc8617
  - https://datatracker.ietf.org/doc/html/rfc8551
---

# Problem

Rust has multiple mail crates, but “modern secure email” is still a minefield:
- inconsistent MIME normalization and canonicalization behaviors,
- fragmented implementations for DKIM/SPF/DMARC/ARC,
- hard-to-debug interop failures (providers, mailing lists, forwarders),
- S/MIME and OpenPGP/MIME are frequently bolted on with ad-hoc tooling.

Teams need a **single shipkit** that can validate, explain, and bundle evidence.

# What it provides

- `mailkit` Rust library:
  - robust RFC 5322 parsing + MIME tree model + *deterministic canonicalization layer*
  - DKIM verify/sign, DMARC evaluate, SPF checks, ARC verify (pluggable DNS)
  - S/MIME (CMS) verify/sign and OpenPGP/MIME verify/sign (feature-gated)

- `mailkit` CLI:
  - `verify <eml>` → `*.mailbundle.zip` (redacted) with a complete explain report
  - `sign` / `seal` pipelines for outbound mail
  - `normalize` (deterministic) for “same message, different representation” diffs

- `mailbundle.zip` format:
  - `message.eml` (optional, redacted)
  - `mime-tree.json`
  - `auth-report.json` (DKIM/SPF/DMARC/ARC steps + DNS evidence)
  - `crypto-report.json` (S/MIME / PGP results)
  - `policy.json` (redaction + trust roots)

# Users & user stories

- **Deliverability**: “Why did this message fail DMARC after forwarding? Give me a portable bundle.”
- **Security**: “Verify ARC chains and DKIM signatures in our pipeline, deterministically.”
- **Client authors**: “Interoperate with provider quirks without reimplementing everything.”

# Prior art (and why it’s insufficient)

Mail stacks tend to be siloed: parsers, DKIM, DMARC, S/MIME are separate and don’t share a common evidence format.

# Design goals

- Deterministic normalization/canonicalization as a first-class primitive.
- Pluggable DNS and trust stores (so CI is deterministic).
- “Explain mode” designed for humans and incident tickets.
- Redaction presets for sharing.

# Non-goals

- Replacing an MTA.
- Bundling a full IMAP/SMTP client stack.

# Architecture & API sketch

Crates:
- `mailkit-core` (parsing + MIME model + normalization)
- `mailkit-auth` (DKIM/SPF/DMARC/ARC with pluggable DNS)
- `mailkit-crypto` (S/MIME / OpenPGP/MIME; feature-gated)
- `mailkit-cli` (bundles + reports)

Key API:
- `Verifier::verify(message, env) -> VerificationReport`
- `BundleWriter::write(report, policy) -> mailbundle.zip`

# Security / safety model

- Redaction policy is always applied before bundle output unless explicitly overridden.
- Trust roots and DNS evidence are captured (or stubbed) to enable reproducibility.
- Crypto operations are constant-time where applicable; use well-reviewed primitives.

# Maintenance & governance plan

- Keep a compatibility corpus: real-world samples (redacted) + expected outcomes.
- Treat canonicalization behavior as a semver-sensitive contract.

# Milestones

1. MVP: parser + MIME tree + DKIM verify + `mailbundle.zip`
2. SPF/DMARC/ARC verify with pluggable DNS snapshots
3. Deterministic normalization + diff tool
4. S/MIME and OpenPGP/MIME modules
5. Provider interop corpus + CI matrix

# Open questions

- Best deterministic DNS evidence format (zone snapshot vs query transcript)?
- How to support “provider-specific canonicalization quirks” without becoming a quirk zoo?

# Sources

- RFC 5322 (Internet Message Format) — https://datatracker.ietf.org/doc/html/rfc5322
- RFC 6376 (DKIM) — https://datatracker.ietf.org/doc/html/rfc6376
- RFC 7489 (DMARC) — https://datatracker.ietf.org/doc/html/rfc7489
- RFC 8617 (ARC) — https://datatracker.ietf.org/doc/html/rfc8617
- RFC 8551 (S/MIME 4.0 message format) — https://datatracker.ietf.org/doc/html/rfc8551
