# Rev251: portability follow-up for `2>r` / `2r>` / `2r@`

This revision adds tiny boot-stdlib `2>r`, `2r>`, and `2r@` helpers to
`src/micromax/stdlib/core.mx` and mirrors them in the JSON portability corpus.

Definitions:

```forth
: 2>r ( x1 x2 -- )  swap >r >r ;
: 2r> ( -- x1 x2 )  r> r> swap ;
: 2r@ ( -- x1 x2 )  r> r> 2dup >r >r swap ;
```

Why this is a good Micromax-sized move:

- the current Forth standard still specifies `2>R`, `2R>`, and `2R@` as
  standard return-stack pair helpers
- those words are useful bring-up checkpoints for future Rust/WASM hosts because
  they exercise value order, peeking, and preserved return-stack depth
- the standard's current `2>R` page also explicitly warns that a naive pure-
  Forth source definition can be tricky on systems where return-stack words have
  compile-time / nest-sys caveats; Micromax's simpler execution model does not
  have that exact portability trap, so a tiny source-visible stdlib definition is
  still the honest move here

Replayable corpus cases added:

- `stdlib-2to-r-2r-from-roundtrip`
- `stdlib-2r-fetch-preserves-pair-on-return-stack`
- `stdlib-2r-fetch-keeps-return-stack-depth`

Examples:

- `1 2 2>r 2r>` -> `1 2`
- `10 20 2>r 2r@ 2r>` -> `10 20 10 20`
- `7 8 2>r 2r@ rdepth 2r> rdepth` -> `7 8 2 7 8 0`

Consequence:

Future Python/Rust/WASM hosts no longer have to infer Micromax pair-return-stack
behavior from `core.mx` alone. One more tiny standard-shaped return-stack slice
is now explicit, replayable, and archive-visible.
