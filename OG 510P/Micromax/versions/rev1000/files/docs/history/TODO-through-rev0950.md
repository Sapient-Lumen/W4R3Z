# Archived TODO-through-rev0950

This file preserves the root TODO handoff trail as it existed through rev0950. The current TODO was compacted in rev0951 so the live handoff stays under the living-document budget.

---

Rev0950 note: named marks now route through an editor-owned owner seam, the generated effect/resource contract exposes `ed.mark-register`, and broad rollback no longer double-restores recent files.

Latest tiny landing (rev0950): `Editor.snapshot_mark_group_state` / `restore_mark_group_state` now form the public mark rollback owner seam. Broad failed source/lifecycle registration restore and scoped runtime-group rollback prefer that seam before legacy private fallback; `mxaudit --check` hard-checks `mark_owner_snapshot_present`; the installed generated contract includes `ed.mark-register`; the runtime group restore path no longer double-restores recent files.

# TODO (rev0950)

- [x] package rev0950 with the required filename structure.

## Landed this revision

- [x] researched current resource-lifetime and workspace-trust references and applied them to retained mark navigation authority.
- [x] added public editor mark snapshot/restore owner methods over named marks and `RuntimeRegistrationAuthority` sidecars.
- [x] refactored plugin runtime broad registration restore and scoped group rollback to use the editor owner seam before legacy private fallback.
- [x] removed a duplicate `restore_recent_files_group_state` call from the runtime group restore path.
- [x] added focused tests proving broad restore and scoped group rollback call the public mark owner route and preserve unrelated rows.
- [x] extended `mxaudit --check` and human output with `mark_owner_snapshot_present` / `mark-owner=True`.
- [x] expanded the generated effect/resource contract with `ed.mark-register`, derived from live owner methods, mark capabilities, rollback lanes, and audit flags.
- [x] regenerated the installed `docs/33-effect-resource-contract.md` help surface and recorded the landing in `docs/908-mark-owner-contract.md`.

## Next up (high leverage)

1. Compact duplicated owner-row validation helpers in `effect_contracts.py` only after tests pin the shared behavior.
2. Decide whether successful plugin option and mark writes need explicit ownership or should stay committed editor effects.
3. Choose the next runtime survivor by concrete retained authority, rollback failure, or stale disclosure; avoid registry-completeness work.
4. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0947 note: recovery rollback now routes through an editor-owned owner seam and the generated contract exposes a recovery owner row.

Latest tiny landing (rev0947): `RecoveryRegisterEntry`, `RecoveryBufferRegisterSnapshot`, and `RecoveryRegisterSnapshot` make selection-stack and jump-list recovery rows an editor-owned resource. `plugin_runtime.py` now uses `Editor.snapshot_recovery_*` / `restore_recovery_*` owner methods for group cleanup, generation cleanup, and broad registration restore, while keeping legacy raw `sel_stack` / `jump_list` handling only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `recovery_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.recovery-register` owner row; `docs/905-recovery-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0947)

- [x] package rev0947 with the required filename structure.

## Landed this revision

- [x] researched current resource-lifetime, resource-consumption, and workspace-trust guidance and applied it to retained cursor/selection recovery authority.
- [x] added `RecoveryRegisterEntry`, `RecoveryBufferRegisterSnapshot`, and `RecoveryRegisterSnapshot` as the editor-owned selection/jump recovery snapshot.
- [x] added editor group/generation recovery snapshot and restore owner methods.
- [x] refactored plugin-runtime group, generation, and broad registration recovery rollback to call the editor owner seam before legacy raw fallback.
- [x] fixed broad recovery-register restore so full restore replaces mutated rows instead of duplicating captured rows.
- [x] extended `mxaudit --check` with `recovery_owner_snapshot_present` and human output `recovery-owner=True`.
- [x] expanded the generated effect/resource contract with the live `ed.recovery-register` owner row.
- [x] added focused owner-route, audit, and effect-contract regressions.
- [x] recorded the landing in `docs/905-recovery-owner-contract.md`.

## Next up (high leverage)

1. Render selected generated effect/resource rows in installed help instead of adding more revision notes.
2. Consolidate duplicated owner-route fallback patterns only where live tests prove the shared helper preserves group/generation semantics.
3. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0946 note: help-history rollback now routes through an editor-owned owner seam and the generated contract exposes a help-history owner row.

Latest tiny landing (rev0946): `HelpHistoryRegisterEntry` and `HelpHistoryRegisterSnapshot` make retained help back/forward/session rows an editor-owned resource. `plugin_runtime.py` now uses `Editor.snapshot_help_history_*` / `restore_help_history_*` owner methods for group cleanup, generation cleanup, and broad registration restore, while keeping legacy raw `_help_stack` / `_help_forward_stack` / `_help_session_entry` handling only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `help_history_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.help-history-register` owner row; `docs/904-help-history-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0946)

- [x] Research current resource-lifetime, resource-consumption, and workspace-trust guidance online and apply it to retained help-navigation authority.
- [x] Add `HelpHistoryRegisterEntry` / `HelpHistoryRegisterSnapshot` as editor-owned retained help-navigation value objects.
- [x] Add editor group/generation help-history snapshot and restore owner methods.
- [x] Refactor plugin-runtime group, generation, and broad registration help-history rollback to call the editor owner seam before legacy raw fallback.
- [x] Extend `mxaudit --check` with `help_history_owner_snapshot_present` and human output `help-history-owner=True`.
- [x] Expand the generated effect/resource contract with the live `ed.help-history-register` owner row.
- [x] Add focused owner-route, audit, and effect-contract regressions.
- [x] Record the landing in `docs/904-help-history-owner-contract.md`.
- [x] package rev0946 with the required filename structure.

## Next up (high leverage)

1. Render selected generated effect/resource rows in installed help so the product surface exposes authority without more revision-note prose.
2. Consolidate duplicated owner-route fallback patterns only where live tests prove the shared helper preserves group/generation semantics.
3. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0945 note: command-palette recent rollback now routes through an editor-owned owner seam and the generated contract exposes a palette-recent owner row.

Latest tiny landing (rev0945): `PaletteRecentRegisterEntry` and `PaletteRecentRegisterSnapshot` make retained command-palette command/action MRU rows an editor-owned resource. `plugin_runtime.py` now uses `Editor.snapshot_palette_recent_*` / `restore_palette_recent_*` owner methods for group cleanup, generation cleanup, and broad registration restore, while keeping legacy raw `_palette_recent` / `_palette_recent_authority` handling only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `palette_recent_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.palette-recent-register` owner row; `docs/903-palette-recent-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0945)

- [x] Research current resource-lifetime, resource-consumption, and workspace-trust guidance online and apply it to retained command/action palette launch authority.
- [x] Add `PaletteRecentRegisterEntry` / `PaletteRecentRegisterSnapshot` as editor-owned retained command/action launch value objects.
- [x] Add editor group/generation palette-recent snapshot and restore owner methods.
- [x] Refactor plugin-runtime group, generation, and broad registration palette-recent rollback to call the editor owner seam before legacy raw fallback.
- [x] Extend `mxaudit --check` with `palette_recent_owner_snapshot_present` and human output `palette-recent-owner=True`.
- [x] Expand the generated effect/resource contract with the live `ed.palette-recent-register` owner row.
- [x] Add focused owner-route, audit, and effect-contract regressions.
- [x] Record the landing in `docs/903-palette-recent-owner-contract.md`.
- [x] package rev0945 with the required filename structure.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help so the product surface exposes authority without more revision-note prose.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0944 note: saved-cursor rollback now routes through an editor-owned owner seam and the generated contract exposes a saved-cursor owner row.

Latest tiny landing (rev0944): `SavedCursorRegisterEntry` and `SavedCursorRegisterSnapshot` make retained saved-cursor path+position rows an editor-owned resource. `plugin_runtime.py` now uses `Editor.snapshot_saved_cursor_*` / `restore_saved_cursor_*` owner methods for group cleanup, generation cleanup, and broad registration restore, while keeping legacy raw `_saved_cursors` / `_saved_cursors_authority` handling only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `saved_cursor_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.saved-cursor-register` owner row; `docs/902-saved-cursor-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0944)

