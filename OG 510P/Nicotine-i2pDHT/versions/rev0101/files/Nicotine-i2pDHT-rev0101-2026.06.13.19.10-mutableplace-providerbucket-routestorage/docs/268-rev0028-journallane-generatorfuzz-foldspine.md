# rev0028 — journallane / generatorfuzz / foldspine

This revision pushes on restart, parser, refusal, and transport-shadow boundaries before any live I2P/SAM work.

Strong sentence:

```text
A restart, an empty tail, a useful refusal, and a transport send are all protocol boundaries.
```

New implementation surfaces:

- `journallane.py` — signed append-only toy journal entries with crash-cut replay and hard-negative compaction.
- `generatorfuzz.py` — generated deterministic rejection corpus grown from accepted fuzzwire seed cases.
- `refusaljoin.py` — joins refusalloop reports back into garden scheduling decisions.
- `samwire.py` — no-network SAM-shadow scripts that carry canonical `WireFrame` payloads.
- `foldspine.py` — declarative current-revision audit/refactor spine.

This remains local pressure testing only. No live I2P/SAM transport or production DHT is claimed.

## Compile-check refactor

The rev0028 audit lane also fixes the compile hygiene check for Python 3.13-era behavior: active Python surfaces are now compiled into temporary `.pyc` targets instead of trying to use `/dev/null` as a bytecode sink. This keeps the no-persistent-bytecode property while avoiding a non-regular-file trap in `py_compile`.
## Duplicate active-test fold

A duplicate active rev0028 test file was moved to `artifacts/branchlets/rev0028_duplicate_active_tests/` after the canonical active test was pinned as `tests/test_rev0028_journal_generator_refusal_sam_fold.py`. This keeps the behavioral evidence while reducing current-test surface ambiguity.
