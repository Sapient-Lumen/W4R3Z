# Rev256: portability follow-up for `keep`

This revision does **not** add a new VM primitive. Instead, it makes one already-
source-visible boot-stdlib preserving combinator explicitly replayable from the
JSON portability corpus:

```forth
: keep ( x q -- ... x )  over >r call r> ;
```

Why this is worth pinning down:

- current Factor docs still present `keep` alongside `dip` / `2dip` / `2keep` as
  a preserving combinator, which is useful prior art for Micromax's tiny quote-
  heavy scripting style
- Micromax already has the needed kernel pieces (`over`, `>r`, `call`, `r>`), so
  keeping `keep` source-visible matches the repo's current preference for a tiny
  inspectable VM plus replayable stdlib contracts
- future Python/Rust/WASM hosts should not have to infer the ordering contract
  for preserved values from `core.mx`, broader combinator words like `bi`/`tri`,
  or ad hoc pytest coverage during bring-up

The JSON portability corpus now includes:

- `stdlib-keep`

Focused example:

- `3 4 [ + ] keep` -> `7 4`

That gives future hosts one more tiny preserving-combinator contract they can
replay directly from JSON during bring-up instead of re-deriving it from
stdlib source or from larger composed words.
