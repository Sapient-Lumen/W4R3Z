# Rev250: portability follow-up for `2rot`

This revision adds tiny boot-stdlib `2rot` to `src/micromax/stdlib/core.mx` and
pins it down in the JSON portability corpus.

Why this is worth keeping:

- `2rot` is a standard-shaped pair-stack helper, so future Rust/WASM hosts have
  one more familiar bring-up checkpoint.
- Keeping it in `core.mx` preserves Micromax's preference for source-visible
  convenience words instead of growing the VM primitive set.
- The JSON cases let future ports validate the exact pair rotation without
  importing Python-only helpers.

Portable contract captured here:

- `1 2 3 4 5 6 2rot` -> `3 4 5 6 1 2`
- `10 20 30 40 50 60 2rot` -> `30 40 50 60 10 20`
