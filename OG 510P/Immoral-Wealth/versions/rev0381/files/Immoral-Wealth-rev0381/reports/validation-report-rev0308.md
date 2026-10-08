---
status: validation_report
claim_kind: integrity_report
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

Run target: `Immoral-Wealth-rev0308`.

The validation suite checks JSON parsing, recursive JSON `source_ids`, scoreboard schema conformance, Markdown source references, local Markdown links, frontmatter presence, source-id contiguity, rev0308 measurement scoreboard coverage, and manifest hashes.

Final validation result:

```text
PASSED: 0 errors, 0 warnings
```

Additional manual checks performed in rev0308:

- Source ledger expanded contiguously from `S01` through `S161`.
- Four new case memos each have companion scoreboards.
- Rev0308 scoreboards include measurement/visibility fields.
- `START_HERE.md`, `README.md`, `CHANGELOG.md`, `SOURCES.*`, `ARCHIVE_INDEX.*`, `REVISION-RECEIPT.json`, and `VERSION` were updated.
- New gate and measurement protocols are linked from the front door.
