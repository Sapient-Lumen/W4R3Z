# TRANSFER-CONTROL-PATH-BUDGET-01 maintainer witness

Current-behavior witness for U-271 + U-274 + U-256.

Run against a source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_transfer_control_path_budget_reproducer.py
```

Expected current behavior in rev0024 source lanes: 6 tests pass. A future fix should make the relevant "currently accepted/echoed" assertions fail or be rewritten as regression expectations for bounded rejection.

The test deliberately uses a 256 KiB component path rather than a multi-megabyte path to keep CI/runtime cost low while still proving absence of a small semantic component/path budget.
