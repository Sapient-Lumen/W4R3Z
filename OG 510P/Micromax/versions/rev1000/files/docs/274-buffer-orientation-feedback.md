# Buffer orientation feedback

This revision tightens a small but common flow/trust gap in command-driven buffer movement.

The editor already had the *behavioral* part mostly right:

- MRU-aware `prevbuf`
- searchable `bufferpick`
- safe `close` / `closeall` / `only` guards for dirty buffers
- stable cursor restoration inside surviving buffers

But several success paths still spoke too vaguely.

Before this revision, messages like these were common:

- `buffer: notes.txt`
- `prevbuf: notes.txt`
- `closed`
- `closed all`
- `only: closed others`
- `only error: boom`
- `closeall error: boom`

Those messages confirmed that *something* happened, but they still made the user infer the most important part:

- which buffer is active now?
- where is the cursor now?
- what did closing the current buffer actually land on?

That was not a correctness bug. It was an orientation bug.

## What changes now

Ordinary buffer-navigation commands now report the landed active target more explicitly:

- `buffer: path-or-name @ line:col`
- `prevbuf: path-or-name @ line:col`
- `close: old -> buffer: path-or-name @ line:col` when closing the active buffer
- `close: old` when closing a non-active explicit target
- `only -> buffer: path-or-name @ line:col`
- `closeall -> buffer: path-or-name @ line:col`

The same improvement also reaches live `bufferpick` submission, so typed buffer switching and picker-driven buffer switching stay aligned.

## Why this matters

This is a small change, but it lands in a high-frequency loop.

For command-driven editing, every extra moment of “wait, where did that put me?” costs flow. The editor already knew the answer. It just was not saying it clearly enough.

This revision keeps the implementation intentionally small:

- no new subsystem
- no new persistent UI surface
- no richer layout model
- no new buffer-management feature

It just makes existing navigation commands tell the truth more completely.

## Product fit

This change fits the repo’s current sequence well:

- **Trust**: successful commands should describe the state they produced.
- **Flow**: navigation should preserve orientation instead of asking the user to reconstruct it.

It is also a natural follow-up to the recent trust-first message work:

- rev328: clean default startup
- rev329: honest replace feedback
- rev330: honest save feedback
- rev331: honest explicit open feedback
- rev332: honest buffer-navigation/orientation feedback

## Tests

Focused coverage now pins down:

- `bufferpick` reporting the landed buffer/cursor
- `prevbuf` reporting the landed buffer/cursor
- `prevbuf` failing plainly as `prevbuf: no previous buffer` when there is no MRU target
- `close` on the active buffer reporting the next active buffer/cursor
- `only` and `closeall` reporting the resulting active buffer/cursor

The goal is simple: buffer movement should preserve orientation, not merely change state. A small follow-up now also applies that same trust rule on misses and cleanup success paths: explicit named-buffer commands say which command failed, and successful `close` / `closeall` calls now identify themselves with the same typed dialect as the rest of the command bar.
