Rev0893 note: saved macros from retired plugin generations now prune before playback/read/list exposure, and ed.after has a host-owned pending timer budget.

Latest tiny landing (rev0893): stale plugin macro slots now fail closed and clear themselves even if reinserted after reload/unload, macro slot mutation goes through stable last-preserving helpers, and timer scheduling refuses to exceed max_pending_timers before queuing another delayed callback.

# TODO (rev0893)

- [x] Add stale-generation detection for saved macro slots.
- [x] Drop reinserted retired plugin macros before playback/read/list/detail exposure.
- [x] Refactor macro slot store/clear paths through stable last-preserving helpers.
- [x] Route `ed.after` through `Editor.schedule_timer_checked()`.
- [x] Add a host-owned `max_pending_timers` budget with scheduling/cancel tests.
- [x] Extend `mxaudit --check` with retired macro playback and timer budget seams.
- [x] Record the landing in `docs/851-stale-macro-timer-budget.md`.
- [x] package rev0893 with the required filename structure.

## Next up (high leverage)

1. **Finish remaining resource-handle enumeration.** Dictionary lookup, direct XTs, generated callbacks, active interactions, and saved macros now have stale-generation refusal or cleanup; search for plugin-owned objects outside those lanes.
2. **Split one broad source/lifecycle effect family.** Pick one mutable family still owned by `RuntimeRegistrationSnapshot`, add typed capture/commit/abort helpers, and prove parity against the broad oracle.
3. **Add more host-owned budgets.** Bound hostcall payload/result sizes, output capture, prompt rows, buffer creation, and cancellation/timeout surfaces before process or Wasm isolation work.
4. **Build only executable lifecycle contracts.** Generate the smallest useful matrix from live code paths where it removes implementation risk; avoid standalone registry paperwork.
5. **Make release evidence reproducible.** Add lock/CI/package-inspection/provenance lanes and define archive-revision versus package-version policy.
6. **Compact docs/evidence overhead.** Consolidate older micro-notes by subsystem and count deletion/consolidation as progress.
7. **Cut one contract-backed responsibility out of `Editor`.** Extract only after tests prove the new owner controls policy, state, and rollback rather than forwarding back to the monolith.

## Prior revision handoff

Rev0892 note: delayed prompt/qreplace/open-url/keymode state now snapshots and cleans up by plugin generation, and stale interaction replies clear the retired object.

Latest tiny landing (rev0892): `RuntimeInteractionGenerationSnapshot` scopes active interaction rows by plugin root/generation; reload/unload cleanup removes old prompt/qreplace/open-url/keymode state, and reinserted retired prompt, query-replace, or URL-confirmation objects refuse and clear themselves.

# TODO (rev0892)

- [x] Add a generation-scoped interaction snapshot for active keymodes, prompts, query-replace sessions, and pending URL confirmations.
- [x] Include delayed interaction cleanup in plugin generation cleanup alongside recovery, recent, palette, prompt-history, saved-cursor, clipboard, search, help-history, and macro rows.
- [x] Add stale authority denial for prompt/qreplace/open-url responses so retired plugin generations cannot borrow ambient user/editor authority.
- [x] Clear stale prompt, qreplace, and pending URL interaction objects after denial so repeated responses do not keep hitting the same retired object.
- [x] Add preservation tests for generation-scoped interaction restore and reinserted retired prompt/qreplace/open-url objects.
- [x] Extend `mxaudit --check` with generation-interaction and retired-interaction seams.
- [x] Record the landing in `docs/850-generation-interaction-cleanup.md`.
- [x] package rev0892 with the required filename structure.

## Next up (high leverage)

1. **Finish non-interaction stale-handle enumeration.** Direct XTs, generated callbacks, and active interactions now fail or clean up by generation; search for resource handles that bypass all three.
2. **Narrow one broad source/lifecycle effect family.** Pick a real mutable family from `RuntimeRegistrationSnapshot`, make typed capture/commit/abort helpers, and keep the broad snapshot only as a differential oracle until parity is proved.
3. **Add host payload and pending-work budgets.** Bound hostcall argument/result payloads, output capture, pending timers/callbacks, prompt rows, buffer creation, and cancellation/timeout surfaces before process/Wasm isolation work.
4. **Build only executable lifecycle contracts.** Generate the smallest useful effect matrix from live code paths where it removes implementation risk; avoid standalone registry paperwork.
5. **Make release evidence reproducible.** Add lock/CI/package-inspection/provenance lanes and define archive-revision versus package-version policy.
6. **Compact docs/evidence overhead.** Consolidate older micro-notes by subsystem and count deletion/consolidation as progress.
7. **Cut one contract-backed responsibility out of `Editor`.** Extract only after tests prove the new owner controls policy, state, and rollback rather than forwarding back to the monolith.

