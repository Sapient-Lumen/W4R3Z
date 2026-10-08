---
id: P-0456
title: Formality Counterexample Bridge Kit — rustc/a-mir-formality/MiniRust witness bundles and minimized divergence cases for language-model validation
status: idea
domains: [formal-methods, compiler, language, mir, semantics, testing, fuzzing, research]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
  - https://github.com/rust-lang/a-mir-formality
  - https://github.com/minirust/minirust
  - https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
---

# Problem

Rust is investing in a-mir-formality as a model that should remain recognizably close to the compiler while helping validate type safety, and the current project goal explicitly aims to integrate function bodies via MiniRust, add a MIR type checker, and model key parts of Polonius. The long-term payoff is enormous — but the day-to-day workflow for comparing model behavior against rustc is still underbuilt.

Today, contributors and researchers often need to answer questions like:

- “Does rustc accept this program because the model is incomplete, or because the compiler is buggy?”
- “Can we package this divergence into a minimized case another contributor can replay?”
- “Which assumptions, feature gates, and model scopes were in force when this counterexample was found?”
- “Can we hand one compact witness bundle between compiler engineers, language designers, and formal-methods people?”

The missing crate is not another formal model.

The missing crate is a **counterexample bridge** that turns model/compiler divergences into portable artifacts.

# What it provides

- `formality-profile.toml` — pins rustc/toolchain versions, model versions, enabled scopes, and comparison policy.
- `formality-cases/` — small source programs or MIR-shaped fixtures used for comparison.
- `formality.results.json` — normalized outcome records from rustc, a-mir-formality, and optional operational-model consumers.
- `formality.diff.json` — categories such as `rustc_accepts_model_rejects`, `model_accepts_rustc_rejects`, `ub_classification_drift`, `out_of_scope`, and `needs_manual_review`.
- `formality.assumptions.json` — explicit record of feature gates, model limitations, unsupported constructs, and operational semantics assumptions.
- `cargo formality-bridge check` — run one case corpus across configured engines.
- `cargo formality-bridge reduce` — minimize a divergence into a compact witness case.
- `cargo formality-bridge bundle` — emit a portable counterexample bundle for issues, papers, or design review.
- `*.formalitybundle.zip` — shareable artifact containing cases, results, diffs, and scope notes.

# What the crate should provide other people

1. **A boring divergence artifact** for formal-model versus compiler discussions.
2. **A scope-and-assumptions ledger** so counterexamples are interpretable later.
3. **A reduced-case handoff bundle** for compiler teams, language teams, and researchers.
4. **A bridge** between static and operational model work as MiniRust integration grows.
5. **A teaching aid** for explaining where a model is intentionally incomplete versus unexpectedly divergent.

# Persona / who it’s for

- compiler contributors
- language designers
- formal-methods and PL researchers
- advanced tool authors using formal Rust models
- educators teaching Rust semantics at the MIR/type-system boundary

# Users & user stories

- **Compiler contributor**: “Bundle a minimized program showing a rustc-vs-model disagreement and the exact assumptions in force.”
- **Researcher**: “Compare one corpus under a-mir-formality and an operational semantics layer, then publish the witness bundle with the paper.”
- **Language designer**: “Review whether a divergence is a compiler bug, a model gap, or an intended out-of-scope case.”
- **Educator**: “Use compact witness cases to explain how the model differs from implementation detail.”

# Prior art (and why it’s insufficient)

- a-mir-formality is becoming a serious official modeling effort.
- MiniRust exists as a precise operational semantics project and is explicitly relevant to future integration.
- Individual repositories and issues can store examples, but they do not define a shared, boring counterexample artifact.

What remains missing is a **portable witness / assumptions / reduction layer** above raw repositories and ad hoc issue text.

# Design goals

1. **Assumption-explicit** — model scope and unsupported features must be first-class.
2. **Reduction-friendly** — minimized counterexamples are the default currency.
3. **Multi-engine** — keep room for rustc, a-mir-formality, MiniRust-like consumers, and future adapters.
4. **Conservative** — distinguish true divergence from “out of current model scope”.
5. **Research-to-maintainer bridge** — artifacts should be legible outside the originating repo.

# MVP surface

