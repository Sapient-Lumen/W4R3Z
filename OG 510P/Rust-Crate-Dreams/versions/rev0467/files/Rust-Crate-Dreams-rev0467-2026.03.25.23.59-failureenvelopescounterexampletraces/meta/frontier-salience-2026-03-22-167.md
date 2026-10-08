# Frontier salience refresh — 2026-03-22-167

This refresh reranks the frontier after another archive pass plus fresh official unsafe/safety-critical research.

## Broad rerank

1. **P-0484 Toolchain & Target Support Contract Kit** — still strongest because honest support claims remain fragmented across Cargo, rustup, docs.rs, target tiers, and CI practice.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — remains extremely strong because cross-language interop is explicit Rust application-area work and still lacks shared review vocabulary.
3. **P-0120 Unsafe Contract Auditor Kit** — remains unusually strong because official Rust work now treats unsafe obligations and contract expression as real ecosystem substrate.
4. **P-0036 MSRV Workspace Lab** — still near the top because version-floor truth and dependency drift keep biting real projects.
5. **P-0535 Dependency Lifecycle Transition Kit** — still high because criticality-aware dependency movement is real practice but mostly undocumented as a reviewable contract.
6. **P-0460 Unsafe Field Invariant Ledger Kit** — promoted because the field-carried-invariant problem is now explicit in official Rust planning while the ecosystem still lacks a receiver-facing contract for field authority and mutator trust.
7. **P-0455 Doctest Extraction & Support Contract Kit** — remains high because docs are still canonical and example-support truth is finally inspectable.

## Why P-0460 moved up

The strongest new signal is that Rust’s unsafe story is getting more specific about **where invariants live**, not just where `unsafe` blocks appear.
The unsafe-fields goal says invariant-bearing fields should be denoted explicitly and uses that could violate those invariants should require `unsafe` context. The std-contracts goal simultaneously pushes invariants toward machine-readable contract expression, while the 2026 flagships elevate normative unsafe documentation as shared safety-critical substrate.

That means the missing crate is not another generic unsafe inventory tool.
It is a crate that makes **field authority**, **mutation lanes**, **constructor trust**, and **witness scope** legible to other people.

## Anti-duplication guardrail

When a future idea says any of the following:

- “the crate documents its invariants,”
- “unsafe blocks are all commented,”
- “Miri passes,”
- “safe helpers preserve the invariant,”
- or “future unsafe fields will solve this,”

first ask whether it is actually best expressed as **P-0460** plus one adjacent lane rather than as a brand-new proposal.
