# Design: Epic contribution hot substrate watchcards (2026 Q1)

## Goal
The archive already has ranking, packets, kernels, operating-surface grammar, stewardship guidance, and a portfolio control loop.
What it still lacked was a concrete artifact family for the **fastest loop**.

This note answers a narrow practical question:

> where should fast-moving Rust substrate truth live before it is allowed to change packets, charters, or canon?

This is a **hot-substrate / watchcard / drift-lane** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It exists so the repo can preserve fresh source truth without becoming memo-shaped or continuity-lossy.

Read with:
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `meta/HOT_SUBSTRATE_WATCH_PROTOCOL.md`
- `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md`
- current `evidence/hot-substrate-*.md` files

## Why this pass is merited now
Official Rust signals keep exposing substrate that matters immediately but should not be mistaken for broad canon.

The current examples are unusually clear:
- Cargo build analysis is still prototype-shaped around recorded build facts and unstable `cargo report` surfaces.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo build-dir layout remains a live migration surface and the testing call says many tools still depend on unspecified target/build-dir details.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- crates.io has a new Security tab, trusted-publishing work remains active, and the March 2026 Project Director update names capability analysis and vulnerability surfacing explicitly.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/
- machine-readable surfaces are strengthening but remain caveat-heavy: Cargo external-tools, `cargo metadata`, rustc JSON, docs.rs rustdoc JSON, and libtest JSON are all useful but compatibility-sensitive.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  https://doc.rust-lang.org/beta/rustc/json.html
  https://docs.rs/about/rustdoc-json
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- institutional-readiness signals are live too: Foundation strategy, the Innovation Lab hosting route, and FLS sustainability all change what long-horizon commons can realistically look like in practice.
  https://rustfoundation.org/strategic-plan/
  https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html

The repo therefore needed one more layer:
**watchcards that capture imported truths, non-claims, reissue triggers, and downstream effects.**

## Headline answer
A worthy Rust ecosystem repo should treat hot substrate truth as its own first-class artifact family.

A **watchcard** is not:
- a packet,
- a charter,
- a broad strategy note,
- or a generic “latest updates” memo.

A watchcard is a short renewable record of:
1. what source family is moving;
2. what truths the archive is allowed to import from it;
3. what the source still does **not** prove;
4. what assets may care;
5. what stayed the same.

## Minimum watchcard fields
Every serious watchcard should say:
- lane;
- drift horizon;
- authoritative sources;
- imported truths;
- non-claims;
- reissue triggers;
- downstream assets;
- current implication;
- what did not change.

## Current watch-lane ranking
### 1) Build-state substrate watch
This is first because it serves the archive's strongest current seam and because Cargo build-evidence and build-dir behavior are moving right now.

### 2) Package + release-boundary watch
This is second because crates.io security/publishing truth, advisory routing, and capability-analysis posture directly affect the archive's clearest operator-boundary program.

### 3) Machine-readable tooling surfaces watch
This is third because it multiplies Tooling Contract and Compatibility Claims work, but it is still better treated as import substrate than as a whole top seam by itself.

### 4) Institutional-readiness watch
This is fourth because it moves slower than the first three but still faster than broad canon and still materially affects what stewardship shapes are credible.

## How watchcards should be used
Default rule:
1. refresh the watchcard first;
2. update a packet only if the watchcard clearly changes current requested posture;
3. update a charter only if the watchcard changes host or steward shape;
4. update canon only if multiple sources or watchcards now point to a larger strategic shift.

## Wrong shapes to refuse
- a giant latest-signals memo that mixes hot drift, packet requests, and canon claims;
- a new top-band seam invented because one watch lane got interesting;
- service-side or prototype truth treated as a universal stable contract;
- assistant synthesis that cannot say what changed, what did not, and what exact downstream assets should care.

## Current archive decision
This revision adds:
- `design/epic-contribution-hot-substrate-watchcards-2026Q1.md`
- `meta/HOT_SUBSTRATE_WATCH_PROTOCOL.md`
- `evidence/hot-substrate-build-state-watch-2026-03.md`
- `evidence/hot-substrate-package-boundary-watch-2026-03.md`
- `evidence/hot-substrate-machine-readable-surfaces-watch-2026-03.md`
- `evidence/hot-substrate-institutional-readiness-watch-2026-03.md`

Interpretation:
- no new worthy-contribution seam was promoted;
- the broad ladder is unchanged;
- the repo now has a concrete landing zone for the fastest loop.
