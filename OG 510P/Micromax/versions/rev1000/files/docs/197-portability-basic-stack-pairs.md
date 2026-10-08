# Rev255: portability follow-up for `nip` / `tuck` / `2dup` / `2drop`

This revision does **not** add new VM primitives. Instead, it makes four already-
source-visible boot-stdlib helpers explicitly replayable from the JSON portability
corpus:

```forth
: nip   ( a b -- b )          swap drop ;
: tuck  ( a b -- b a b )      swap over ;
: 2dup  ( a b -- a b a b )    over over ;
: 2drop ( a b -- )            drop drop ;
```

Why this is worth pinning down:

- the current Forth standard still lists `NIP` and `TUCK` as CORE EXT words, and
  `2DUP` / `2DROP` as CORE words, so these are standard-shaped stack helpers
  rather than Micromax-specific flourish words
- Micromax already has all the needed kernel pieces (`swap`, `drop`, `over`), so
  keeping these helpers source-visible matches the repo's current preference for
  a tiny inspectable VM plus replayable stdlib contracts
- future Python/Rust/WASM hosts should not have to infer these tiny stack
  contracts from `core.mx`, broad pytest coverage, or Gforth muscle memory during
  bring-up

The JSON portability corpus now includes:

- `stdlib-nip-drops-under-top-item`
- `stdlib-tuck-copies-top-under-next`
- `stdlib-2dup-copies-pair`
- `stdlib-2drop-removes-pair`

Focused examples:

- `1 2 nip` -> `2`
- `1 2 tuck` -> `2 1 2`
- `1 2 2dup` -> `1 2 1 2`
- `1 2 2drop` -> *(empty stack)*

That gives future hosts one more tiny standard-shaped stack-shuffle slice they
can replay directly from JSON during bring-up instead of re-deriving it from
stdlib source.
