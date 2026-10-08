# Rev772 — script cap-mutation guard and contained persistence I/O

## Why this mattered

The previous file-capability work made `ed.open`, `ed.save`, `ed.fs-read`, `ed.fs-list`, `ed.fs-stat`, `ed.require`, and scripted recovery paths much more honest about `cap.fs-root`. While auditing adjacent authority seams, two quieter gaps stood out.

First, script-originated command paths could still mutate capability options. A script blocked from saving could run `set cap.fs-save true` through `ed.command`, then immediately call `save`. That made the capability checks look strong at the file operation, while the script still held a nearby self-escalation route through option mutation.

Second, editor-owned persistence files still used older `Path.read_text()` / `Path.write_text()` flows. Persistence is gated by `cap.persist`, but once enabled it should not be a weaker host-file boundary than normal save/recovery. Late symlink swaps and huge JSON files were still more wasteful or surprising there than in the main file I/O path.

## What changed

`Editor` now has a shared option-mutation policy seam:

- `Editor.set_option_value(...)`
- `Editor.toggle_option_value(...)`
- `Editor._guard_option_mutation(...)`

Command-bar `set` / `setlocal` / `toggle` / `togglelocal`, VM hostcalls `ed.opt-set` / `ed.opt-set-local`, and immediate Micromax option words `set` / `toggle` now route through that seam. In editor script context, attempts to mutate canonical `cap.*` options fail with a clear error and do not refresh or advertise the requested capability. Trusted user init/config code and direct interactive commands can still enable capabilities explicitly.

New module:

`src/micromax_editor/persist_io.py`

It moves recent-file, prompt-history, and savecursor persistence onto a contained I/O seam:

- persistence reads use `read_file_bytes_contained(...)` with `cap.persist-root` as the containment root;
- persistence writes use `write_file_bytes(...)` with `containment_root=cap.persist-root`;
- parent creation uses `ensure_parent_directory(..., containment_root=cap.persist-root)`;
- reads are bounded by `persist.maxbytes`;
- writes use `persist.atomic` by default and can opt into `persist.fsync`.

New options:

- `persist.atomic` default `true`;
- `persist.fsync` default `false`;
- `persist.maxbytes` default `1048576`.

## Regression coverage

New tests cover script self-escalation attempts through:

- `ed.command` + command-bar `set cap.fs-save true`;
- direct `ed.opt-set` inside `script_context()`;
- `ed.command` + `toggle cap.fs-open`.

They also pin that trusted direct VM/config evaluation can still set capability options, preserving the intended user-init path.

Persistence tests now cover:

- a late symlink swap before a recent-file persistence write, verifying the outside target is not overwritten;
- a late symlink swap before prompt-history load, verifying outside JSON is not imported;
- `persist.maxbytes` refusing oversized persistence JSON.

`tools/mxdoctor.py` includes `tests/test_editor_persistence_cap_persist.py` in the bounded default risk lane so this does not regress outside one-off focused runs.

## Remaining risk

This is still an application-level boundary, not an OS sandbox. Trusted init/plugin code that the user chooses to run is still allowed to enable capabilities; that is intentional because Micromax uses init files as the normal configuration surface. The important change is narrower: lower-authority script-originated callbacks into the editor cannot grant themselves new host capabilities mid-call.

Persistence writes intentionally overwrite editor-owned JSON files rather than doing document-style external-change conflict prompts. The new safety boundary is containment and bounded I/O, not merge/conflict UX for recent/history/cursor metadata.

The next adjacent risk lane is to audit the remaining language-level load surfaces (`include`, core VM `require`/`reload`, and plugin bootstrap paths) and decide which ones are trusted-configuration-only versus script-context host authority.
