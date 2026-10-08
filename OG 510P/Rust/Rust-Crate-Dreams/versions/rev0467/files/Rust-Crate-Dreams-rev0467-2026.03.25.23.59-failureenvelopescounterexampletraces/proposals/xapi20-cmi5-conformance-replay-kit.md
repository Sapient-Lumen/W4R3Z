---
id: P-0338
title: xAPI 2.0 + cmi5 Conformance & Replay Kit — profile-pinned learning-event interoperability, explainable statement failures, and portable LMS/content bundles
status: idea
domains: [edtech, learning, xapi, cmi5, lrs, interoperability, conformance]
last_reviewed: 2026-03-06
evidence:
  - https://standards.ieee.org/ieee/9274.1.1/7321/
  - https://opensource.ieee.org/xapi/xapi-base-standard-documentation
  - https://aicc.github.io/CMI-5_Spec_Current/
  - https://github.com/adlnet/xapi-profiles
  - https://crates.io/crates/xapi-rs
---

# Problem

Rust now has an actual xAPI 2.0 implementation path, but the painful failures in real learning-data ecosystems are rarely “could not parse JSON.” They live at the seam between **statement validity, profile assumptions, and LMS/content-launch behavior**:

- statements that are technically accepted but semantically drift from a pinned profile,
- document-resource concurrency and state behavior that differs between learning record stores,
- cmi5 launches that appear successful but later produce unusable progress/completion traces,
- support cases that still move around as screenshots, redacted browser logs, and hand-written timelines instead of deterministic artifacts,
- and integration work that repeatedly rediscovers the same profile or authorization mismatch.

The worthy crate contribution is a **conformance and replay kit** that pins xAPI and cmi5 assumptions, wraps real LRS/content flows, and ships reproducible bundles for debugging and certification-style testing.

# What it provides

- `xapi-ir` — canonical Rust IR for statements, documents, profiles, statement batches, authority/context semantics, and cmi5 launch/session artifacts.
- `xapi-profile-lock` — lockfiles pinning xAPI version assumptions, profile vocabularies, allowed verbs/activity types, and cmi5 launch/reporting rules.
- `xapi-verify` — stable validation above raw schema acceptance: profile mismatches, idempotency drift, forbidden field combinations, and state-resource hazards.
- `cmi5-replay` — deterministic playback for LMS ↔ content ↔ LRS flows with explainable session verdicts.
- `statement-diff` — semantic diffs such as “completion was reported without the required launch/session lineage” or “same learner session, different authority semantics”.
- `cargo xapi-evidence` — emit `*.xapibundle.zip` for vendor handoff, regression testing, or interoperability review.

# What the crate should provide other people

1. **A boring default for xAPI/cmi5 debugging** rather than custom dashboards and log archaeology.
2. **One place to pin profile rules** across authoring, content delivery, and analytics systems.
3. **Replayable LMS/content sessions** that make integration bugs portable.
4. **Explainable validation above raw acceptance** so teams know why a statement is wrong, not only that it failed.
5. **Safer vendor handoff artifacts** with redaction-aware session bundles.

# Persona / who it’s for

- Learning Record Store implementers
- LMS and courseware integration teams
- Learning analytics engineers
- Compliance/interoperability QA teams
- Rust developers building on `xapi-rs`

# Users & user stories

- **LRS maintainer**: “Show me why the same batch of statements passes one profile but fails another.”
- **Courseware vendor**: “Replay this cmi5 session and tell me where launch, auth, or completion semantics drifted.”
- **District or enterprise integrator**: “Produce a redactable evidence bundle for the vendor without sharing the whole platform.”
- **Analytics engineer**: “Diff two session traces semantically instead of comparing raw JSON dumps.”

# Prior art (and why it’s insufficient)

- xAPI now has an IEEE standard surface and open documentation artifacts.
- cmi5 is a formal profile that exists precisely because xAPI needs extra interoperability rules for LMS/courseware use.
- ADL-authored xAPI profiles exist, and Rust has `xapi-rs`.
- But there is still no boring-default Rust crate family for **profile locking + cmi5 session replay + semantic diffs + portable evidence bundles**.

# Design goals

