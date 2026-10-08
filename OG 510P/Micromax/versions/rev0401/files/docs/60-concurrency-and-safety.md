# Concurrency and safety plan (early sketch)

This document is a planning artifact, not an implementation spec.

## Why concurrency is “dangerous” in editors
Editors are stateful. Even seemingly harmless background tasks (syntax highlighting, file watchers, LSP clients) can:
- mutate shared state at awkward times
- freeze the UI if they block
- create subtle races if truly concurrent

So we want: **responsiveness** without chaotic shared-memory concurrency.

Neovim’s Lua ecosystem is a modern contrast case: plugins frequently rely on callbacks and
coroutines to avoid blocking the UI.

- Neovim Lua docs: https://neovim.io/doc/user/lua.html
- Example coroutine patterns (blog): https://dzx.fr/blog/async-lua-in-neovim/

## Forth precedent: cooperative vs real parallelism
Gforth documents two approaches:
- a traditional **cooperative round-robin multitasker**
- a **pthread-based multitasker** for real concurrency

- Gforth multitasker overview: https://gforth.org/manual/Multitasker.html
- Gforth pthread notes emphasize that pthreads are really concurrent and require conflict-avoidance techniques:
  https://gforth.org/manual/Pthreads.html

This maps well to editor needs: cooperative is easier to reason about; real concurrency demands careful design.

## Micromax stance: cooperative-first
### Principle 1 — The UI task owns editor mutations
All editor state mutation happens on the UI task.

Background tasks do *work* (IO, indexing, parsing), then send messages to UI to apply results.

### Principle 2 — Budget + yield are the default safety rails
Untrusted code (plugins, callbacks) must not freeze the editor.

- **Step budget** prevents infinite loops (rev3 implemented this)
- **Explicit yield points** allow long operations to cooperate with responsiveness

### Principle 3 — Isolation boundaries are real
Longer term, isolate plugins with one or more of:
- per-plugin VM instances
- separate Python interpreters (multiprocessing)
- a language-level capability system for hostcalls

## A minimal cooperative task model (planned)
Not yet implemented, but the intended shape:

- `spawn ( q -- taskid )` create a task from a quotation
- `yield` / `pause` yield to the scheduler
- `run-tasks` runs the cooperative scheduler until the UI says stop

The scheduler will enforce:
- per-task step budgets
- “UI-only” hostcalls that mutate editor state

## Planning for real parallelism (later)
If/when we need true parallelism:

1) Treat parallel tasks as **pure workers**:
   - no direct access to editor state
   - communicate via message passing (queues)

2) Put all hostcalls behind a capability boundary:
   - a worker can request an operation; UI task decides

3) Prefer a small number of well-defined concurrent subsystems:
   - file IO + watchers
   - parsing/indexing
   - LSP bridge

## Extra guardrails for a Forth-centric editor

- **Crash containment**: every event handler runs under `catch`, errors are reported with file/line + trace.
- **Resource limits**: step budgets by default; later add time budgets.
- **Namespace hygiene**: plugins get their own wordlist; they don’t pollute global search order.
- **Hostcall allowlist**: no ambient power (already in rev2).
- **Deterministic core**: avoid hidden global state that changes parsing/meaning.

