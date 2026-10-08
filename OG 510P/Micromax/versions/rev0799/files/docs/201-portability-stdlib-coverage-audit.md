# Rev259: explicit portability coverage audit for boot stdlib

This revision does two small but leverage-heavy things:

1. it adds missing JSON portability cases for `rdrop` and the success path of
   `recover`
2. it adds a tiny manifest test that checks every `: word` defined in
   `src/micromax/stdlib/core.mx` against explicit portability case names

That matters because the recent Micromax portability work has been steadily
turning the boot stdlib into a cross-host handoff contract, but until this rev
future humans and future LLMs still had to answer the boring question
“did we forget to pin down any stdlib words?” by manually diffing `core.mx`
against `portability/kernel_cases.json`.

The newly added replayable cases are:

- `stdlib-rdrop-removes-top-return-stack-item`
- `stdlib-rdrop-preserves-older-return-stack-items`
- `stdlib-recover-success-ignores-handler`

Focused examples:

- `1 >r rdrop rdepth` -> `0`
- `77 >r 99 >r rdrop r> rdepth` -> `77 0`
- `1 [ 2 + ] [ drop drop 0 ] recover` -> `3`

The audit itself lives in `tests/test_portability_suite.py` as a small explicit
manifest mapping boot-stdlib words to portability case names. That keeps the
check intentionally hand-readable instead of inventing another metadata file or
parser layer.

The practical result is simple: after rev259, every boot-stdlib definition in
`core.mx` now has an explicit portability breadcrumb future Python/Rust/WASM
hosts can replay, and future archive readers can verify that claim with one
small focused test instead of trust.
