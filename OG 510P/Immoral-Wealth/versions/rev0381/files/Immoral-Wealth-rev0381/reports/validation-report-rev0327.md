---
status: active
claim_kind: audit_report
route_role: archive_governance_core
route_refs: [archive_governance_core, public_balance_sheet_core]
revision_current: rev0355
source_refresh_due: 2026-09-30
---

# Validation report — rev0355

Generated: `2026-06-12T23:50:55Z`

Command:

```bash
python3 tools/validate_archive.py
```

Expected result after rev0327 repair:

```text
PASSED: 0 errors, 0 warnings
```

The validator includes release-surface checks, source metadata checks, source/case refresh synchronization, Gate 20 burndown locks from rev0326, and the rev0327 status-parity burndown lock for the four promoted public-backstop cases.

<!-- current_revision: rev0327; codename: compute-climate-health-minerals-backstop-burndown -->
