# Archived worklist through rev0951

Preserved before the rev0952 living-document compaction.

---

Rev0951 note: mxtimely summaries now distinguish partial prefixes from completed lanes, and mxaudit hard-checks completion-honest summary evidence.

# Worklist (rev0951)

## Landed this revision

- Read the datacube as a mission/evidence system, not just a code tree.
- Researched current timeout, cancellation, workspace-trust, WASI, Starlark, WIT, OWASP resource-consumption, and SLSA provenance guidance.
- Found and corrected the cloudtainer handoff truth bug where an outer-stopped `make timely` prefix could leave fresh summary JSON with `ok: true`.
- Changed `tools/mxtimely.py` to emit summary v3 with `status`, `complete`, `planned_steps`, `planned_step_count`, `completed_steps`, and `pending_steps`.
- Made interrupted prefixes report `status: partial`, `complete: false`, and `ok: false`; completed skip-doctor lanes still pass for their own planned steps.
- Added focused mxtimely summary tests and a release-hygiene audit check named `timely_summary_completion_honest`.
- Archived the old root TODO trail through rev0950 in `docs/history/TODO-through-rev0950.md`.
- Recorded the mission/gap/waste diagnosis and validation in `docs/909-timely-summary-completion-honesty.md`.

## Next up (high leverage)

1. Add an actual-summary verifier that reads `.artifacts/mxtimely-summary.json` and classifies full pass, skip-doctor pass, failure, or partial prefix.
2. Compact duplicated owner-row validation helpers in `effect_contracts.py` only after tests pin the shared behavior.
3. Decide whether successful plugin option and mark writes need explicit ownership or should stay committed editor effects.
4. Choose the next runtime survivor by concrete retained authority, rollback failure, or stale disclosure; avoid registry-completeness work.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0950 note: named marks now route through an editor-owned owner seam, the generated effect/resource contract exposes `ed.mark-register`, and broad rollback no longer double-restores recent files.

# Worklist (rev0950)

## Landed this revision

- Researched current resource-lifetime and workspace-trust references and applied them to retained mark navigation authority.
- Added public `Editor.snapshot_mark_group_state` / `Editor.restore_mark_group_state` owner methods over named marks and mark authority sidecars.
- Refactored plugin runtime broad registration restore and scoped group rollback to prefer the public editor owner seam before legacy private fallback.
- Removed a redundant `restore_recent_files_group_state` call from the runtime group restore path.
- Added focused tests proving broad restore and scoped group rollback call the public mark owner route and preserve unrelated trusted/during rows.
- Extended `mxaudit --check` with `mark_owner_snapshot_present` and human output `mark-owner=True`.
- Expanded the generated effect/resource contract with `ed.mark-register`, derived from live owner methods, mark capabilities, rollback lanes, and audit flags.
- Regenerated the installed `docs/33-effect-resource-contract.md` help surface and recorded the landing in `docs/908-mark-owner-contract.md`.

## Next up (high leverage)

1. Compact duplicated owner-row validation helpers in `effect_contracts.py` only after tests pin the shared behavior.
2. Decide whether successful plugin option and mark writes need explicit ownership or should stay committed editor effects.
3. Choose the next runtime survivor by concrete retained authority, rollback failure, or stale disclosure; avoid registry-completeness work.
4. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0947 note: recovery rollback now routes through an editor-owned owner seam and the generated contract exposes a recovery owner row.

# Worklist (rev0947)

## Landed this revision

- Researched current resource-lifetime, resource-consumption, and workspace-trust guidance and applied it to retained cursor/selection recovery authority.
- Added `RecoveryRegisterEntry`, `RecoveryBufferRegisterSnapshot`, and `RecoveryRegisterSnapshot` as the editor-owned selection/jump recovery row/value snapshot.
- Added editor group/generation recovery snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration recovery rollback to call the editor owner seam before legacy raw fallback.
- Fixed broad recovery-register restore so full restore replaces mutated rows instead of duplicating captured rows.
- Extended `mxaudit --check` with `recovery_owner_snapshot_present` and human output `recovery-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.recovery-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/905-recovery-owner-contract.md`.

## Next up (high leverage)

1. Render selected generated effect/resource rows in installed help instead of adding more revision notes.
2. Consolidate duplicated owner-route fallback patterns only where live tests prove the shared helper preserves group/generation semantics.
3. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0946 note: help-history rollback now routes through an editor-owned owner seam and the generated contract exposes a help-history owner row.

