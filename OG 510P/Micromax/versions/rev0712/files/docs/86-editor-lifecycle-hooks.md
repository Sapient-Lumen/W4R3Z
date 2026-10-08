# Editor lifecycle hooks (rev1)

micromax-editor exposes a small set of **notification hooks** inside the embedded
Micromax VM.

They are deliberately conservative:
- real hook inventories are also available through the tiny shared `hook_inventory_rows(NAME)` / `ed.hook-inventory-rows` register, so `showhook NAME` and host-side scripting stay aligned
- they are **best-effort** (errors are caught and surfaced as editor messages)
- hook failures now use the same typed runtime-error dialect as other scripted editor surfaces: `hook NAME: error: DETAILS`
- they are **notifications** (handlers can't affect editor control flow)
- they are **stack-isolated per handler** (see below)

This keeps the editor debuggable and reload-friendly while still enabling
plugins to react to events. When you inspect one of these names with
`showhook NAME`, real hooks report count-aware handler detail and non-hook
lookups fail plainly as `showhook: not a hook: NAME`.

## Stack isolation rule (important)

Hook handlers are treated as notifications.

When a hook word runs multiple handlers (and `showhook NAME` now reports their count explicitly):
- each handler runs with the **same initial data stack**
- any stack effects are **discarded between handlers**
- the return stack is truncated back to its initial depth

In other words, handlers do **not** form a pipeline.

This makes handler ordering irrelevant and prevents accidental coupling.

## Editor hook names and stack contracts

These hooks are defined at editor boot:

### `ed.pre-action`

Called before an editor action executes.

Stack:
- `( "action" -- )`

### `ed.on-action`

Called after an editor action executes.

Stack:
- `( "action" ok -- )`

Where `ok` is `1` for success and `0` for failure.

### `ed.on-change`

Called after an action that **mutates the active buffer's text**.

Stack:
- `( "buffer" "action" -- )`

This is driven by a monotonic `Buffer.version` counter bumped on any text
mutation.

### `ed.on-open`

Called after `open` / `Editor.open_file()` creates a buffer.

Stack:
- `( "buffer" "path" "filetype" -- )`

### `ed.on-save`

Called after `save` writes the active buffer to disk.

Stack:
- `( "buffer" "path" -- )`

## Example

Increment a counter every time the user edits text:

```forth
variable edits

: on-change ( buf action -- )
  2drop
  edits @ 1 + edits !
;

' on-change hook-add ed.on-change
```


Rev393 follow-up: best-effort lifecycle hooks now keep the hook name visible on failures too, so a broken `ed.on-save` or `ed.on-change` handler is immediately attributable in headless logs and tests.
