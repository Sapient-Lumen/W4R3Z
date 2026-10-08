# Frontier salience refresh — 2026-03-22-165

This refresh reranks the top frontier after another archive pass plus fresh official Rust research.

## Broad rerank

1. **P-0484 Toolchain & Target Support Contract Kit** — still the strongest broad leverage lane because honest support claims remain fragmented across Cargo, rustup, docs.rs, target tiers, and CI practice.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — remains extremely strong because cross-language interop is now an explicit application area and still lacks shared review vocabulary.
3. **P-0120 Unsafe Contract Auditor Kit** — promoted sharply because official Rust work is now concrete about normative unsafe documentation and contract-like substrate, while everyday unsafe review still lacks a portable evidence layer.
4. **P-0036 MSRV Workspace Lab** — still near the top because dependency drift and support-floor truth keep biting real projects.
5. **P-0535 Dependency Lifecycle Transition Kit** — still high because criticality-aware dependency movement is real practice but mostly undocumented as a reviewable contract.
6. **P-0434 Sanitizer Profile & Evidence Kit** — still high because operational evidence for sanitizer use remains badly under-standardized.

## Why P-0120 moved up

The strongest new signal is that unsafe work is no longer just “some reviewers care about this.”
The official goals and safety-critical work now make unsafe documentation, contract expression, and safety evidence look like reusable ecosystem substrate.

That means the missing crate is not just another witness engine.
It is a crate that makes unsafe obligations and witness boundaries legible to *other people*.

## Anti-duplication guardrail

When a future idea says any of the following:

- “runs Miri and archives the results,”
- “documents safety contracts,”
- “shows all unsafe blocks,”
- “proves our FFI layer is okay,”
- or “tracks unsafe evidence in CI,”

first ask whether it is actually best expressed as **P-0120** plus one adjacent lane rather than as a brand-new proposal.
