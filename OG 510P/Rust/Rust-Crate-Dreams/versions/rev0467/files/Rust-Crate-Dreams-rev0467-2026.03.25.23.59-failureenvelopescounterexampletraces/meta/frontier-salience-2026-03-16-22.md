# Frontier salience scan — 2026-03-16 (lock-contention lane upgraded around exactness and optional session linkage)

This pass did not add a new top-level proposal.
It upgraded **P-0490 Cargo Lock Contention Witness Kit** into a more implementation-shaped lane by freezing the next missing support-layer artifacts: **evidence sources, exactness classes, and optional build-analysis session links**.

## Main judgment

The strongest contribution here is not another profiler, not another editor wrapper, and not another cache-governance crate.
It is the boring crate that can hand other people:

- one root-sharing report,
- one lock-wait receipt,
- one collision diagnosis,
- one mitigation plan,
- one evidence-source receipt,
- one exactness report,
- and one optional build-analysis session link.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0429 rustc_public Analysis Workbench Kit**
5. **P-0490 Cargo Lock Contention Witness Kit**
6. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
7. **P-0478 Cargo Future-Incompat Triage Kit**
8. **P-0470 Cargo Package Review Kit**
9. **P-0125 Cargo SBOM Precursor Workbench Kit**
10. **P-0471 Cargo Artifact Handoff Kit**
11. **P-0055 Cargo Workspace Toolchain Manifest Kit**
12. **P-0244 SemVer API Diff Evidence Kit**

## Why P-0490 moved up

Fresh official substrate now lines up around three sharper truths:

- Cargo’s build cache docs explicitly distinguish **target-dir** from **build-dir**.
- The March 13, 2026 build-dir-layout-v2 call says teams should test anything touching `build-dir` / `target-dir`, and says Cargo 1.91 already lets users separate intermediate build artifacts from final ones.
- Cargo’s unstable build-analysis docs now expose persisted sessions plus `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.

That means the crate can now promise something better than “I saw Cargo wait once.”
It can promise a compact bundle that says:

- which roots were in play,
- which roots were actually shared,
- what wait was observed,
- which facts came from direct observation versus normalization,
- and whether an imported Cargo session was only supporting context or part of the direct evidence lane.

## What changed in the archive

Added:
- `meta/cargo-lock-contention-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-22.md`
- `fixtures/cargo-lock-contention-witness-kit/evidence-source.receipt.schema.json`
- `fixtures/cargo-lock-contention-witness-kit/exactness.report.schema.json`
- `fixtures/cargo-lock-contention-witness-kit/build-analysis-session.link.schema.json`
- scenario families for imported-session context and build-dir-layout-v2 manual review
- `entries/2026-03-16-193.md`

Updated:
- `proposals/cargo-lock-contention-witness-kit.md`
- `fixtures/cargo-lock-contention-witness-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- rebuild explanation,
- historical build-analysis warehousing,
- compile-time-deps parity,
- build-dir consumer migration,
- or target-dir lease coordination

into one fake “Cargo performance doctor” crate.

## Sources

- Call for Testing: Build Dir Layout v2: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo unstable docs (`build-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- rust-analyzer FAQ: https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
