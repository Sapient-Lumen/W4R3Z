# Close success feedback

This revision tightens a tiny wording seam in the buffer-cleanup loop.

The editor already had the *behavioral* part right:

- `close` preserved the dirty-buffer safety guard
- closing the active buffer reported the landed active buffer/cursor target
- closing a non-active named buffer reported which target disappeared
- `closeall` reported the surviving active buffer after mass close

But the success wording still lagged behind the newer typed command dialect.

Before this revision, success lines looked like:

- `closed: notes.txt`
- `closed: notes.txt -> buffer: todo.txt @ 4:2`
- `closed all -> buffer: *scratch* @ 1:0`

Those messages were understandable, but they no longer matched the newer command-specific style used by nearby navigation and editing surfaces.

## What changes now

Successful close commands now keep the command family visible too:

- `close: target`
- `close: target -> buffer: landed @ line:col`
- `closeall -> buffer: landed @ line:col`

Misses stay unchanged from the earlier trust cleanup:

- `close: no such buffer: NAME`

## Why this matters

This is a tiny change, but it lands in a high-frequency loop. Close operations show up in tests, logs, demos, and future LLM traces. Self-identifying success feedback makes those traces easier to skim without forcing the reader to remember which older verb belonged to which command.

## Product fit

This change continues the same direction as the recent tiny feedback pass:

- successful edits and navigation should identify themselves plainly
- failure and success should stay in one consistent command dialect
- headless-first traces should be easy to scan line by line

## Tests

Focused coverage now pins down:

- closing the active buffer: `close: old -> buffer: new @ line:col`
- closing all buffers: `closeall -> buffer: *scratch* @ line:col`

The goal is simple: buffer cleanup should speak as plainly as buffer navigation.
