Rev249 note: the JSON portability corpus now also covers tiny boot-stdlib `2over` / `2swap` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

# Portability follow-up: boot-stdlib `2over` / `2swap`

Rev249 adds tiny source-defined `2over` and `2swap` helpers to `src/micromax/stdlib/core.mx`:

```forth
: 2over ( a b c d -- a b c d a b )  3 pick 3 pick ;
: 2swap ( a b c d -- c d a b )      rot >r rot r> ;
```

Micromax already had the needed pieces (`pick`, `rot`, `>r`, `r>`) so this stays a stdlib move rather than a VM-primitive change.

These words are small but genuinely useful bring-up checkpoints:
- `2over` exercises deeper stack indexing without inventing new VM semantics
- `2swap` exercises pair shuffling plus return-stack round-tripping in source form
- both help future ports avoid subtle off-by-one or wrong-end stack bugs

The current Forth standard still defines `2OVER` as copying the leading pair to the top of the stack and `2SWAP` as exchanging the top two cell pairs. That makes them a good fit for Micromax's tiny boot-stdlib + JSON portability style.

The portability corpus now includes:
- `stdlib-2over-copies-leading-pair`
- `stdlib-2swap-exchanges-top-pairs`

Focused coverage lives in:
- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`

Future Python/Rust/WASM hosts no longer have to infer Micromax `2over` / `2swap` behavior from source alone. One more tiny stack-shuffle slice is now explicit, replayable, and archive-visible.
