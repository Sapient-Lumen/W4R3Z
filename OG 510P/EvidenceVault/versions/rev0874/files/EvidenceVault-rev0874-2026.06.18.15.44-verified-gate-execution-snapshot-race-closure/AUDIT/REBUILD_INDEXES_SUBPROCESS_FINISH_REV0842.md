# Rebuild-indexes subprocess finish audit — rev0842 refreshed in rev0847

- Status: `rebuild_indexes_dedupe_spdx_and_source_index_subprocess_isolated_refreshed_with_atomic_outputs`
- Revision context: `rev0842-audit-refreshed-in-rev0847-overlay`
- Purpose: Finish the highest-risk part of the rev0839 refactor by moving the remaining heavy material builders, build_dedupe_report.py and build_spdx_inventory.py, out of the long-lived rebuild_indexes.py interpreter.
- Risk reduced: Dedupe and SPDX refreshes no longer share Python module state with rebuild_indexes.py; failures surface as child-process return codes before final index/manifest emission.

- Changed/rebuild script: `scripts/rebuild_indexes.py`
- SHA-256: `df31735a8f0d6bbeec632094880ed2e6f218a57f623d01c522766f2422b12477`

## Limits

- No known heavy material-surface builders remain imported in-process in the changed rebuild_indexes.py path; rev0843 moved source-index refresh to a subprocess and rev0847 kept that contract.