# Worklist (rev0946)

## Landed this revision

- Researched current resource-lifetime, resource-consumption, and workspace-trust guidance and applied it to retained help-navigation authority.
- Added `HelpHistoryRegisterEntry` / `HelpHistoryRegisterSnapshot` as the editor-owned help-history row/value snapshot.
- Added editor group/generation help-history snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration help-history rollback to call the editor owner seam before legacy raw fallback.
- Extended `mxaudit --check` with `help_history_owner_snapshot_present` and human output `help-history-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.help-history-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/904-help-history-owner-contract.md`.

## Next up (high leverage)

1. Render selected generated effect/resource rows in installed help instead of adding more revision notes.
2. Consolidate duplicated owner-route fallback patterns only where live tests prove the shared helper preserves group/generation semantics.
3. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0945 note: command-palette recent rollback now routes through an editor-owned owner seam and the generated contract exposes a palette-recent owner row.

# Worklist (rev0945)

## Landed this revision

- Researched current resource-lifetime, resource-consumption, and workspace-trust guidance and applied it to retained command/action palette launch authority.
- Added `PaletteRecentRegisterEntry` / `PaletteRecentRegisterSnapshot` as the editor-owned palette-recent row/value snapshot.
- Added editor group/generation palette-recent snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration palette-recent rollback to call the editor owner seam before legacy raw fallback.
- Extended `mxaudit --check` with `palette_recent_owner_snapshot_present` and human output `palette-recent-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.palette-recent-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/903-palette-recent-owner-contract.md`.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help instead of adding more revision notes.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0944 note: saved-cursor rollback now routes through an editor-owned owner seam and the generated contract exposes a saved-cursor owner row.

# Worklist (rev0944)

## Landed this revision

- Researched current resource-consumption, workspace-trust, Python snapshot/copy, and metadata/privacy exposure guidance and applied it to retained saved-cursor path+position authority.
- Added `SavedCursorRegisterEntry` / `SavedCursorRegisterSnapshot` as the editor-owned saved-cursor row/value snapshot.
- Added editor group/generation saved-cursor snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration saved-cursor rollback to call the editor owner seam before legacy raw fallback.
- Extended `mxaudit --check` with `saved_cursor_owner_snapshot_present` and human output `saved-cursor-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.saved-cursor-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/902-saved-cursor-owner-contract.md`.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help instead of adding more revision notes.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0943 note: recent-files rollback now routes through an editor-owned owner seam and the generated contract exposes a recent-files owner row.

# Worklist (rev0943)

## Landed this revision

- Researched current sensitive-information, private-information, resource-consumption, and WIT resource-owner guidance and applied it to retained recent-file path authority.
- Added `RecentFilesRegisterEntry` / `RecentFilesRegisterSnapshot` as the editor-owned recent-file row/value snapshot.
- Added editor group/generation recent-files snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration recent-files rollback to call the editor owner seam before legacy raw fallback.
- Extended `mxaudit --check` with `recent_files_owner_snapshot_present` and human output `recent-files-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.recent-files-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/901-recent-files-owner-contract.md`.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help instead of adding more revision notes.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0942 note: prompt-history rollback now routes through an editor-owned owner seam and the generated contract exposes a prompt-history owner row.

# Worklist (rev0942)

## Landed this revision

- Researched current resource-lifetime, retained-text/logging, package-resource lifetime, and WIT resource-owner guidance and applied it to retained prompt-history replay authority.
- Added `PromptHistoryRegisterEntry` / `PromptHistoryRegisterSnapshot` as the editor-owned prompt-history row/value snapshot.
- Added editor group/generation prompt-history snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration prompt-history rollback to call the editor owner seam before legacy raw fallback.
- Extended `mxaudit --check` with `prompt_history_owner_snapshot_present` and human output `prompt-history-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.prompt-history-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/900-prompt-history-owner-contract.md`.

## Next up

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retention, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help so authority truth is product-visible.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0941 note: active-search rollback now routes through an editor-owned owner seam and the generated contract exposes an active-search owner row.

# Worklist (rev0941)

## Landed this revision

