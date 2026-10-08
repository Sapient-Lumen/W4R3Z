# rev0075 focused validation

- `PYTHONPATH=daemon/src python -m pytest -q tests/test_e2e_fixturelab.py` ✅
- `cd extension && npm run typecheck` ✅
- `cd extension && npm run build` ✅
- `PYTHONPATH=daemon/src python scripts/e2e-fixturelab.py --output validation/rev0075-focused/e2e-fixturelab.json --timeout 25` ⚠️ left a usable JSON report even though the run ended at phase `finished` and recorded signal `15`

The revision is packaged on the strength of the focused test/build evidence plus the new durable-report behavior, not on a successful live browser/native-host smoke.