1. **Profile-first** — xAPI statements should be judged relative to explicit profiles, not vague “looks okay” logic.
2. **Session-aware** — cmi5 launch and progression semantics must be first-class.
3. **Replayability** — bundles should make support and certification-style work deterministic.
4. **Implementation neutrality** — useful whether the surrounding LMS/LRS/content stack is Rust or not.
5. **Privacy-aware artifacts** — enough detail for debugging without leaking sensitive learner information.

# MVP surface

- Minimal types: `StatementEnvelope`, `XapiProfile`, `SessionTrace`, `LaunchSnapshot`, `ValidationReport`, `SessionDiff`
- Minimal functions:
  - `load_statements()`
  - `verify_profile()`
  - `replay_session()`
  - `diff_sessions()`
  - `write_bundle()`
- Feature flags:
  - `xapi`
  - `cmi5`
  - `serde`
  - `redaction`
  - `profiles`

# Compatibility story

- MVP should target **xAPI 2.0 / IEEE 9274.1.1** semantics plus the current **cmi5** profile surface first.
- Profile support should be explicit and pinned; no hidden “best effort” behavior.
- The crate should complement `xapi-rs` and other LRS/client stacks rather than replace them.
- MVP should intentionally avoid becoming an LMS or reporting warehouse.

# Conformance & fixtures

- Tiny statement fixtures for actor/verb/object, attachments, contexts, documents, and concurrency-sensitive document-resource cases.
- Session fixtures for launch, assignable units, moveOn rules, completion, satisfaction, and suspend/resume behavior.
- Golden semantic verdicts for profile mismatch, cmi5 sequencing drift, and document-resource hazards.
- Public or synthetic fixtures preferred; private learning traces should only appear through redacted bundle tests.

# Path to boring stability

- First stabilize the profile and finding vocabularies.
- Then prove session replay is stable across LRS implementations.
- Freeze bundle format only after redaction preserves enough causal/session detail.
- Keep analytics and dashboard ambitions out of core.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that ingest a batch of xAPI statements plus optional cmi5 launch/session records, validate them against a pinned profile, replay the session, produce semantic findings, and emit a redactable `*.xapibundle.zip` suitable for CI or vendor debugging.

# De-risk plan

1. Start with statement/profile verification before tackling broad LRS compatibility.
2. Treat cmi5 as a replayable overlay over the xAPI core, not a separate platform.
3. Use synthetic fixtures for learner privacy by default.
4. Keep redaction and time-normalization rules explicit and testable.

# Non-goals

- Not a full LMS or LRS product.
- Not a reporting dashboard.
- Not a course-authoring suite.

# Architecture & API sketch

```rust
pub struct SessionReport {
    pub profile_id: String,
    pub statement_findings: Vec<Finding>,
    pub session_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_profile(profile: &XapiProfile, statements: &[StatementEnvelope]) -> SessionReport;
pub fn replay_session(profile: &XapiProfile, trace: &SessionTrace) -> Result<SessionReport>;
```

Bundle draft: `profile.toml`, `statements.ndjson`, `launch.json`, `documents/`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact learner identifiers, auth headers, and organization-specific routing metadata by default.
- Preserve timestamps and correlation identifiers in normalized form when needed for replay.
- Record exact profile pack version and validator version used.
- Bound attachment handling and binary capture by default.

# Maintenance & governance plan

- Keep core focused on IRs, profiles, replay, and finding vocabularies.
- Version profile packs separately from bundle schema.
- Encourage public synthetic course/session fixtures.
- Document how profile drift is handled so downstream users can compare reports over time.

# Milestones

## 0.1
- statement/profile IR
- basic validator
- bundle writer

## 0.2
- cmi5 session replay
- semantic diffs
- redaction support

## 1.0
- stable `*.xapibundle.zip`
- CI-ready interoperability corpus
- documented policy for profile/version drift

# Open questions

- How much cmi5 launch-state detail should be standardized in the bundle versus left implementation-specific?
- Should profile vocabularies be modeled as full RDF/graph artifacts or as a constrained normalized IR?
- How opinionated should session replay be about partial or offline reporting?

# Sources

- IEEE xAPI base standard page: https://standards.ieee.org/ieee/9274.1.1/7321/
- Open xAPI base documentation: https://opensource.ieee.org/xapi/xapi-base-standard-documentation
- cmi5 current specification: https://aicc.github.io/CMI-5_Spec_Current/
- xAPI profiles: https://github.com/adlnet/xapi-profiles
- `xapi-rs`: https://crates.io/crates/xapi-rs