- [x] Research current resource-consumption, workspace-trust, Python snapshot/copy, and metadata/privacy exposure guidance online and apply it to retained saved-cursor path+position authority.
- [x] Add `SavedCursorRegisterEntry` / `SavedCursorRegisterSnapshot` as editor-owned retained cursor-navigation value objects.
- [x] Add editor group/generation saved-cursor snapshot and restore owner methods.
- [x] Refactor plugin-runtime group, generation, and broad registration saved-cursor rollback to call the editor owner seam before legacy raw fallback.
- [x] Extend `mxaudit --check` with `saved_cursor_owner_snapshot_present` and human output `saved-cursor-owner=True`.
- [x] Expand the generated effect/resource contract with the live `ed.saved-cursor-register` owner row.
- [x] Add focused owner-route, audit, and effect-contract regressions.
- [x] Record the landing in `docs/902-saved-cursor-owner-contract.md`.
- [x] package rev0944 with the required filename structure.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help so the product surface exposes authority without more revision-note prose.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0943 note: recent-files rollback now routes through an editor-owned owner seam and the generated contract exposes a recent-files owner row.

Latest tiny landing (rev0943): `RecentFilesRegisterEntry` and `RecentFilesRegisterSnapshot` make retained recent-file path MRU rows an editor-owned resource. `plugin_runtime.py` now uses `Editor.snapshot_recent_files_*` / `restore_recent_files_*` owner methods for group cleanup, generation cleanup, and broad registration restore, while keeping legacy raw `recent_files` / `recent_files_authority` handling only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `recent_files_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.recent-files-register` owner row; `docs/901-recent-files-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0943)

- [x] Research current sensitive-information, private-information, resource-consumption, and WIT resource-owner guidance online and apply it to retained recent-file path authority.
- [x] Add `RecentFilesRegisterEntry` / `RecentFilesRegisterSnapshot` as editor-owned retained path-history value objects.
- [x] Add editor group/generation recent-files snapshot and restore owner methods.
- [x] Refactor plugin-runtime group, generation, and broad registration recent-files rollback to call the editor owner seam before legacy raw fallback.
- [x] Extend `mxaudit --check` with `recent_files_owner_snapshot_present` and human output `recent-files-owner=True`.
- [x] Expand the generated effect/resource contract with the live `ed.recent-files-register` owner row.
- [x] Add focused owner-route, audit, and effect-contract regressions.
- [x] Record the landing in `docs/901-recent-files-owner-contract.md`.
- [x] package rev0943 with the required filename structure.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retained disclosure, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help so the product surface exposes authority without more revision-note prose.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0942 note: prompt-history rollback now routes through an editor-owned owner seam and the generated contract exposes a prompt-history owner row.

Latest tiny landing (rev0942): `PromptHistoryRegisterSnapshot` and `PromptHistoryRegisterEntry` make replayable prompt-history rows an editor-owned retained-history resource. `plugin_runtime.py` now uses `Editor.snapshot_prompt_history_*` / `restore_prompt_history_*` owner methods for group cleanup, generation cleanup, and broad registration restore, while keeping legacy raw `history` / `history_authority` handling only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `prompt_history_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.prompt-history-register` owner row; `docs/900-prompt-history-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0942)

- [x] Research current resource-lifetime, retained-text/logging, package-resource lifetime, and WIT resource-owner guidance online.
- [x] Add `PromptHistoryRegisterEntry` / `PromptHistoryRegisterSnapshot` as editor-owned retained replay-history value objects.
- [x] Add editor group/generation prompt-history snapshot and restore owner methods.
- [x] Refactor plugin-runtime group, generation, and broad registration prompt-history rollback to call the editor owner seam before legacy raw fallback.
- [x] Extend `mxaudit --check` with `prompt_history_owner_snapshot_present` and human output `prompt-history-owner=True`.
- [x] Expand the generated effect/resource contract with the live `ed.prompt-history-register` owner row.
- [x] Add focused owner-route, audit, and effect-contract regressions.
- [x] Record the landing in `docs/900-prompt-history-owner-contract.md`.
- [x] package rev0942 with the required filename structure.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
2. Choose the next runtime survivor by concrete stale lifetime, authority clobber, retention, or rollback failure rather than by registry completeness.
3. Render selected generated effect/resource rows in installed help so the product surface exposes authority without more revision-note prose.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0941 note: active-search rollback now routes through an editor-owned owner seam and the generated contract exposes an active-search owner row.

Latest tiny landing (rev0941): `ActiveSearchRegisterSnapshot` makes the active search query/provenance pair an editor-owned delayed-navigation resource. `plugin_runtime.py` now uses `Editor.snapshot_search_*` / `restore_search_*` owner methods for group cleanup, generation cleanup, and broad registration fallback, while keeping legacy tuple helpers only as alternate-embedder fallback. `tools/mxaudit.py --check` enforces `active_search_owner_snapshot_present`; `src/micromax_editor/effect_contracts.py` now emits the generated `ed.active-search-register` owner row; `docs/899-active-search-owner-contract.md` records research, audit/refactor notes, validation, and remaining owner-contract risks.

# TODO (rev0941)

- [x] Research current resource-consumption/resource-lifetime/component-resource guidance online and apply it to active-search delayed navigation authority.
- [x] Add `ActiveSearchRegisterSnapshot` as the editor-owned active-search query/provenance snapshot.
- [x] Add editor group/generation active-search snapshot and restore owner methods.
- [x] Refactor plugin-runtime group, generation, and broad registration search rollback to call the editor owner seam first.
- [x] Extend `mxaudit --check` with `active_search_owner_snapshot_present` / `active-search-owner=True`.
- [x] Expand the generated effect/resource contract with the live `ed.active-search-register` owner row.
- [x] Add focused owner-route, audit, and effect-contract regressions.
- [x] Record the landing in `docs/899-active-search-owner-contract.md`.
- [x] package rev0941 with the required filename structure.

## Next up (high leverage)

1. Keep expanding generated owner rows only when live owner methods and focused tests can supply facts.
2. Pick the next runtime survivor by concrete stale lifetime, authority clobber, retention, or rollback failure; do not add a broad ownership registry first.
3. Render selected generated contract rows in installed help so the product surface exposes effect authority without more revision-note prose.
4. Compact stale handoff/docs material when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0940 note: first generated effect/resource contract slice now emits live host-effect budget/capability rows and is checked by audit.

Latest tiny landing (rev0940): `src/micromax_editor/effect_contracts.py` generates `micromax.effect-resource-contract.v1` rows from live hostcall registry, capability registry, resource defaults, stdlib contract, regex defaults, and `mxaudit` runtime evidence. `tools/mxeffects.py --json --check` and `make effect-contracts` expose the slice; `tools/mxaudit.py --check` now fails if the generated contract cannot validate; `tools/mxcontext.py` points future sessions at the generator. `docs/898-generated-effect-resource-contract.md` records research, audit/refactor notes, validation, and the remaining owner-graph risks.

# TODO (rev0940)

- [x] Research current resource-consumption, subprocess-timeout, component-contract, WIT resource, and embedded-language guidance online.
- [x] Generate the first effect/resource contract slice from live code facts instead of a hand-maintained doctrine table.
- [x] Add `src/micromax_editor/effect_contracts.py` with rows for filesystem, process, source-load, clipboard-process, regex, and bundled-stdlib effects.
- [x] Add `tools/mxeffects.py --json --check` and `make effect-contracts`.
- [x] Refactor `tools/mxaudit.py --check` to consume the generated contract as hard audit evidence.
- [x] Update `tools/mxcontext.py` so the contract generator is a curated future entrypoint.
- [x] Add focused contract, audit, and context tests.
- [x] Record the landing in `docs/898-generated-effect-resource-contract.md`.
- [x] package rev0940 with the required filename structure.

## Next up (high leverage)

1. Expand the contract from high-risk host effects into plugin-owned owner rows only where live owner methods and tests can generate the facts.
2. Consider active-search ownership next only if a route test exposes a concrete stale lifetime, authority clobber, retention, or rollback failure.
3. Render selected effect-contract rows in installed help instead of installing more revision-note prose.
4. Keep docs compaction/product truth high-priority: deleting stale handoff burden is progress when generated evidence replaces it.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0939 note: deep cloudtainer audit refreshed the heart/gap/waste diagnosis and now makes curated entrypoint freshness an audit-checked invariant.

Latest tiny landing (rev0939): `docs/897-cloudtainer-entrypoint-freshness-audit.md` records the current heart, missing contract, waste, online research implications, and speculation. `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, and `docs/43-worklist.md` were refreshed to the current revision after the deep read found stale curated entrypoints. `tools/mxaudit.py --check` now fails if `README.md`, `TODO.md`, `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, or `docs/43-worklist.md` point at a stale revision, and `tests/test_mxaudit.py` covers the JSON and human-output signals.

