---
id: P-0236
title: TUF Repository + Client Conformance & Evidence Kit
status: idea
domains: [supply-chain, update-systems, security, interop, testing, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://theupdateframework.io/
  - https://theupdateframework.io/spec/
  - https://theupdateframework.github.io/specification/latest/
  - https://crates.io/crates/tuf
  - https://crates.io/crates/tough
---

# Problem

TUF is the “secure software update” workhorse: it’s widely recommended and used, but it’s also *easy to implement partially* and hard to debug when multiple tools disagree on metadata, versioning rules, or snapshot/rollback behavior. Rust has building blocks (`tuf`, `tough`), but is missing a **default conformance + interop harness** that produces **portable, redactable evidence bundles** for “client X rejected repo Y” class failures. citeturn0search8turn0search0turn0search4turn0search3turn0search7

# What it provides

Deliverables other people can rely on:

1. `tuflab` workspace (crates):
   - `tuflab-model`: pinned TUF metadata IR (typed) + strict/lenient parsers.
   - `tuflab-canon`: canonicalization + normalization rules (JSON encoding stability, key ordering policy, signature encoding notes).
   - `tuflab-verify`: verification engine with **“explain” traces** (why a role/target failed: threshold, expiry, delegation walk, rollback check).
   - `tuflab-repo`: tiny repo builder to generate edge-case repos (for tests; not a production repo server).
   - `tuflab-adapters`: adapter traits for external clients/servers (e.g., `tough` client; future: RSTUF service client).
   - `tuflab-runner`: run scenarios, capture traces, produce bundles.

2. Evidence bundle format: `*.tufbundle.zip`
   - `manifest.json`: spec version pin, keys, thresholds, scenario seed, clock model
   - `repo/`: minimal repo snapshot used for the run (or a redacted/hashed representation)
   - `fetch.ndjson`: client fetch log (URLs, ETags, cache semantics) with redaction knobs
   - `verify.json`: decision tree + “explain” traces + derived invariants
   - `expected.json`: oracle assertions (when using the bundled reference engine)
   - `compat.md`: human summary + guidance (“likely root cause: inconsistent snapshot versioning”)

3. CLI: `tuflab`
   - `tuflab gen` (generate a minimal repo with specific properties)
   - `tuflab run --adapter tough` (execute scenario against a client)
   - `tuflab diff a.tufbundle.zip b.tufbundle.zip`

# Minimum lovable MVP (4–8 weeks)

- Parser + canonical IR for core metadata (root/timestamp/snapshot/targets).
- Reference verification engine for *one* config profile.
- Scenario generator for common failure classes: expiry, rollback attempt, key rotation, inconsistent snapshot.
- Bundle emit + diff tool with 2–3 golden fixtures.

# De-risk plan

- Start by matching **spec_version semantics** and common edge cases (expiry, rollback, snapshot consistency) using a reference verifier.
- Add adapter for `tough` early to ensure real-world shape. citeturn0search7

# Non-goals

- Not a general-purpose TUF repo server.
- Not a replacement for existing clients; it’s the **shared evidence + conformance layer**.

# Why this is “missing middle”

Most teams don’t need “another TUF crate”; they need a **shared way to reproduce and communicate** update failures safely across vendors, CI, and incident reports.
