# VM storage model (ZFS-native first)

ZFS can make microVM lifecycle fast and safe.

## Model

- **Base image**: immutable dataset/zvol snapshot produced by Derive.
- **Instance overlay**: clone/snapshot for writable state (optional).
- **State policy**:
  - stateless: ephemeral overlays
  - stateful: managed dataset with backup/replication policy

## Ops

- replication/backup = ship base snapshots or whole instances via signed ZFS send streams (optional; see `docs/126-zfs-send-distribution.md`).
- create instance = clone base snapshot
- update = switch base pointer and recreate overlay
- rollback = revert overlay snapshot + pointer switch

For persistent datasets, schema evolution and migrations should be explicit artifacts and produce receipts.
See: `docs/217-state-datasets-and-migrations-as-evidence.md`.

Last updated: 2026-02-24