# TODO (rev0939)

- [x] Read the archive as a mission/architecture system rather than a terminal-editor feature list.
- [x] Research current resource-consumption, subprocess/cancellation, workspace-trust, embedded-language, component-contract, and supply-chain provenance guidance online.
- [x] Record the heart/gap/waste/speculation diagnosis in `docs/897-cloudtainer-entrypoint-freshness-audit.md`.
- [x] Refresh curated handoff entrypoints to the current revision.
- [x] Add curated entrypoint revision freshness metrics to `tools/mxaudit.py`.
- [x] Make `mxaudit --check` fail on stale curated entrypoint revision markers.
- [x] Add focused JSON and human-output coverage in `tests/test_mxaudit.py`.
- [x] package rev0939 with the required filename structure.

## Next up (high leverage)

1. Generate the first effect/resource-contract slice from live owner methods, tests, and audit facts.
2. Move the next raw runtime snapshot field behind a typed owner only when a concrete stale/lifetime or authority failure justifies it.
3. Promote resource/effect/security truth into installed help through living contracts, not by installing every revision note.
4. Treat documentation compaction and generated contract evidence as product work.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.

## Prior revision handoff

Rev0938 note: generation-scoped saved macro and live recording rollback now route through an editor-owned macro snapshot/restore seam while reporting `macro-owner=True` in audit.

Latest tiny landing (rev0938): `MacroGenerationSnapshot` makes plugin-owned saved macro slots and live recordings an editor-owned delayed-executable resource. `plugin_runtime.py` now asks `snapshot_macro_generation_state()` / `restore_macro_generation_state()` before falling back to alternate-embedder raw macro field handling, so the editor owns the stable `last` alias and recording-origin invariants. A focused regression monkeypatches the owner methods to prove the generation rollback route. `tools/mxaudit.py --check` reports `macro_owner_generation_snapshot_present` / `macro-owner=True`. `docs/896-macro-owner-generation-snapshot.md` records research, audit/refactor, validation, and remaining active-search/broad-snapshot risks.

# TODO (rev0938)

- [x] Research current resource-consumption / resource-lifetime guidance online and apply it to delayed executable macro state.
- [x] Add editor-owned macro generation snapshot value objects for saved slots and live recordings.
- [x] Add `Editor.snapshot_macro_generation_state()` and `Editor.restore_macro_generation_state()`.
- [x] Refactor plugin-runtime macro generation snapshot+restore helpers to ask the editor owner first.
- [x] Preserve alternate-embedder fallback behavior without making it the in-tree primary path.
- [x] Add a focused owner-route regression for generation macro snapshot+restore.
- [x] Extend `mxaudit --check` with `macro_owner_generation_snapshot_present` / `macro-owner=True`.
- [x] Record the landing in `docs/896-macro-owner-generation-snapshot.md`.
- [x] package rev0938 with the required filename structure.

## Next up (high leverage)

1. Consider active-search owner methods next only if the route test proves a concrete stale/lifetime or authority issue.
2. Avoid broad macro snapshot work until a test demonstrates a real clobber, retention, or overwrite recovery problem.
3. Keep runtime owner refactors narrow and behavior-backed; do not add a registry table first.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0937 note: clipboard group/generation and broad registration rollback now route through editor-owned clipboard snapshot/restore methods while reporting `clipboard-owner=True` in audit.

Latest tiny landing (rev0937): `ClipboardRegisterSnapshot` makes the internal clipboard register an editor-owned authority singleton. `plugin_runtime.py` now uses `snapshot_clipboard_*` / `restore_clipboard_*` owner methods for group cleanup, generation cleanup, and broad registration fallback, rather than reading/writing the live `clipboard_items/kind/authority/serial/from_script` fields in the primary path. Focused regressions monkeypatch the owner methods to prove group, generation, and broad registration rollback routes. A scoped-generation authority clobber in the legacy broad restore path was fixed while validating the owner route. `tools/mxaudit.py --check` reports `clipboard_owner_snapshot_present` / `clipboard-owner=True`. `docs/895-clipboard-owner-snapshot.md` records research, audit/refactor, validation, and remaining active-search/broad-snapshot risks.

# TODO (rev0937)

- [x] Research current resource-lifetime/resource-consumption guidance online and apply it to the internal clipboard singleton rollback seam.
- [x] Add `ClipboardRegisterSnapshot` as an editor-owned clipboard register snapshot.
- [x] Add editor group/generation clipboard snapshot and restore owner methods.
- [x] Refactor plugin-runtime clipboard group/generation snapshot+restore helpers to ask the editor owner first.
- [x] Route broad `RuntimeRegistrationSnapshot` clipboard capture/restore through the clipboard owner method.
- [x] Fix scoped-generation clipboard authority clobber from the legacy broad raw-field restore block.
- [x] Add focused owner-route regressions for group, generation, and broad registration rollback.
- [x] Extend `mxaudit --check` with `clipboard_owner_snapshot_present` / `clipboard-owner=True`.
- [x] Record the landing in `docs/895-clipboard-owner-snapshot.md`.
- [x] package rev0937 with the required filename structure.

## Next up (high leverage)

1. Consider active-search owner methods next only if the slice stays small: it is another authority singleton, but it needs a route test and clobber/failure story, not a registry quota.
2. Keep broad `RuntimeRegistrationSnapshot` reductions tied to concrete stale/lifetime or authority failures.
3. Sweep editor cleanup coupling only where it removes double-clear, authority loss, or retention behavior.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0936 note: broad failed-callback interaction snapshot/restore now routes through an editor-owned aggregate owner, removing direct prompt/query/keymode/open-url/input field access from runtime callback rollback while reporting `callback-interaction-owner=True` in audit.

Latest tiny landing (rev0936): `PluginCallbackInteractionSnapshot` aggregates the existing editor-owned keymode, prompt, query-replace, and pending-open-url snapshots plus input scratch for failed callback rollback. `plugin_runtime.py` now calls `snapshot_plugin_callback_interaction_state()` / `restore_plugin_callback_interaction_state()` instead of reading or rewriting raw interaction fields. A focused regression monkeypatches those owner methods to prove the route, and `tools/mxaudit.py --check` hard-checks `plugin_callback_interaction_owner_present`. `docs/894-plugin-callback-interaction-owner.md` records research, audit/refactor, validation, and remaining broad registration-snapshot risks.

# TODO (rev0936)

- [x] Research current resource-lifetime/resource-consumption guidance online and apply it to broad failed-callback delayed interaction rollback.
- [x] Add `PluginCallbackInteractionSnapshot` as an editor-owned aggregate interaction snapshot.
- [x] Add editor aggregate snapshot/restore methods for failed plugin callbacks.
- [x] Compose the aggregate from existing keymode, prompt, query-replace, and pending-open-url owner snapshots.
- [x] Refactor runtime callback interaction snapshot/restore to use the aggregate owner instead of direct field access.
- [x] Add a focused owner-route regression for broad failed-callback rollback.
- [x] Extend `mxaudit --check` with `plugin_callback_interaction_owner_present` / `callback-interaction-owner=True`.
- [x] Record the landing in `docs/894-plugin-callback-interaction-owner.md`.
- [x] package rev0936 with the required filename structure.

## Next up (high leverage)

1. Move the next broad `RuntimeRegistrationSnapshot` field only if it has a concrete stale/lifetime or authority failure; do not wrapperize by registry doctrine.
2. Keep active-interaction owner work tied to runtime behavior, tests, and audit predicates.
3. Sweep internal editor cleanup coupling only where it removes a concrete double-clear or retention bug.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0933 note: query-replace group/generation snapshot/restore now routes through editor-owned owner methods, coupling session and cursor/selection state while reporting `qreplace-owner=True` in audit.

Latest tiny landing (rev0933): `QueryReplaceInteractionSnapshot` and `QueryReplaceInteractionCursorSnapshot` make query-replace a typed editor-owned delayed interaction row. `plugin_runtime.py` group/generation interaction snapshot+restore now calls `snapshot_qreplace_*` / `restore_qreplace_*` methods instead of reading/writing `Editor.qreplace` directly, cleanup uses `_clear_qreplace_runtime_row()`, focused regressions monkeypatch the owner methods to prove the route, and `tools/mxaudit.py --check` hard-checks `qreplace_owner_snapshot_present`. `docs/891-qreplace-owner-snapshot.md` records research, audit/refactor, validation, and remaining prompt-owner risk.

