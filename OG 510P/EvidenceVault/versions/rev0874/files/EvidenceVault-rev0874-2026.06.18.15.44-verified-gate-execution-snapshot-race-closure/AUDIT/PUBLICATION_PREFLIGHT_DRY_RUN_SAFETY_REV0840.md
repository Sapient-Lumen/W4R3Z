# Publication preflight and dry-run safety audit — rev0840

This audit covers two practical operator-safety issues: publication preflight should fail fast while rights are blocked, and queue-publisher dry-runs must not create public-release snapshots or records.

- Status: `publication_preflight_and_dry_run_safety_hooks_present`
- Current rights status: `publication_blocked_pending_rights_decision`
- Current tree expected to refuse publication entrypoints: `true`

## Static checks

- Shared helper CLI present: `true`
- `publish_preflight.sh` guard precedes root-name check: `true`
- `publish_preflight.sh` guard precedes development gate run: `true`
- `make release-ledgers` guard precedes ledger/materializer builders: `true`
- `publish_queue_item.py --dry-run` branch precedes snapshot write: `true`
- `publish_queue_item.py --dry-run` branch precedes record write: `true`

## Protected operator paths

| Path | Protection |
| --- | --- |
| `scripts/publish_preflight.sh` | `python3 scripts/publication_rights_gate.py --context publish-preflight` |
| `Makefile` target `release-ledgers` | `$(PYTHON) scripts/publication_rights_gate.py --context release-ledgers` |
| `scripts/publish_queue_item.py` | dry-run returns before `write_public_surface_snapshot()` and atomic release-record writes |

## Validator behavior

`scripts/validate_publication_preflight_dry_run_safety_rev0840.py` regenerates this audit, probes rights-blocked `publish_preflight.sh` and `make release-ledgers` for fail-fast non-mutation, and runs `publish_queue_item.py --dry-run` in a minimal rights-ready temporary tree to prove the preview path writes no public snapshot, release record, or queue transition.

## Current blocking finding IDs

- `missing_root_license_or_notice`
- `missing_local_license_reference_targets`
