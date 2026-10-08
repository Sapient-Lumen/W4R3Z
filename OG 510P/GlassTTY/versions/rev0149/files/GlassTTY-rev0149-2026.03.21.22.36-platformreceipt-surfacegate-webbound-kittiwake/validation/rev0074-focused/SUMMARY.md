# rev0074 focused validation

- `PYTHONPATH=daemon/src python -m pytest -q tests/test_e2e_fixturelab.py` ✅
- `cd extension && npm run typecheck` ✅
- `cd extension && npm run build` ✅
- `PYTHONPATH=daemon/src python scripts/e2e-fixturelab.py --output validation/rev0074-focused/e2e-fixturelab.json --timeout 25` ⚠️ attempted, but no usable JSON report artifact was left behind in this container

The revision is packaged on the strength of the focused test/build evidence and the new trace-artifact code path, not on a successful live browser/native-host smoke.