# TODO (rev0933)

- [x] Research resource-lifetime/resource-consumption guidance online and apply it to the query-replace delayed interaction row.
- [x] Add editor-owned query-replace session/cursor snapshot value objects.
- [x] Add group/generation query-replace snapshot/restore owner methods.
- [x] Refactor runtime group/generation interaction snapshot+restore to use those owner methods instead of direct `Editor.qreplace` access.
- [x] Centralize query-replace cleanup so the live session and visible selection are cleared together.
- [x] Add focused owner-route regressions for group and generation snapshot+restore.
- [x] Extend `mxaudit --check` with `qreplace_owner_snapshot_present` / `qreplace-owner=True`.
- [x] Record the landing in `docs/891-qreplace-owner-snapshot.md`.
- [x] package rev0933 with the required filename structure.

## Next up (high leverage)

1. Move prompt interaction snapshot/restore through owner methods only if it stays a small code+test slice like open-url and query-replace.
2. Keep active-interaction owner work tied to runtime behavior, tests, and audit predicates; do not add a manual registry first.
3. Revisit package locks/CI/signatures only when a real package lane exists to protect.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0932 note: pending external-URL confirmation snapshot/restore now routes through editor-owned group/generation methods with audit coverage.

Latest tiny landing (rev0932): `PendingOpenUrlInteractionSnapshot` made the pending external-URL confirmation row editor-owned for group/generation snapshot and restore. `plugin_runtime.py` now calls the editor owner methods instead of reading/writing pending URL/source/authority fields directly, cleanup reuses the owner clear helper, focused regressions prove the runtime route, and `tools/mxaudit.py --check` reports `pending_open_url_owner_snapshot_present` / `open-url-owner=True`. `docs/890-pending-open-url-owner.md` records the research, audit/refactor, validation, and remaining prompt/query-replace owner risk.

# TODO (rev0932)

- [x] Research current resource-lifetime/resource-consumption guidance online.
- [x] Add pending open-url editor owner snapshot/restore methods.
- [x] Refactor runtime group/generation interaction snapshot+restore to use pending open-url owner methods.
- [x] Reuse the pending open-url clear helper in group and generation cleanup paths.
- [x] Add focused owner-route regressions for pending open-url snapshot+restore.
- [x] Extend `mxaudit --check` with `pending_open_url_owner_snapshot_present` / `open-url-owner=True`.
- [x] Record the landing in `docs/890-pending-open-url-owner.md`.
- [x] package rev0932 with the required filename structure.

## Prior revision handoff

Rev0931 note: `qreplace all` now enforces a host-owned per-action replacement budget, keeps the session active at the next match when the budget is reached, and reports `qreplace-all-budget=True` in audit.

Latest tiny landing (rev0931): `qreplace.max` (default `10000`, `0` = explicit unlimited) bounds one query-replace-all response. `Editor.qreplace_all()` counts applied replacements, stops with a visible message while preserving the active query-replace session, and retries can continue in bounded chunks. Focused regressions cover budget-stop and explicit unlimited behavior, and `tools/mxaudit.py --check` hard-checks `qreplace_all_replacement_budget`. `docs/889-qreplace-all-budget.md` records research, audit/refactor, validation, and remaining active-interaction owner work.

# TODO (rev0931)

- [x] Research resource-consumption/effective-lifetime guidance online (CWE-400/CWE-772).
- [x] Audit delayed interaction response risk instead of adding registry doctrine.
- [x] Add `qreplace.max` as a host-owned per-action replacement limit.
- [x] Bound `qreplace_all()` and preserve the active session when the budget is reached.
- [x] Add focused query-replace budget/explicit-unlimited regressions.
- [x] Extend `mxaudit --check` with `qreplace_all_replacement_budget` / `qreplace-all-budget=True`.
- [x] Record the landing in `docs/889-qreplace-all-budget.md`.
- [x] package rev0931 with the required filename structure.

## Next up (high leverage)

1. Move one active-interaction cleanup/snapshot path through typed owner methods; `plugin_runtime` still reaches directly into prompt/query-replace/open-url/keymode fields.
2. Keep runtime budgets tied to visible recovery behavior; do not add a registry matrix unless it is generated from live owner methods/tests.
3. Revisit package locks/CI/signatures only after a real package lane exists; rev0930's no-runtime-deps policy is still honest but not signed provenance.
4. Keep validation split and honest under cloudtainer limits.

## Prior revision handoff

Rev0930 note: package/dependency inputs now have an executable no-runtime-deps/no-lock policy report embedded in handoff archives and checked by audit.

Latest tiny landing (rev0930): `tools/mxrelease.py --package-inputs` now verifies the explicit current release stance: no runtime project dependencies, no lock file by policy, dev requirements mirroring `pyproject.toml`, pinned pre-commit hook revisions, and an explicit archive-revision/package-version independence policy. `tools/mkrevzip.py` embeds that report in every archive manifest, `make release-inputs` exposes it, and `tools/mxaudit.py --check` reports `package_input_policy_present=True`. `docs/888-package-input-policy.md` records the research, audit/refactor, validation, and remaining lock/signature/CI/runtime-owner risks.

# TODO (rev0930)

- [x] Research current Python lock-file/reproducible-install guidance and SLSA provenance/materials guidance online.
- [x] Audit the rev0929 next-up risk: archives verified their members but still could not explain dependency/package inputs.
- [x] Add explicit `[tool.micromax.release]` dependency and package-version policy in `pyproject.toml`.
- [x] Add `mxrelease.package_input_report()` and `python tools/mxrelease.py --package-inputs`.
- [x] Enforce the current no-lock stance only when runtime dependencies remain absent.
- [x] Check that `requirements-dev.txt` mirrors `[project.optional-dependencies].dev`.
- [x] Check pre-commit hook `rev:` values for obvious floating revisions.
- [x] Add `make release-inputs` and context run-command coverage.
- [x] Embed package-input policy reports into `mkrevzip` archive manifests.
- [x] Extend `mxaudit --check` with `package_input_policy_present` / `package-input policy present=True`.
- [x] Add focused regressions for accepted policy, runtime-dependency refusal, dev-requirement drift, unpinned pre-commit revisions, archive embedding, and audit output.
- [x] Record the landing in `docs/888-package-input-policy.md`.
- [x] package rev0930 with the required filename structure.

## Next up (high leverage)

1. **Return to a runtime owner seam.** Prompt-history rows, active interactions, macros, or clipboard state should get typed ownership only where it removes concrete retention or rollback ambiguity.
2. **Do not add signatures before locks/CI are real.** The package-input report is honest no-lock evidence, not signed provenance; a future published package lane should add lock consumption, CI, SBOM/signature, or SLSA-style attestations in that order.
3. **Keep release checks executable.** If runtime dependencies appear, `mxrelease --package-inputs` should fail until the dependency policy changes to consume a lock.
4. **Clarify version policy only when publishing.** `rev####` handoff archives and `pyproject.toml` package versions are explicitly independent for now; published package workflows should revisit this.
5. **Keep validation split and honest.** The full `tests/test_mkrevzip.py` selector printed `14 passed, 1 warning`, but the outer wrapper did not return cleanly afterward; use split evidence unless the wrapper behavior is diagnosed.

## Prior revision handoff

Rev0929 note: revision zips now self-verify their embedded archive-member provenance, rejecting duplicate/unsafe members, budget overflows, and digest drift before handoff.

Latest tiny landing (rev0929): `tools/mkrevzip.py` now owns both archive-member provenance production and consumption. `verify_archive()` checks ZIP CRC/header integrity, rejects unsafe or duplicate member names, applies member/compressed/uncompressed byte budgets before reading payloads, recomputes per-file SHA-256 rows from actual archive bytes, compares the aggregate digest/count/byte totals, and normal packaging self-verifies before printing the archive path. `make revzip-verify ZIP=...`, `tools/mxaudit.py --check`, `tools/mxcontext.py`, and focused regressions make the verifier an executable release-hygiene seam rather than a manifest nobody consumes. `docs/887-archive-provenance-verifier.md` records the research, audit/refactor, validation, and remaining dependency/signature/version-policy work.

# TODO (rev0929)

