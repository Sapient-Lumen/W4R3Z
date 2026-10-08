---
status: validation_report
claim_kind: archive_integrity
route_ref: source_governance
revision: rev0307
---

# Validation Report — rev0355

Command:

```bash
python3 tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

Validation coverage in this revision:

- JSON parsing across the archive.
- Recursive `source_ids` checks in JSON files.
- Scoreboard validation against `docs/20-program/scoreboard-schema.json`.
- Markdown source-reference checks against `SOURCES.json`.
- Local Markdown link checks.
- Markdown frontmatter presence/closure checks.
- Manifest hash verification.

Zip integrity was checked after packaging with `unzip -t`.
