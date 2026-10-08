---
status: validation_report
claim_kind: release_validation
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

Validation command:

```bash
python tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Checks covered:

- JSON parsing for all JSON files;
- scoreboard validation against `docs/20-program/scoreboard-schema.json`;
- Markdown source-reference resolution against `SOURCES.json`;
- recursive JSON `source_ids` validation;
- local Markdown link resolution;
- frontmatter closure checks;
- contiguous source ID sequence;
- rev0308 measurement-scoreboard presence check;
- rev0309 enforcement-scoreboard presence check;
- rev0310 democratic-power-scoreboard presence check;
- manifest hash validation.

ZIP integrity was checked after packaging.
