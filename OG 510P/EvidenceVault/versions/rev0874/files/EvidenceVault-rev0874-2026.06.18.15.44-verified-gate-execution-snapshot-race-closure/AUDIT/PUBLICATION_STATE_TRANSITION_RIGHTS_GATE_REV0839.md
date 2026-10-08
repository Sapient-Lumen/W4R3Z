# Publication state transition rights gate audit — rev0839

rev0838 guarded public/full release emitters. rev0839 closes the lower-level queue-state bypass: direct transitions into `published` must also refuse while rights are blocked.

- Status: `direct_published_state_transition_rights_gated`
- Transition utility: `scripts/transition_queue_item.py`
- Transition utility SHA-256: `5a56d8a49a551716e2bbc346778b6132c90163474480f581bda589e5118ad1f4`
- Rights ledger: `RIGHTS/component_license_ledger.json`
- Rights blocked: `true`
- Rights blocked reasons: `decision_required_before_publication, blocking_findings_present, ledger_status_blocks_publication, ledger_reports_no_root_license_or_notice, root_license_or_notice_file_absent`
- Static checks pass: `true`
- Blocked probe pass: `true`

## Static guard placement

- Imports shared helper: `true`
- Conditional `--to-state published` guard present: `true`
- Guard call present: `true`
- Guard precedes queue lookup: `true`
- Guard precedes first mutation: `true`

## Refusal probe

- Probe item: `EV-QUEUE-2026-03-20-full-archive-mirror-not-public`
- Return code: `1`
- Output contains rights block: `true`
- Output contains transition OK: `false`
- Queue/publication files changed: `false`

## Why this matters

A rights-blocked tree should remain development-testable, but no path should mark a release queue item as executed/public. This guard blocks the direct state mutation path separately from the higher-level `publish_queue_item.py` emitter.
