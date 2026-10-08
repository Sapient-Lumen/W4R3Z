# Research: small combinators (Factor / Joy / micro-adjacent)

Micromax is deliberately tiny, but *a few* higher-order words go a long way toward
making a concatenative language ergonomic.

This note is a quick capture of ideas we can "steal" without turning micromax into a
full Factor clone.

## Why combinators matter

Concatenative languages stay pleasant when you can avoid "stack gymnastics".
Factor and Joy both lean heavily on quotation-passing combinators (words that *execute*
quotations in useful patterns).

We do **not** (yet) have Factor's stack checker or inference, so we favor combinators
that are:

- mechanically simple
- easy to reason about dynamically
- easy to test

## Low-hanging, high-leverage

### `dip`

Pattern: temporarily hide a value while running a quotation.

```
( x [P] -- ... x )
```

Example:

```
4 [ 1 2 + ] dip   \ => 3 4
```

Use cases:

- keep a "context" object (editor, buffer, options) around while doing work on the
  rest of the stack
- reduce explicit locals/variables in small scripts

### `keep`

Pattern: run a quotation *with* a value available, but also keep the value afterward.

```
( x [P] -- ... x )
```

Example (Factor-style):

```
3 4 [ + ] keep    \ => 7 4
```

Use cases:

- compute a derived value but keep the original around for the next step
- build small pipelines that don't constantly `dup`/`swap`/`over`

## Now implemented in stdlib (rev45)

The following words are now defined in `src/micromax/stdlib/core.mx` rather than as
VM primitives:

- `2dip` — hide two values while running a quotation
- `2keep` — run a quotation with two values available, then restore them
- `bi` — apply two quotations to the same input
- `tri` — apply three quotations to the same input

That is a good fit for Micromax’s current phase:

- the semantics stay readable in ordinary Micromax code
- the surface remains portable to future Rust/WASM ports
- we get real ergonomic leverage for editor/config/plugin scripts without committing
  to a large combinator zoo yet

## Still future candidates

These remain tempting, but we should add them only after we have good tests and some
real editor scripts that *need* them:

- `2bi` / `2tri` / spread variants
- list/sequence combinators such as `each` / `map` (but mind safety budgets!)
- any stack-effect-aware checker/inference beyond docstrings and tooling
