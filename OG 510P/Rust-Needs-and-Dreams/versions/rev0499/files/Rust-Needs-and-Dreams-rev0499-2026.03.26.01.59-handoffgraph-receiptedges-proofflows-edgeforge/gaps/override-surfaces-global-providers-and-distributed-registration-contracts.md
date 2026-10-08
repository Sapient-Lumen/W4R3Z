# Gap: override surfaces, global providers, and distributed registration contracts

## What is missing
Rust already has many ways for one crate or binary to **supply process-wide behavior, replace a default handler, or contribute entries to a shared registry**, but the ecosystem still lacks a **portable way to describe what those override surfaces actually promise**.

Today there is no standard way to say:
- whether a slot is unique in the dependency graph, unique per process, thread-local, task-local, scoped by guard, or multi-registration,
- whether installation happens at link time, startup, lazy runtime init, or explicit registration,
- whether replacement is forbidden, one-shot, atomic-update, stackable/layered, or deliberately last-writer-wins,
- whether a default fallback exists and whether wrappers are expected to call through to it,
- whether the surface is meant for libraries, executables, tests, plugins, or downstream application crates only,
- whether ordering matters across distributed registration,
- what reset / teardown / test-isolation story exists,
- what panic / allocation / logging / tracing / discovery side effects the provider is allowed to perform,
- and which of those claims were actually checked.

That gap matters because Rust already spans materially different override modes:
- `#[panic_handler]` is a unique dependency-graph hook in `no_std`;
- `#[global_allocator]` is a unique dependency-graph allocator slot;
- `std::panic::set_hook` replaces the current panic hook, while `update_hook` composes with the previous one;
- allocation error hooks are separately replaceable;
- `log::set_logger` installs one process-global logger and may only succeed once;
- `tracing::subscriber::set_global_default` installs one process-global default while still allowing thread-local defaults;
- `inventory` collects distributed plugin registrations across linked code;
- `linkme` gathers distributed slices at link time.

So the missing contribution is not one more service locator, one more singleton helper, or one more magical registration macro.
It is a **reviewable override-surface layer** for publishing installation rules, scope, precedence, fallback, and evidence honestly across Rust’s many ambient/provider patterns.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://doc.rust-lang.org/reference/panic.html
- https://doc.rust-lang.org/reference/attributes.html
- https://doc.rust-lang.org/std/alloc/index.html
- https://doc.rust-lang.org/std/panic/fn.set_hook.html
- https://doc.rust-lang.org/std/panic/fn.update_hook.html
- https://docs.rs/log/latest/log/fn.set_logger.html
- https://docs.rs/tracing/latest/tracing/subscriber/fn.set_global_default.html
- https://docs.rs/tracing/latest/tracing/subscriber/index.html
- https://docs.rs/inventory
- https://docs.rs/linkme

## The current seam is awkward
Rust’s override and registration mechanisms are real, useful, and already heavily relied upon, but they are scattered across compiler built-ins, std APIs, and crate-specific conventions.

Some surfaces are **compiler-shaped today**:
- `#[panic_handler]` must be unique in the dependency graph and has a fixed signature;
- `#[global_allocator]` can only be used once and feeds the program-wide default allocator path;
- the project-goals work on Externally Implementable Items exists specifically to make `#[panic_handler]`, global allocator, and similar features more like regular library features.

Other surfaces are **runtime-installed ambient slots**:
- `std::panic::set_hook` replaces the current panic hook and `update_hook` atomically composes around the previous one;
- allocation error hooks are a distinct hook family with their own default behavior and replacement API;
- `log::set_logger` is one-shot and any logs before initialization completes are ignored;
- `tracing::subscriber::set_global_default` is also one-shot, but `tracing` separately exposes thread-local defaults as scoped fallbacks.

Still others are **distributed discovery surfaces**:
- `inventory` lets linked code submit typed registrations without a central list;
- `linkme` lets crates contribute elements to linker-collected distributed slices.

