---
id: P-0372
title: OpenFeature + OFREP Conformance & Incident Replay Kit — profile locks, evaluation traces, and portable flag-behavior bug bundles
status: idea
domains: [feature-flags, application-platforms, standards, interoperability, testing, observability, devtools]
last_reviewed: 2026-03-06
evidence:
  - https://openfeature.dev/specification/
  - https://openfeature.dev/docs/reference/other-technologies/ofrep/
  - https://openfeature.dev/docs/reference/sdks/server/rust/
  - https://flagd.dev/providers/rust/
  - https://github.com/open-feature/rust-sdk-contrib/releases
---

# Problem

Rust now has real OpenFeature substrate, OFREP exists as a vendor-neutral remote protocol, and `flagd`/provider workflows are increasingly usable. But teams still debug feature-flag incidents with screenshots, ad hoc logs, and application-specific guesses instead of a portable artifact that says:

- which provider profile and protocol surface were assumed,
- which evaluation context fields mattered,
- which defaults, hooks, and reason codes were observed,
- which transport/cache mode was in play,
- and how two providers or two backends differ semantically for the same scenario.

The missing Rust contribution is not another feature-flag backend. It is a **profile-aware conformance and incident-replay crate** that turns flag behavior into deterministic, reviewable evidence.

# What it provides

- `flag-profile.lock` — pins OpenFeature/OFREP assumptions, provider behavior toggles, context requirements, cache mode, and transport expectations.
- `eval-trace` — a neutral IR for evaluation requests, resolved values, variants, reasons, errors, hooks, and tracking events.
- `scenario-pack` — small reproducible test scenarios for context merges, missing keys, fallback behavior, targeting, events, and config reloads.
- `provider-bridge` — adapters for Rust OpenFeature providers and OFREP endpoints that normalize outputs into one report shape.
- `cargo flag-evidence` — emits `*.flagbundle.zip` with lockfile, captured traces, normalized findings, request/response fixtures, and human notes.

# What the crate should provide other people

1. **A boring default artifact for feature-flag incidents**.
2. **Provider- and backend-neutral replay** for the same evaluation scenario.
3. **Explicit context/profile locks** instead of “it worked in staging”.
4. **Reason-code and fallback visibility** so rollout mistakes are explainable.
5. **A bridge from OpenFeature abstractions to real operational debugging**.

# Persona / who it’s for

- Application-platform teams standardizing feature flags across services
- Rust backend developers integrating OpenFeature providers
- SREs and incident responders diagnosing rollout regressions
- Provider authors who need a portable behavioral test surface

# Users & user stories

- **Platform engineer**: “Show me why provider A and provider B disagree for this context.”
- **Incident responder**: “Package the exact failing evaluation scenario without shipping production logs wholesale.”
- **Provider maintainer**: “Run the same behavioral corpus against local, OFREP, and embedded evaluation paths.”
- **Experiment owner**: “Verify that tracking hooks and evaluation reasons are stable across upgrades.”

# Prior art (and why it’s insufficient)

- OpenFeature gives the abstraction and normative behavior surface.
- OFREP gives a vendor-neutral remote-evaluation protocol.
- Rust has an official SDK and increasingly real provider substrate.
- `flagd` and Rust contrib providers show that cross-runtime/provider conformance is becoming practical.

What is still missing is the **exchangeable artifact layer above those pieces**: profile locks, replay scenarios, normalized traces, and redactable incident bundles.

# Design goals

1. **Provider-neutral first** — compare behavior without forcing one backend choice.
2. **Context-honest** — make merges, defaults, and missing fields explicit.
3. **Replayable** — the same scenario should run against local, remote, and recorded providers.
4. **Incident-friendly** — capture enough evidence to debug without dumping whole application state.
5. **Spec-aware** — align with OpenFeature requirements and OFREP behavior instead of inventing a parallel model.

# MVP surface

