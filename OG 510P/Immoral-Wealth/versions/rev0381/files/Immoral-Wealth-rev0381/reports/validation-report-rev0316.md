---
status: validation_report
claim_kind: integrity_check
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

```text
python3 tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Checks covered JSON parsing, scoreboard schema validation, recursive JSON `source_ids`, Markdown source references, local Markdown links, frontmatter presence, source sequence, release-specific scoreboard checks through rev0316, and manifest hashes.