- Researched current resource-consumption/resource-lifetime/component-resource guidance and applied it to active-search delayed navigation authority.
- Added `ActiveSearchRegisterSnapshot` as the editor-owned active-search query/provenance snapshot.
- Added editor group/generation active-search snapshot and restore owner methods.
- Refactored plugin-runtime group, generation, and broad registration search rollback to call the editor owner seam before legacy tuple fallback.
- Extended `mxaudit --check` with `active_search_owner_snapshot_present` and human output `active-search-owner=True`.
- Expanded the generated effect/resource contract with the live `ed.active-search-register` owner row.
- Added focused owner-route, audit, and effect-contract regressions.
- Recorded the landing in `docs/899-active-search-owner-contract.md`.

## Next up (high leverage)

1. Keep generated owner rows behavior-backed: live owner methods plus focused route tests first, contract row second.
2. Pick the next runtime survivor by concrete stale lifetime, authority clobber, retention, or rollback failure.
3. Render selected generated contract rows in installed help before adding more revision-note prose.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0940 note: first generated effect/resource contract slice now emits live host-effect budget/capability rows and is checked by audit.

# Worklist (rev0940)

## Landed this revision

- Researched current resource-consumption, subprocess-timeout, component-contract, WIT resource, and embedded-language guidance online.
- Added `src/micromax_editor/effect_contracts.py`, which generates high-risk host-effect/resource rows from live hostcall registry entries, capability registry entries, default budgets, regex defaults, the stdlib resource contract, and optional `mxaudit` evidence.
- Added `tools/mxeffects.py --json --check` and `make effect-contracts`.
- Refactored `tools/mxaudit.py --check` to validate the generated effect/resource contract as hard audit evidence.
- Updated `tools/mxcontext.py` to keep the contract generator in the curated handoff surface without growing the code list.
- Added `tests/test_effect_contracts.py` and extended audit/context coverage.
- Recorded the landing in `docs/898-generated-effect-resource-contract.md`.

## Next up (high leverage)

1. Expand the generated contract into owner rows only when live owner methods and tests can supply facts.
2. Consider active-search ownership next only if it removes a concrete stale lifetime, authority clobber, retention, or rollback failure.
3. Render selected generated contract rows in installed help instead of installing more revision notes.
4. Treat docs compaction and generated evidence as product work.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0939 note: deep cloudtainer audit refreshed the heart/gap/waste diagnosis and audit-checks curated entrypoint freshness.

# Worklist (rev0939)

## Landed this revision

- Read the datacube as a least-authority automation substrate rather than a terminal-editor project.
- Researched current resource-consumption, subprocess/cancellation, workspace-trust, embedded-language, component-contract, and supply-chain provenance guidance.
- Added `docs/897-cloudtainer-entrypoint-freshness-audit.md` with the heart, missing contract, waste, speculation, and next-change sequence.
- Refreshed `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, and this worklist to the current revision.
- Added curated entrypoint revision metrics to `tools/mxaudit.py`.
- Made `mxaudit --check` fail if `README.md`, `TODO.md`, `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, or `docs/43-worklist.md` point at a stale revision.
- Added focused JSON and human-output assertions in `tests/test_mxaudit.py`.

## Next up (high leverage)

1. Generate the first effect/resource-contract slice from live owner facts instead of adding a hand-maintained doctrine table.
2. Move the next raw runtime snapshot field behind a typed owner only when a concrete stale/lifetime or authority failure justifies it.
3. Promote resource/effect/security truth into installed help through living contracts, not by installing every micro-note.
4. Treat docs compaction and generated contract evidence as product work.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0934 note: prompt group/generation snapshot/restore now routes through editor-owned owner methods with audit coverage.

# Worklist (rev0934)

## Landed this revision

- Researched current resource-lifetime/resource-consumption guidance and applied it to the active prompt delayed interaction row.
- Added `PromptInteractionSnapshot` as the editor-owned active-prompt state object.
- Added group/generation prompt snapshot/restore owner methods on `Editor`.
- Refactored runtime group/generation interaction snapshot+restore to call those methods instead of directly reading/writing `Editor.prompt`.
- Added focused regressions proving runtime snapshot/restore routes through the prompt owner.
- Extended `mxaudit --check` with `prompt_owner_snapshot_present` and human output `prompt-owner=True`.
- Recorded the slice in `docs/892-prompt-owner-snapshot.md`.

