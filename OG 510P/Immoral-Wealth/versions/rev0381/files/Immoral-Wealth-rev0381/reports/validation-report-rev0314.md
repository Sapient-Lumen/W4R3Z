---
status: validation_report
claim_kind: release_integrity
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
supersedes: null
depends_on:
- ../tools/validate_archive.py
source_refresh_due: 2026-12-31
case_pressure: rev0314_household_market_extraction
---

# Validation report — rev0355

Validation was run after adding Gate 16, five rev0314 cases, companion scoreboards, schema fields, source-ledger entries through `S280`, validation-tool requirements, regenerated archive index, and regenerated manifest.

```text
PASSED: 0 errors, 0 warnings
```

Validated surfaces:

- JSON parsing
- scoreboard schema validation
- Markdown source references
- Markdown local links
- Markdown frontmatter presence/closure
- contiguous source IDs
- rev0308 measurement scoreboards
- rev0309 enforcement scoreboards
- rev0310 democratic-power scoreboards
- rev0311 jurisdictional-mobility scoreboards
- rev0312 workplace-power scoreboards
- rev0313 place-public-finance scoreboards
- rev0314 household-market-extraction scoreboards
- manifest hashes
