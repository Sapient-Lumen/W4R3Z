# Trait-solver drift lane boundaries — 2026-03-22

Keep **P-0442** separate from these adjacent lanes.

## 1. Not Polonius / borrowck transition work

If the primary question is borrow-check acceptance, region reasoning, or lending-iterator support, that belongs primarily to **P-0446 Polonius Borrowck Transition Witness Kit**.

P-0442 owns trait-solver drift, not borrowck drift.

## 2. Not SemVer witness generation

If the primary question is “is this public API change breaking?”, that belongs primarily to **P-0244 SemVer API Diff Evidence Kit** and related public-API readiness lanes.

P-0442 may import witness-generation style techniques, but it should not become the SemVer tool.

## 3. Not generic compile-fail harnessing

`ui_test`, `trybuild`, and `compiletest_rs` are corpus runners.
P-0442 owns the higher review layer:

- solver-lane truth,
- obligation-class reporting,
- diagnostic normalization,
- minimization lineage.

## 4. Not compiler tracing / proof-tree debugging by itself

If the main job is developer debugging of the compiler internals, that is a different lane.
P-0442 may later import tracing or proof-tree-derived hints, but must stay useful without them.

## 5. Not release-note dashboards

If the main job is compiler release summarization or edition migration, that belongs elsewhere.
P-0442 owns **case-level drift evidence** and the bundle others can review.
