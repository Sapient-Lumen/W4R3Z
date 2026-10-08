# Rev810 — open-buffer register authority

Rev810 closes the next protected-register gap from the rev809 worklist: open-buffer inventory and cross-buffer navigation.

## Why this was risky

Open buffers are not just UI chrome. A buffer row can expose host paths, dirty/protected state, cursor positions, line counts, project-root grouping, and picker ranking. A lower-authority script that cannot read recent-file history, prompt state, marks, macros, search state, messages, or clipboard registers should not be able to enumerate every inactive trusted/user buffer and then switch into one through `ed.set-active-buffer`, `ed.with-buffer`, `buffer NAME`, `prevbuf`, or buffer-prompt submit.

The active buffer remains deliberately ambient. Micromax scripts are editor automation, and many useful scripts are invoked specifically to operate on the current buffer. Rev810 therefore protects **inactive protected buffers** by default while keeping the current active buffer and same-origin script-created buffers usable.

## What changed

The existing partial buffer provenance seam is now completed and covered:

- `src/micromax_editor/buffer_policy.py` owns open-buffer access decisions.
- Each live buffer has a `_buffer_authority` sidecar keyed by buffer name.
- `new_buffer(...)` stamps buffers with the current runtime authority.
- close, close-all, rename, save-as rollback, macro replay, and with-undo snapshots preserve the buffer-authority sidecar.
- `close NAME`, `closeall`, and `only` no longer let a lower-authority script erase inactive trusted/user buffer session state unless the buffer is same-origin, active/ambient, or `cap.buffer-discard` is enabled.
- `visible_buffer_names()` is now the public script-visible inventory root.
- `buffer_inventory_rows()`, `buffer_detail_row()`, `buffer_prompt_rows()`, grouped buffer section rows, buffer section summaries, status buffer fields, and `ed.buffers` use the authority filter.
- `ed.buffer-detail-row` preflights access before consuming the name operand.
- `ed.set-active-buffer`, `ed.with-buffer`, scripted `buffer NAME`, scripted `prevbuf`, and buffer-prompt submit use the switch guard.
- `open_file(...)` refuses to silently switch a script into an already-open protected inactive buffer; that path now needs switch authority rather than laundering through `cap.fs-open`.

## Capabilities

New unsafe capabilities:

- `cap.buffer-read` / `ed.buffer-read` — inspect trusted/user or other-origin inactive buffer metadata and picker rows.
- `cap.buffer-switch` / `ed.buffer-switch` — switch into trusted/user or other-origin inactive buffers.
- `cap.buffer-discard` / `ed.buffer-discard` — explicitly allow destructive buffer-state cleanup, including force-discard of dirty buffers and closing protected inactive clean buffers.

The split is intentional. Read authority reveals inactive session metadata; switch authority is delayed navigation/replay; discard authority erases editor session state. Granting one does not automatically grant the others.

## Compatibility decision

The active buffer is still visible to scripts. That is the object the script was invoked to automate. The protection boundary is around inactive buffers and cross-origin/session-wide inventory, where a script previously got more information and navigation authority than it needed.

## Validation

Focused coverage lives in:

- `tests/test_editor_buffer_authority.py`
- `tests/test_editor_capabilities_registry.py`

The focused run during rev810 also exercised buffer lifecycle/marks, protected inactive close/close-all denial, and selected script filesystem capability regressions.

## Remaining risk

The broader protected-register audit should continue on session/UI read surfaces that are still intentionally broad, especially keymode/binding discovery and action/command inventories. Those may be acceptable public editor dictionaries, but they should be explicitly audited rather than assumed safe by age.
