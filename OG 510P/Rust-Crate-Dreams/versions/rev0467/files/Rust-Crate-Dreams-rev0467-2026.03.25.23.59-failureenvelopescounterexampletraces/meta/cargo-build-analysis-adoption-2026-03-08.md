# Cargo build-analysis adoption layer — 2026-03-08

## Main judgment

This pass deliberately did **not** add another top-level proposal.

Instead, it makes a tighter claim about the current Cargo explainability frontier:

- Cargo is now growing a real **build-analysis recording/query substrate**.
- The archive should therefore stop planning P-0469 as though it must invent that substrate from scratch.
- The missing crate value is increasingly the **stable receipt, redaction, diff, and support-handoff layer above Cargo's evolving `cargo report` surface**.

## What changed upstream

Cargo now documents an unstable `-Zbuild-analysis` feature that records and persists detailed build metrics on disk and exposes:

- `cargo report sessions`
- `cargo report timings`
- `cargo report rebuilds`

The tracking issue also makes clear that the story is **not done**. Open design questions still include programmable formats, schema evolution, session-ID ergonomics, nested Cargo calls, and the wording/actionability of rebuild reasons.

That is exactly the kind of situation where a crate can be valuable **without fighting upstream**.

## Sharper crate-family split

### P-0469 — Cargo Rebuild Explanation Kit
Should become the **stable session-import and rebuild-bundle layer**.

What it should provide other people:

1. one stable `session-index.json` even if Cargo's session listing/UI evolves,
2. one conservative `unit-rebuilds.json` that distinguishes observed facts from imported report text and local inference,
3. one `rebuild.receipt.json` that records exactly which Cargo session/report inputs were imported,
4. one `timings-pointer.json` that keeps timing replay attached without pretending HTML is the contract,
5. and one redactable `*.rebuildbundle.zip` that can travel across CI, issue filing, and support.

### P-0468 — Cargo Resolver Explanation Kit
Should remain the **graph-choice / cause-chain layer**.

It should not pretend that build-analysis solves resolver explanation.
But it should borrow the same bundle/receipt vocabulary: comparison baselines, command receipts, redaction policy, and conservative inference labels.

### P-0494 — Cargo Compile-Time-Deps Workflow Kit
Should remain the **tool-invocation parity layer**.

It does not need to claim ownership of Cargo build-analysis.
But it should be able to attach or import the same session/baseline vocabulary when a tool-only run is compared against a fuller build.

## Why this matters

Without this clarification, future revisions are likely to make one of two mistakes:

1. inventing another generic build-performance tool that duplicates Cargo's new work, or
2. assuming upstream Cargo therefore already solved the boring support workflow.

Both are wrong.

The archive should aim for the missing middle:

- stable receipts
- conservative classification
- diffable bundles
- redaction and support handoff
- and a crate contract that stays useful while nightly Cargo keeps evolving

## 0.1 recommendation

For **P-0469**, the first valuable slice now looks like:

- import the latest or selected Cargo build-analysis session,
- freeze it into a small stable bundle,
- classify rebuilt vs reused units coarsely,
- attach a timing replay pointer when available,
- and export one support-grade ZIP.

That is narrower, more adoptable, and more future-proof than trying to be a whole alternative build-analysis recorder.

## Anti-patterns

- Do **not** treat Cargo's unstable report/session format as a stable public contract.
- Do **not** make the crate require Cargo nightly for all value; imported reports should be preferred, not mandatory.
- Do **not** turn the crate into another historical dashboard product.
- Do **not** collapse human HTML replay and machine contracts into one format.

## Repo implication

For the next few passes, the archive should prefer:

1. session-import schemas and tiny example bundles for **P-0469**,
2. vocabulary harmonization across **P-0469 / P-0468 / P-0494**,
3. proposal-file upgrades clarifying what another person actually receives,
4. and freshness checks as Cargo's build-analysis/report surface evolves.

## Sources

- Cargo unstable features (`build-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog (`cargo report timings`, `--compile-time-deps`): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo tracking issue (`-Zbuild-analysis`): https://github.com/rust-lang/cargo/issues/15844
- Cargo issue (`cargo report` session selection): https://github.com/rust-lang/cargo/issues/16472
- Cargo issue (man pages for new `cargo report *` commands): https://github.com/rust-lang/cargo/issues/16488
- Cargo external tools JSON: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo timings docs: https://doc.rust-lang.org/cargo/reference/timings.html
