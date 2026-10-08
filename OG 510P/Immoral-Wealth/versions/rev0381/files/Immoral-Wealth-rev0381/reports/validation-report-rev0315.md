---
status: validation_report
claim_kind: archive_integrity
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

Generated: 2026-05-23T18:32:00Z

Scope: JSON parsing, scoreboard schema validation, Markdown source references, local Markdown links, YAML frontmatter presence, source-id sequence, rev0308–rev0315 surface-specific scoreboard checks, and manifest hashes.

Result after final manifest regeneration:

```text
PASSED: 0 errors, 0 warnings
```

Notes:

- rev0315 added Gate 17 score-mediated-exclusion scoreboards and required validation coverage.
- rev0315 also restored explicit validation calls for rev0313 and rev0314 surface-specific scoreboard checks.
- ZIP integrity was checked after packaging.
