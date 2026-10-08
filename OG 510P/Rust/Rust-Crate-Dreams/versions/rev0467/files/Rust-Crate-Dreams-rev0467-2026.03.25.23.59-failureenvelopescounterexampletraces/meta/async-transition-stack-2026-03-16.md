
# Async transition stack — 2026-03-16

This note exists to stop the archive from collapsing several nearby async-adoption ideas into one vague “async transition crate”.

The 2026 Rust flagships make this more important, not less:

- `async fn in dyn trait` is now an explicit **Just Add Async** milestone.
- return type notation is also in scope for the same flagship.
- the ecosystem still materially depends on `async-trait`, `trait-variant`, and bridge crates like `dynosaur`.

That means the next missing value is often a **migration and comparison artifact**, not another executor or proc macro.

## The stack to preserve

### 1. Language and compiler evolution
This layer is about the language itself:

- native `async fn in dyn trait`
- return type notation
- trait-system and object-safety rules
- compiler diagnostics and stabilization windows

This layer is **substrate**, not the missing crate.

### 2. Bridge recipes in today’s ecosystem
This layer is about the concrete strategy a crate uses *today*:

- `async-trait`
- native async-in-traits plus `trait-variant`
- `dynosaur`
- local adapters and hand-written boxing/shim strategies

This layer is where a migration workbench like **P-0458 Async Dyn Transition Kit** should look.

### 3. Receiver-facing migration artifacts
This layer is the real missing coordination surface:

- `async-dyn-plan.toml`
- `dispatch-recipe.json`
- `allocation-profile.json`
- `object-surface.diff.json`
- `migration.receipt.json`

The question here is not “can Rust do async dyn yet?”
The question is:

> what recipe did this crate choose, what public promise does that imply, what changes if it migrates, and what caveats remain?

### 4. Runtime and executor ergonomics
This is adjacent, but different:

- structured concurrency
- task supervision
- runtime portability
- cancellation semantics
- deterministic replay or simulation

Do not collapse this into P-0458. Those are different crates with different artifacts.

### 5. Replay / determinism / debugging lanes
Also adjacent, but different:

- async replay debuggers
- deterministic simulation
- chaos/fault injection
- hardship suites

These preserve *execution truth*, not *dispatch-recipe transition truth*.

## Working rule

When touching async transition work, future revisions must state explicitly:

1. which parts are **upstream language/compiler milestones**,
2. which parts are **today’s recipe choices**,
3. which parts are **public promise diffs** versus mere implementation diffs,
4. which parts concern **allocation/sendability/object-surface** consequences,
5. and which parts belong to **executor/runtime** work instead.

Do not let the archive silently rewrite:

- “there are several bridge recipes”
- into “the missing crate is another bridge recipe”,
- or “native support is coming”
- into “maintainers no longer need migration receipts”.

The worthy crate here is the **boring transition workbench** above real substrate.