- [x] Research current Python zipfile verification/path-safety guidance, SLSA artifact provenance guidance, and OWASP SCVS supply-chain verification guidance online.
- [x] Audit the rev0928 next-up risk: archive-member provenance was embedded but not consumed.
- [x] Add `ArchiveVerificationError` and `verify_archive()` as the owner for revision-zip provenance consumption.
- [x] Reject duplicate ZIP members and unsafe member names before treating archive paths as repo-relative facts.
- [x] Add verifier member-count, compressed-byte, and uncompressed-byte budgets before payload reads.
- [x] Recompute actual archive member byte/SHA-256 rows and compare them to `MICROMAX-CONTEXT.json` provenance entries and aggregate digest metadata.
- [x] Make normal `mkrevzip` self-verify the archive it wrote before printing the handoff path.
- [x] Add `python tools/mkrevzip.py --verify-archive` plus `make revzip-verify ZIP=...`.
- [x] Extend `mxaudit --check` with `mkrevzip_verifier_present` / `mkrevzip verifier present=True`.
- [x] Add focused regressions for successful verification, CLI JSON, digest drift, duplicate members, unsafe members, and verifier byte-budget refusal.
- [x] Record the landing in `docs/887-archive-provenance-verifier.md`.
- [x] package rev0929 with the required filename structure.

## Next up (high leverage)

1. **Lock or inspect dependency inputs.** The archive can now verify itself locally, but release hygiene still lacks a dependency lock or explicit package-input policy.
2. **Clarify archive revision versus package version.** `rev####` handoff archives and `pyproject.toml` package versioning should have a small executable check or written policy.
3. **Only add signatures after the local verifier settles.** Detached digest/signature or SLSA-style attestation is useful, but not before the local manifest-verifier loop stays green.
4. **Return to a runtime owner seam.** Prompt/history rows, macro slots, active interactions, or clipboard state should get typed ownership only where it removes concrete retention/rollback ambiguity.
5. **Keep validation split and honest.** The combined mkrevzip+mxaudit selector hit the outer tool timeout; the split selectors are the evidence for this revision.

## Prior revision handoff

Rev0928 note: canceled timers now release live callback rows immediately, raw stale heap ids are bounded, and plugin-runtime timer rollback goes through the timer owner seam.

Latest tiny landing (rev0928): `src/micromax_editor/timers.py` now treats `TimerQueue` as the owner of delayed callback lifetime: `cancel()` and `cancel_group()` remove live task rows immediately, stale heap ids compact under a bounded drift rule, and diagnostic owner methods expose retained task and heap counts. `src/micromax_editor/plugin_runtime.py` now snapshots/restores timer state through `snapshot_state()` / `restore_state()` and group timer rows through `snapshot_group_tasks()` / `restore_group_tasks()` on the real editor timer path. `tools/mxaudit.py` hard-checks `timer_cancellation_releases_tasks`, and `docs/886-timer-owner-cancel-release.md` records the audit, online research, validation, and remaining archive-provenance verifier work.

# TODO (rev0928)

- [x] Research current Python heapq mutable-priority-queue guidance, weak-reference/lifetime practice, and OWASP resource-consumption guidance online.
- [x] Audit the timer queue as the riskiest plugin-owned delayed resource family named by rev0927.
- [x] Make `TimerQueue.cancel()` remove the live task row immediately instead of retaining canceled callback payloads until due time.
- [x] Make `TimerQueue.cancel_group()` remove live group task rows and rebuild the heap after group cleanup.
- [x] Bound raw stale heap id drift from repeated schedule/cancel loops.
- [x] Add timer owner diagnostics for retained live tasks and raw heap entries.
- [x] Move broad and group-scoped plugin-runtime timer snapshots/restores through timer-owner methods on the real editor path.
- [x] Add regressions proving canceled callback payload release and bounded heap drift.
- [x] Update plugin-runtime group rollback expectations for immediate cancellation release.
- [x] Extend `mxaudit --check` with `timer_cancellation_releases_tasks` / `timer-release=True`.
- [x] Record the landing in `docs/886-timer-owner-cancel-release.md`.
- [x] package rev0928 with the required filename structure.

## Next up (high leverage)

1. **Consume archive provenance.** Rev0926 started member SHA-256 provenance and rev0928 reduced timer lifetime risk; the next best release-hygiene repair is a verifier/package-inspection lane that checks a zip against its embedded manifest.
2. **Apply typed owners only where they retire real risk.** Prompt/history rows, macro slots, active interactions, or clipboard state should get this treatment only when it removes concrete retention/rollback ambiguity.
3. **Keep code ahead of doctrine.** Build any compact resource/effect matrix from owner methods, tests, and audit rows after the next concrete seam; avoid a hand-maintained registry essay.
4. **Keep validation honest.** Split focused commands under cloudtainer limits and record selector typos/timeouts separately from completed evidence.

## Prior revision handoff

Rev0927 note: bundled stdlib startup now has an explicit package-resource contract with a 64 KiB byte cap, SHA-256 provenance, health rows, and audit visibility.

Latest tiny landing (rev0927): `src/micromax/stdlib_resource.py` now owns bounded package-resource loading for `micromax/stdlib/core.mx`; `src/micromax/vm.py` records the contract in `stdlib_health()` / `startup_health()` and reports oversized stdlib bytes as `stdlib-resource-limit`; `tools/mxaudit.py` hard-checks `stdlib_resource_contract_present`; and `docs/885-stdlib-resource-contract.md` records the audit, online research, validation, and remaining typed-resource-owner/release-provenance work.

# TODO (rev0927)

- [x] Research current Python `importlib.resources` package-resource semantics and OWASP resource-consumption guidance online.
- [x] Audit the stdlib package-resource survivor named by rev0926 and classify it separately from workspace/plugin filesystem authority.
- [x] Factor bundled stdlib loading out of `VM._load_stdlib()` into `src/micromax/stdlib_resource.py`.
- [x] Replace text-mode unbudgeted stdlib resource loading with a binary package-resource read capped at `max_bytes + 1`.
- [x] Record stdlib byte count, SHA-256, trust class, authority note, and source pseudo-filename in machine-readable health metadata.
- [x] Add focused regressions for loaded health metadata and oversized stdlib resource rejection.
- [x] Preserve missing-resource degraded mode and `strict_stdlib=True` fail-closed behavior.
- [x] Validate installed wheel/package behavior after the new resource module was added.
- [x] Extend `mxaudit --check` with `stdlib_resource_contract_present`.
- [x] Record the landing in `docs/885-stdlib-resource-contract.md`.
- [x] package rev0927 with the required filename structure.

## Next up (high leverage)

1. **Move one plugin-owned resource family to a typed owner.** Timers are the best next target because they mix deferred callbacks, unload/revoke semantics, stale-reference risk, and pending-work budgets.
2. **Consume archive provenance, not just embed it.** Add a verifier or package-inspection lane for rev0926's archive member SHA-256 manifest.
3. **Keep code progress ahead of doctrine.** Build any resource/effect matrix from code/test/audit facts after these seams land; do not hand-write another registry first.
4. **Keep short-window validation honest.** Split selected test commands when the outer cloudtainer timeout is tight; do not summarize timed-out combined commands as full passes.

## Prior revision handoff

Rev0926 note: prompt path completion now uses the contained directory-list seam for standalone and editor paths, and mkrevzip embeds archive-member SHA-256 provenance in the context manifest.

Latest tiny landing (rev0926): `src/micromax_editor/prompt_completion.py` removes the standalone direct `Path.exists()/Path.is_dir()/Path.iterdir()/child.is_dir()` branch from path completion and always observes directories through `list_dir_contained_bounded()`, with editor callers still passing VM scan/time budgets and standalone callers using a synchronous contained list bounded to the return page. `tools/mkrevzip.py` now embeds `archive.provenance` in `MICROMAX-CONTEXT.json`, covering packaged member path/byte/SHA-256 rows plus an aggregate digest. `tools/mxaudit.py` hard-checks the contained prompt-completion branch and `release_hygiene.mkrevzip_provenance_present`. `docs/884-prompt-completion-contained-provenance.md` records the audit, online research, validation, and remaining stdlib/resource-owner risks.

# TODO (rev0926)

- [x] Research current Python pathlib/subprocess/concurrent-futures, OWASP resource-consumption, and WASI capability guidance online.
- [x] Audit the rev0925 prompt-completion no-timeout survivor and choose a contained-list refactor over another registry/table.
- [x] Route standalone `path_completion_candidates()` directory observation through `list_dir_contained_bounded()` instead of direct pathlib probes.
- [x] Preserve editor/script context behavior: VM scan budgets and filesystem-list timeouts still flow into path completion.
- [x] Add/adjust focused prompt-completion tests for contained-list scan limits and timeout propagation.
- [x] Add archive-member SHA-256 provenance to the mkrevzip embedded context manifest.
- [x] Add mkrevzip regression coverage for member provenance rows and embedded archive provenance.
- [x] Extend `mxaudit --check` for the contained prompt-completion branch and `mkrevzip_provenance_present`.
- [x] Record the landing in `docs/884-prompt-completion-contained-provenance.md`.
- [x] package rev0926 with the required filename structure.

