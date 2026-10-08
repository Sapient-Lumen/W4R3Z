---
id: P-0138
title: Email Authentication Lab Kit — DKIM/DMARC/SPF/ARC/BIMI verification + reports + reproducible evidence bundles
status: idea
domains: [security, networking, devtools, observability]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/stalwartlabs/mail-auth
  - https://datatracker.ietf.org/doc/html/rfc8617
  - https://www.ietf.org/blog/arc/
  - https://docs.rs/email-auth
needs:
  - A “one command” way to verify DKIM/SPF/DMARC/ARC results locally and in CI, with deterministic, shareable artifacts for bug reports.
  - An opinionated bridge from low-level verification libraries to operational workflows: DNS caching, message canonicalization pitfalls, reporting formats, and policy gates.
  - Tooling that adapts to real-world mail flows (forwarders, mailing lists) and the state of ARC in practice (experiment learnings, partial deployments).
non_goals:
  - Building an SMTP server or full MTA; integrate with existing MTAs and logs.
---

## What this crate should provide

### 1) Reproducible evidence bundles
Standardize `*.mailauthbundle.zip`:

- `message.eml` (optionally redacted with a reversible map)
- `dns.json` (the exact TXT/A/AAAA lookups used, with TTLs and timestamps)
- `auth-results.json` (normalized SPF/DKIM/DMARC/ARC decisions + reasons)
- `headers.normalized.txt` (canonicalization inputs)
- `policy.json` (what policy was applied: strict vs tolerant, ARC handling, etc.)
- `report.md` (human-readable summary)

Command UX:
- `cargo mailauth verify ./message.eml --bundle out.mailauthbundle.zip`
- `cargo mailauth replay out.mailauthbundle.zip` (no network access required)

Why: verification disputes often come down to “what DNS did you see?” or “what canonicalization did you apply?”.

### 2) A “policy doctor”
- A small policy language for “what we accept”:
  - required alignment rules
  - relaxed handling for known forwarders
  - ARC evaluation strategy (explicitly configurable)
- Output `policy-report.json` suitable for CI gating (e.g., fail if DMARC would reject).

### 3) Operational adapters
- DNS resolver trait + optional caching layer
- Parsers for common MTA logs (feature-gated), so you can reconstruct bundles from production incidents
- Optional support for generating and validating aggregated reports (DMARC RUA/RUF) *as artifacts*, not emails

## MVP plan
- Bundle schema + `cargo mailauth` CLI
- Verification pipeline using `mail-auth` and/or `email-auth` as the engine(s)
- Deterministic replay mode by pinning DNS answers into the bundle
- 20–30 curated test fixtures:
  - correct DKIM with relaxed/strict canonicalization variants
  - SPF softfail vs fail
  - DMARC alignment edge cases
  - ARC pass/fail sequences from RFC-style examples

## v1 plan
- Add “redaction mode” for safe sharing:
  - header value hashing with a reversible map stored separately
  - attachment stripping
- Add “deliverability lab” mode:
  - generate test messages with controlled header/body transforms
  - validate downstream auth-results emitted by MTAs

## Adoption strategy
- Aim for:
  - MTA operators (incident response)
  - SaaS teams (outbound email correctness)
  - library maintainers (regression tests and bug bundles)
- Keep core strict: stable schemas, no hidden network access in replay.

## Risks and mitigations
- **ARC ambiguity in the field**: treat ARC as explicitly policy-controlled; never silently “trust” it.
- **Privacy**: make redaction first-class and auditable.