## Next up (high leverage)

1. Consider a keymode owner value object only if it stays small and removes concrete runtime coupling.
2. Keep active-interaction owner work code-backed; avoid manual registries until generated owner facts exist.
3. Keep package locks/CI/signatures deferred until there is a real package lane.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0933 note: query-replace group/generation snapshot/restore now routes through editor-owned owner methods with session+cursor state coupled and audit coverage.

# Worklist (rev0933)

## Landed this revision

- Researched current resource-lifetime/resource-consumption guidance and applied it to the query-replace delayed interaction row.
- Added `QueryReplaceInteractionSnapshot` and `QueryReplaceInteractionCursorSnapshot` as editor-owned query-replace state objects.
- Added group/generation query-replace snapshot/restore owner methods on `Editor`.
- Refactored runtime group/generation interaction snapshot+restore to call those methods instead of directly reading/writing `Editor.qreplace`.
- Centralized query-replace cleanup so the session and visible primary selection clear together.
- Added focused regressions proving runtime snapshot/restore routes through the query-replace owner.
- Extended `mxaudit --check` with `qreplace_owner_snapshot_present` and human output `qreplace-owner=True`.
- Recorded the slice in `docs/891-qreplace-owner-snapshot.md`.

## Next up (high leverage)

1. Move prompt interaction snapshot/restore through owner methods only if it stays small and testable.
2. Keep the active-interaction lane code-backed; wait on registries until owner facts can be generated from live methods/tests.
3. Keep package locks/CI/signatures deferred until there is a real package lane.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0932 note: pending external-URL confirmation snapshot/restore now routes through editor-owned group/generation methods with audit coverage.

# Worklist (rev0932)

## Landed this revision

- Researched current resource-lifetime/resource-consumption guidance and applied it to the active external-URL confirmation row.
- Added `PendingOpenUrlInteractionSnapshot` plus editor group/generation snapshot/restore owner methods.
- Refactored runtime group/generation interaction snapshot+restore to use those owner methods instead of direct pending URL/source/authority field access.
- Reused the owner clear helper in group and generation cleanup paths.
- Added focused regressions proving runtime snapshot/restore routes through the owner methods.
- Extended `mxaudit --check` with `pending_open_url_owner_snapshot_present` and human output `open-url-owner=True`.
- Recorded the slice in `docs/890-pending-open-url-owner.md`.

## Next up (high leverage)

1. Move the next active-interaction family through owner methods only as a small code+test slice; prompt or query-replace are better candidates than another registry table.
2. Keep runtime budgets connected to visible recovery behavior and focused tests.
3. Return to package locks/CI/signatures only when there is a real package lane to protect.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0931 note: `qreplace all` now has a host-owned per-action replacement budget with visible recovery behavior and audit coverage.

# Worklist (rev0931)

## Landed this revision

- Researched current CWE resource-consumption/effective-lifetime guidance and applied it to a concrete delayed-interaction response seam.
- Added `qreplace.max` as a host-owned per-action replacement limit (`10000` default, `0` = explicit unlimited).
- Refactored `Editor.qreplace_all()` so one `all` response stops at the budget, keeps the session active at the next match, and emits a visible status message.
- Added regressions for budget stop/retry behavior and explicit unlimited all-replace behavior.
- Extended `mxaudit --check` with `qreplace_all_replacement_budget` and human output `qreplace-all-budget=True`.
- Recorded the slice in `docs/889-qreplace-all-budget.md`.

## Prior revision handoff

Rev0897 note: shared tool timeouts now reap escaped descendant process groups and the deep audit names the mission/correction path.

# Worklist (rev0897)

## Landed this revision

- Read the datacube as a mission/effect-lifecycle problem rather than a terminal-editor problem.
- Added `docs/855-cloudtainer-process-tree-timeout-audit.md` with the heart/missing/waste/change diagnosis plus online research notes.
- Fixed `tools/mxtoolrun.py` timeout teardown so nested tool children that create separate process groups are found through `/proc` descendant scanning and signaled before the direct child group.
- Added `tests/test_mxtoolrun.py::test_run_captured_timeout_reaps_detached_grandchild` to preserve the escaped-grandchild case.

## Next up (high leverage)

