Rev0893 note: saved plugin macro slots now stale-check by generation and ed.after enforces a pending timer budget.

# Worklist (rev0893)

## Landed this revision

- Added stale-generation detection for saved macro slots using the same authority model as delayed callbacks and active interactions.
- Refused and cleared reinserted saved macro slots from retired plugin generations before playback/read/list/detail exposure.
- Centralized macro slot store/clear helpers so cleanup and user surfaces preserve the stable `last` alias consistently.
- Routed `ed.after` through `Editor.schedule_timer_checked()` and added `max_pending_timers` as a host-owned pending-work budget.
- Added focused tests for stale macro reinsertion and timer-budget exhaustion/recovery.
- Extended `mxaudit --check` with retired-macro and timer-budget seams.

## Lane 0 — remaining resource handles

Dictionary lookup, direct saved XTs, generated callbacks, active delayed interactions, and saved macros now fail or clean up by plugin generation. Continue searching for plugin-owned objects that are not words, callback rows, active interactions, macro steps, or metadata-only diagnostics.

Stop condition: every plugin-owned resource handle either routes through a live-generation check, is removed/retagged by generation cleanup with preservation tests, or is explicitly metadata-only.

## Lane 1 — one real transaction split

Do not add more registry doctrine first. Pick one mutable family still covered by the broad source/lifecycle snapshot, build typed capture/commit/abort helpers, and prove parity against the broad oracle with focused tests.

Stop condition: one family leaves `RuntimeRegistrationSnapshot` ownership without broadening rollback or touching unrelated trusted state.

## Lane 2 — budgets before isolation theater

Add small host-owned budgets where plugins can allocate or block through legitimate APIs: payload/result sizes, output capture, prompt rows, buffer creation, cancellation/timeout surfaces, and any remaining pending callback queues.

Stop condition: common in-process denial-of-service paths have visible limits even before a process or Wasm boundary exists.

## Lane 3 — release confidence and doc compaction

Keep evidence useful but smaller: lock inputs, add focused CI/provenance, and consolidate older per-revision notes by subsystem.

Stop condition: the archive can state what was tested and built reproducibly, while docs grow slower than source.

## Prior revision handoff

Rev0892 note: active delayed interactions now snapshot, restore, and clean up by plugin generation; stale prompt/qreplace/open-url replies clear retired objects.

# Worklist (rev0892)

## Landed this revision

- Added `RuntimeInteractionGenerationSnapshot` for active keymodes, prompts, query-replace sessions, and pending URL confirmations owned by one plugin root/generation.
- Added generation cleanup for delayed interaction rows so reload/unload prunes old active interaction state without sweeping unrelated trusted/user rows.
- Added stale authority denial for prompt/qreplace/open-url responses and prompt-origin actions.
- Cleared stale prompt, qreplace, and pending URL state after denial.
- Added preservation tests for scoped interaction restore and reinserted retired prompt/qreplace/open-url objects.
- Extended `mxaudit --check` with generation-interaction cleanup and retired-interaction response seams.

## Lane 0 — remaining non-interaction stale handles

Dictionary lookup, direct saved XTs, generated callbacks, and active delayed interactions now fail or clean up by plugin generation.  Continue searching for plugin-owned resource handles that are neither executable callbacks nor active interaction rows.

Stop condition: every plugin-owned resource handle either routes through a live-generation check, is removed/retagged by generation cleanup with preservation tests, or is explicitly metadata-only.

## Lane 1 — one real transaction split

Do not add more registry doctrine first.  Pick one mutable family still covered by the broad source/lifecycle snapshot, build typed capture/commit/abort helpers, and prove parity against the broad oracle with focused tests.

Stop condition: one family leaves `RuntimeRegistrationSnapshot` ownership without broadening rollback or touching unrelated trusted state.

## Lane 2 — budgets before isolation theater

Add small host-owned budgets where plugins can allocate or block through legitimate APIs: payload/result sizes, output capture, pending callbacks/timers, prompt rows, buffer creation, and cancellation/timeout surfaces.

Stop condition: common in-process denial-of-service paths have visible limits even before a process or Wasm boundary exists.

## Lane 3 — release confidence and doc compaction

Keep evidence useful but smaller: lock inputs, add focused CI/provenance, and consolidate older per-revision notes by subsystem.

Stop condition: the archive can state what was tested and built reproducibly, while docs grow slower than source.

## Prior revision handoff

Rev0891 note: deferred plugin callbacks now reject retired generations before executing callback bodies.

# Worklist (rev0891)

## Landed this revision

- Added a shared stale-generation check for plugin-origin deferred callbacks.
- Stopped captured retired keybindings from running after reload, even when their action spec would otherwise succeed without package-local includes.
- Routed script-originated hook handlers and timers through `run_script_origin_callback()` so stale-generation behavior is shared instead of duplicated.
- Added preservation tests for captured retired keybinding, hook-handler, and timer-task objects that bypass normal cleanup.
- Extended `mxaudit --check` and human audit output with the retired deferred-callback seam.

## Lane 0 — remaining stale resource handles