## Next up (high leverage)

1. **Classify trusted bundled stdlib loading before calling it a filesystem survivor.** `micromax.vm.VM._load_stdlib()` is package-resource startup, not workspace/plugin authority; put that fact in code-adjacent evidence so future sweeps stop rediscovering it as an apparent bug.
2. **Move one plugin-owned resource family to a typed owner.** Timers, prompt/history rows, or macro slots remain good candidates; success is a single owner, commit/abort journal, stale-reference rule, unload/revoke behavior, and headless/audit evidence.
3. **Keep release provenance concrete.** Next improvements should be dependency input recording, package inspection, and archive-revision/package-version policy, not another prose-only registry.
4. **Build the first compact resource/effect matrix from facts after the survivor classification pass.** It should be generated or code-adjacent, not manually maintained doctrine.
5. **Keep short-window validation honest.** Split selected test commands when the outer cloudtainer timeout is tight; do not summarize timed-out combined commands as full passes.

## Prior revision handoff

Rev0925 note: optional plugin.json existence now uses the contained plugin-file seam, escaping optional metadata fails closed, the docs-index private fallback uses contained prefix reads, and mxtimely writes summary evidence incrementally to avoid stale prior-revision artifacts after outer termination.

Latest tiny landing (rev0925): `src/micromax_editor/plugin_meta.py` routes optional `plugin.json` existence through `plugin_file_exists()` instead of `Path.exists()`, `src/micromax_editor/plugin_io.py` refuses containment failures rather than collapsing them into missing optional files, `src/micromax_editor/docs_index.py::_scan_doc_file()` now uses contained prefix reads instead of direct `Path.read_text()`, `tools/mxtimely.py` persists summary JSON after each bounded child so interrupted handoff runs cannot leave stale evidence behind, `tools/mxaudit.py` hard-checks plugin metadata, docs-catalog fallback, and incremental timely evidence, and `docs/883-plugin-meta-contained-existence.md` records the audit, online research, validation, and remaining survivor list.

# TODO (rev0925)

- [x] Research current Python `pathlib`, subprocess timeout, concurrent futures teardown, OWASP resource-consumption, and WASI capability guidance online.
- [x] Patch optional plugin metadata existence to use the contained plugin-file seam instead of ambient `Path.exists()`.
- [x] Preserve fail-closed behavior for escaping optional metadata instead of treating containment errors as metadata absence.
- [x] Add focused regression coverage for absent optional metadata using the contained probe and for escaping `plugin.json` behavior.
- [x] Move the docs-index private fallback off direct `Path.read_text()` and onto contained prefix reads.
- [x] Fix the stale handoff-evidence waste path by making `mxtimely` write summary JSON after each completed child.
- [x] Add regression coverage that an interrupted `mxtimely` run still leaves fresh partial summary evidence.
- [x] Extend `mxaudit --check` with `plugin_optional_meta_exists_contained` and `timely_summary_incremental`.
- [x] Re-audit direct filesystem/proc survivors and classify lower-priority remaining paths without starting a broad doctrine table.
- [x] Record the landing in `docs/883-plugin-meta-contained-existence.md`.
- [x] package rev0925 with the required filename structure.

## Next up (high leverage)

1. **Split the prompt-completion no-timeout standalone branch if it grows.** Editor/hostcall paths should keep proving they pass a timeout; standalone direct `iterdir()` should not be reachable from capability-sensitive callers by accident.
2. **Classify trusted package-resource reads.** `micromax.vm.VM._load_stdlib()` is trusted bundled stdlib loading, not workspace/plugin authority; record that in the eventual effect/resource contract instead of treating it like a survivor bug.
3. **Build the first compact resource/effect matrix from code/test facts.** Now that the plugin metadata survivor is patched, generate or code-adjacent the table rather than writing another hand-maintained registry.
4. **Move one plugin-owned family to a typed owner.** Timers, prompt/history rows, or macro slots remain good candidates; success is a single owner, commit/abort journal, stale-reference rule, and audit row.
5. **Add release provenance.** Dependency input recording, CI/package inspection, artifact digesting, and archive-revision/package-version policy remain unfinished.

## Prior revision handoff

Rev0924 note: deep cloudtainer audit re-centers the mission on least-authority automation, names remaining waste, and recommends bounded optional plugin metadata existence as the next tiny code landing.

Latest tiny landing (rev0924): `docs/882-cloudtainer-heart-mission-waste-audit.md` records the heart/missing/change/waste diagnosis, current online resource-boundary research, cloudtainer validation notes, and a concrete rev0925 recommendation: replace optional plugin metadata `Path.exists()` with the existing contained plugin-file seam before generating a broader effect/resource table.

# TODO (rev0924)

- [x] Research current subprocess timeout, executor cancellation, resource-consumption, workspace-trust, and WASI/component-model guidance online.
- [x] Read the rev0923 datacube as a mission/effect/resource lifecycle system rather than as isolated help-doc timeout work.
- [x] Record the heart of the mission: least-authority end-user automation with explicit effects, provenance, recoverable failure, and headless truth.
- [x] Name the missing contracts: living effect/resource-budget matrix, typed plugin resource owners, honest process boundary, release provenance, and smaller living docs.
- [x] Identify waste/severe drift: survivor patch loop, giant coordinator, proof machinery overhead, repeated research notes, stale handoff evidence, and stale curated entrypoints.
- [x] Recommend the next small code repair: route optional plugin metadata existence through contained plugin I/O instead of direct `Path.exists()`.
- [x] Record the landing in `docs/882-cloudtainer-heart-mission-waste-audit.md`.
- [x] package rev0924 with the required filename structure.

## Next up (high leverage)

1. **Patch optional plugin metadata existence.** In `src/micromax_editor/plugin_meta.py`, replace `meta_path.exists()` with the contained `plugin_file_exists()` seam already used for plugin entry validation; add a focused regression and an `mxaudit` predicate.
2. **Classify remaining direct local reads/probes.** Installed docs/plugins root selection, private docs-index fallback reads, prompt-completion no-timeout standalone mode, and stdlib package-resource loading should be patched only if hot/capability-sensitive or explicitly documented as trusted/local/tooling surfaces.
3. **Build one living resource-budget contract after the survivor sweep.** Consolidate repeated subprocess/future/OWASP research and point each row to source/test evidence.
4. **Move one plugin-owned family to a typed owner.** Choose prompt/history rows, timers, or macro slots; keep broad snapshots as a differential oracle until parity is proved.
5. **Add release provenance.** Dependency lock or recorded inputs, a small CI/package-inspection lane, artifact digests, and an explicit archive-revision versus package-version policy remain unfinished.
6. **Refresh living entrypoints.** `docs/01-llm-start-here.md` and `docs/43-worklist.md` should summarize the current rev09xx resource/effect state instead of leaving old handoff context at the top.

## Prior revision handoff

Rev0923 note: help-doc opening, explicit docs path resolution, relative help-link following, and target-heading metadata reads now use bounded contained filesystem read/stat seams instead of direct help-path `Path.read_text()` / `Path.is_file()` probes.

Latest tiny landing (rev0923): `src/micromax_editor/editor.py` adds `_docs_containment_root()` and `_read_help_doc_text()`; help buffers and help-link target-heading search now use `read_file_bytes_contained_bounded()` with docs-root containment, docs per-file byte budget, and the VM filesystem read timeout. `tools/mxaudit.py` hard-checks `help_doc_read_timeout_boundary`. `docs/881-help-doc-read-timeout.md` records the online research, validation, and remaining exact-survivor sweep risk.

# TODO (rev0923)

- [x] Research current subprocess timeout, executor cancellation, and resource-consumption guidance online.
- [x] Audit the next named survivor after project-root marker batching: help-doc open/read and link-target metadata.
- [x] Replace direct help-doc `Path.read_text()` with bounded contained reads.
- [x] Replace explicit docs path `Path.is_file()` and relative help-follow `exists()/is_file()` probes with bounded stat-backed resolution.
- [x] Keep CLI `allow_outside_root=True` behavior while preserving byte/time read limits.
- [x] Add focused regressions for help-doc read, relative link path resolution, and target-heading metadata.
- [x] Extend `mxaudit --check` with `help_doc_read_timeout_boundary`.
- [x] Record the landing in `docs/881-help-doc-read-timeout.md`.
- [x] package rev0923 with the required filename structure.

