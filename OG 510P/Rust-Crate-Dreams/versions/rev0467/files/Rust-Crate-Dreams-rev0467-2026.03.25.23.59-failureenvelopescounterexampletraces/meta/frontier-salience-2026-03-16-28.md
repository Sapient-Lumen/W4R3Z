# Frontier salience scan — 2026-03-16 (crate runtime handoff packs promoted as the runtime-side supportiveness lane)

This pass added a new top-level proposal: **P-0513 Crate Runtime Handoff Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a fifth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared ecosystem interop profiles), and **P-0512** (compile-time / early-failure guidance packs).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another crate picker,
- another metadata contract,
- another shared profile pack,
- another pretty error renderer,
- or a whole observability backend.

It is the boring crate that can hand other people:

- one **runtime handoff pack**,
- one **runtime-context receipt**,
- one **panic-handoff receipt**,
- one **redaction profile**,
- one **runtime-handoff check report**,
- and one **failure-shape diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0512 Crate Guidance Pack Kit**
6. **P-0513 Crate Runtime Handoff Pack Kit**
7. **P-0510 Crate Capability Contract & Interop Profile Kit**
8. **P-0511 Crate Interop Profile Pack Kit**
9. **P-0429 rustc_public Analysis Workbench Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**
11. **P-0430 Build-Std Workbench Kit**
12. **P-0478 Cargo Future-Incompat Triage Kit**
13. **P-0470 Cargo Package Review Kit**
14. **P-0451 Cfg Availability Ledger Kit**
15. **P-0011 Crate Health**

## Why P-0513 moved up

Fresh official and substrate signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces** from crates, which opens the door to runtime supportiveness as well as compile-time guidance.
- The 2025 State of Rust survey says debugging remains a meaningful productivity problem, and also says that online docs and code remain the main learning path.
- The `std::error` docs explicitly define errors as Rust’s mechanism for anticipated **runtime failure modes**.
- `Error::source()` is documented as the right way to preserve lower-level causes across abstraction boundaries.
- `std::backtrace` and `std::panic::set_hook` provide real runtime-reporting substrate, but they leave capture policy, redaction, and release-to-release support-surface review to crate authors.
- Existing ecosystem crates such as `error-stack`, `miette`, `tracing-error`, and `human-panic` prove the individual pieces are useful, but they still do not provide one maintainer-facing pack/check/redact/diff workflow.

That means the lane is both:

- **timely** — because official Rust guidance now names crate-authored supportiveness directly and debugging remains a live pain,
- and **distinct** — because the missing value is a runtime handoff contract above raw error/panic substrate and below domain-specific incident labs.

## What changed in the archive

Added:
- `proposals/crate-runtime-handoff-pack-kit.md`
- `meta/crate-runtime-handoff-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-28.md`
- `fixtures/crate-runtime-handoff-pack-kit/`
- `entries/2026-03-16-199.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first decision packs,
- producer-side capability contracts,
- shared interop profiles,
- compile-time guidance packs,
- generic report renderers,
- tracing/observability stacks,
- and domain-specific incident bundles

into one fake “supportiveness solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/std/error/index.html
- https://doc.rust-lang.org/std/error/trait.Error.html
- https://doc.rust-lang.org/std/backtrace/index.html
- https://doc.rust-lang.org/std/panic/fn.set_hook.html
- https://doc.rust-lang.org/std/error/struct.Request.html
- https://doc.rust-lang.org/beta/std/error/struct.Report.html
- https://rust-lang.github.io/rfcs/3192-dyno.html
- https://docs.rs/error-stack/latest/error_stack/
- https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
- https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
- https://docs.rs/crate/human-panic/latest
