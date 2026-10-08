---
id: P-0422
title: Common Expression Language (CEL) Conformance & Portability Kit — env locks, extension packs, and explainable evaluation diffs
status: idea
domains: [language, policy, config, portability, conformance, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://cel.dev/overview/cel-overview
  - https://github.com/google/cel-spec
  - https://github.com/google/cel-spec/blob/master/tests/simple/testdata/basic.textproto
  - https://github.com/cel-rust/cel-rust
  - https://github.com/cel-rust/cel-rust/releases
---

# Problem

CEL is already a real embedded language with a formal spec, a growing conformance story, and a live Rust implementation. That means the remaining pain is no longer “can Rust parse and execute expressions at all?”

The hard parts now sit above the parser:

- **which CEL revision and macro behavior a deployment assumes**,
- **which host functions, variables, and opaque types are available**,
- **which expressions are expected to be portable across runtimes and which are host-specific**,
- **which result differences are caused by environment drift versus expression drift**,
- and **how to hand another team a reproducible explanation for an authorization, routing, or validation decision.**

The missing Rust contribution is a **conformance-and-portability kit** that treats CEL expressions as artifacts with pinned type environments, extension packs, evaluation receipts, and portability classifications.

# What it provides

- `cel.lock` — pins CEL language/conformance baseline, enabled macros, numeric/string semantics assumptions, and host extension packs.
- `env.schema.json` — declares variables, types, opaque values, and functions expected by an expression bundle.
- `portability-class.json` — marks expressions as `strict-core`, `core-plus-macros`, `host-extension`, or `non-portable`.
- `eval.receipt.json` — records input shape, environment digest, selected overloads, result, and diagnostics.
- `conformance.corpus/` — fixture pack for parser/evaluator/host-extension behavior.
- `cargo cel-evidence` — emits `*.celbundle.zip` with lockfile, env schema, expressions, receipts, and portability report.

# What the crate should provide other people

1. **A boring handoff artifact for CEL-backed decisions**.
2. **A way to separate portable CEL from deployment-local CEL**.
3. **Explainable diffs when runtime upgrades or extension packs change behavior**.
4. **A Rust-native conformance core** that gateways, policy engines, and config platforms can all reuse.
5. **A stable review surface** for embedded-expression risk instead of “read the source and hope.”

# Persona / who it’s for

- platform and gateway engineers embedding CEL in configs
- authorization / policy teams using CEL-like conditions
- API and admission-control tool builders
- teams migrating CEL expressions between runtimes or vendors

# Users & user stories

- **Policy engineer**: “Tell me whether this rule stopped matching because the expression changed, the environment changed, or the runtime changed.”
- **Platform owner**: “Ship one bundle that proves the exact variables, functions, and CEL behavior behind a rollout decision.”
- **SDK/tool author**: “Reuse one env-lock format instead of inventing a custom ‘expression context’ schema.”
- **Security reviewer**: “See which expressions rely on host-only functions or opaque values before approving them.”

# Prior art (and why it’s insufficient)

- CEL has a formal language definition and conformance suite.
- The `cel` / `cel-rust` ecosystem provides a Rust interpreter.
- Many systems embed CEL-like rules for filters, routing, validation, and authorization.

What Rust still lacks is a **portable artifact layer** that pins environment assumptions, host extensions, and evaluation receipts in a form other tools can inspect and compare.

# Design goals

1. **Spec-honest** — distinguish CEL core semantics from runtime-local extension behavior.
2. **Environment-explicit** — variables, types, and functions must be pinned, not implicit.
3. **Replay-first** — a past decision must be reproducible from one bundle.
4. **Portability-aware** — classify which expressions should travel safely across engines.
5. **Small-core-first** — avoid turning the crate into yet another full CEL implementation.

# MVP surface

- Minimal types: `CelLock`, `EnvSchema`, `ExtensionPack`, `EvalReceipt`, `PortabilityClass`, `CelBundle`
- Minimal functions:
  - `capture_env()`
  - `classify_expression()`
  - `evaluate_with_receipt()`
  - `diff_receipts()`
  - `write_bundle()`
- Feature flags:
  - `core`
  - `macros`
  - `opaque`
  - `protobuf`
  - `json`

# Compatibility story

- Treats the official CEL spec and conformance corpus as the normative core.
- Treats host functions, opaque values, and deployment-local types as **extension packs**, not silent defaults.
- Supports bundling results from existing evaluators rather than forcing adoption of one runtime.
- Keeps authorization/routing products out of scope.

# Conformance & fixtures

- Goldens for parser acceptance/rejection, macro behavior, numeric edge cases, string/bytes handling, and null/unknown propagation.
- Tiny corpora for `strict-core` versus `host-extension` portability classification.
- Receipts showing the same expression under changed variable schemas or function overloads.
- Redacted example bundles safe for CI and bug reports.

# Path to boring stability

- Stabilize `cel.lock`, `env.schema.json`, and `eval.receipt.json` before adding lots of adapters.
- Start with offline capture and diffing around already-executed decisions.
- Keep evaluator integration thin.
- Treat host extensions as data packs, not compile-time sprawl.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin a CEL environment, classify portability, execute a small expression corpus, emit receipts, and explain why two runs diverged.

# De-risk plan

1. Start from official CEL conformance fixtures plus a few Rust-specific receipts.
2. Keep the core schema evaluator-agnostic.
3. Treat protobuf/opaque support as optional overlays.
4. Publish a tiny public corpus for host-extension drift.

# Non-goals

- Not a new general-purpose policy engine.
- Not a replacement for existing CEL runtimes.
- Not a secrets-aware decision service.
- Not a generic rules UI.

# Architecture & API sketch

```rust
pub struct CelLock {
    pub cel_spec: String,
    pub conformance_baseline: String,
    pub enabled_macros: Vec<String>,
    pub extension_pack_digests: Vec<String>,
}

pub fn capture_env(env: &HostEnv) -> EnvSchema;
pub fn classify_expression(src: &str, env: &EnvSchema) -> PortabilityClass;
pub fn evaluate_with_receipt(src: &str, env: &EnvSchema, input: &serde_json::Value) -> Result<EvalReceipt>;
pub fn diff_receipts(a: &EvalReceipt, b: &EvalReceipt) -> EvalDiff;
pub fn write_bundle(bundle: &CelBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `cel.lock`, `env.schema.json`, `expressions/`, `receipts/`, `portability-report.json`, `diagnostics.ndjson`, `notes.md`.

# Security / safety model

- Separate safe-to-share environment schemas from sensitive runtime values.
- Support redaction of input payloads while preserving structural hashes.
- Distinguish spec-core behavior from host-defined behavior to reduce false portability claims.
- Preserve enough provenance to investigate decision drift without leaking secrets.

# Maintenance & governance plan

- Track official CEL spec and conformance-suite revisions explicitly.
- Keep extension packs data-driven and versioned.
- Maintain a small public fixture corpus that exercises portability boundaries.
- Avoid engine-specific favoritism in the core schema.

# Milestones

## 0.1
- `cel.lock`
- environment schema
- offline evaluation receipt writer

## 0.2
- portability classifier
- receipt diffing
- redacted example corpus

## 1.0
- stable `*.celbundle.zip`
- conformance-suite import helpers
- CI-friendly drift gates

# Open questions

- What is the smallest portable environment schema that still explains host-extension drift?
- Which macro and overload details belong in the receipt versus derived diagnostics?
- How should unknown/partial evaluation states be encoded across engines?

# Sources

- CEL overview: https://cel.dev/overview/cel-overview
- CEL spec repository: https://github.com/google/cel-spec
- Example official conformance tests: https://github.com/google/cel-spec/blob/master/tests/simple/testdata/basic.textproto
- Rust CEL implementation: https://github.com/cel-rust/cel-rust
- Recent Rust CEL release activity: https://github.com/cel-rust/cel-rust/releases