- Minimal types: `FlagProfileLock`, `EvaluationScenario`, `EvaluationTrace`, `ProviderFinding`, `FlagBundle`
- Minimal functions:
  - `capture_evaluation()`
  - `replay_scenario()`
  - `diff_traces()`
  - `write_bundle()`
- Feature flags:
  - `ofrep-http`
  - `flagd`
  - `tracking`
  - `recording`
  - `redaction`

# Compatibility story

- Works above the Rust OpenFeature SDK instead of replacing it.
- Accepts remote OFREP-backed providers and local/in-process providers.
- Keeps provider-specific details in adapters while bundle and lockfile formats stay neutral.
- Can start with scalar and structured evaluation cases before touching streaming or exotic provider features.

# Conformance & fixtures

- Tiny fixtures for missing-context keys, fallback hits, type mismatches, disabled flags, and provider errors.
- Goldens for “same context, different reason” and “same value, different metadata/hook behavior”.
- Replay packs for local provider, OFREP HTTP, and `flagd`-backed flows.
- Redaction tests for evaluation context while preserving the structural evidence needed to reproduce bugs.

# Path to boring stability

- Stabilize lockfile, scenario DSL, and normalized trace schema before adding many provider adapters.
- Keep the crate focused on behavior capture/replay, not feature-flag authoring or serving.
- Publish a tiny public corpus of cross-provider behavior scenarios.
- Make context redaction and comparison semantics explicit early.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that run a small set of OpenFeature evaluations against a Rust provider or OFREP endpoint, normalize the results, and emit a compact `*.flagbundle.zip` capturing context requirements, values, reasons, and diffs.

# De-risk plan

1. Start with read-only evaluation capture and replay, not config management.
2. Treat evaluation-context redaction as a first-class design constraint.
3. Keep the first adapter set tiny: Rust SDK + OFREP HTTP + `flagd` path.
4. Let provider-specific findings remain attached as notes rather than warping the core schema.

# Non-goals

- Not a flag-management control plane.
- Not a new OpenFeature SDK.
- Not an experimentation analytics platform.
- Not a replacement for provider-specific admin APIs.

# Architecture & API sketch

```rust
pub struct FlagProfileLock {
    pub spec_profile: String,
    pub required_context_keys: Vec<String>,
    pub transport: TransportMode,
}

pub fn capture_evaluation(
    provider: &dyn FeatureProvider,
    scenario: &EvaluationScenario,
) -> Result<EvaluationTrace>;

pub fn diff_traces(a: &EvaluationTrace, b: &EvaluationTrace) -> TraceDiff;
```

Bundle draft: `profile.toml`, `scenarios/`, `trace.json`, `diff.json`, `context-redaction.json`, `notes.md`.

# Security / safety model

- Treat evaluation context as potentially sensitive input.
- Support redaction and hashing of user identifiers, tenant IDs, and custom attributes.
- Record transport/auth mode and adapter versions in every bundle.
- Keep bundles deterministic enough for CI and postmortems.

# Maintenance & governance plan

- Keep the core schema vendor-neutral and small.
- Version provider adapters independently where possible.
- Publish a public corpus of behavioral edge cases derived from spec requirements and real incident patterns.
- Resist drift into becoming a feature-flag product.

# Milestones

## 0.1
- scenario DSL
- provider capture
- normalized trace writer

## 0.2
- OFREP adapter
- semantic diffs
- context redaction

## 1.0
- stable `*.flagbundle.zip`
- public behavior corpus
- documented compatibility guarantees

# Open questions

- Which smallest scenario set catches the most real provider drift?
- How should hooks and tracking events be represented without overfitting one backend?
- What is the best default redaction strategy for evaluation context while preserving reproducibility?

# Sources

- OpenFeature specification: https://openfeature.dev/specification/
- OFREP reference: https://openfeature.dev/docs/reference/other-technologies/ofrep/
- OpenFeature Rust SDK: https://openfeature.dev/docs/reference/sdks/server/rust/
- flagd Rust provider docs: https://flagd.dev/providers/rust/
- Rust contrib/provider release history: https://github.com/open-feature/rust-sdk-contrib/releases
