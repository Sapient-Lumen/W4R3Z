---
revision_current: rev0355
status: validation_report
claim_kind: validation_surface
route_role: archive_governance_core
route_refs:
- archive_governance_core
---

# Validation report — rev0355

Command: `python3 tools/validate_archive.py`

Expected result after manifest regeneration: `PASSED: 0 errors, 0 warnings`.

This report is intentionally lightweight; the validator owns the executable checks for source sequence, source-use synchronization, evidence-ledger synchronization, currentness-ledger synchronization, current front-door counts, rev0354 River Bend source binding, and manifest hashes.
