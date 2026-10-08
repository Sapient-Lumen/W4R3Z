---
status: validation_report
claim_kind: bundle_integrity
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- certification_core
supersedes: rev0318
depends_on:
- ../tools/validate_archive.py
source_refresh_due: 2027-03-31
---

# Validation report — rev0355

Generated: 2026-05-25T21:45:50Z

Command:

```bash
python3 tools/validate_archive.py
```

Result:

```text
PASSED: 0 errors, 0 warnings
```

## Validator scope added in rev0319

The validator now checks:

- JSON parse integrity and scoreboard schema conformance;
- source references in Markdown and JSON;
- local Markdown links;
- frontmatter closure and duplicate embedded frontmatter blocks;
- source ID sequence and source metadata completeness;
- uniform `SOURCES.json` coverage-map shape;
- current-release visibility on front-door and portfolio surfaces;
- scoreboard schema/spec field-count sync;
- full 20-gate inventory coverage across all scoreboards;
- Gate 20 register, subgate, and seniority-waterfall presence;
- `CASE_LEDGER.json` coverage of all case/scoreboard pairs;
- repeated generic Gate 20 proof-debt lists;
- legacy release-specific scoreboard field coverage; and
- manifest hashes.