## Next up (high leverage)

1. **Retire one more small but real filesystem survivor.** Candidate seams include optional plugin metadata existence, installed docs/plugins root selection, and fallback/private markdown helpers; touch only if hot, delayed, or capability-sensitive.
2. **Keep code progress ahead of doctrine.** Do not start the generated effect table until the visible direct filesystem survivors are either removed or deliberately documented as one-shot local tooling.
3. **Compact repeated timeout evidence after the survivor sweep.** The recent notes repeat subprocess/thread/OWASP evidence enough that a living budget contract should absorb it once current revision entries are stable.
4. **Continue resource-handle enumeration.** Search plugin-owned objects outside dictionaries, generated callbacks, active interactions, saved macros, timer queues, prompt/completion callbacks, and clipboard helper state.
5. **Add remaining release engineering.** Dependency lock, small CI/package inspection, artifact provenance, and archive-revision versus package-version policy remain unfinished.

## Prior revision handoff

Rev0922 note: project-root discovery now batches parent marker observation through the bounded filesystem stat worker and a tiny short-lived cache instead of direct `Path.exists()` probes in hot recent/buffer grouping.

Latest tiny landing (rev0922): `src/micromax_editor/editor.py` adds `PROJECT_ROOT_MARKERS`, `PROJECT_ROOT_MARKER_BATCH_LIMIT`, and `_seed_project_root_cache()`; recent-file and buffer grouping preseed visible rows so labels/details reuse one bounded marker batch. `tools/mxaudit.py` hard-checks `project_root_marker_batch_boundary`. `docs/880-project-root-marker-batch.md` records the online research, validation, and remaining exact-survivor sweep risk.

# TODO (rev0922)

- [x] Research current subprocess timeout, executor cancellation, resource-consumption, and workspace-trust guidance online.
- [x] Audit the next named survivor after docs-root catalog scanning: `_project_root_for_path()` parent marker probes.
- [x] Replace direct project marker `Path.exists()` loops with bounded batched `stat_paths_contained_bounded()` observation.
- [x] Add a small TTL cache so recent/buffer grouping does not repeat marker work for label and display rewrites in the same render.
- [x] Preseed project-root cache from hot recent-file and buffer grouping rows.
- [x] Add focused regressions for bounded project-root discovery and recent-project cache reuse.
- [x] Extend `mxaudit --check` with `project_root_marker_batch_boundary`.
- [x] Record the landing in `docs/880-project-root-marker-batch.md`.
- [x] package rev0922 with the required filename structure.

## Next up (high leverage)

1. **Sweep one more concrete survivor before effect-table generation.** Candidate leftovers include markdown/source helper direct reads around exact commands and any remaining direct filesystem checks in editor hot paths; patch only if hot, delayed, or capability-sensitive.
2. **Keep killing survivor probes, not writing more doctrine.** Direct helper sweeps still beat another hand-maintained registry until the obvious filesystem survivors are retired.
3. **Compact repeated timeout evidence after code progress.** The resource-budget notes are numerous enough that older micro-notes should be folded into living contracts once revision-index coverage is stable.
4. **Continue resource-handle enumeration.** Search plugin-owned objects outside dictionaries, generated callbacks, active interactions, saved macros, timer queues, prompt/completion callbacks, and clipboard helper state.
5. **Add remaining release engineering.** Dependency lock, small CI/package inspection, artifact provenance, and archive-revision versus package-version policy remain unfinished.

## Prior revision handoff

Rev0921 note: docs/help catalog scanning now uses a bounded killable top-level inventory with file-count, byte-prefix, total-byte, and wall-clock budgets instead of direct glob/stat/read_text probes over the docs root.

Latest tiny landing (rev0921): `src/micromax_editor/docs_index.py` adds bounded docs-root scan records, a killable docs catalog worker, and process-local record reuse that avoids repeated worker scans during long help/status renders; `src/micromax_editor/file_access.py` adds `read_file_prefix_contained()` for fd-bound preview reads; `tools/mxaudit.py` hard-checks `docs_catalog_scan_timeout_boundary`. `docs/879-docs-catalog-scan-timeout.md` records the online research, validation, and remaining project-root discovery sweep risk.

# TODO (rev0921)

- [x] Research current subprocess timeout, executor cancellation, resource-consumption, and editor extension/workspace-trust guidance online.
- [x] Audit the next hot discovery surface after plugin discovery.
- [x] Add `read_file_prefix_contained()` for fd-bound preview/catalog reads that should not load whole files.
- [x] Replace docs catalog direct `glob/is_file/stat/read_text` scanning with one bounded docs-root inventory worker.
- [x] Preserve process-local docs cache behavior and parent-side heading/summary parsing.
- [x] Fix the safe-but-wasteful repeated worker scan regression found in long help/status renders.
- [x] Add focused docs-index regressions for no direct `Path.glob()/Path.read_text()` and prefix-budget large-doc discovery.
- [x] Extend `mxaudit --check` with `docs_catalog_scan_timeout_boundary`.
- [x] Record the landing in `docs/879-docs-catalog-scan-timeout.md`.
- [x] package rev0921 with the required filename structure.

## Next up (high leverage)

1. **Sweep project-root discovery before effect-table generation.** `_project_root_for_path()` still walks parents with ordinary marker probes. Convert it to a bounded/batched marker check if it proves hot or delayed.
2. **Keep killing survivor probes, not writing more doctrine.** Direct helper sweeps still beat another hand-maintained registry until the obvious filesystem survivors are retired.
3. **Compact repeated timeout evidence.** The resource-budget notes are numerous enough that older micro-notes should be folded into living contracts once revision-index coverage is stable.
4. **Continue resource-handle enumeration.** Search plugin-owned objects outside dictionaries, generated callbacks, active interactions, saved macros, timer queues, prompt/completion callbacks, and clipboard helper state.
5. **Add remaining release engineering.** Dependency lock, small CI/package inspection, artifact provenance, and archive-revision versus package-version policy remain unfinished.

## Prior revision handoff

Rev0920 note: plugin discovery now uses bounded contained top-level listing, and restricted manual-load package fingerprinting runs recursive scan plus contained byte reads in a killable worker with file, byte, and time budgets.

Latest tiny landing (rev0920): `src/micromax_editor/plugins.py` adds explicit plugin discovery and package fingerprint timeout budgets, replaces plugin-root `Path.iterdir()` discovery with `list_dir_contained_bounded()`, and moves manual-load grant package fingerprint scanning into `_plugin_package_fingerprint_worker`. `tools/mxaudit.py` hard-checks `plugin_discovery_fingerprint_timeout_boundary`. `docs/878-plugin-discovery-fingerprint-timeout.md` records the online research, validation, and remaining docs/project-root discovery sweep risk.

# TODO (rev0920)

- [x] Research current subprocess timeout, executor cancellation, and resource-consumption guidance online.
- [x] Audit plugin discovery and manual-load package grant fingerprinting before adding another effect registry.
- [x] Add explicit plugin discovery row/time budgets and package fingerprint time budget knobs.
- [x] Replace plugin-root `Path.iterdir()` discovery with bounded contained top-level listing.
- [x] Preserve contained symlink-directory behavior with bounded stat for top-level plugin dir candidates.
- [x] Move recursive package scan plus contained byte reads into a killable fingerprint worker.
- [x] Preserve existing package file-count and total-byte budgets.
- [x] Add focused regressions for bounded plugin discovery and fingerprint timeout fail-closed behavior.
- [x] Extend `mxaudit --check` with `plugin_discovery_fingerprint_timeout_boundary`.
- [x] Record the landing in `docs/878-plugin-discovery-fingerprint-timeout.md`.
- [x] package rev0920 with the required filename structure.

## Next up (high leverage)

1. **Sweep docs-root and project-root discovery helpers before adding policy tables.** Plugin discovery is now bounded; docs/project marker discovery are the next exact ambient probes worth touching if they are hot, delayed, or capability-sensitive.
2. **Compact repeated evidence overhead.** The timeout/resource notes are now numerous enough that old micro-notes should be folded into living contracts once revision-index entries cover them.
3. **Generate the first data-backed filesystem effect slice only after the survivor sweep.** The table becomes valuable after the remaining obvious direct probes are retired, not before.
4. **Continue resource-handle enumeration.** Search plugin-owned objects outside dictionary words, generated callbacks, active interactions, saved macros, timer queues, prompt/completion callbacks, and clipboard helper state.
5. **Add remaining release engineering.** Dependency lock, small CI/package inspection, artifact provenance, and archive-revision versus package-version policy remain unfinished.

