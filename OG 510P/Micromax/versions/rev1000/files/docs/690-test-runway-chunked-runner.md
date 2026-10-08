# Chunked test runway (rev748)

The full pytest suite has grown large enough that a single monolithic `make test` can be awkward in constrained handoff sessions.  Rev748 adds `tools/mxtest.py`, a deterministic collection/chunking wrapper that records what was collected, what was selected, and which slice ran.

The ordinary path remains available:

```bash
make test
```

The new runway adds planning and balanced chunk execution:

```bash
make test-plan
make test-chunk CHUNK=1/8
python tools/mxtest.py --chunk 3/8 --isolate-files --json .artifacts/mxtest-3-of-8.json
```

## Why this belongs in the trust lane

A large archive should not collapse test confidence into a vague "ran some tests" claim.  The runner surfaces three states separately:

- collected test count
- selected slice count
- run return code and duration, when JSON output is requested

It also keeps pytest plugin autoloading disabled by default, matching `scripts/test.sh` and `tools/mxdoctor.py`, so host-level pytest plugins do not change archive behavior accidentally.  `make test-chunk` uses `--isolate-files`, which runs each selected test file in a fresh pytest process; that costs some startup time but makes handoff slices less vulnerable to cross-file global state leaks in large editor/doc suites.  Isolated files also have a default per-file timeout (`--file-timeout 120`) so one stuck file is recorded as return code 124 instead of consuming the whole handoff run.

## Chunk policy

Chunks are one-based (`INDEX/TOTAL`) and balanced contiguously over pytest node ids after collection.  For example, if 10 tests are split into 3 chunks, counts are `[4, 3, 3]`.

The runner is intentionally small.  It is not a CI orchestrator; it is a handoff-friendly way to prove and resume validation in slices.  JSON summaries include per-file records, durations, return codes, and timeout flags when file isolation is enabled.
