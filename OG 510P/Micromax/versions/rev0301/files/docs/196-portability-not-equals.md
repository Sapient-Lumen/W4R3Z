# Rev254: portability follow-up for `<>`

This revision adds a tiny boot-stdlib `<>` helper to `src/micromax/stdlib/core.mx`:

```forth
: <> ( a b -- flag )  = 0= ;
```

Why this is worth pinning down:

- the current Forth standard still lists `<>` as a CORE EXT word, so it is a
  standard-shaped comparison helper rather than a Micromax-specific flourish
- Micromax already has the needed kernel pieces (`=` and `0=`), so keeping `<>`
  source-visible matches the repo's current preference for a tiny inspectable VM
  plus replayable stdlib contracts
- Micromax uses the language-wide `0` / nonzero truthiness convention rather than
  Forth's stricter “all bits set” well-formed `TRUE`, so `<>` is a cleaner next
  standard-shaped flag helper than adding `TRUE`/`FALSE` right now

The JSON portability corpus now includes:

- `stdlib-not-equals-predicate`
- `stdlib-not-equals-handles-strings`

Focused examples:

- `3 3 <> 3 4 <>` -> `0 1`
- `"a" "a" <> "a" "b" <>` -> `0 1`

Future Python/Rust/WASM hosts no longer have to infer Micromax `<>` behavior from
`core.mx` or ad hoc pytest assertions; they can replay the tiny contract directly
from JSON during bring-up.