Direct saved XTs fail with `Retired execution token`; generated deferred callbacks fail with `stale plugin callback` once their plugin generation is retired.  The remaining risk is narrower: objects that carry plugin-owned data but execute or mutate state without going through either guard.

Stop condition: every plugin-owned resource handle either routes through a live-generation check, is metadata-only, or is removed/retagged by generation cleanup with a preservation test.

## Lane 1 — one real transaction split

Do not add more registry doctrine first.  Pick one mutable family still covered by the broad source/lifecycle snapshot, build typed capture/commit/abort helpers, and prove parity against the broad oracle with focused tests.

Stop condition: one family leaves `RuntimeRegistrationSnapshot` ownership without broadening rollback or touching unrelated trusted state.

## Lane 2 — budgets before isolation theater

Add small host-owned budgets where plugins can allocate or block through legitimate APIs: payload/result sizes, output capture, pending callbacks/timers, prompt rows, buffer creation, and cancellation/timeout surfaces.

Stop condition: common in-process denial-of-service paths have visible limits even before a process or Wasm boundary exists.

## Lane 3 — release confidence and doc compaction

Keep evidence useful but smaller: lock inputs, add focused CI/provenance, and consolidate older per-revision notes by subsystem.

Stop condition: the archive can state what was tested and built reproducibly, while docs grow slower than source.

## Prior revision handoff

Rev0890 note: successful plugin reload/unload now tombstones retired committed wordlists, scrubs their word authority, and bounds restricted package fingerprinting.

# Worklist (rev0890)

## Landed this revision

- Replaced unbounded old committed plugin wordlist retention with bounded `PluginWordlistTombstone` metadata.
- Removed retired wordlists from `vm.wordlists`, `vm.wordlist_names`, and search order on successful reload/unload.
- Added `_forget_wordlist_authority()` so dictionary-keyed provenance is live-only after a wordlist is retired.
- Marked retired `Word` objects so direct saved XTs fail with a clear stale-token error.
- Made `plugin info NAME` report retired wordlist and compacted word counts.
- Added file-count and total-byte budgets to restricted package fingerprinting so manual grant checks cannot walk/hash arbitrarily large plugin trees.
- Added focused tests and `mxaudit --check` seams for both runtime tombstones and package budgets.

## Lane 0 — remaining stale reference observability

Retired wordlists are no longer reachable through VM dictionary lookup after successful reload/unload, and direct saved XTs now fail with a stale-token error.  The next risk is other references outside dictionary lookup: callback records, deferred cells, resource handles, or any stale pointer not yet covered by the retired-word marker.

Stop condition: the repo can enumerate or test each callback/deferred/resource escape pattern; stale dictionary lookup stays dead; surviving references either have a justified live handle or fail with a clear stale-plugin-generation error.

## Lane 1 — executable effect lifecycle contract

Deliver one machine-readable matrix, not another doctrine pile:

- classify each public hostcall and delayed state family;
- name capability, authority key, owner/resource identity, persistence, reversibility, and schema/stability version;
- state discovery, approval, load, callback, commit, abort, reload, deinit, unload, revoke, and crash behavior;
- generate concise docs and audit checks from the same source.

Stop condition: every public effect says what is staged, reversible, undoable, retained, removed, persisted, or irreversible; no API promises rollback broader than its implementable effect class.

## Lane 2 — source/lifecycle transaction narrowing

Live callbacks are scoped, and dictionary provenance is now coupled to dictionary rollback. Failed plugin source loading, lifecycle hooks, and discarded deinit mutations still use the 40-field broad registration snapshot.

Stop condition: one typed effect family moves to a preservation-tested scoped transaction, differential tests compare it against the broad oracle, and unrelated trusted state is not captured or rewound.

## Lane 3 — public extension contract and resource budgets

Deliverables:

- stable/experimental/internal API tiers;
- versioned lifecycle and hostcall schemas with explicit imports/exports;
- compatibility, feature negotiation, deprecation, and persistence migration rules;
- per-plugin capability inventory and diagnostics;
- guest/host payload, output, pending-work, memory-sensitive resource, timeout, and cancellation budgets.

Stop condition: plugins target documented contracts rather than incidental `Editor` internals, and a plugin cannot obtain unbounded host allocation or indefinite blocking merely by staying within instruction fuel.

## Lane 4 — release confidence and provenance

The repo still lacks a dependency lock, CI workflow, hosted provenance, and a fresh complete aggregate manifest.

Stop condition: fast policy/schema lanes, package/install lanes, subprocess/CLI lanes, and aggregate release evidence are separately named and reproducible; archive revision and package version have a written policy; output artifacts carry digests and build records.

## Lane 5 — reduce cloudtainer self-overhead

Documentation exceeds source by line count, root revision notes continue to grow, and evidence orchestration is itself a large subsystem.

Stop condition: living contracts plus the machine revision ledger replace most new micro-notes; historical notes are bundled by epoch/subsystem; audit metrics expose docs/evidence budgets; at least one consolidation deletes more maintenance surface than it adds.

## Lane 6 — contract-backed monolith cut

Stop condition: one typed plugin/effect coordinator or hostcall family is extracted behind existing contracts and preservation tests, with a measured reduction in `Editor` methods/state ownership rather than another forwarding layer.
