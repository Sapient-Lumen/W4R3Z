Rev244 note: the JSON portability corpus now also covers tiny boot-stdlib `?dup` behavior (`0 ?dup -> 0`, `-1 ?dup -> -1 -1`), so future Python/Rust/WASM hosts can replay one more standard-shaped stack helper from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

# Portable `?dup` boot-stdlib slice

Micromax now ships one tiny replayable `?dup` slice in `portability/kernel_cases.json`:

- `stdlib-qdup-zero-leaves-zero`
- `stdlib-qdup-nonzero-duplicates`

Why this belongs in the corpus:
- `?dup` is a small, standard-shaped stack helper that future hosts are likely to want early
- the current Forth standard still specifies `?DUP` as “duplicate x if it is non-zero,” with test examples for both zero and non-zero inputs
- Micromax implements it in boot stdlib (`src/micromax/stdlib/core.mx`), so replayable JSON cases are the easiest way to keep Python/Rust/WASM hosts aligned without reading Python internals

Implementation:

```forth
: ?dup ( x -- 0 | x x )  dup [ dup ] [ ] if ;
```

Focused coverage:
- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`

Useful replay command:

```bash
PYTHONPATH=src python tools/mxportable.py --name stdlib-qdup-zero-leaves-zero --name stdlib-qdup-nonzero-duplicates --json
```
