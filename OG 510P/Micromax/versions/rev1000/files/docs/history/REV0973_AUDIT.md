# Revision 0973 audit

## Priority judgment

Rev0972 deliberately deferred process or WebAssembly isolation until a resource
failure was measured. The first such failure was immediate and severe: valid
Micromax plugin code could run forever on the editor thread. Source evaluation,
lifecycle, retained callbacks, and graceful unload all had non-returning paths.
The apparent `VM.eval(step_budget=...)` defense was guest-controlled because
`set-budget` could clear the same stack.

The smallest honest correction is therefore deterministic host-owned instruction
fuel. It directly restores event-loop liveness for Micromax dispatch loops while
preserving the reduced plugin interface and existing transaction owners. A
process/Wasm host would be larger, harder to remove, and still would not by itself
solve a blocking host function without explicit cancellation.

## Severe or wasteful findings

| Finding | Consequence | Correction |
|---|---|---|
| Host and guest budgets shared `_budget_stack` | Code under `VM.eval(step_budget=N)` could execute `-1 set-budget` and remove the limiter | Add a private host-budget stack that language words cannot mutate |
| Only the innermost apparent budget was conceptually important | Nested evaluation could start a larger allowance and evade a caller if outer frames were not charged | Decrement every active host frame on every VM dispatch |
| `set-budget` replaced the entire script stack | Calling it inside `with-budget` destroyed the enclosing safety frame | Give the persistent base and nested script frames separate owners |
| Plugin source and lifecycle had no finite dispatch owner | A broken entry file or `init` prevented load from returning | Wrap the existing plugin execution context in fresh host fuel |
| Delayed surfaces could drift independently | Fixing commands alone would leave keys, timers, hooks, prompts, or macros as liveness bypasses | Install fuel once in the recognized plugin callback context used by the shared funnel |
| `deinit` could monopolize graceful unload | A user could not recover through the ordinary unload path | Bound deinit; on failure leave the live generation intact and retain force unload/revoke |
| Plugin `set-budget` persisted in the shared VM | One plugin turn could alter later editor/script execution | Snapshot and restore script budget state around every plugin turn |
| A permissive numeric conversion truncated `0.5` to `0` | A malformed positive tuning value could accidentally disable the guard | Reject fractional/boolean counts; malformed tuning falls back to the finite default |
| The first working tree accumulated unrelated terminal-cell code | Packaging it would mix an unreviewed renderer refactor into a liveness release | Reconstruct from a clean archive and reapply only the eight intended code/test files plus docs |
| Doctrine could have expanded into one limiter per callback type | Duplicate policy would drift and obscure the actual execution owner | Reuse `run_script_origin_callback()` / `plugin_callback_context()` and one plugin budget module |

## Execution-boundary review

`VM.host_step_budget()` is embedding state, not a Micromax word. `VM.eval()` uses
it when a host supplies `step_budget`. `_consume_step()` charges the persistent
script base, every nested script frame, and every host frame independently.
Language code may tune its own base or create a narrower nested frame, but cannot
name the host stack.

Plugin source and each lifecycle word enter
`PluginManager._plugin_execution_context()`, which already owns exact package
bytes, namespace order, writable dictionary, generation identity, runtime group,
and script authority. Adding fuel there keeps failure rollback on the existing
transaction. Retained plugin callbacks enter `Editor.plugin_callback_context()`
inside `run_script_origin_callback()`, so commands, keys, timers, hooks,
prompt-origin operations, and macro replay share the same boundary.

Host-budget frames unwind in `finally`. Source/init exhaustion does not commit a
candidate. Delayed callback exhaustion restores dictionary and managed runtime
state. Deinit exhaustion raises before cleanup claims success and leaves the
plugin live; force unload/revoke remains the host-owned escape route. Focused
journeys verify the VM can evaluate ordinary code after each interruption.

## Performance and tuning review

Five local tight-loop samples per budget produced:

| Steps | Median cutoff | Range |
|---:|---:|---:|
| 1,000 | 1.41 ms | 1.39–1.87 ms |
| 10,000 | 16.18 ms | 14.45–17.42 ms |
| 100,000 | 146.81 ms | 145.55–155.92 ms |

The 100,000-step default is intentionally an embedding attribute, not another
user option or registry row. Missing and malformed values fail safe. A host may
explicitly use an integer `<= 0` only when it accepts unbounded in-process
execution or supplies stronger containment.

No wall-clock equivalence is promised. Different primitives can do radically
different work per dispatch, and one primitive may not return at all.

## Research judgment

Current Wasmtime documentation distinguishes deterministic fuel from
lower-overhead, non-deterministic epoch interruption. More importantly, it states
that neither fuel nor epochs interrupt execution blocked inside a host call; the
embedder must own timeout, cancellation, or asynchronous yielding. Micromax
adopts the same boundary description rather than treating instruction counting
as universal containment.

Official sources checked 2026-07-18:

- https://docs.wasmtime.dev/examples-interrupting-wasm.html
- https://docs.wasmtime.dev/api/wasmtime/struct.Config.html

## Residual risk

- A blocking or expensive Python/native hostcall can still monopolize the editor
  after one dispatch enters it.
- Fuel does not cap allocation or retained object graphs inside one primitive.
- Tokenization/parsing precede dispatch; existing package/source byte ceilings
  bound input size but not every parser cost shape.
- The plugin host remains one Python process and does not contain syscalls,
  signals, `os._exit`, interpreter corruption, or process crashes.
- Script-budget restoration isolates plugin mutations but script budgets remain
  cooperative controls, not the authority boundary.
- The measured default is machine/implementation tuning, not a stable timing API.

## Recommended next correction

Select one plugin-accessible primitive that can block, allocate without a useful
bound, or enter expensive native code. Capture the real journey and determine
whether the smallest owner is input preflight, bounded result construction,
async cancellation, a killable worker, process isolation, or a Wasm component.
Carry rev0972's reduced import/surface contract and rev0973's fuel across any
stronger boundary instead of exposing the trusted bridge wholesale.