## Prior revision handoff

Rev0891 note: retired plugin generations now refuse deferred callback execution through the shared callback runner.

Latest tiny landing (rev0891): generated plugin callbacks that carry a root and generation now refuse to execute after that generation is retired; keybindings, hooks, and timers share the same host runner.

# TODO (rev0891)

- [x] Add a generation-scoped stale plugin callback guard before deferred callback bodies run.
- [x] Route script-originated timer execution through the shared callback runner.
- [x] Route script-originated hook handlers through the shared callback runner when the editor host is available.
- [x] Add preservation tests for captured retired keybindings, reinserted retired hook handlers, and reinserted retired timer tasks.
- [x] Preserve legacy malformed-root behavior: rows without a generation still lose private package-root authority and fail through normal filesystem capability checks.
- [x] Extend `mxaudit --check` with the retired deferred-callback seam.
- [x] Record the runtime landing in `docs/849-retired-deferred-callback-guard.md`.
- [x] package rev0891 with the required filename structure.

## Next up (high leverage)

1. **Finish resource-handle enumeration.** The main stale execution lanes now go through retired `Word` checks or `run_script_origin_callback()`; find any remaining handles that carry plugin-owned data but bypass both.
2. **Narrow one broad source/lifecycle effect family.** Pick a real mutable family from `RuntimeRegistrationSnapshot`, make a typed capture/commit/abort helper, and use the broad snapshot only as a differential oracle.
3. **Add host payload and pending-work budgets.** Bound hostcall argument/result payloads, output capture, pending timers/callbacks, prompt rows, and buffer creation before process/Wasm isolation work.
4. **Build the executable effect lifecycle matrix only where it removes code risk.** Start with the plugin load/reload/unload path and generate audit checks from it; avoid standalone registry bureaucracy.
5. **Make release evidence reproducible.** Add a standards-based lock, focused CI, package inspection, artifact digests/provenance, and an explicit archive-revision versus package-version policy.
6. **Compact docs/evidence overhead.** Consolidate historical notes by subsystem and keep new revision notes short unless they encode a live contract.
7. **Cut one contract-backed piece out of `Editor`.** Extract a typed coordinator only after tests prove it owns policy, state, and rollback rather than forwarding calls back to the monolith.

## Prior revision handoff

Rev0890 note: successful plugin reload/unload now retires committed plugin wordlists into bounded metadata tombstones and scrubs dictionary-keyed word authority, avoiding unbounded executable `Word` retention across generations.

Latest tiny landing (rev0890): `PluginManager` now replaces unloaded/replaced plugin wordlists with compact `PluginWordlistTombstone` rows, keeps the live VM wordlist count flat across repeated reloads, and exposes small diagnostic rows without retaining executable definitions. Restricted-workspace package fingerprinting also has file-count and total-byte budgets so an approval check cannot walk or hash arbitrarily large plugin trees.

# TODO (rev0890)

- [x] Retire old committed plugin wordlists on successful reload and unload.
- [x] Preserve compact plugin/generation/wid/word-name/span/package tombstones without retaining `Word` objects.
- [x] Scrub `_word_authority` rows for retired wordlists so dictionary-keyed provenance remains live-only.
- [x] Mark retired plugin `Word` objects so direct saved execution tokens fail clearly instead of running old code.
- [x] Add reload/unload preservation tests proving live wordlist count stays flat and tombstones carry metadata.
- [x] Add package fingerprint file-count and total-byte budgets with direct failure tests.
- [x] Extend `mxaudit --check` with wordlist-tombstone and package-budget invariants.
- [x] Record the runtime-retention/budget landing in `docs/848-retired-wordlist-tombstones-package-budgets.md`.
- [x] package rev0890 with the required filename structure.

## Next up (high leverage)

