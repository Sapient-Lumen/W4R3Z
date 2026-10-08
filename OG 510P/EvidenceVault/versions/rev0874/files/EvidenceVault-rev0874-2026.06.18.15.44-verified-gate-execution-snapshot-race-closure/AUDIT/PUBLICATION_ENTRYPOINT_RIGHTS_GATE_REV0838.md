# Publication entrypoint rights gate audit — rev0838

This audit covers artifact-emitting publication paths, not general development validation. A rights-blocked tree may remain development-gate-clean, but it must not create or refresh distributable release outputs.

- Status: `all_publication_entrypoints_rights_gated_and_current_tree_blocked`
- Shared helper: `scripts/publication_rights_gate.py`
- Shared-helper SHA-256: `ce759579502f836b6e3ee2192d5834f8d091316a35384f4655506095e14f9fd9`
- Rights ledger: `RIGHTS/component_license_ledger.json`
- Rights-ledger SHA-256: `71cb7b935fd732ebc91934ebb20955b71bd09f1d156910bf7e477d9ec385c2ea`
- Current rights status: `publication_blocked_pending_rights_decision`
- Current tree expected to refuse publication entrypoints: `true`
- Publish-audit inherits materializer gate: `true`

## Shared-helper required snippets

- `RIGHTS/component_license_ledger.json` — present
- `publication_rights_gate_status` — present
- `assert_publication_rights_ready` — present
- `publication rights gate blocked` — present
- `decision_required_before_publication` — present
- `blocking_findings` — present
- `root_license_or_notice_file_present` — present
- `root_license_or_notice_file_absent` — present

## Protected entrypoints

| Entrypoint | Purpose | Imports helper | Guard present | Guard before first mutation marker |
| --- | --- | ---: | ---: | ---: |
| `scripts/publish_audit.py` | run the bounded public-release ledger/materialization audit sequence | `true` | `true` | `true` |
| `scripts/package_release.py` | emit the named full-archive ZIP, SHA-256 sidecar, and artifact-verifier replay | `true` | `true` | `true` |
| `scripts/materialize_public_release.py` | rewrite public release bundle ZIPs, bundle manifests, and the public artifact index | `true` | `true` | `true` |
| `scripts/publish_queue_item.py` | write public release records, snapshots, notes, and transition queue items to published state | `true` | `true` | `true` |

## Blocking finding IDs

- `missing_root_license_or_notice`
- `missing_local_license_reference_targets`

## Validator behavior

`scripts/validate_publication_entrypoint_rights_gate_rev0838.py` regenerates this audit and invokes the publish-audit runner, full-archive packager, public-release materializer, and queue publisher probe. In the current rights-blocked tree each must fail with `publication rights gate blocked` before its mutation markers are reached.
