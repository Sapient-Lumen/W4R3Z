Rev247 note: the JSON portability corpus now also covers tiny boot-stdlib `1+`, `1-`, `0>`, and `0<>` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic/predicate slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

# Portable `1+` / `1-` / `0>` / `0<>` boot-stdlib slice

Micromax now ships one more tiny replayable arithmetic slice in `portability/kernel_cases.json`:

- `stdlib-one-plus-increments`
- `stdlib-one-minus-decrements`
- `stdlib-zero-greater-predicate`
- `stdlib-zero-not-equals-predicate`

## Why these words

These are good bring-up checkpoints because they stay tiny while still exercising the same arithmetic and flag paths future hosts will need early.

Micromax implements them in boot stdlib (`src/micromax/stdlib/core.mx`), which keeps the VM primitive surface small and the intended behavior visible in source form.

```forth
: 1+  ( n|u -- n|u )  1 + ;
: 1-  ( n|u -- n|u )  1 - ;
: 0>  ( n -- flag )  0 > ;
: 0<> ( x -- flag )  0= 0= ;
```

That shape matches the current Forth standard well: `1+` adds one, `1-` subtracts one, `0>` is true only for values greater than zero, and `0<>` is true only for values not equal to zero. The standard also still allows a system to provide standard words in source form only, which fits Micromax's tiny boot-stdlib style.

## Replay examples

```bash
PYTHONPATH=src python tools/mxportable.py \
  --name stdlib-one-plus-increments \
  --name stdlib-one-minus-decrements \
  --name stdlib-zero-greater-predicate \
  --name stdlib-zero-not-equals-predicate
```

Or replay the broader arithmetic slice:

```bash
PYTHONPATH=src python tools/mxportable.py --tag arithmetic --json
```

## Focused verification

- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`

## Why this is a good Micromax-sized step

Future Python/Rust/WASM hosts no longer have to infer Micromax `1+`, `1-`, `0>`, or `0<>` behavior from boot-stdlib source alone. One more tiny arithmetic/predicate slice is now explicit, replayable, and archive-visible.
