# Rev0850 — doctor chunked budget knob parity

Rev0850 closes the next workflow drift in the aggregate evidence lane. Rev0849 made `make doctor-chunked` forward the manifest and runtime budget, but the doctor chunked lane still did not share the rest of the aggregate budget shape used by `make test-all-chunks`.

The Makefile aggregate lane was bounded by:

```text
MAX_NEW_TESTS
MAX_NEW_FILES
TEST_BATCH_SIZE
FILE_TIMEOUT
MAX_RUNTIME_SECONDS
TEST_MANIFEST
```

while the doctor chunked path only had the chunk count, manifest, and runtime budget. That meant a doctor run could advance the same manifest but with different per-invocation work limits and a different per-file timeout.

Rev0850 makes `make doctor-chunked` pass the full budget set through to `mxdoctor --chunked`, and gives `mxdoctor` matching direct CLI defaults:

```bash
make doctor-chunked \
  TEST_MANIFEST=.artifacts/mxtest-all-64.json \
  MAX_RUNTIME_SECONDS=25 \
  MAX_NEW_TESTS=120 \
  MAX_NEW_FILES=8 \
  TEST_BATCH_SIZE=0 \
  FILE_TIMEOUT=180
```

## Why this matters

The issue was not only speed. Resume-safe evidence depends on predictable work slicing. If one command uses a different file/test budget than the other, a future handoff can spend time debugging apparent progress differences that are only command-shape drift.

The fix keeps the lane boring: `test-all-chunks` and `doctor-chunked` now agree on manifest, runtime budget, new-test budget, new-file budget, test-batch size, and file timeout unless the caller explicitly overrides them.

## Evidence

Focused tests now cover both surfaces:

- `tools/mxdoctor.py` builds a chunked command with the matching budget defaults and accepts explicit overrides.
- `Makefile` forwards the same budget variables into `mxdoctor --chunked`.

After this workflow/tooling/test/docs change, refresh `.artifacts/mxtest-all-64.json` before claiming current-source aggregate evidence.