These are not all the same thing, and pretending they are creates confusion:
- uniqueness in the dependency graph is not the same as one-shot process-global runtime init,
- one-shot init is not the same as thread-local scoped override,
- replace/update hooks are not the same as multi-registration registries,
- and distributed registration is not the same as an ordinary mutable singleton.

Yet today those distinctions usually live in doc comments, examples, or issue-thread folklore instead of a shared artifact family.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://doc.rust-lang.org/reference/panic.html
- https://doc.rust-lang.org/std/alloc/index.html
- https://doc.rust-lang.org/std/panic/fn.set_hook.html
- https://doc.rust-lang.org/std/panic/fn.update_hook.html
- https://doc.rust-lang.org/beta/std/alloc/fn.set_alloc_error_hook.html
- https://docs.rs/log/latest/log/fn.set_logger.html
- https://docs.rs/tracing/latest/tracing/subscriber/fn.set_global_default.html
- https://docs.rs/tracing/latest/tracing/subscriber/index.html
- https://docs.rs/inventory
- https://docs.rs/linkme

## Why this matters
This gap matters because override points are where Rust programs often decide **who gets to define ambient behavior**.

1. **language-to-library transition** — if Externally Implementable Items lands as intended, more override points may move from special compiler treatment toward ordinary library-defined surfaces. The ecosystem needs a way to publish those surfaces honestly instead of multiplying bespoke magic.
2. **startup and test fragility** — one-shot globals are notorious sources of “already initialized” conflicts, especially in tests, plugins, examples, or reusable helper crates.
3. **library/application boundary clarity** — `tracing` explicitly warns libraries not to install the global default subscriber. That is strong evidence that install authority, not just provider type, is part of the public contract.
4. **distributed extension ecosystems** — metrics registries, plugin registries, flag tables, codecs, and type registries often need decentralized contribution. The missing layer is not another registry primitive; it is a common way to describe registration/discovery posture and ordering assumptions.
5. **policy and review** — override points are authority surfaces. Who may install them, when, with what fallback behavior, and how they compose are review questions, not just ergonomics.

A worthy contribution here is therefore not another global-state helper.
It is a way to treat override and registration surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://docs.rs/tracing/latest/tracing/subscriber/fn.set_global_default.html
- https://docs.rs/log/latest/log/fn.set_logger.html
- https://docs.rs/inventory
- https://docs.rs/linkme

## What “good” looks like
A worthy contribution here is **not** one universal provider trait that erases the real differences between handlers, hooks, defaults, and registries.

It is a shared override-surface boundary:
- one `override-surface/v0` describing the installable or discoverable slot,
- one `provider-slot-profile/v0` describing identity, intended owner, fallback/default behavior, and allowed provider kinds,
- one `install-lifecycle-profile/v0` describing link-time, startup, lazy-init, replace, update, reset, or teardown behavior,
- one `scope-multiplicity-profile/v0` describing dependency-graph uniqueness, process-global once, thread/task-local scopes, guard-based scopes, or multi-registration collection,
- one `registry-discovery-profile/v0` describing explicit registration, linker-assisted collection, ordering assumptions, iteration guarantees, and duplicate-handling posture,
- one `override-adapter-profile/v0` describing wrapper/bridge behavior such as calling through to previous hooks or bridging `log` records into `tracing`,
- one `override-vector-set/v0` for init-order, double-install, fallback, wrapping, reset, discovery, and test-isolation vectors,
- one `override-check-report/v0` recording what was actually exercised,
- and one `override-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams review override surfaces with explicit artifacts instead of inferring them from ad hoc init code and crate docs.

## Non-goals
This gap should not be used to:
- define one canonical service locator or global singleton framework,
- flatten compiler built-ins, runtime hooks, thread-local defaults, and distributed registries into one fake mechanism,
- bless ambient global state as good practice for every library,
- or hide initialization-order and test-isolation hazards behind one cheerful “easy setup” badge.

The job is smaller and sharper:
**make override surfaces, global providers, and distributed registration contracts legible, honest, and checkable across the ecosystem.**
