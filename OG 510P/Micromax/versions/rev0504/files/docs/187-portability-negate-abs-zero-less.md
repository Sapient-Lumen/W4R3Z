Rev245 note: the JSON portability corpus now also covers tiny boot-stdlib `negate`, `0<`, and `abs` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

# Portable `negate` / `0<` / `abs` boot-stdlib slice

Micromax now ships one tiny replayable arithmetic slice in `portability/kernel_cases.json`:

- `stdlib-negate-zero-is-zero`
- `stdlib-negate-inverts-sign`
- `stdlib-zero-less-predicate`
- `stdlib-abs-normalizes-sign`

Why this is useful:

- these are small, standard-shaped arithmetic helpers future hosts are likely to want early
- Micromax implements them in boot stdlib (`src/micromax/stdlib/core.mx`), so replayable JSON cases are the easiest way to keep Python/Rust/WASM hosts aligned without reading Python internals
- `abs` is deliberately defined in terms of `0<` + `negate`, which keeps the implementation tiny and easy to port by hand

Current boot-stdlib definitions:

```forth
: negate ( n -- -n )  0 swap - ;
: 0<     ( n -- flag )  0 < ;
: abs    ( n -- u )  dup 0< [ negate ] [ ] if ;
```

Focused replay:

```sh
PYTHONPATH=src python tools/mxportable.py \
  --name stdlib-negate-zero-is-zero \
  --name stdlib-negate-inverts-sign \
  --name stdlib-zero-less-predicate \
  --name stdlib-abs-normalizes-sign \
  --json
```
