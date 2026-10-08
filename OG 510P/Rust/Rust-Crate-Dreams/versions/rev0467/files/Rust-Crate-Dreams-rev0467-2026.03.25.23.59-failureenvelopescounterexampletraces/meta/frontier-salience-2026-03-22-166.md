# Frontier salience refresh — 2026-03-22-166

This refresh reranks the frontier after another archive pass plus fresh official Rust documentation/tooling research.

## Broad rerank

1. **P-0484 Toolchain & Target Support Contract Kit** — still strongest because honest support claims remain fragmented across Cargo, rustup, docs.rs, target tiers, and CI practice.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — remains extremely strong because cross-language interop is explicit Rust application-area work and still lacks shared review vocabulary.
3. **P-0120 Unsafe Contract Auditor Kit** — remains unusually strong because official Rust work now treats unsafe obligations and contract expression as real ecosystem substrate.
4. **P-0036 MSRV Workspace Lab** — still near the top because version-floor truth and dependency drift keep biting real projects.
5. **P-0535 Dependency Lifecycle Transition Kit** — still high because criticality-aware dependency movement is real practice but mostly undocumented as a reviewable contract.
6. **P-0455 Doctest Extraction & Support Contract Kit** — promoted because Rust docs are still the preferred canonical reference while doctest extraction, runtool, ignore-target, and grouping substrate is now concrete enough to support a real receiver-facing contract.

## Why P-0455 moved up

The strongest new signal is that documentation examples are no longer just prose with opportunistic tests attached.
The official docs/tooling substrate now makes extraction, execution wrappers, ignore-target policy, and grouping mode concrete enough that “our docs are tested” can and should become a support contract other people can inspect.

That means the missing crate is not another docs portal.
It is a crate that makes documentation-example support and drift legible to *other people*.

## Anti-duplication guardrail

When a future idea says any of the following:

- “our docs examples run in CI,”
- “we support docs.rs,”
- “our examples work on embedded / target X,”
- “we can extract doctests,”
- or “we show docs coverage,”

first ask whether it is actually best expressed as **P-0455** plus one adjacent lane rather than as a brand-new proposal.
