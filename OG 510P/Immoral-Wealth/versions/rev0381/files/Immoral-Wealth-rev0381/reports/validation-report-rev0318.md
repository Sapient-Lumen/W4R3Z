---
status: validation_report
claim_kind: validation_report
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- public_balance_sheet_core
supersedes: null
depends_on: []
source_refresh_due: 2027-03-31
case_pressure: rev0318_public_balance_sheet
---

# Validation report — rev0355

Generated: 2026-05-25T04:45:00Z

Command:

```bash
python3 tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Coverage added in this release:

- Gate 20 public balance-sheet scoreboards exist for all seven rev0318 cases.
- Gate 20 source references resolve through `S372`.
- Markdown links, JSON parsing, scoreboard schema validation, frontmatter, source-sequence checks, route files, and manifest hashes validate cleanly.
