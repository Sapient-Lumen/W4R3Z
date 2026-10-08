---
revision_current: rev0374
generated_at: 2026-06-18T18:42:00Z
status: validation_report
---

# Validation report — rev0374

Validation was run after extraction-ready manifest regeneration.

## Commands and expected results

```text
$ python3 tools/audit_ma_appeal_burden_pilot.py
PASSED: MA appeal-burden public pilot audit

$ python3 tools/audit_ma_row_contract_workbench.py
PASSED: MA row-contract workbench audit

$ python3 tools/validate_live_surfaces.py
PASSED: 0 live-surface issues

$ python3 tools/validate_archive.py
PASSED: 0 errors, 0 warnings
```

The archive remains **not certified current** for all cases; this validation only confirms structural/operator-surface consistency for rev0374.
