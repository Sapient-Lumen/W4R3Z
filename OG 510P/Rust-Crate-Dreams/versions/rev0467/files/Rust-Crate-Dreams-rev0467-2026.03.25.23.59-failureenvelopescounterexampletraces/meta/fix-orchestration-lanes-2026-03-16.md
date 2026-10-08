# Fix orchestration lanes — 2026-03-16

## Main judgment

This pass adds a missing boundary the archive needed:

- **P-0507** is the generic **lint-fix campaign orchestration** layer.
- **P-0461** is the **edition-specific rehearsal / migration witness** layer.
- **P-0478** is the **future-incompat ownership / waiver / upgrade-path** layer.
- **P-0432** is the lower **Cargo phase and plumbing receipt** layer.

The repo was at risk of flattening all four into one fake “migration tool”.
That would make the archive worse.

## The crate-family split

### P-0507 — Cargo Fix Campaign Kit
Use when the question is:

> How do we plan, batch, rehearse, apply, and review automated lint fixes across a real workspace?

What it should hand other people:
- one lint-selection ledger,
- one target-batch plan,
- one receipt per pass,
- and one manual-review queue.

### P-0461 — Edition Drift Witness Kit
Use when the question is:

> Are we ready for this edition migration, and what edition-specific compatibility lints or macro risks remain?

What it should hand other people:
- one edition rehearsal bundle,
- one lint ledger for the edition transition,
- one macro-risk witness,
- and one compact proof that the migration was rehearsed.

### P-0478 — Cargo Future-Incompat Triage Kit
Use when the question is:

> Which future-incompat findings are owned, waived, unresolved, or likely fixable by dependency updates?

What it should hand other people:
- one dependency-risk ledger,
- one owner/waiver map,
- one upgrade-path bundle,
- and one diff across toolchains or lockfile updates.

### P-0432 — Cargo Plumbing Interop Kit
Use when the question is:

> Which Cargo phases were captured, what inputs were really consumed, and where did current Cargo APIs force a compromise?

What it should hand other people:
- one phase lock,
- one phase-input intent receipt,
- one phase snapshot bundle,
- and one blocker-aware plumbing receipt.

## Working rule for future passes

If a future pass touches `cargo fix`, edition migration, or lint cleanup, ask first:

1. is this a **generic fix campaign** problem,
2. an **edition migration evidence** problem,
3. a **future-incompat triage** problem,
4. or a **Cargo plumbing / phase I/O** problem?

If the answer is unclear, sharpen the boundary before adding another proposal.

## Anti-patterns

- Do **not** merge generic fix orchestration into edition migration just because `cargo fix --edition` exists.
- Do **not** merge future-incompat ownership into edit orchestration just because some warnings might be auto-fixable.
- Do **not** pretend Cargo plumbing is solved merely because some subcommands exist.
- Do **not** turn a boring receipt-and-batching crate into a general IDE/codemod platform.

## Sources

- `cargo fix` docs: https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Edition Guide advanced migrations: https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo 1.90 development cycle update (`cargo-fixit`): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- GSoC 2025 results (`cargo-fixit`, `cargo-plumbing`): https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
