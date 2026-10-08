---
status: validation_report
claim_kind: bundle_integrity
route_role: source_governance
canonical_anchor: false
route_refs:
- source_governance_core
supersedes: null
depends_on:
- ../tools/validate_archive.py
source_refresh_due: 2026-12-31
---

# Validation report — rev0355

Command:

```bash
python tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Checks covered JSON parsing, recursive JSON source references, scoreboard schema validation, Markdown source references, local Markdown links, frontmatter presence, contiguous source IDs, rev0308 measurement scoreboards, rev0309 enforcement scoreboards, rev0310 democratic-power scoreboards, rev0311 jurisdictional-mobility scoreboards, and manifest hashes.
