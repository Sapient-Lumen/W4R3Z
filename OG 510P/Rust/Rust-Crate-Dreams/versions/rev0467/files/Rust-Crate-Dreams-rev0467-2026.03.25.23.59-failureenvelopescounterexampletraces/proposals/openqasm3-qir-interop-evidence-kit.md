---
id: P-0426
title: OpenQASM 3 + QIR Interop & Evidence Kit — program locks, lowering receipts, and target-profile diffs
status: idea
domains: [quantum, compiler, ir, interoperability, evidence, hpc]
last_reviewed: 2026-03-06
evidence:
  - https://openqasm.com/versions/3.0/intro.html
  - https://openqasm.com/versions/3.0/grammar/index.html
  - https://github.com/Qiskit/openqasm3_parser
  - https://www.qir-alliance.org/projects/
  - https://github.com/qir-alliance/qir-spec
  - https://crates.io/crates/qir-qis
---

# Problem

Quantum toolchains are finally rich enough that the harder problem is now **handoff between language-level programs and profile-constrained IR**, not just syntax trees in isolation.

OpenQASM 3 gives an expressive language surface with classical control and timing-oriented constructs. QIR gives an LLVM-based interoperability target with profiles and lowering tools. But practitioners still lack a boring default for:

- **which OpenQASM 3 features a source actually uses**,
- **which includes/gate libraries and semantic assumptions were in force**,
- **which target profile or backend constraints shaped the lowering to QIR**,
- **which constructs were lowered faithfully, approximated, rewritten, or rejected**,
- and **how to compare two “equivalent” quantum programs after compilation choices diverge.**

Rust already has real parser pieces and emerging QIR-targeting crates. The missing contribution is an **interop-and-evidence kit** that turns source programs, semantic assumptions, target profiles, and lowering outcomes into one portable artifact.

# What it provides

- `quantum.lock` — pins OpenQASM revision, include/library assumptions, target QIR profile, and backend constraint pack.
- `source.receipt.json` — records parsed features, includes, gate declarations, extern usage, and semantic diagnostics.
- `lowering.receipt.json` — records source-to-QIR mapping decisions, rejected constructs, rewrites, and target constraints.
- `profile.diff.json` — explains why a program fits one target profile and not another.
- `interop.corpus/` — tiny programs for classical control, timing, externs, includes, and profile-sensitive lowering.
- `cargo quantum-evidence` — emits `*.quantumbundle.zip` with source, diagnostics, receipts, and target-profile notes.

# What the crate should provide other people

1. **A boring handoff artifact between language-level and IR-level quantum tooling**.
2. **Explainable lowering receipts** instead of opaque compile failures.
3. **Target-profile diffs** that help one source target multiple machines or compiler paths.
4. **A Rust-native evidence core** for compiler teams, researchers, and platform integrators.
5. **A trustworthy place to record loss and approximation**, not silently hide it.

# Persona / who it’s for

- quantum compiler and transpiler authors
- tool builders working on hybrid quantum-classical pipelines
- researchers comparing source-language and IR behavior
- platform teams targeting multiple quantum backends

# Users & user stories

- **Compiler engineer**: “Show which OpenQASM constructs were lowered directly and which required profile-specific rewrites.”
- **Researcher**: “Package one source program plus target-profile receipts so another lab can reproduce the same compilation outcome.”
- **Platform integrator**: “Compare two target profiles and see why the same source passes one but fails another.”
- **Tool builder**: “Reuse one portable bundle schema instead of inventing a custom compiler-debug format.”

# Prior art (and why it’s insufficient)

- OpenQASM 3 has an official language specification and grammar.
- QIR has an official specification and profile-oriented ecosystem.
- Rust already has parser pieces and QIR-related crates.

What Rust still lacks is a **portable artifact layer** that connects source semantics, target-profile assumptions, and lowering decisions in a form other tools can inspect and compare.

# Design goals

1. **Language/IR boundary explicitness** — source semantics and IR semantics must remain distinguishable.
2. **Profile-honest** — target constraints must be pinned, not hand-waved.
3. **Loss-visible** — rewrites, approximations, and unsupported constructs must be reported explicitly.
4. **Compiler-neutral** — the bundle should survive multiple lowering pipelines.
5. **Research-friendly** — small enough to support papers, corpora, and CI.

# MVP surface

