---
status: active
claim_kind: validation_report
route_role: archive_governance_core
route_refs:
- archive_governance_core
revision_current: rev0355
source_refresh_due: 2026-09-30
---

# Validation report — rev0355

Expected command:

```text
python3 tools/validate_archive.py
```

Expected result:

```text
PASSED: 0 errors, 0 warnings
```

rev0332 adds a validator invariant that no seed scoreboard remains and that the six promoted target cases keep active status, required source anchors, and sourced watch/blocked gate-inventory rows.

<!-- current_revision: rev0332; codename: seed-backlog-closure-and-gate-inventory-source-refactor -->
