# Publication rights gate audit — rev0837

This audit checks a concrete release-safety invariant: an archive may keep development validation green while rights are unresolved, but the full named packager must fail fast before creating a distributable ZIP.

- Status: `package_release_guarded_and_current_tree_blocked`
- Protected operator path: `scripts/package_release.py`
- Shared helper: `scripts/publication_rights_gate.py`
- Rights ledger: `RIGHTS/component_license_ledger.json`
- Package-release SHA-256: `ee8de1fb9ac6b18e512a94d3f85eae469a69941e391d7ecdd8f74bfaead820fd`
- Shared-helper SHA-256: `ce759579502f836b6e3ee2192d5834f8d091316a35384f4655506095e14f9fd9`
- Rights-ledger SHA-256: `71cb7b935fd732ebc91934ebb20955b71bd09f1d156910bf7e477d9ec385c2ea`
- Imports shared helper: `true`
- Guard call precedes package refresh: `true`
- Guard resolves before ZIP writer: `true`
- Current rights status: `publication_blocked_pending_rights_decision`
- Decision required before publication: `true`
- Root LICENSE/COPYING/NOTICE present: `false`
- Current tree expected to refuse package release: `true`

## Blocking finding IDs surfaced by the rights ledger

- `missing_root_license_or_notice`
- `missing_local_license_reference_targets`

## Required guard snippets

- `RIGHTS/component_license_ledger.json` — present
- `assert_publication_rights_ready` — present
- `publication rights gate blocked` — present
- `decision_required_before_publication` — present
- `blocking_findings` — present
- `root_license_or_notice_file_present` — present
- `before any release-root checks` — present

## Shared-helper required snippets

- `RIGHTS/component_license_ledger.json` — present
- `assert_publication_rights_ready` — present
- `publication_rights_gate_status` — present
- `publication rights gate blocked` — present
- `decision_required_before_publication` — present
- `blocking_findings` — present
- `root_license_or_notice_file_present` — present

## Validator behavior

`scripts/validate_publication_rights_gate_rev0837.py` regenerates this audit and invokes `scripts/package_release.py` in the current blocked tree. The expected result is a non-zero exit containing `publication rights gate blocked` before any package-refresh or package-write step appears.
