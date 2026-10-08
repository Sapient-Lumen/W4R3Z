---
id: P-0008
title: Scoped Tasks — structured concurrency + cancellation ergonomics for async Rust
status: idea
domains: [async, tokio, concurrency, reliability]
last_reviewed: 2026-03-01
evidence:
  - https://tmandry.gitlab.io/blog/posts/2023-03-01-scoped-tasks/
  - https://github.com/sunshowers/cancelling-async-rust
  - https://docs.rs/task_scope/latest/task_scope/
  - https://without.boats/blog/the-scoped-task-trilemma/
---

## What it should provide others

A **drop-in structured concurrency layer** for async Rust that makes “spawned tasks you forgot to await” much harder to create, and makes cancellation *predictable*.

The crate should give users:

- **Task scopes**: spawn tasks tied to a lexical scope; leaving the scope joins or cancels them.
- **Cancellation tokens** with consistent semantics across runtimes (Tokio first, adapters later).
- **Timeout and shutdown patterns**: APIs that encode “cancel children on drop” and “graceful then hard stop”.
- **Ergonomic failure handling**: first-error-wins, collect-all, retryable subsets, etc.
- **Debuggability**: task tree introspection (names, parents, states) compatible with `tracing`.

## Why this is still missing

People know the patterns, but they’re not packaged as a widely-adopted, runtime-friendly crate with:
- a clear *safety story* around lifetimes,
- a coherent cancellation model,
- and migration docs from `tokio::spawn` everywhere.

## Design principles

- **Make the correct thing easy**: structured spawn should be the default path.
- **Explicit “escape hatches”**: allow unstructured spawn, but make it noisy.
- **Runtime-agnostic core**: traits for “spawn”, “sleep”, “time”, “join”, implemented for Tokio first.
- **No hidden background work**: cancellation and joining should be observable and testable.

## API sketch (conceptual)

```rust
use scoped_tasks::{Scope, Cancel};

Scope::new().run(|scope| async move {
    let cancel = scope.cancel_token();

    let a = scope.spawn("fetch-a", async { ... });
    let b = scope.spawn("fetch-b", async { ... });

    // graceful shutdown: signal, then wait with deadline
    cancel.cancel();

    scope.join_all_with_deadline(Duration::from_secs(2)).await?;
    Ok::<_, scoped_tasks::Error>(())
}).await?;
```

## Related work and gaps

- Tokio provides powerful primitives, but not a “task nursery” default.
- Various blog posts and experiments outline patterns; a crate should operationalize them.

## MVP (4–8 weeks)

1. Tokio backend: `Scope::spawn`, `join_all`, cancellation token integration.
2. Structured error handling policies: `JoinPolicy::{CancelOnError, CollectAll, FirstError}`.
3. `tracing` integration: automatically attach task/span metadata.
4. Docs: “stop leaking tasks” migration guide.

## De-risk spike

- Prove a scope implementation that is:
  - sound w.r.t. lifetimes (no self-referential pitfalls),
  - cancellation-safe (no deadlocks on drop),
  - and supports nested scopes.

## Sustainability plan

- Keep dependency surface minimal.
- Provide an RFC-like “design record” in the repo so future maintainers can reason about tradeoffs.
