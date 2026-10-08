# Frontier salience refresh — 2026-03-22 (178)

## Main rerank for this broad pass

1. **P-0484 Toolchain & Target Support Contract Kit** — still the strongest structural gap because cross-compilation, target readiness, docs posture, and host-vs-target exercise truth remain scattered even as upstream substrate improves.
2. **P-0011 Crate Health Contract Kit** — promoted again because the sustainability and support-intent story now matters as much as raw technical capability.
3. **P-0535 Dependency Lifecycle Transition Kit** — remains unusually leverage-heavy because safety-critical, embedded, and long-lived teams keep needing a reusable playbook for when to adopt, wrap, pin, fork, internalize, or replace crates.
4. **P-0120 Unsafe Contract Auditor Kit** — remains central because 2026 safety-critical work makes normative unsafe obligations and witness honesty harder to ignore.
5. **P-0532 Async Runtime Assurance Profile Kit** — promoted because async adoption is still strategically important while runtime lock-in, shutdown truth, and qualification posture remain under-specified.
6. **P-0486 Debuggability Support Contract Kit** — promoted because debugging remains a named productivity pain and the Rust project is now actively surveying the problem.
7. **P-0536 Crate Knowledge Pack Kit** — new entrant because docs are still Rust’s canonical reference while more learning and support activity is clearly shifting toward machine-mediated tooling.
8. **P-0490 Cargo Lock Contention Witness Kit** — remains high because build-root and shared-lock friction is now operational enough to package cleanly.
9. **P-0469 Cargo Rebuild Explanation Kit** — remains high because compile-time pain is still the universal productivity tax and developers still need receiver-facing causality instead of timing folklore.
10. **P-0431 Public Dependency Boundary Kit** — remains top-tier because public/private dependency stabilization is now a flagship supply-chain lane rather than a side experiment.

## Why this rerank changed

Fresh upstream signals line up unusually well:

- the 2025 survey still says online docs are the preferred canonical reference, while productivity limits still center resource usage and compile-time friction;
- the March 2026 Rust challenges write-up says experts still hit async complexity, certification gaps, embedded ecosystem maturity issues, and ecosystem-navigation pain;
- the compiler-performance survey says incremental rebuilds and understanding why builds are slow are central workflow problems;
- the debugging survey says the project still lacks stellar debugger/version/OS coverage, async debugging support, and reliable expression evaluation;
- the 2026 flagships explicitly prioritize supply-chain, safety-critical, and Cargo-facing work;
- and the Rust Foundation’s 2026–2028 strategy makes stable infrastructure and sustainable maintenance first-class ecosystem priorities.

Together these make one conclusion sharper:

> The next truly worthy Rust crates are disproportionately **boring support contracts**, not just more wrappers around existing substrate.

## Why P-0536 entered the frontier

The archive already had strong docs-facing lanes:

- P-0051 for rustdoc JSON normalization,
- P-0472 for docs.rs parity,
- P-0476 for docs coverage review,
- and P-0455 for doctest extraction/support truth.

What remained missing was the **joined handoff artifact**:
a crate-shaped bundle that another human, search engine, or assistant can consume without scraping HTML docs, guessing example authority, or confusing hosted docs presence with canonical entrypoint truth.

That is why **P-0536 Crate Knowledge Pack Kit** deserves a real lane instead of being dissolved into yet another docs portal, JSON parser, or “chat with your crate” gimmick.

## Broad synthesis rule after this pass

When doing a broad “what is Rust still missing?” scan, default to:

1. reranking a structural lane,
2. deepening a support-contract lane,
3. or adding exactly one new lane that joins already-real substrate into a receiver-facing artifact.

Do **not** reward ideas merely for being flashy, AI-shaped, or large in scope.

## Guardrail

Do not add:

- another generic Rust docs portal unless it clearly beats **P-0536 + P-0472 + P-0476 + P-0051**;
- another generic build dashboard unless it clearly beats **P-0490 + P-0469**;
- another “safe async runtime chooser” without a sharper contract than **P-0532**;
- or another crate-quality score without a clearer stewardship contract than **P-0011 + P-0535**.
