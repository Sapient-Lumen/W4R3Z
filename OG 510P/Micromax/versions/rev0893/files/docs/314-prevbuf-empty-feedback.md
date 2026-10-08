# `prevbuf` empty feedback

This revision tightens one last tiny buffer-navigation message seam.

`prevbuf` already had the right behavior when a previous MRU buffer existed:

- switch to the most-recently-used *other* buffer
- restore the landed cursor
- report the landed target as `prevbuf: name @ line:col`

But the empty path still fell back to a raw placeholder:

- `prevbuf: (none)`

That was technically accurate enough for tests, but it was a poor action message.
It did not say *what* was missing, and it spoke a different dialect from nearby
navigation failures like `no earlier jump` / `no later jump`.

## What changes now

`prevbuf` now fails plainly as:

- `prevbuf: no previous buffer`

This covers both practical empty cases:

- there was never another buffer in the MRU list
- the remembered previous buffer no longer exists by the time the command runs

## Why this matters

This is a tiny change, but it lands in a high-frequency recovery loop.

When users ask to go back to the previous buffer, the failure mode should say
exactly why the action cannot complete. A placeholder like `(none)` forces a bit
of interpretation right at the moment where the command should be boring.

## Product fit

This small follow-up fits the repo's current sequence well:

- **Trust**: failed navigation commands should explain themselves directly.
- **Flow**: recovery loops should not make the user decode placeholders.

It is also a natural extension of the recent buffer and jump honesty work:

- rev332: landed buffer-orientation feedback
- rev341: explicit jumpback/jumpforward empty feedback
- rev365: count-aware plain `buffers` inventory
- rev372: explicit `prevbuf` empty feedback

## Tests

Focused coverage now pins down:

- `prevbuf` with no other MRU target
- `prevbuf` after the remembered previous buffer disappeared
- the existing landed-buffer success path

The goal is simple: buffer recovery should fail plainly, not cryptically.
