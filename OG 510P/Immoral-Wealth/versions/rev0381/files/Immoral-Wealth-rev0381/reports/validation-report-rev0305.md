---
status: integrity_artifact
claim_kind: validation_report
route_role: archive_governance
canonical_anchor: false
route_refs:
- archive_governance_core
supersedes: null
depends_on:
- ../tools/validate_archive.py
source_refresh_due: 2026-12-31
---

# Validation report — rev0355

The final pre-ZIP archive validation command was:

```bash
python tools/validate_archive.py
```

Result after regenerating `MANIFEST.json` and `MANIFEST.sha256`:

```text
PASSED: 0 errors, 0 warnings
```

Validated surfaces:

- JSON parsing;
- scoreboard schema validation, including the rev0305 gate/evidence-debt extensions;
- source-reference resolution against `SOURCES.json`;
- local Markdown link resolution;
- Markdown frontmatter presence/closure;
- manifest hash checking.

ZIP integrity is checked after packaging with `zipfile.ZipFile(...).testzip()`.
