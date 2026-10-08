# Rev0881 — touched hook/mark rollback

Rev0881 continues the practical typed-journal migration on the plugin cleanup path. Runtime-group cleanup and retag rollback now scopes two more live surfaces to the affected runtime group(s): hook handlers and named marks.

## Why this mattered

Rev0880 had already narrowed commands, actions, keybindings, and pending timers. Hooks and marks still used broader snapshot fields inside `RuntimeGroupStateSnapshot`. That kept cleanup rollback correct in common cases, but it remained wasteful and hid a sharper bug: hook handlers are mutable `HookHandler` dataclasses, and retagging changes their `group` in place. A shallow hook snapshot could therefore save references to the same handler objects that retag later mutated.

In that failure mode, a later surface could fail after hook retag had already run, and restore would reinstall hook handlers whose saved rows had already been mutated from the staged group to the stable group. The rollback evidence was not detached from the operation it was supposed to undo.

## What changed

- Added `RuntimeHookGroupSnapshot`.
- Added `RuntimeMarkGroupSnapshot`.
- Added `snapshot_hook_group_state()` and `restore_hook_group_state()`.
- Added `snapshot_mark_group_state()` and `restore_mark_group_state()`.
- `RuntimeGroupStateSnapshot` now carries `hook_state` and `mark_state` instead of full hook-handler and mark dictionaries.
- Hook snapshots clone mutable `HookHandler` rows with `dataclasses.replace()`.
- Broad hook snapshots used by `RuntimeRegistrationSnapshot` also clone mutable hook handlers, so source/lifecycle/callback rollback does not keep shallow handler evidence either.
- Focused tests prove unrelated trusted hook and mark rows are not copied into the group snapshot and are not rewound by restore.
- A retag-failure test proves hook-handler groups and mark groups return to the staged group when a later surface fails after hook and mark promotion.
- `mxaudit` now checks the hook/mark group snapshot seam and the mutable-hook clone helper.

## What this guarantees

For runtime-group cleanup/retag commit guards, hook and mark recovery is now scoped to affected runtime groups. If a cleanup or retag sweep partially mutates hook or mark rows and a later surface fails, the guarded operation restores affected hook handlers and marks from detached evidence.

For unaffected hook words and mark rows outside the group snapshot, restore does not rewind unrelated mutations. This matches the touched-surface behavior already landed for commands, actions, keybindings, and timers.

## What this does not claim

This is not the full typed effect journal. It still leaves several delayed-state sidecars copied at broader granularity. It does not sandbox hostile Python code, make same-process plugins safe, roll back arbitrary document edits, reverse shell/URL/network/file effects, or make cleanup diagnostics durable across process restart.

The repeated touched-group helper shape is now obvious across six live surfaces. The next useful refactor is to factor that pattern carefully, not to create another universal registry bureaucracy.
