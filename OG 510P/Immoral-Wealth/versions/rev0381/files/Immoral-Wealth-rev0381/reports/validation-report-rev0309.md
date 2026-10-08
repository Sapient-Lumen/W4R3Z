---
status: validation_report
claim_kind: archive_integrity
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- enforcement_remedy_core
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

- JSON parsing across the archive;
- recursive JSON `source_ids` references;
- scoreboard validation against `docs/20-program/scoreboard-schema.json`;
- Markdown source references;
- local Markdown links;
- frontmatter presence/closure;
- contiguous source IDs;
- rev0308 measurement scoreboard requirements;
- rev0309 enforcement/remedy scoreboard requirements;
- manifest file hashes.
