# Portability follow-up: `pick` / `roll` failure edges (rev243)

Rev243 extends the tiny JSON portability corpus with four explicit `pick` / `roll`
error contracts:

- `pick-negative-index-errors`
- `roll-negative-index-errors`
- `pick-underflow-errors-on-too-shallow-stack`
- `roll-underflow-errors-on-too-shallow-stack`

## Why this belongs in the corpus

The recent rev239–rev242 thread already pinned down the success-path indexing story:

- `0 pick` = `dup`
- `1 pick` = `over`
- `1 roll` = `swap`
- `2 roll` = `rot`
- `0 roll` = null op
- `2 pick` = copy the third item
- `3 pick` / `3 roll` = four-item general cases
- `4 pick` / `4 roll` = five-item general cases

That is useful, but a future host still had to guess what Micromax does for the
failure edges.

The Forth standard documents normal `PICK` / `ROLL` behavior, but out-of-range
inputs are still described as ambiguous conditions rather than portable
exceptions. Micromax already chooses concrete behavior here:

- negative indices are rejected explicitly
- too-shallow stacks raise `Stack underflow`

Making those choices part of the JSON corpus gives future Python/Rust/WASM hosts
one more small replayable truth during bring-up.

## Added corpus rows

```json
{
  "name": "pick-negative-index-errors",
  "category": "kernel",
  "tags": ["stack", "stack-shuffle", "errors", "core-ext"],
  "source": "10 -1 pick",
  "expect_error_contains": "pick: u must be >= 0"
}
```

```json
{
  "name": "roll-underflow-errors-on-too-shallow-stack",
  "category": "kernel",
  "tags": ["stack", "stack-shuffle", "errors", "core-ext"],
  "source": "10 20 2 roll",
  "expect_error_contains": "Stack underflow"
}
```

## Why this is a good Micromax-sized step

It stays tiny and data-only, but it removes one more implementation-shaped guess
from future hand ports.
