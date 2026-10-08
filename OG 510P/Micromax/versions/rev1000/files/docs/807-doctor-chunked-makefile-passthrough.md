# Rev0849 — doctor chunked Makefile passthrough

Rev0849 fixes a narrow workflow drift in the aggregate evidence lane. `make test-all-chunks` already honored the archive-carried `TEST_MANIFEST` and cloudtainer-safe `MAX_RUNTIME_SECONDS` knobs, but `make doctor-chunked` invoked `mxdoctor --chunked` without passing either knob.

That meant a user could run a custom manifest lane with `TEST_MANIFEST=...` or disable the short cloudtainer budget with `MAX_RUNTIME_SECONDS=0`, then accidentally route the doctor chunked lane back through the default manifest or default doctor budget.

The Makefile target now forwards both values explicitly:

```bash
make doctor-chunked TEST_MANIFEST=.artifacts/custom.json MAX_RUNTIME_SECONDS=0
```

which expands to the matching `mxdoctor --chunked --manifest ... --max-runtime-seconds ...` command.

## Why this matters

This is a handoff-risk fix rather than a new test registry. The project has spent several revisions eliminating side evidence lanes. Leaving the doctor target with hidden defaults would recreate that class of waste: a chunked doctor run could appear to advance the requested lane while actually touching a different manifest or runtime budget.

## Evidence

Focused Makefile coverage now asserts that `doctor-chunked` uses the same manifest and runtime-budget variables as the aggregate target. The current-source aggregate manifest must be reverified after this workflow/test/docs edit before claiming full evidence.