- Minimal types: `FormalityProfile`, `FormalityCase`, `EngineResult`, `FormalityDiff`, `AssumptionsLedger`, `FormalityBundle`
- Minimal functions:
  - `run_case_corpus()`
  - `normalize_results()`
  - `classify_divergence()`
  - `reduce_case()`
  - `write_bundle()`
- Feature flags:
  - `rustc`
  - `amf`
  - `minirust`
  - `serde`
  - `cargo`

# Compatibility story

- Starts as a wrapper around explicit tool invocations and model outputs; it does not reimplement any semantics.
- Must allow “out of scope” to be a legitimate outcome.
- Can begin with a rustc + a-mir-formality comparison before deeper operational-model adapters mature.
- Should preserve exact repo/tool revisions and feature-gate assumptions in every receipt.

# Conformance & fixtures

- Small fixtures for trait reasoning, MIR type checking, borrow-checking, and const-eval-adjacent cases as model support grows.
- Goldens for “rustc accepts, model rejects”, “model accepts, rustc rejects”, “both reject but disagree on reason class”, and “out of scope”.
- A minimized witness corpus suitable for issue trackers and design discussions.
- Example paper/review bundles with notes and caveats.

# Path to boring stability

- Stabilize the assumptions and diff schema before adding many engines.
- Start with one comparison axis: rustc versus a-mir-formality.
- Keep reduction deterministic and review-friendly.
- Treat operational semantics adapters as optional until the core workflow proves useful.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A library and cargo subcommand that run a small corpus through rustc and a-mir-formality, classify divergences conservatively, record scope assumptions, and export a minimized witness bundle.

# De-risk plan

1. Start with rustc + a-mir-formality only.
2. Treat unsupported constructs as explicit `out_of_scope`, not failures.
3. Keep the first reduction pipeline tiny and deterministic.
4. Validate usefulness on one real compiler-model disagreement before widening scope.

# Non-goals

- Not a new proof assistant or theorem prover.
- Not a replacement for a-mir-formality or MiniRust.
- Not a promise to classify every divergence automatically.
- Not a generic fuzzing engine for all of Rust.

# Architecture & API sketch

```rust
pub enum DivergenceClass {
    RustcAcceptsModelRejects,
    ModelAcceptsRustcRejects,
    ReasonClassDrift,
    OutOfScope,
    Unknown,
}

pub fn run_case_corpus(profile: &FormalityProfile, corpus: &Path) -> Result<FormalityRunSet>;
pub fn classify_divergence(rustc: &EngineResult, model: &EngineResult) -> DivergenceClass;
pub fn reduce_case(case: &FormalityCase, diff: &FormalityDiff) -> Result<FormalityCase>;
pub fn write_bundle(bundle: &FormalityBundle, out: &Path) -> Result<()>;
```

Bundle draft: `formality-profile.toml`, `cases/`, `formality.results.json`, `formality.diff.json`, `formality.assumptions.json`, `notes.md`.

# Security / safety model

- Preserve exact engine revisions and feature gates in every bundle.
- Support redaction of local file paths and proprietary test names.
- Never conflate unsupported scope with validated correctness.
- Keep minimized witnesses deterministic and inspectable.

# Maintenance & governance plan

- Track a-mir-formality scope changes closely.
- Keep the core bundle schema adapter-neutral.
- Maintain a small public corpus of representative divergence cases.
- Publish guidance for interpreting “model gap” versus “compiler bug suspicion”.

# Milestones

## 0.1
- rustc + a-mir-formality comparison
- assumptions ledger
- bundle export

## 0.2
- reduction helpers
- optional MiniRust metadata adapter
- richer divergence classes

## 1.0
- stable bundle schema
- curated public corpus
- issue/research-review adapters

# Open questions

- What is the smallest useful divergence taxonomy?
- How much reduction logic belongs in core versus engine-specific adapters?
- Which corpus families best expose meaningful model/compiler drift early?

# Sources

- a-mir-formality goal: https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- `rust-lang/a-mir-formality`: https://github.com/rust-lang/a-mir-formality
- `minirust/minirust`: https://github.com/minirust/minirust
- const-trait goal (shows formalization pressure moving through a-mir-formality too): https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
