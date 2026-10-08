# Rev0803 — named-mark read/replay authority

Rev0803 continues the protected-register audit after the macro-register landing.  Named marks already carried mutation provenance, but their read and replay surfaces were still too broad: a lower-authority script could inventory trusted mark names, buffer names, positions, and line previews, or jump to a user mark as delayed navigation state.

## Failure mode

Before this revision, `mark_set(...)` guarded overwrites, but these surfaces did not check mark ownership:

- `ed.marks`
- `ed.mark-inventory-rows`
- `ed.mark-detail-row`
- `mark_prompt_rows()` / mark picker rows / command completion
- command-bar `marks`, `showmark`, and `showmarkgroups`
- `ed.mark-jump`, `markjump`, and mark picker submission

That made named marks inconsistent with the protected-register model already used for undo/redo, prompt history, recent rows, clipboard, saved cursors, selections, jumps, help/message history, and saved macros.  A mark is small, but it can expose private workflow evidence through its name, buffer, exact position, and source-line preview.  It can also move the editor later, so mark replay is a delayed navigation operation.

I also found a related destructive edge: closing or renaming a clean buffer dropped or retargeted marks pointing at that buffer without consulting mark authority.  A script did not need write access or dirty-buffer discard authority to erase a trusted mark if the target buffer happened to be clean.

## Change

New module:

`src/micromax_editor/mark_policy.py`

It introduces a small mark access policy using the existing runtime-authority shape.  Trusted interactive/editor callers keep normal access.  Script-origin callers may read or jump to marks they created themselves, including same loaded plugin-generation marks.  Trusted/user marks and marks owned by another script/plugin generation are hidden or denied by default.

New unsafe capabilities:

- `cap.mark-read` / `ed.mark-read`: allow scripts to inspect trusted/user or other-origin mark rows.
- `cap.mark-jump` / `ed.mark-jump`: allow scripts to jump to trusted/user or other-origin mark targets.

`cap.mark-jump` is intentionally not also a read grant.  A script can be allowed to jump to a protected mark without being allowed to inventory all mark names, buffers, positions, and source-line previews.

## Bound surfaces

Read/inventory paths now filter through the current runtime authority:

- `mark_rows()`
- `mark_detail_row(...)`
- `mark_inventory_rows()`
- `mark_prompt_rows()`
- mark picker grouping/summary rows
- command completion for `showmark`, `mark`, and `markjump`
- hostcalls and command rows that reuse those models

Replay paths now preflight the mark authority before moving the editor:

- `Editor.mark_jump(...)`
- `ed.mark-jump`
- `markjump NAME`
- mark picker submission

Denied `ed.mark-jump` and `ed.mark-detail-row` calls now peek before consuming their mark-name operand, preserving failed-operation evidence on the VM stack.

Close/rename cleanup also became authority-aware.  `close`, `closeall`, `only`, and save/revert retitle flows that call `rename_buffer(...)` can no longer erase or retarget protected marks from lower-authority script context.  Same-origin script marks are still cleaned up normally when their buffer is intentionally closed.

## Validation

New focused tests in:

`tests/test_editor_mark_access_authority.py`

They cover denied script reads of trusted marks, explicit `cap.mark-read`, denied script jumps, explicit `cap.mark-jump`, same-origin script mark access, cross-script isolation, command-completion filtering, close-buffer protection, same-origin close cleanup, and rename-retarget protection.

The default `mxdoctor` target set now includes the mark-access authority file while staying under the existing bounded target budget.

## Remaining risk

This is still an editor-level provenance model, not an OS sandbox.  Trusted interactive code can read and jump all marks by design.  Future mark persistence/import/export should stamp persisted rows as lower-authority state and reuse `mark_access_policy(...)` rather than walking `self.marks` directly.
