# Rev365: keep plain `buffers` / `marks` inventory count-aware

This is a tiny trust/flow follow-up to rev344 and rev346.

## Problem

Micromax already made plain buffer and mark inventory much more honest:

- `buffers` shows the active marker, visible `dirty` / `readonly` flags, and cursor targets
- `marks` shows active-buffer ownership, keeps `@ line:col` target spelling, and adds a tiny `[here]` cue for the anchor under the current primary cursor

But both commands still had one small structural mismatch:

- empty inventories fell back to `(none)`
- non-empty inventories made you mentally count how many buffers or marks existed before reading the real rows

That meant the same ordinary inspection commands still changed dialect exactly when the answer dropped to zero.

## Change

Both commands now start with tiny count-aware prefixes:

- `buffers: 0 buffer(s)`
- `buffers: 2 buffer(s), alpha [dirty] @ 2:0; *beta @ 1:2`
- `marks: 0 mark(s)`
- `marks: 2 mark(s), here -> *alpha [here] @ 2:0; there -> beta @ 1:1`

The old per-entry detail stays intact.
Only the inventory head became explicit and structurally consistent.

## Why this matters

This is small, but it helps both humans and future LLMs answer the first inventory question faster:

- how many things are there?
- is the answer really zero?
- do I need to scan several rows or not?

A good rule here is:

> ordinary navigation inventory should stay glanceable whether the answer is zero, one, or many.

## Scope discipline

This intentionally does **not** add richer grouping, persistence, or new picker behavior.
It only tightens the plain message dialect for two already-existing commands.
