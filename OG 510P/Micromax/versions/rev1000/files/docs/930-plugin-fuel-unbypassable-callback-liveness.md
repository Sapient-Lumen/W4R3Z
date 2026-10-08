# Plugin fuel: unbypassable callback liveness (rev0973)

## Why this was the next risk

Rev0972 made the imported plugin world explicit, but one valid in-process plugin
could still prevent the editor from ever returning to its event loop. The failure
was not hypothetical:

- an entry file containing `-1 set-budget [ 1 ] [ ] while` did not return;
- the same loop in `init` prevented a candidate generation from completing;
- a retained command, keybinding, timer, or hook could monopolize the editor on a
  later user action; and
- a hostile or broken `deinit` could prevent graceful unload from returning.

The host appeared to have a limiter because `VM.eval(..., step_budget=N)` existed.
It was not an authority boundary. Host and script limits shared `_budget_stack`,
and the guest-visible `set-budget` word could clear that stack with `-1`. Code
inside the limit therefore controlled the limit.

## Correction

The VM now has two budget domains:

1. **script budgets** — one persistent base owned by `set-budget`, plus nested
   `with-budget` frames; and
2. **host budgets** — private frames installed by `VM.host_step_budget()` and by
   `VM.eval(step_budget=...)`.

Every dispatched VM step decrements every active host frame. A nested evaluation
cannot reset its caller by asking for a fresh larger allowance. Guest
`set-budget` and `with-budget` continue to work, but cannot clear, enlarge, or
observe the host frame.

This separation also fixes a latent language bug: `set-budget` previously
replaced or cleared the whole script stack, so invoking it inside `with-budget`
could destroy the enclosing frame. The base and nested script frames now have
separate state, and `budget` reports only script-owned limits.

## Plugin turn boundary

`plugin_execution_budget.py` owns one small embedding policy:

- the safe default is 100,000 VM dispatch steps;
- missing or malformed tuning falls back to that default;
- an embedding may explicitly set a nonpositive value only when it accepts the
  risk or supplies a stronger external boundary; and
- each plugin turn restores the shared VM's prior script-budget state, so plugin
  `set-budget` calls neither relax the host limit nor poison later editor work.

The same fresh host-owned budget now covers:

- plugin entry/source evaluation;
- `preinit`, `init`, `postinit`, and `deinit`;
- retained commands and keybindings;
- timer and hook callbacks; and
- other delayed plugin execution that funnels through
  `Editor.run_script_origin_callback()`, including prompt-origin work and macro
  replay.

Source and lifecycle use `PluginManager._plugin_execution_context()`. Retained
callbacks use `Editor.plugin_callback_context()`. There is no parallel callback
registry or per-surface limiter to drift.

## Failure and rollback behavior

An exhausted plugin turn raises the existing `MicromaxError` code `-100` with
`Execution budget exceeded`.

- A source or lifecycle failure does not commit the candidate plugin generation.
- A failed delayed callback restores plugin dictionary and managed runtime state
  through the existing callback snapshot.
- Command/key/timer/hook adapters keep their existing user-facing error path.
- A failed graceful `deinit` leaves the live plugin generation installed; the
  existing force-unload/revoke recovery lane can remove it without executing the
  hostile lifecycle word again.
- All budget frames unwind in `finally`, and the shared VM remains usable after
  interruption.

## Measured cutoff

A local five-run measurement in the release container on 2026-07-18 used an
infinite Micromax loop and recorded these median times to exhaust host fuel:

| Host steps | Median | Observed range |
|---:|---:|---:|
| 1,000 | 1.41 ms | 1.39–1.87 ms |
| 10,000 | 16.18 ms | 14.45–17.42 ms |
| 100,000 | 146.81 ms | 145.55–155.92 ms |

These numbers select a practical default for this implementation and machine;
they are not a wall-clock contract. Different primitives, machines, Python
versions, and hostcalls can consume very different time per VM dispatch.

## Online research checked 2026-07-18

Wasmtime's current interruption guidance distinguishes deterministic instruction
fuel from epoch-based interruption. Fuel is the closer precedent for Micromax's
small replayable VM because a fixed input and fuel allowance should fail at a
repeatable dispatch boundary:

- https://docs.wasmtime.dev/examples-interrupting-wasm.html
- https://docs.wasmtime.dev/api/wasmtime/struct.Config.html

The more important lesson is the stated limitation: fuel and epochs do not help
while guest execution is blocked inside a host call. The embedder must separately
own cancellation, timeout, or asynchronous yielding for those operations. That
maps directly to Micromax: the new budget bounds Micromax instruction dispatch,
not a Python primitive after dispatch has entered it.

## Audit of delayed execution surfaces

A call-site audit found one shared retained-callback funnel rather than separate
execution implementations:

- command callbacks enter `run_script_origin_callback()` from the bridge;
- keybindings, timers, hooks, prompt-origin operations, and recorded macro steps
  re-enter the captured script/plugin authority through the same helper;
- recognized live plugin generations then enter `plugin_callback_context()`;
- that context now installs the host budget beside the existing immutable package,
  namespace, generation, and rollback state.

Focused regressions directly exercise source, `init`, `deinit`, command,
keybinding, timer, and hook loops. Existing callback-authority suites exercise the
shared paths for prompt/macro and delayed registration behavior without adding a
second policy mechanism.

## What this does not claim

The in-process Python host is still not a hostile-code sandbox. The host budget
cannot preempt:

- a blocking or unbounded Python hostcall;
- expensive native code entered by one primitive;
- memory growth inside one primitive or retained object graph;
- process crashes, `os._exit`, signals, syscalls, or interpreter corruption; or
- tokenization/parsing work before dispatch begins.

Known filesystem, process, and caller-regex operations already use explicit
worker/deadline owners where their journeys justify it. Moving every plugin into
a process or Wasm runtime remains premature until one of the residual failures is
measured through a real plugin journey and the reduced rev0972 interface can be
carried across that boundary without importing the trusted bridge wholesale.

## Next high-value experiment

Choose one concrete plugin-accessible primitive that can block, allocate without
a useful bound, or enter native code. Reproduce its foreground/fault impact,
identify the resource owner and cancellation semantics, then select the smallest
honest correction: input preflight, bounded result construction, a killable
worker, asynchronous host operation, process boundary, or eventually a Wasm
component host. Instruction fuel should remain the first line of defense, not be
misrepresented as the last one.
