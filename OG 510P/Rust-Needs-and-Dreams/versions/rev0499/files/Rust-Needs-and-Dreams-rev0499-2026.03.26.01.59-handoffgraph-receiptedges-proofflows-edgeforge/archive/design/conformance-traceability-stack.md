# Design: Conformance Traceability Stack (Spec Conformance + Acceptance Surface + Safety-Critical Evidence)

## Goal
Treat Rust’s growing specification, acceptance, and assurance work as one shared **Conformance Traceability Stack** instead of three adjacent conversations.

The stack is:
- [`design/spec-conformance-kit.md`](./spec-conformance-kit.md) for spec references, executable vectors, capability declarations, and conformance reports
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md) for compiler-lane and pattern-acceptance truth when implementation reality is still moving
- [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md) for coverage, dynamic-analysis, proof, and safety-case consumers that should import conformance evidence rather than restate language semantics from scratch

This is **not** a claim that these should become one mega-tool.
It is a claim that ideal Rust still lacks the bridge from specification work to attachable evidence and from attachable evidence to honest assurance conclusions.

## Why this needs synthesis now
Current Rust signals have made the missing bridge much clearer:
1. **Specification work is now operational, not aspirational.** RFC 3355 defines the specification effort as serving unsafe-code authors, safety-critical users, and tooling maintainers; the FLS was brought under rust-lang infrastructure; and the Rust project is now explicitly working on keeping it up to date sustainably.
   https://rust-lang.github.io/rfcs/3355-rust-spec.html
   https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
   https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
2. **The 2026 roadmap says safety-critical Rust depends on evidence, not just language features.** The flagship milestones explicitly pair MC/DC, normative `unsafe` documentation, safety-critical Clippy work, and FLS release cadence.
   https://rust-lang.github.io/rust-project-goals/2026/flagships.html
   https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
   https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
   https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
   https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
3. **Rust is also experimenting with a live process for pre-stable language documentation.** The experimental language-specification goal is about a nightly/reference branch with stability markers and team-integrated review. That means ideal Rust needs artifacts that can preserve “experimental text”, “official text”, and “tested behavior” as different truths.
   https://rust-lang.github.io/rust-project-goals/2026/experimental-language-specification.html
   https://rust-lang.github.io/rust-project-goals/2025h2/reference-expansion.html
4. **Formal models and executable contracts are becoming part of the ecosystem conversation.** a-mir-formality is explicitly framed as integrating with the Rust specification, and std-contract work treats safety conditions as programmatic contracts that can support runtime checks and formal verification.
   https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
   https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
5. **The archive already has the ingredients, but not the stack framing.** Spec Conformance Kit existed as a worthy standalone idea. Safety-Critical Evidence Stack already existed as an assurance band. Acceptance Surface Kit already modeled compiler-lane reality. The missing move is to connect them without flattening them.

## What each layer owns
### 1) Specification sources and experimental-spec process
Official text and proposed text should own:
- normative language/reference/FLS prose
- paragraph ids and anchors
- stability markers / experimental text
- team-review provenance
- release-cadence identity

Their question is:
> what text is authoritative, proposed, experimental, or merely descriptive?

### 2) Spec Conformance Kit
[`design/spec-conformance-kit.md`](./spec-conformance-kit.md) owns:
- pointer-based `spec-pack/v0`
- executable vectors
- implementation-capability declarations
- conformance reports and diffs

Its question is:
> which observable behavior was actually exercised against which text references, on which toolchain/runner profile?

### 3) Acceptance Surface Kit
[`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md) owns:
- stable/beta/nightly lane identity
- solver/borrow-check/pattern-specific acceptance diffs
- workaround truth
- compiler-lane profiles

Its question is:
> where is implementation reality still ahead of, behind, or differently scoped than the current conformance profile?

### 4) Safety-Critical Evidence Stack
[`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md) owns:
- unsafe-contract evidence
- criterion-aware coverage evidence
- runtime-checking lane evidence
- proof assumptions and outputs
- derived safety-case summaries

Its question is:
> after importing conformance and acceptance truth, what assurance conclusion may a reviewer honestly draw?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without reconstructing the story from prose docs, compiler tests, review threads, and certification binders:
1. Which text was in scope: stable Reference, FLS, experimental-spec text, or local rationale?
2. Which vectors and capabilities actually defined the conformance run?
3. Which outcomes were true conformance results versus compiler-lane acceptance quirks?
4. Which safety-critical consumers imported those results, and with which additional evidence lanes?
5. Which areas remained out of scope, provisional, or inconclusive?
6. Which claims are safe to attach to a release, issue, audit, or qualification dossier months later?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs a ranked execution layer, captured in:
- [`design/conformance-traceability-pilot-program.md`](./conformance-traceability-pilot-program.md)
- [`design/spec-conformance-pilot-program.md`](./spec-conformance-pilot-program.md)

That stack-level pilot program should prove the stack in this order:
1. **stable paragraph-linked core-profile lane**
2. **experimental-language-spec lane**
3. **acceptance-diff lane**
4. **unsafe-contract / safety-doc lane**
5. **release / qualification / archaeology lane**

That ordering is intentional.
The archive should not jump straight to a compiletest clone, a fake “Rust conformant” badge, or “certification in a box”.
It should first prove that Rust can publish enough traceability for narrower, reviewable claims.
The proposal-layer candidate is now [`proposals/epic-conformance-traceability-stack.md`](../proposals/epic-conformance-traceability-stack.md).

## Design principles
1. **Source text is not execution evidence.** Spec prose, vectors, and reports must remain different artifacts.
2. **Profiles beat universal claims.** `core_language`, `unsafe_basics`, `no_std`, and other narrow profiles are more credible than one giant conformance promise.
3. **Experimental text must stay explicit.** Nightly or pre-stable language-spec work should not silently inherit the authority of stable text.
4. **Acceptance and conformance are different truths.** A compiler-lane quirk or solver transition is not automatically a spec violation.
5. **Assurance imports conformance; it does not replace it.** Coverage, sanitizers, and proofs should cite the same subject and capability story instead of re-deriving semantics ad hoc.
6. **Archaeology matters.** Reports should still explain themselves after the original team, issue, and CI logs have moved on.

## What an epic contribution would look like in practice
A serious contribution here would:
- let specification work point to executable vectors without turning prose into a test harness;
- preserve stable, experimental, and implementation-specific truths without hiding the differences;
- let safety-critical consumers import conformance packs instead of re-documenting language semantics from scratch;
- attach narrow but durable evidence to releases, issue reports, and qualification workflows;
- and create a path for future language-team and toolchain work to publish traceability instead of folklore.

## Anti-goals
Do not turn this stack into:
- one compiletest replacement,
- one fake “official Rust compiler certification” badge,
- one universal safety dossier template,
- or one mega-schema that erases the difference between text, vectors, acceptance quirks, and assurance conclusions.

The stack is a **traceability boundary**, not a substitute for specification authorship, compiler review, or domain certification process.
