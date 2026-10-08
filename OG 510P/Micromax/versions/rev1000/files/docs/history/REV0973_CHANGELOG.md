# Revision 0973 changelog

## Unbypassable VM host budgets

- Split script-visible execution state into a persistent `set-budget` base and
  nested `with-budget` frames.
- Added a separate embedding-owned host-budget stack and made every dispatched VM
  step consume every active host frame.
- Made `VM.eval(step_budget=...)` enter the host stack, so guest code cannot erase
  the host limit with `-1 set-budget` or reset an outer allowance through nested
  evaluation.
- Rejected fractional and boolean host step counts instead of silently truncating
  them.
- Preserved standalone unlimited execution when no script or host budget exists.

## Plugin execution liveness

- Added `plugin_execution_budget.py` as the single owner of the finite plugin-turn
  default and script-budget-state restoration.
- Installed a fresh default 100,000-step host budget around plugin entry source,
  `preinit`, `init`, `postinit`, and `deinit`.
- Installed the same boundary for recognized live retained callbacks through
  `Editor.plugin_callback_context()`, covering commands, keybindings, timers,
  hooks, prompt-origin work, macro replay, and other shared delayed paths.
- Kept malformed, fractional, boolean, and missing tuning on the safe finite
  default; only an explicit integer nonpositive value disables this guard.
- Preserved candidate-load rollback, callback dictionary/runtime rollback,
  graceful-unload failure semantics, and force-unload/revoke recovery.

## Language and portability refactor

- Fixed the latent case where `set-budget` inside `with-budget` replaced or
  cleared the enclosing frame.
- Made `budget` report script-owned limits only; embedding host frames stay
  private.
- Added a portability corpus case proving base-budget clearing cannot erase an
  active nested script frame.
- Updated the core registry and language/host documentation to distinguish
  cooperative script budgets from host authority.

## Audit, research, and scope control

- Reproduced non-returning plugin source, init, delayed command, and deinit paths
  before selecting the correction.
- Audited retained execution call sites and reused one existing callback funnel
  rather than adding per-surface budget registries.
- Measured a tight-loop 100,000-step cutoff at 146.81 ms median in the release
  container; recorded that this is tuning evidence, not a wall-clock contract.
- Reviewed current official Wasmtime deterministic-fuel, epoch, and blocking
  hostcall guidance.
- Rebuilt from a clean rev0972 extraction after detecting unrelated terminal-cell
  work-in-progress in the first working tree; the final editor diff contains only
  the budget import and callback context wrapper.
- Documented that blocking Python/native hostcalls, memory growth, parsing,
  syscalls, crashes, and interpreter corruption remain outside instruction fuel.

## Context curation

- Added `docs/930-plugin-fuel-unbypassable-callback-liveness.md` and decision D27.
- Updated the compact mission, handoff, repo map, security, host API, portability,
  roadmap, worklist, and behavior contracts.
- Moved the two oldest root-level recent evidence triplets, rev0964 and
  rev0965, into `docs/history/` and repaired their revision-index paths so
  the generated handoff remains inside its 64-document ceiling.
