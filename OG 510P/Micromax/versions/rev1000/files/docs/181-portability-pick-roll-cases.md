# Rev239 — portability corpus for PICK / ROLL stack shuffles

Rev239 keeps working the current portability-discipline priority instead of pretending the long-range Rust spike is testable in this archive.

The tiny JSON portability corpus now also covers four small stack-shuffle contracts the Python VM already supports and future Rust/WASM hosts should replay exactly:

- `pick-zero-equivalent-to-dup`
- `pick-one-equivalent-to-over`
- `roll-one-equivalent-to-swap`
- `roll-two-equivalent-to-rot`

## Why these cases

These are tiny, high-signal contracts:

- they are already implemented and unit-tested in the Python VM
- they are cheap for future hosts to replay from JSON alone
- they pin down stack-indexing behavior that is easy to get subtly wrong during a hand port

The goal is still the same portability-suite philosophy: small data-only replayable truth, not a bigger compliance harness.

## What changed

The corpus additions live in `portability/kernel_cases.json` and intentionally stay simple:

- plain kernel snippets
- plain final stack expectations
- a small shared `stack-shuffle` tag so future humans/LLMs can slice them quickly with `mxportable`

You can inspect or replay just these cases with:

```bash
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle --list
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle
PYTHONPATH=src python tools/mxportable.py --tag stack-shuffle --json
```

## Why this helps future hosts

`pick`/`roll` bugs are the sort of low-level mistakes that can survive a lot of ordinary smoke tests because they only show up once stack depth and indexing interact. These four tiny cases make the intended indexing story explicit without needing the whole pytest suite or a richer compliance framework.