1. **Make timeout/process ownership auditable.** Add an `mxaudit --check` seam for descendant cleanup in the shared runner.
2. **Create the first generated effect-matrix slice.** Start with timers or prompt interactions and generate docs/audit coverage from live metadata.
3. **Add a host-owned payload/output budget.** Bound output capture or hostcall result sizes before chasing process/Wasm isolation.
4. **Consolidate revision notes by subsystem.** Treat deletion/compaction as progress.
5. **Add dependency lock, CI/package inspection, artifact digests, and version/revision policy.**
6. **Extract one contract-backed host owner from `Editor`.** Only after the effect matrix identifies its state, policy, and rollback behavior.

## Prior revision handoff

Rev0896 note: testing tools now share timed child-process handling and release manifests tell weaker handoff agents the next action.

# Worklist (rev0896)

## Landed this revision

- Added `tools/mxtoolrun.py` as the shared timed child-process, heartbeat, teardown, output-tail, and deterministic-environment helper for short-window test tools.
- Refactored `mxtimely` onto the shared helper and upgraded its summary JSON to include total elapsed time and the slowest step.
- Extended `mxrelease` manifests with per-batch command timing, aggregate timing, slowest-batch samples, and a machine-readable `next_action`.
- Added `make release-next` / `mxrelease --next` so a weaker model can ask the manifest what to do next.
- Added focused tests for the shared runner, timing summaries, next-action states, and Makefile/audit/context seams.
- Updated `mkrevzip` so compact timely and full-suite release evidence manifests survive handoff packaging.

## Prior revision handoff

Rev0895 note: short-window tooling now has a resumable splitting selected-file/node-batch full-suite release lane.

# Worklist (rev0895)

## Landed this revision

- Added `tools/mxrelease.py` as a bounded selected-file/node-batch full-suite release runner for constrained cloudtainer runs.
- Added `make release-suite` for resumable clean partial checkpoints, slow-batch and slow-file node splitting, and `make release-verify` for the complete/current release claim.
- Added `.artifacts/mxrelease-full-suite.json` as the default release evidence manifest.
- Reused the source/environment attestation path from `mxtest` so completed release evidence is invalidated by source changes.
- Wired the release runway into `mxcontext`, `mxaudit --check`, and Makefile contract tests.

## Prior revision handoff

Rev0894 note: bounded Python tooling now has a timely cloudtainer runway for short verification sessions.

# Worklist (rev0894)

## Landed this revision

- Added `tools/mxtimely.py` as a bounded Python handoff wrapper for constrained cloudtainer runs.
- Added `make timely` for context, audit, lint, quiet portability, and fast doctor checks.
- Added `make timely-tests` for an optional tiny resumable `mxtest` checkpoint that skips doctor to keep the lane short.
- Added `tools/mxportable.py --quiet` so portability checks can report a compact pass/fail summary.
- Narrowed default `mxdoctor` preflight to selected smoke, filesystem, hostcall, stale callback/macro, plugin reload, and mxtest-manifest seams.
- Wired the timely runway into `mxcontext` and `mxaudit --check`.

## Lane 0 — remaining resource handles

Dictionary lookup, direct saved XTs, generated callbacks, active delayed interactions, and saved macros now fail or clean up by plugin generation. Continue searching for plugin-owned objects that are not words, callback rows, active interactions, macro steps, or metadata-only diagnostics.

Stop condition: every plugin-owned resource handle either routes through a live-generation check, is removed by generation cleanup, or is proven metadata-only.

## Lane 1 — next host-owned budget

Add one more concrete budget before process/Wasm isolation. Best candidates: hostcall payload/result sizes, output capture, prompt rows, buffer creation, or cancellation/timeout surfaces.

Stop condition: a new budget has a host-owned option/default, refusal path, user-visible error, and tests that prove recovery after the pressure is relieved.

## Lane 2 — split one broad lifecycle surface

Pick one mutable family still owned by `RuntimeRegistrationSnapshot`, add typed capture/commit/abort helpers, and keep the broad snapshot only as a differential oracle until parity is proved.

Stop condition: one real source/lifecycle surface is no longer restored by the broad snapshot on its primary path, and tests prove the narrow owner controls policy, state, and rollback.

## Lane 3 — remaining release engineering

The selected-file-batch release manifest is now communicative and resumable. Add dependency lock, CI/package inspection, artifact digests, and a clear archive-revision versus package-version policy.

## Prior revision handoff

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