1. **Track remaining stale reference paths explicitly.** Direct saved XTs now fail after their plugin wordlist is retired; callbacks, deferred/resource handles, and other reference escape patterns still need observability before stronger revocation.
2. **Build the executable effect lifecycle matrix.** Every public hostcall and delayed-state family needs an effect class, capability, authority key, stage/commit/abort/unload/revoke/crash behavior, persistence rule, reversibility, schema version, and stability tier.
3. **Split remaining broad source/lifecycle transactions carefully.** Use typed effect slices and differential tests against the 40-field `RuntimeRegistrationSnapshot`; keep the broad snapshot as an oracle until parity is proved.
4. **Version the public extension contract.** Separate stable, experimental, and internal surfaces; define typed imports/exports, feature negotiation, schema migration, and per-plugin capability diagnostics before process/Wasm work.
5. **Add more resource budgets.** Bound guest-to-host payloads, output capture, pending callbacks/timers, buffer creation, and blocking host operations; instruction fuel alone is not a wall-clock or memory boundary.
6. **Make release evidence reproducible.** Add a standards-based lock, focused CI, package inspection, artifact digests/provenance, and an explicit archive-revision versus package-version policy.
7. **Compact docs and evidence machinery.** Prefer living contracts plus a machine ledger over another root note per micro-revision; measure deletion/consolidation as progress.
8. **Make one contract-backed monolith cut.** Extract a typed plugin/effect coordinator with preservation tests and require a measured reduction in `Editor`, not a forwarding shell.

## Prior revision handoff

Rev0889 note: VM dictionary rollback now restores dictionary-keyed word provenance, closing a source/lifecycle leak that left stale `_word_authority` rows after transient plugin definitions failed.

Latest tiny landing (rev0889): `VmDictionarySnapshot` carries optional word-authority state. Dictionary restore now reinstates topology first and then filters/restores provenance against live words. Failed source loads, failed reload lifecycle hooks, failed unload `deinit`, and failed live callbacks share this invariant; callback-only duplicate restoration was removed.

# TODO (rev0889)

- [x] Reproduce stale `_word_authority` rows after failed plugin source evaluation.
- [x] Attach word provenance to `VmDictionarySnapshot` rather than another broad registration field.
- [x] Restore provenance only after dictionary topology so dead transient keys are filtered.
- [x] Remove duplicate callback-only word-authority rollback.
- [x] Add preservation tests for failed source, failed staged lifecycle, and failed unload `deinit` paths.
- [x] Extend `mxaudit --check` with the dictionary/provenance invariant.
- [x] Record the mission, missing contract, unbounded wordlist retention, docs/evidence waste, research, and sequencing in `docs/847-cloudtainer-heart-gap-waste-word-authority.md`.
- [x] package rev0889 with the required filename structure.

## Next up (high leverage)

1. **Bound retired plugin wordlists.** Add liveness/reference observability, then replace unloaded/replaced executable wordlists with bounded provenance tombstones. Preserve stale-callback and direct-XT safety in tests.
2. **Build the executable effect lifecycle matrix.** Every public hostcall and delayed-state family needs an effect class, capability, authority key, stage/commit/abort/unload/revoke/crash behavior, persistence rule, reversibility, schema version, and stability tier.
3. **Split remaining broad source/lifecycle transactions carefully.** Use typed effect slices and differential tests against the 40-field `RuntimeRegistrationSnapshot`; keep the broad snapshot as an oracle until parity is proved.
4. **Version the public extension contract.** Separate stable, experimental, and internal surfaces; define typed imports/exports, feature negotiation, schema migration, and per-plugin capability diagnostics before process/Wasm work.
5. **Add resource budgets.** Bound guest-to-host payloads, output capture, pending callbacks/timers, buffer creation, and blocking host operations; instruction fuel alone is not a wall-clock or memory boundary.
6. **Make release evidence reproducible.** Add a standards-based lock, focused CI, package inspection, artifact digests/provenance, and an explicit archive-revision versus package-version policy.
7. **Compact docs and evidence machinery.** Prefer living contracts plus a machine ledger over another root note per micro-revision; measure deletion/consolidation as progress.
8. **Make one contract-backed monolith cut.** Extract a typed plugin/effect coordinator with preservation tests and require a measured reduction in `Editor`, not a forwarding shell.
