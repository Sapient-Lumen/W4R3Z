# Rev240 — portability corpus for one more PICK / ROLL indexing edge

Rev240 keeps working the current portability-discipline priority instead of pretending the long-range Rust spike is testable in this archive.

The tiny JSON portability corpus now also covers two adjacent stack-shuffle contracts the Python VM already supports and future Rust/WASM hosts should replay exactly:

- `roll-zero-is-null-op`
- `pick-two-copies-third-item`

## Why these cases

These are tiny, high-signal follow-ups to rev239:

- `0 roll` is the do-nothing edge that can easily get mishandled by recursive or loop-based implementations
- `2 pick` makes the general skip/count indexing rule explicit instead of only documenting the named `dup` / `over` equivalences
- both cases stay cheap for future hosts to replay from JSON alone

The goal is still the same portability-suite philosophy: small data-only replayable truth, not a bigger compliance harness.

## What changed

The corpus additions live in `portability/kernel_cases.json` and intentionally stay simple:

- plain kernel snippets
- plain final stack expectations
- the same shared `stack-shuffle` tag rev239 introduced, so future humans/LLMs can slice the whole family quickly with `mxportable`

You can inspect or replay just these cases with:

```bash
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle --list
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle --json
```

## Why this helps future hosts

`pick`/`roll` bugs are the sort of low-level mistakes that can survive a lot of ordinary smoke tests because they only show up once stack depth and indexing interact. These two follow-up cases make the zero-index rotation edge and one more general indexing point explicit without needing the whole pytest suite or a richer compliance framework.
