Rev252 note: the JSON portability corpus now also covers tiny boot-stdlib `2nip` / `2tuck` behavior, so future Python/Rust/WASM hosts can replay one more small pair-stack convenience slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

# Portability follow-up: `2nip` / `2tuck`

This pass adds two tiny source-visible pair-stack helpers to `src/micromax/stdlib/core.mx`:

- `: 2nip  ( a b c d -- c d )  2swap 2drop ;`
- `: 2tuck ( a b c d -- c d a b c d )  2swap 2over ;`

Why these two:
- they are small, readable, and built entirely from already-portable stack words
- they are useful in hand-written concatenative code that manipulates cell pairs
- they keep the VM primitive surface flat while still making a common pair-stack vocabulary available

Replayable corpus cases:
- `stdlib-2nip-drops-underlying-pair`
- `stdlib-2tuck-tucks-top-pair-under-copy`

Focused verification lives in:
- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`

For future ports, this is the important part: pair-stack convenience behavior is now explicit in both source and JSON. A Rust/WASM host can validate these helpers without reverse-engineering them from boot stdlib source or from a larger Python-shaped test harness.
