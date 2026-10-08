# Frontier salience scan — 2026-03-16 (crate-authored guidance packs promoted as a receiver-facing supportiveness lane)

This pass added a new top-level proposal: **P-0512 Crate Guidance Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a fourth distinct lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), and **P-0511** (shared ecosystem interop profiles).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another crate picker,
- another metadata contract,
- another shared interop profile,
- or another terminal diagnostic renderer.

It is the boring crate that can hand other people:

- one **guidance pack**,
- one **compile-guidance receipt**,
- one **recovery-recipe manifest**,
- one **guidance-check report**,
- and one **support-surface diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0512 Crate Guidance Pack Kit**
6. **P-0510 Crate Capability Contract & Interop Profile Kit**
7. **P-0511 Crate Interop Profile Pack Kit**
8. **P-0429 rustc_public Analysis Workbench Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0430 Build-Std Workbench Kit**
11. **P-0478 Cargo Future-Incompat Triage Kit**
12. **P-0470 Cargo Package Review Kit**
13. **P-0451 Cfg Availability Ledger Kit**
14. **P-0484 Toolchain & Target Support Contract Kit**
15. **P-0011 Crate Health**

## Why P-0512 moved up

Fresh official Rust signals line up around five sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces** — better diagnostics and guidance from crates — as part of Rust’s extensibility story.
- That same work says crates currently do not benefit from the same kind of supportiveness Rust has built into compiler diagnostics, and it specifically points to proc-macro-like DSL surfaces as one place that matters.
- The 2025 State of Rust survey says online documentation is still the preferred canonical reference and studying the code itself comes next, which means crate support surfaces remain a central learning path.
- Rust 1.78 stabilized the `#[diagnostic]` namespace and `#[diagnostic::on_unimplemented]`, and the Reference now documents `diagnostic::do_not_recommend` as another crate-facing diagnostic hook.
- RFC 3368 exists precisely because trait-heavy crates can emit large, incomprehensible errors and authors need a way to improve them; but the RFC and Reference still do not provide a maintainer-facing pack/check/diff workflow.

That means the lane is both:

- **timely** — because official Rust guidance now names crate-authored supportiveness directly,
- and **distinct** — because the missing value is a receiver-facing guidance workflow above raw compiler hooks and below docs portals or crate selection.

## What changed in the archive

Added:
- `proposals/crate-guidance-pack-kit.md`
- `meta/crate-guidance-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-27.md`
- `fixtures/crate-guidance-pack-kit/`
- `entries/2026-03-16-198.md`

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
- shared ecosystem interop profiles,
- generic diagnostic renderers,
- and docs-portal / cookbook browsing surfaces

into one fake “supportiveness solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/reference/attributes.html
- https://doc.rust-lang.org/beta/releases.html
- https://rust-lang.github.io/rfcs/3368-diagnostic-attribute-namespace.html
