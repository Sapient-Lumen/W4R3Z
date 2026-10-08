---
id: P-0328
title: OCFL 1.1 + BagIt Profiles Preservation Interop & Evidence Kit — canonical object diffs, profile-pinned transfers, and replayable ingest bundles
status: idea
domains: [preservation, archives, ocfl, bagit, storage, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://ocfl.io/1.1/spec/
  - https://github.com/OCFL/spec/blob/main/1.1/spec/validation-codes.md
  - https://datatracker.ietf.org/doc/html/rfc8493
  - https://bagit-profiles.github.io/bagit-profiles-specification/
  - https://crates.io/crates/rocfl
  - https://crates.io/crates/async_bagit
---

# Problem

Digital-preservation teams often use **BagIt for transfer** and **OCFL for storage**, but the painful breakages happen between those layers:

- bags that validate locally but violate the receiving institution’s profile,
- path, digest, or metadata conventions that survive transfer but fail at ingest,
- OCFL objects that are structurally valid yet drift in fixity, inventory intent, or storage policy,
- and escalation packages that still move around as giant tarballs plus hand-written notes rather than deterministic evidence.

Rust already has some preservation substrate, but the missing epic contribution is a **shared interop and evidence layer** around ingest, validation, and semantic object diffs.

# What it provides

- `bag-ir` — canonical IR for payloads, manifests, tag files, profile references, digests, and transfer metadata.
- `ocfl-ir` — canonical IR for storage roots, objects, inventories, versions, content paths, and extension state.
- `preservation-profile` — lockfiles pinning BagIt profile assumptions, digest policies, OCFL version/extension expectations, and ingest rules.
- `preserve-verify` — semantic checks for bag/profile validity, ingest readiness, OCFL object integrity, and cross-layer consistency.
- `ingest-plan` — a deterministic plan from bag intake to OCFL object materialization with explainable checkpoints.
- `preserve-diff` — semantic diffs: “payload changed but tag manifest not updated”, “inventory digest set changed”, “content path rewritten”, “profile URI drifted”.
- `cargo preserve` — emit `*.preservebundle.zip` for handoff, ingest debugging, migration testing, and audit evidence.

# What the crate should provide other people

1. **A boring artifact for preservation ingest incidents** instead of bespoke zip files and emails.
2. **Profile pinning** for the exact transfer and storage assumptions a repository expects.
3. **Cross-layer validation** spanning BagIt transfer semantics and OCFL storage semantics.
4. **Canonical diffs** that explain object evolution in repository terms instead of raw filesystem deltas.
5. **A neutral layer** above local filesystems, S3-backed OCFL stores, and institution-specific ingest tooling.

# Persona / who it’s for

- Digital repository maintainers
- Library/archive engineering teams
- Preservation workflow authors
- Institutional transfer/onboarding teams
- Vendors integrating with preservation repositories

# Users & user stories

- **Repository engineer**: “Show me why this bag passed creation but failed our ingest profile.”
- **Archive ops team**: “Diff this OCFL object against the prior version in a way that explains preservation significance.”
- **Migration lead**: “Replay the ingest path and prove that the resulting inventory is equivalent to the source assumptions.”
- **Partner institution**: “Redact sensitive metadata fields while keeping the transfer failure reproducible.”

# Prior art (and why it’s insufficient)

- OCFL 1.1 and its validation-code surface are explicit and mature.
- BagIt is stable as RFC 8493, and BagIt Profiles add machine-readable agreement around optional conventions.
- Rust has `rocfl`, `async_bagit`, and `bagr` as meaningful substrate.
- But there is still no boring-default Rust crate family for **BagIt profile pinning + OCFL ingest planning + semantic diffs + portable preservation evidence bundles**.

# Design goals

1. **Transfer-to-storage continuity** — the seam between BagIt and OCFL is the first-class problem.
2. **Digest explicitness** — hash policy and manifest assumptions must always be visible.
3. **Preservation semantics over raw files** — diffs should describe object meaning, not just path churn.
4. **Rebuildability-friendly** — outputs must help prove that repositories can reconstruct intent from stored artifacts.
5. **Implementation neutrality** — useful whether the ingest stack is Rust, Java, Python, or shell scripts.

# MVP surface

- Minimal types: `BagSnapshot`, `OcflSnapshot`, `PreservationProfile`, `IngestPlan`, `PreservationReport`
- Minimal functions:
  - `load_bag()`
  - `verify_bag()`
  - `plan_ingest()`
  - `verify_ocfl()`
  - `diff_objects()`
  - `write_bundle()`
- Feature flags:
  - `bagit`
  - `ocfl`
  - `s3`
  - `redaction`
  - `serde`

# Compatibility story

- MVP should target **BagIt RFC 8493**, **BagIt Profiles 1.4.0**, and **OCFL 1.1**.
- It should consume existing Rust and non-Rust repository outputs through adapters.
- It should not require users to adopt a new repository architecture.
- MVP should intentionally avoid becoming a full digital repository or migration platform.

# Conformance & fixtures

- Synthetic bags covering digest mismatches, missing tag files, profile violations, and serialized transfer variants.
- Synthetic OCFL objects covering inventory drift, content-path rewrites, extension declarations, and digest-policy changes.
- Ingest fixtures mapping source bags to expected OCFL objects with golden semantic verdicts.
- Optional adapters for `rocfl` or institutional validation outputs.

# Path to boring stability

- First stabilize IRs and finding vocabulary on synthetic corpora.
- Then validate replay and diff semantics on one or two redacted real ingest cases.
- Freeze bundle layout only after redaction preserves enough evidence for auditing.
- Keep profile packs and extension expectations explicitly versioned.

# Scorecard

- Impact: 3/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A CLI and library that ingest one BagIt transfer, validate it against a pinned profile, produce a deterministic OCFL ingest plan, verify the resulting object against OCFL 1.1 expectations, diff it against a previous object snapshot, and emit a redactable `*.preservebundle.zip`.

# De-risk plan

1. Start offline with filesystem snapshots only.
2. Keep OCFL extension support read-only at first.
3. Prove usefulness on synthetic failures before taking on full repository adapters.
4. Treat serialization and transport wrappers as adapters, not core semantics.

# Non-goals

- Not a full preservation repository platform.
- Not an end-user desktop bagging tool.
- Not a replacement for institutional policy or appraisal workflows.

# Architecture & API sketch

```rust
pub struct PreservationReport {
    pub profile_id: String,
    pub bag_findings: Vec<Finding>,
    pub ocfl_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn plan_ingest(profile: &PreservationProfile, bag: &BagSnapshot) -> IngestPlan;
pub fn verify_ocfl(profile: &PreservationProfile, obj: &OcflSnapshot) -> PreservationReport;
```

Bundle draft: `profile.toml`, `bag/`, `ocfl/`, `ingest-plan.json`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact donor metadata, internal paths, secrets, and accession identifiers where needed.
- Bound archive expansion and path traversal behavior by default.
- Preserve fixity and object-graph meaning after redaction.
- Record digest algorithms and verifier versions explicitly.

# Maintenance & governance plan

- Keep validation rules profile-driven and data-backed where possible.
- Version profile packs and bundle schema separately.
- Encourage institutions to contribute redacted fixture packs rather than giant bespoke repos.
- Keep adapters optional so the core stays small and durable.

# Milestones

## 0.1
- BagIt + OCFL IRs
- Bag/profile validation
- Ingest-plan draft and bundle writer

## 0.2
- Semantic object diffs
- Redaction support
- OCFL validation-code mapping

## 1.0
- Stable `*.preservebundle.zip`
- Real-world ingest replay corpus
- CI-friendly preservation regression workflows

# Open questions

- How much serialized-bag transport logic belongs in core versus adapters?
- Should extension policy live in profiles or an extension companion crate?
- Can we keep object diffs preservation-meaningful without forcing repository-specific vocabulary?

# Sources

- OCFL 1.1 spec: https://ocfl.io/1.1/spec/
- OCFL validation codes: https://github.com/OCFL/spec/blob/main/1.1/spec/validation-codes.md
- BagIt RFC 8493: https://datatracker.ietf.org/doc/html/rfc8493
- BagIt Profiles 1.4.0: https://bagit-profiles.github.io/bagit-profiles-specification/
- `rocfl`: https://crates.io/crates/rocfl
- `async_bagit`: https://crates.io/crates/async_bagit
