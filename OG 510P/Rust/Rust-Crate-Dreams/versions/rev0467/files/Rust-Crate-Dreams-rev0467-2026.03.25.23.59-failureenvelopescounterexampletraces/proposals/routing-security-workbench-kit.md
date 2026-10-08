---
id: P-0155
title: Routing Security Workbench Kit
status: idea
domains: [networking, security, interop, devtools, conformance, reproducibility]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/rpki
  - https://routinator.docs.nlnetlabs.nl/en/stable/manual-page.html
  - https://routinator.docs.nlnetlabs.nl/en/v0.12.2/rtr-service.html
  - https://crates.io/crates/krill
---
# Problem

Routing incidents are still “debugged by vibes” too often: different validators, different RTR servers, different policy knobs, and logs that don’t replay.

Rust has strong building blocks for RPKI parsing/validation and operational validators/daemons, but there is no **artifact-first workbench** that helps operators and library authors reproduce:

- “Why did this origin validation decision change?”
- “Why did my router’s RTR client reject the cache?”
- “Is this a policy change, a data change, or an implementation bug?”

# What it should provide

## 1) A standard evidence bundle for routing-validation incidents

A portable `rpkibundle.zip` intended for bug reports and CI regression gates:

- `manifest.json` (kit version, feature flags, OS/arch, time window)
- `rpki/` fetched repositories or a minimal curated subset
- `tal/` trust anchors + `fetch-plan.json` (URLs, hashes)
- `validation-report.json` (validated payloads, rejected objects, reason codes)
- `rtr/` captures (session transcript, serial/intervals, protocol version)
- `bgp/` optional normalized BGP update stream (MRT/pcap-derived summaries)
- `policy.toml` (ROV policy knobs, local exceptions)
- `diff/` optional “before/after” reports for change attribution

Design principle: **redaction first** (strip private ASNs/prefixes via policy), but preserve decision structure.

## 2) A replay + diff harness

CLI/workflow (likely `cargo rpki`) that can:

- `bundle` — build a minimal bundle from a live system (or from fixtures)
- `replay` — deterministically replay validation/RTR decisions
- `diff` — compute a stable diff between two bundles (“data changed” vs “policy changed” vs “impl changed”)
- `conformance` — run protocol and semantic checks (RTR v1 vs legacy compatibility, payload invariants)

## 3) Conformance packs for the tricky parts

Start with small, high-value packs:

- **RTR interop vectors**: version negotiation, session resets, serial queries, refresh/expire behaviors
- **Validation corner cases**: malformed manifests/CRLs, timing edges, algorithm transitions, repository freshness

# MVP → v1 plan

### MVP (usable by operators)
- Bundle format + `replay` for validation results
- RTR transcript capture + basic sanity checks
- “Diff of decisions” report (per prefix/ASN)

### v1 (ecosystem glue)
- Adapters for common validators/servers (starting with Routinator-style outputs)
- Router-side RTR client replay harness (feed transcript into a dummy client)
- Policy schema versioning + best-practice profiles (strict vs permissive vs debug)

# Why this is “epic” (and realistic)

It’s epic because it gives the ecosystem a shared language for routing security bugs: **portable incidents**. It’s realistic because it can layer on top of existing RPKI crates/validators and start with bundles + replay before attempting full “one validator to rule them all”.
