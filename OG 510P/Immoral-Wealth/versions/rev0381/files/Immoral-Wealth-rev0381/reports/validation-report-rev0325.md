---
status: validation_report
claim_kind: validation
route_role: certification_core
canonical_anchor: false
route_refs:
- certification_core
- archive_governance_core
supersedes: rev0324
depends_on:
- tools/validate_archive.py
- MANIFEST.json
source_refresh_due: 2026-12-31
---

# Validation report — rev0355

Command: `python3 tools/validate_archive.py`

Result:

```text
PASSED: 0 errors, 0 warnings
```

Validator changes in this revision include current `SOURCES.md` visibility, strict source publication-date format checks, and memo/scoreboard `source_refresh_due` synchronization.
