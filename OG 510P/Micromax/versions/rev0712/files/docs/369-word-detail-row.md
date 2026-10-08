# Word detail row (rev427)

Micromax already had the important visible-word inspection loop before rev427: editor `showword NAME` exposed the winning visible word's kind/effect/doc/source detail, prompt completion could already surface compact word metadata for discovery, and the VM itself already had lower-level introspection words like `help`, `see`, and `where`.

The remaining seam was not word lookup; it was **host-boundary symmetry**.
Humans could inspect the richer visible-word register directly through `showword`, but scripts and future UIs still had to reach through VM internals or parse command text to recover the same tiny detail truth.

Rev427 adds one deliberately small shared surface instead of a bigger dictionary browser:

- `word_detail_row(NAME)` returns one canonical visible-word detail row inside the editor
- `ed.word-detail-row` exposes the same row to Micromax scripts and future UIs
- plain `showword NAME` now reuses that same row surface instead of rebuilding it inline
- prompt word metadata now also reuses that same row, so command completion and explicit inspection stop drifting apart

The row stays intentionally tiny:

- `name` — the visible word name as resolved through the current search order
- `kind` — tiny word kind (`primitive`, `colon`, `deferred`, `hook`, or `word`)
- `effect` — best-effort stack effect text when known
- `wordlist` — winning visible wordlist name
- `doc` — best-effort summary/doc text
- `[file line col]|0` — best-effort definition span when known
- `source|0` — best-effort `xt-src` text when available

This deliberately complements the existing VM-side introspection words instead of replacing them.
The design goal is simple: if one visible word already matters enough for humans to inspect from the editor prompt, the same tiny register should be available headlessly too.
