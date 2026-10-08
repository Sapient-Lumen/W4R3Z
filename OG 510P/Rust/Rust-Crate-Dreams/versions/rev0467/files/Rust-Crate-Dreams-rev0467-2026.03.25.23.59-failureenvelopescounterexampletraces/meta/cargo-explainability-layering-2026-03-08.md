# Cargo explainability layering — 2026-03-08

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it clarifies a repo-wide ambiguity that had started to matter more as Cargo's build-analysis surfaces became real:

- **P-0469** is the per-run or pair-of-runs **support bundle**.
- **P-0035** is the multi-session **warehouse + regression adjudication** layer.
- **P-0468** is the **resolver / graph-choice cause-chain** layer.
- **P-0494** is the **tool-invocation parity** layer.

The repo now needs this split more than it needs another Cargo proposal.

## Why the split got sharper

Cargo now has an explicit unstable `-Zbuild-analysis` feature with `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
At the same time, the unstable docs also note that the machine-readable `--timings=json` output is gone on 1.94-nightly.

That combination matters:

- Cargo is more real than before as a *capture/query substrate*.
- But the machine-contract story is still not something downstream tools should simply treat as solved.

That creates two distinct worthy crate opportunities rather than one blurry one.

## The crate-family split

### P-0469 — Cargo Rebuild Explanation Kit
Use when the question is:

> Why did this rebuild here and now?

What it should hand other people:
- one support-grade bundle,
- one conservative rebuild-cause classification,
- one receipt of imported sessions / commands / caveats,
- and one compact artifact suitable for CI or issue filing.

### P-0035 — cargo-build-insights
Use when the question is:

> When did this regression begin, how often is it happening, and how does the current series differ from the baseline series?

What it should hand other people:
- one stable imported-session warehouse record,
- one regression explanation artifact,
- one trend alert artifact,
- and one portable historical analysis bundle.

### P-0468 — Cargo Resolver Explanation Kit
Use when the question is:

> Why is this version, feature, or duplicate-build state present?

What it should hand other people:
- one short cause-chain bundle,
- one reviewable duplicate-build / feature-cause artifact,
- and one diffable graph-choice receipt.

### P-0494 — Cargo Compile-Time-Deps Workflow Kit
Use when the question is:

> Did a tool-only build diverge from a fuller build, and what should I do about it?

What it should hand other people:
- one parity receipt,
- one fallback recommendation,
- and one honest bundle that does not pretend tool-only semantics are a stable promise.

## Design rule for future passes

If the archive touches Cargo explainability again, it should ask first:

1. is this a **support artifact** problem (P-0469),
2. a **historical regression warehouse** problem (P-0035),
3. a **graph-choice explanation** problem (P-0468),
4. or a **tool/workflow parity** problem (P-0494)?

If the answer is unclear, the pass should sharpen the layer boundary before proposing another crate.

## Repo implication

The best next Cargo-facing work should now prefer:

1. fixture/schema stubs for **P-0035**,
2. further proposal-file sharpening around what each crate *hands another person*,
3. vocabulary reuse across receipts (`observed_fact`, `conservative_inference`, `manual_review_required`, `comparison_baseline`),
4. and freshness checks as `cargo report` evolves.

## Anti-patterns

- Do **not** merge P-0035 and P-0469 into one generic performance product.
- Do **not** assume HTML timing replay is the durable machine contract.
- Do **not** treat stable `cargo metadata` and stable Cargo JSON messages as interchangeable with nightly build-analysis sessions.
- Do **not** add another generic Cargo performance crate unless the layer is clearly different from the four above.

## Sources

- Cargo unstable features (`build-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo tracking issue (`-Zbuild-analysis`): https://github.com/rust-lang/cargo/issues/15844
- Cargo issue (`cargo report` session selection): https://github.com/rust-lang/cargo/issues/16472
- Cargo external-tools JSON: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo metadata docs: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