- Minimal types: `QuantumLock`, `SourceReceipt`, `LoweringReceipt`, `ProfileDiff`, `QuantumBundle`
- Minimal functions:
  - `inspect_openqasm()`
  - `capture_target_profile()`
  - `record_lowering()`
  - `diff_profiles()`
  - `write_bundle()`
- Feature flags:
  - `openqasm3`
  - `qir`
  - `profiles`
  - `timing`
  - `externs`

# Compatibility story

- Treats OpenQASM 3 source and QIR target as distinct layers, not one merged ontology.
- Supports capture from existing parsers and lowerers.
- Treats target profiles as pinned overlays, not implicit backend magic.
- Keeps execution/simulation backends out of the portable core.

# Conformance & fixtures

- Tiny source programs for includes, classical control, extern declarations, timing-sensitive constructs, and backend-sensitive rewrites.
- Goldens for “fits generic profile / fails target profile” explanations.
- Corpora comparing source-feature usage against allowed profile subsets.
- Receipts that distinguish parser success, semantic success, and lowering success.

# Path to boring stability

- Stabilize `quantum.lock`, `source.receipt.json`, and `lowering.receipt.json` before broad backend support.
- Start with offline compiler evidence, not execution traces.
- Keep profile packs and backend adapters separate.
- Resist drift into becoming a whole quantum SDK.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 23/30**

# Minimum lovable MVP

A Rust library and CLI that inspect one OpenQASM 3 program, capture one target profile, record one lowering attempt to QIR, and emit a compact evidence bundle explaining the outcome.

# De-risk plan

1. Start with parser and profile receipts before attempting rich lowering comparisons.
2. Keep QIR target information data-driven and profile-oriented.
3. Focus on explainability rather than “best” compilation.
4. Publish a tiny public corpus of profile-sensitive programs.

# Non-goals

- Not a full quantum compiler.
- Not a simulator or hardware runtime.
- Not a language server.
- Not a general LLVM toolkit.

# Architecture & API sketch

```rust
pub struct QuantumLock {
    pub openqasm_revision: String,
    pub include_pack_digest: Option<String>,
    pub qir_profile: String,
    pub target_constraints_digest: String,
}

pub fn inspect_openqasm(src: &str) -> Result<SourceReceipt>;
pub fn capture_target_profile(profile: &TargetProfile) -> QuantumLock;
pub fn record_lowering(src: &SourceReceipt, target: &TargetProfile) -> Result<LoweringReceipt>;
pub fn diff_profiles(a: &TargetProfile, b: &TargetProfile) -> ProfileDiff;
pub fn write_bundle(bundle: &QuantumBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `quantum.lock`, `source.qasm`, `source.receipt.json`, `lowering.receipt.json`, `profile.diff.json`, `diagnostics.ndjson`, `notes.md`.

# Security / safety model

- Support redaction of proprietary gate libraries and include packs while preserving digests.
- Clearly mark inferred lowering explanations versus directly observed compiler diagnostics.
- Keep target-profile assumptions explicit so “successful compile” claims are not over-generalized.
- Separate research/benchmark metadata from source-language and IR artifacts.

# Maintenance & governance plan

- Track official OpenQASM 3 and QIR ecosystem revisions explicitly.
- Keep profile packs as versioned data overlays.
- Maintain a small fixture corpus focused on boundary constructs and unsupported features.
- Avoid tying the core schema to one quantum vendor or compiler stack.

# Milestones

## 0.1
- `quantum.lock`
- source receipt
- profile capture

## 0.2
- lowering receipt
- profile diffing
- redacted example corpus

## 1.0
- stable `*.quantumbundle.zip`
- importers for multiple lowering pipelines
- CI-friendly profile-compatibility gates

# Open questions

- What is the smallest common schema for lowering receipts across different compilers?
- Which source-language constructs require dedicated loss categories rather than generic “unsupported” findings?
- How much target-profile detail can be made portable without becoming backend-specific noise?

# Sources

- OpenQASM 3 introduction: https://openqasm.com/versions/3.0/intro.html
- OpenQASM 3 official grammar: https://openqasm.com/versions/3.0/grammar/index.html
- Rust OpenQASM 3 parser work: https://github.com/Qiskit/openqasm3_parser
- QIR Alliance projects overview: https://www.qir-alliance.org/projects/
- QIR specification repository: https://github.com/qir-alliance/qir-spec
- Example Rust-facing QIR tooling crate: https://crates.io/crates/qir-qis
