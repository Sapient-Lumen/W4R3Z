# Gap: Defect escalation, minimal repros, routing, and regression handoffs

## Missing today
Rust has better ingredients for good bug reporting than it used to have, but still lacks a portable boundary between:
- **what failed locally**,
- **what reduced case still reproduces**,
- **where that case should go**,
- and **whether it is ready to become a regression test**.

Today those truths are fragmented across:
- local shell history and terminal output,
- one-off MCVEs or gists,
- issue-template prose,
- triage labels,
- Cargo report/build-analysis output,
- and maintainer memory.

That fragmentation causes three recurring failures:
1. evidence stays local and never becomes actionable upstream;
2. minimization destroys traceability back to the observed case;
3. issue filing stops before regression-test handoff becomes visible.

## Why this is now a first-class gap
Official/project signals are unusually aligned:
- the Rust goals process explicitly frames `cargo script` as a reproducible-bug-report tool;
- the February 2026 update says single-file reproducers are materially easier to share;
- Forge triage already treats repros, missing info, MCVEs, and bisections as explicit workflow state;
- the rustc-dev-guide says bug fixes should carry succinct regression tests;
- libtest-JSON work is about richer machine-usable reporting surfaces; and
- Cargo report work keeps making local evidence more structured.

So the missing contribution is not another generic bug template.
It is the contract that preserves:
- observation truth,
- minimization-lineage truth,
- routing/dedup truth,
- regression-candidate truth,
- and consumer-handoff truth.

## What a worthy contribution would add
A real solution should add a thin artifact family such as:
- `defect-observation/v0`
- `defect-minimization-report/v0`
- `defect-routing-report/v0`
- `defect-regression-candidate/v0`
- `defect-escalation-pack/v0`

And it should prove at least these routes:
1. single-file repro → issue-ready pack
2. workspace slice → issue-ready pack
3. issue-ready pack → regression-candidate pack
4. uncertain-routing pack that stays honest instead of fabricating confidence

## Adjacent files
- `design/defect-escalation-contract-2026Q1.md`
- `design/defect-escalation-stack.md`
- `design/prototype-elevation-stack.md`
- `design/cargo-report-kit.md`
- `design/debuggability-stack.md`
- `proposals/epic-defect-escalation-stack.md`
