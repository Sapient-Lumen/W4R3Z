# Frontier salience update — 2026-03-24 (231)

This pass deepened the archive around **supportive surfaces**, **first-release bundles**, and **hard-domain adoption ladders**.
It still does **not** justify a major salience rerank.

## Main judgment

The strongest ecosystem-worthy missing crates are still mostly **control-plane crates** that help other people:
- choose foundational crates,
- retrieve pinned crate knowledge,
- debug real systems,
- understand async/runtime semantics,
- survive docs/build drift,
- migrate dependencies,
- and verify target/support truth.

What changed is the practical emphasis.
The archive should now treat **supportive, cited, machine-usable packet surfaces** as part of the core product for top-ranked crates rather than a later documentation polish step.

## Salience board

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0538 Concurrency Contract Kit**
4. **P-0472 Docs.rs Build Parity & Evidence Kit**
5. **P-0535 Dependency Lifecycle Transition Kit**
6. **P-0489 Cargo Build-Dir Consumer Transition Kit**
7. **P-0484 Toolchain & Target Support Contract Kit**
8. **P-0536 Crate Knowledge Pack Kit**
9. **P-0058 Native Deps Kit**
10. **P-0046 Buildscript UX Kit**
11. **P-0537 Compile Iteration Feedback Kit**
12. **P-0125 Cargo SBOM Precursor Workbench Kit**

## Practical queue

1. **P-0509** — review packets and scenario packs
2. **P-0536** — pinned citation + knowledge packs for those packets
3. **P-0486** — debug capability packets for the same receiver workflows
4. **P-0472** — docs.rs parity doctor and hosted/local gap bundles
5. **P-0489** — dual-support transition support
6. **P-0535** — lifecycle / off-ramp packets
7. **P-0484** — hard-domain target/support truth
8. **P-0058** — native prerequisite / ABI provenance for offline and mixed-language stacks

## What changed

### 1. Knowledge-pack work moved closer to the front of the practical queue

The 2025 survey still says online documentation is the preferred canonical reference.
Docs.rs now hosts structured rustdoc JSON.
And the December 2025 Vision Doc write-up explicitly says crates need more **supportive** tooling rather than only efficient abstractions.

That makes **P-0536** more central to the near-term build order even without a big salience rerank.
Pathfinder packets need pinned, cited, machine-usable support to stay trustworthy.

### 2. Hard-domain readiness should now be read as an adoption ladder, not a yes/no support claim

Safety-critical users still report that tooling and certification support thins out fast.
Embedded users still have different resource and support constraints.
Air-gapped, mixed-language, and native-heavy teams have their own prerequisite and provenance burdens.

So future crate proposals should say which adoption tier they support, not just whether they “support the domain.”

### 3. Sector breadth still matters, but mostly through scenario packs

The archive should keep widening scenario coverage across strange and demanding domains.
But it should do so through pathfinder scenarios, support packets, and evidence bundles before promoting more new top-level lanes.

## Watchlist below the current frontier

These still look important enough to watch as scenario families, but not yet strong enough to outrank the current control-plane board:

1. **local-first conflict evidence**
2. **robotics / digital-twin control-vs-ops boundary kits**
3. **geospatial provenance and loss accounting**
4. **media timing / transcoding support contracts**
5. **air-gapped enterprise build + native support bundles**
6. **open-table / lakehouse interop evidence kits**

Guardrail:
- widen the scenario catalog,
- but keep the control-plane queue in front.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
