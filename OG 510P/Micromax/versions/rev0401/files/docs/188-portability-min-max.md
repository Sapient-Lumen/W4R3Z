Rev246 note: the JSON portability corpus now also covers tiny boot-stdlib `max` / `min` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

# Portability follow-up: boot-stdlib `max` / `min`

## What landed

Rev246 adds tiny source-defined `max` and `min` helpers to `src/micromax/stdlib/core.mx`:

```forth
: max ( n1 n2 -- n3 ) 2dup > [ drop ] [ nip ] if ;
: min ( n1 n2 -- n3 ) 2dup < [ drop ] [ nip ] if ;
```

Micromax already had the needed pieces (`2dup`, `>`, `<`, quotation-based `if`, `drop`, `nip`), so this stays a stdlib move rather than a VM-primitive change.

## Why this was worth doing

`max` / `min` are tiny but useful bring-up checkpoints:

- they exercise ordinary signed comparison
- they exercise quotation-based conditionals in the shape Micromax actually uses
- they are easy to get subtly backwards during a hand port
- they are still small enough to validate from JSON alone

The current Forth standard still defines `MAX` as yielding the greater of `n1` and `n2`, and allows standard words to be provided in source form only. That makes source-defined Micromax `max` / `min` a good fit for the project's tiny boot-stdlib style.

## Portability corpus coverage

Rev246 adds two stdlib cases to `portability/kernel_cases.json`:

- `stdlib-max-picks-greater-value`
- `stdlib-min-picks-smaller-value`

Those cases intentionally cover:

- ascending input order
- descending input order
- negative values
- equal values

## Focused verification

The same contract is mirrored in:

- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`

So future hosts can either:

- replay the JSON cases directly, or
- compare behavior against the Python reference VM's focused test slice

## Consequence

Future Python/Rust/WASM hosts no longer have to infer Micromax `max` / `min` behavior from boot-stdlib source alone. One more tiny arithmetic slice is now explicit, replayable, and archive-visible.
