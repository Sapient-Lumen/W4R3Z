Rev248 note: the JSON portability corpus now also covers tiny boot-stdlib `2*` / `2/` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped shift/arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Why keep these in `core.mx` instead of the VM primitive set?

- They are tiny convenience words that stay readable in source form.
- The current Forth standard still defines `2*` and `2/` as one-bit shifts, and its usage requirements still allow standard words to be provided in source form only.
- Micromax already has integer `*` / `/`, so the current source definitions keep the implementation tiny while still making the behavior replayable from JSON.

Words added

```forth
: 2* ( x1 -- x2 ) 2 * ;
: 2/ ( x1 -- x2 ) 2 / ;
```

Replayable portability cases

- `stdlib-two-times-doubles`
- `stdlib-two-slash-halves-with-sign-propagation`

Focused verification

- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`
- `python tools/mxcontext.py --json --check`
