# Publish queue authorized snapshot entries — rev0849

- Status: `snapshot_entry_points_require_queue_authorization`
- Validator: `scripts/validate_publish_queue_item_authorized_snapshot_entries_rev0849.py`

## Purpose

Bind the future publication snapshot to the queue decision: every entry_point digested from published/PUBLIC_SURFACE.json must be explicitly authorized by decision.public_paths, while decision paths that are absent from the snapshot still fail closed.

## Changed surfaces

- `scripts/publish_queue_item.py`

## Validator cases

- all snapshot entry points authorized passes
- source manifest may be listed explicitly as a claimable metadata path
- extra snapshot entry not in decision.public_paths blocks
- decision path absent from snapshot/source_manifest blocks
