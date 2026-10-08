---
status: validation_report
claim_kind: release_validation
route_role: release_governance_core
canonical_anchor: false
route_refs:
- release_governance_core
supersedes: rev0319
depends_on:
- ../tools/validate_archive.py
source_refresh_due: 2027-03-31
---

# Validation report — rev0355

Validator run:

```text
python3 tools/validate_archive.py
PASSED: 0 errors, 0 warnings
```

The validator now checks JSON/source references, links, frontmatter, duplicate frontmatter, source ID sequence, source metadata completeness, current-release sync, schema/spec sync, gate-inventory coverage, Gate 20 register presence, case-ledger coverage, generic Gate 20 proof-debt repetition, source-use register sync, evidence-ledger sync, case/scoreboard pairing, cache-artifact exclusion, rev-specific case-family requirements, and manifest hashes.

Zip integrity after packaging: `unzip -t` reported `No errors detected`.
