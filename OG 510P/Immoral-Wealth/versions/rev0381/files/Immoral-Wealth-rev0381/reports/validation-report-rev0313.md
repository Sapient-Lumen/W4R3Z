---
status: validation_report
claim_kind: bundle_integrity
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
supersedes: null
depends_on:
- ../tools/validate_archive.py
source_refresh_due: 2026-12-31
---

# Validation report — rev0355

Validation command:

```bash
python tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Checks covered:

- JSON parsing across archive.
- Scoreboard schema validation.
- Markdown source references.
- Markdown local links.
- Frontmatter presence and closure.
- Source ID contiguity.
- Recursive JSON `source_ids` references.
- Required rev0308 measurement scoreboards.
- Required rev0309 enforcement scoreboards.
- Required rev0310 democratic-power scoreboards.
- Required rev0311 jurisdictional-mobility scoreboards.
- Required rev0312 workplace-power scoreboards.
- Required rev0313 place-public-finance scoreboards.
- Manifest file hashes.