## Prior revision handoff

Rev0919 note: parsecursor literal-path checks and status read-only refresh now route through bounded filesystem observation, with hot palette parsecursor checks reusing the palette stat cache.

Latest tiny landing (rev0919): `src/micromax_editor/file_access.py` adds `ContainedAccessResult` plus `access_path_contained_bounded()` for status read-only truth under the existing filesystem stat timeout worker. `src/micromax_editor/editor.py` moves parsecursor's colon-literal existence check to `_bounded_fs_stat()` with a palette-cache reuse path for hot row builders and replaces status `Path.exists()/is_dir()/os.access()` refresh with the bounded access helper. `tools/mxaudit.py` hard-checks `status_readonly_parsecursor_bounded`. `docs/877-status-access-bounded.md` records the research, validation, and remaining exact-helper sweep risk.

# TODO (rev0919)

- [x] Research current subprocess timeout, executor cancellation, resource-consumption, and capability-handle guidance online.
- [x] Audit remaining exact single-path UI filesystem helpers after the palette batch pass.
- [x] Add a bounded contained access helper for status read-only truth.
- [x] Route status read-only live refresh through the bounded access helper instead of direct `Path.exists()/Path.is_dir()/os.access()`.
- [x] Route parsecursor colon-literal existence checks through the bounded stat seam.
- [x] Add focused regressions for parsecursor bounded stat and status bounded access refresh.
- [x] Extend `mxaudit --check` with `status_readonly_parsecursor_bounded`.
- [x] Record the landing in `docs/877-status-access-bounded.md`.
- [x] package rev0919 with the required filename structure.

## Next up (high leverage)

1. **Sweep project-root and discovery helpers before adding policy tables.** `_project_root_for_path`, docs-root discovery, and plugin discovery still deserve the same exact-helper audit, but only patch paths that are hot, delayed, or capability-sensitive.
2. **Continue resource-handle enumeration.** Search plugin-owned objects outside dictionary words, generated callbacks, active interactions, saved macros, timer queues, prompt/completion callbacks, and clipboard helper state.
3. **Generate the first data-backed filesystem effect slice after the survivor sweep.** The table is useful only once the obvious direct probes are retired; avoid another hand-written doctrine pass first.
4. **Compact docs/evidence overhead.** Consolidate old micro-notes into living contracts once revision-index entries cover the same facts.
5. **Add remaining release engineering.** Dependency lock, small CI/package inspection, artifact provenance, and archive-revision versus package-version policy remain unfinished.

## Prior revision handoff

Rev0918 note: command-palette recent/known-path disk truth now batches visible path stat work through one bounded filesystem worker and reuses a one-build cache, avoiding the per-row timeout-worker/process-churn trap left open by the status hardening passes.

Latest tiny landing (rev0918): `src/micromax_editor/file_access.py` adds `stat_paths_contained_bounded()` for deduplicated fd-backed stat batches under the existing filesystem timeout worker. `src/micromax_editor/editor.py` adds a one-build `_palette_fs_stat_cache`, seeds it from visible recent rows, recent inventory rows, and known-path completion candidates, and then reuses cached disk truth in `_palette_fs_stat()` instead of spawning one single-path worker per visible row. `tools/mxaudit.py` hard-checks `palette_recent_stat_batch_boundary`. `docs/876-palette-stat-batch.md` records the research, validation, and remaining effect-table/audit-refactor risk.

# TODO (rev0918)

- [x] Research current subprocess timeout, executor cancellation, and resource-consumption guidance online.
- [x] Audit the rev0917 residual palette/recent stat-probe risk and choose batched metadata observation over per-row timeout workers.
- [x] Add `stat_paths_contained_bounded()` as a deduplicated batch wrapper around fd-backed contained stat.
- [x] Add a one-build palette stat cache and cache-key helper in the editor.
- [x] Seed command-palette recent-file rows from the batch stat seam before rendering disk/action cues.
- [x] Seed recent inventory rows from the same batch seam so broad `recent` truth does not multiply stat workers.
- [x] Seed known-path completion candidates before per-row kind classification and add a regression that forbids single-row stat fallback there.
- [x] Extend focused command-palette/recent tests for batch stat behavior.
- [x] Extend `mxaudit --check` with `palette_recent_stat_batch_boundary`.
- [x] Record the landing in `docs/876-palette-stat-batch.md`.
- [x] package rev0918 with the required filename structure.

## Next up (high leverage)

1. **Generate the first data-backed filesystem effect slice.** Now that stat/list/read/open/source/prompt/write/preflight/status/palette seams exist, generate audit predicates from one table instead of hand-writing one more string check.
2. **Continue resource-handle enumeration.** Search plugin-owned objects outside dictionary words, generated callbacks, active interactions, saved macros, timer queues, prompt/completion callbacks, and clipboard helper state.
3. **Sweep exact single-path UI helpers for accidental hot use.** The palette/recent broad surfaces are batched now; any exact helper that becomes hot should either preseed or opt into stale/cached behavior rather than per-row workers.
4. **Compact docs/evidence overhead.** Consolidate old micro-notes into living contracts once revision-index entries cover the same facts.
5. **Add remaining release engineering.** Dependency lock, small CI/package inspection, artifact provenance, and archive-revision versus package-version policy remain unfinished.

## Prior revision handoff

Rev0917 note: hot status disk/read-only observation now has a stale-marked slow-refresh cadence; open/save witness refresh seeds the status cache so the first render after sync does not duplicate stat work.

Latest tiny landing (rev0917): `src/micromax_editor/options_default.py` adds `diskstate.refreshms` (default 1000ms) alongside `diskstate.cachems`. `src/micromax_editor/editor.py` now stores fresh and refresh deadlines for status disk-state/read-only cache entries, returns `disk_status_stale=1` while reusing an expired-but-not-refresh-due witness, and seeds fresh/new status cache rows from the open/save witness already captured. Explicit `diskstate`, disk-state hostcalls, save preflight, revert, and diff still force live bounded checks. `tools/mxaudit.py` hard-checks the seeded stale-refresh status boundary. `docs/875-status-slow-refresh.md` records the research, validation, and remaining palette-stat batching risk.

# TODO (rev0917)

- [x] Research current subprocess timeout, directory metadata caching, and resource-consumption guidance online.
- [x] Audit the rev0916 residual status cache-miss risk and choose stale-marked slow refresh over per-render/per-row workers.
- [x] Add `diskstate.refreshms` as a separate slow live-probe cadence for hot status disk observation.
- [x] Return explicit `disk_status_stale=1` when status reuses an expired-but-not-refresh-due disk-state witness.
- [x] Share fresh/refresh deadline storage between disk-state and OS readonly status cache entries.
- [x] Seed status disk-state cache rows from the open/save freshness witness to avoid a duplicate first-render stat.
- [x] Preserve exact live refresh for `diskstate`, disk-state hostcalls, save preflight, revert, and diff.
- [x] Extend focused status-cache tests for seeded cache, stale marking, and slow refresh.
- [x] Extend `mxaudit --check` with slow-refresh/stale status predicates.
- [x] Record the landing in `docs/875-status-slow-refresh.md`.
- [x] package rev0917 with the required filename structure.

## Prior revision handoff

Rev0916 note: hot status/disk-state rendering now has a short explicit cache/refresh cadence, while live diskstate recovery commands and script hostcalls still force exact stat refreshes; two overlooked directory probes were moved onto bounded stat.

Latest tiny landing (rev0916): `src/micromax_editor/options_default.py` adds `diskstate.cachems` (default 250ms). `src/micromax_editor/editor.py` adds `EditorBuffer.disk_state_cache`, `invalidate_disk_state_cache()`, cached stat-only `buffer_disk_state()` use for `status_model()`, cached OS readonly status truth, live `disk_state_rows(refresh=True)`, and bounded command-palette directory drilldown stat. `src/micromax_editor/file_scriptops.py` routes scripted save directory-kind preflight through `ed._bounded_fs_stat(..., containment_root=cap.fs-root)`. `tools/mxaudit.py` hard-checks `editor_disk_state_cache_boundary`. `docs/874-diskstate-status-cache.md` records the research, validation, and remaining async-refresh risk.
