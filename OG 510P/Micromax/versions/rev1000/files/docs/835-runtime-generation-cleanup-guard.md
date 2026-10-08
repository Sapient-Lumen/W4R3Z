# Rev0877 runtime generation cleanup guard

Rev0877 closes the next practical cleanup hole after the rev0875/rev0876 group
commit work: generation-scoped delayed-state cleanup can no longer fail halfway
through unload or reload while leaving the manager to continue with a false
state transition.

## Problem

Runtime-group cleanup removes command/key/hook/timer-style registrations by
runtime group.  Generation cleanup removes delayed state attributed to one
loaded plugin generation: macros, clipboard rows, recent files, saved cursors,
palette MRU, prompt history, recovery stacks, active search, and help history.

Before this revision those generation removers were ordinary direct calls.  If a
remover raised after earlier cleanup had already changed state, the plugin
manager could stop in a mixed state.  The most dangerous case was unload: the
runtime group could already be swept, but the plugin record and module could
remain loaded because a later generation cleanup method raised.  That created a
loaded plugin with missing registrations and stale delayed state diagnostics.

## Change

- Added `RuntimeGenerationStateSnapshot` for only the delayed-state surfaces that
generation cleanup can mutate.
- Added `snapshot_runtime_generation_state()` and
  `restore_runtime_generation_state()`.
- Added `cleanup_plugin_generation_state()`, which reports every generation
  cleanup surface with the same structured operation-row shape used by group
  cleanup/retag.
- Added `PluginManager._cleanup_plugin_generation_or_restore()` for the reload
  pre-stage prune.
- Added `PluginManager._cleanup_loaded_plugin_state_or_restore()` so unload and
  reload-old cleanup restore both the group snapshot and generation snapshot if
  either cleanup family fails.
- Extended `mxaudit` to check the generation snapshot, report function, pre-stage
guard, and combined group/generation restore guard.

## Guarantees

A failed generation cleanup now:

- records a report with the failing surface and exception summary;
- keeps sweeping the remaining generation cleanup surfaces before reporting;
- raises `RuntimeGroupOperationError` on commit-critical paths;
- restores delayed-state surfaces from the narrow generation snapshot;
- restores runtime-group surfaces too when the failure occurs after group cleanup
  during unload or reload-old cleanup;
- leaves the old plugin as the advertised loaded generation during failed reload
  cleanup.

## Non-guarantees

This is still not hostile-code containment and not a full effect journal.  It does
not roll back arbitrary document edits, new buffers, file I/O, external effects,
or arbitrary mutations outside the enumerated delayed-state surfaces.  The broad
`RuntimeRegistrationSnapshot` remains the oracle for plugin source, lifecycle,
and callback transactions.  Rev0877 merely moves one more cleanup family away
from unguarded direct mutation and toward an explicit effect boundary.
