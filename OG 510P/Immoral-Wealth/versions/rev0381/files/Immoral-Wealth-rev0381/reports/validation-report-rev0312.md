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

Validation command:

```bash
python tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Checks covered by the validator:

- JSON parsing across the archive.
- Recursive JSON `source_ids` references.
- Scoreboard validation against `docs/20-program/scoreboard-schema.json`.
- Markdown source references.
- Local Markdown links.
- Markdown frontmatter presence/closure.
- Contiguous source id sequence.
- Rev0308 measurement scoreboards.
- Rev0309 enforcement scoreboards.
- Rev0310 democratic-power scoreboards.
- Rev0311 jurisdictional-mobility scoreboards.
- Rev0312 workplace-power scoreboards.
- Manifest file presence and SHA-256 hash verification.
