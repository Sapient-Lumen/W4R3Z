# Rev253: portability follow-up for `2rdrop`

This revision adds a tiny boot-stdlib `2rdrop` helper to
`src/micromax/stdlib/core.mx` and mirrors it in the JSON portability corpus so
future Python/Rust/WASM hosts can replay the return-stack-pair drop contract
without inferring it from source alone.

```
: 2rdrop ( -- )  rdrop rdrop ;
```

Why this shape is worth keeping:

- the current Gforth manual still lists `2rdrop` alongside `rdrop`, `2>r`,
  `2r>`, and `2r@` in its return-stack vocabulary, so it is a good tiny
  extension to learn from even though it is not a core standard word
- Micromax already has the needed kernel pieces (`rdrop`), so keeping
  `2rdrop` source-visible matches the repo's preference for a tiny inspectable
  VM plus replayable stdlib contracts
- replayable JSON cases make future hand ports catch pair-return-stack cleanup
  mistakes early instead of discovering them only through larger composed words

The portability cases added in this revision cover:

- `1 2 2>r 2rdrop rdepth` -> `0`
- `77 >r 1 2 2>r 2rdrop r> rdepth` -> `77 0`

Focused validation lives in:

- `tests/test_vm_rev11.py`
- `tests/test_portability_suite.py`
- `tests/test_mxcontext.py`
