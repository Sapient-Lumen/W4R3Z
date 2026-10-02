# 0401: Add native precious-data sign-off porches

Date: 2026-09-22

Status: accepted and implemented; custody terminology superseded by ADR 0405

## Context

ADR 0400 removes storage-media certification from IoTox scope. That leaves the
right precious-data question: not “has IoTox blessed this disk?”, but “does the
operator have enough content-free evidence to trust this synchronized working
copy without confusing it for the only archive?”

Before this decision, the repo had strong storage-science receipts and stable
manifest shape checks, but the human path was still too manual. Backup custody,
restore drills, retention policy, manifest assembly, and “is this dataset ready
yet?” were spread across docs, scripts, and labels.

## Decision

Add native CLI porches for the precious-data sign-off path:

- `iotox sync backup plan PATH ...` prints the exact backup/restore receipt
  commands for a dataset.
- `iotox sync backup verify PATH ...` runs the strict tree-v2 recovery
  comparison and reports whether the restored tree matches the backup tree.
- `iotox sync backup receipt PATH ... --out DIR` writes
  `backup-custody.json`, `restore-drill.json`, and the raw recovery report only
  when the restore matches and the custody shape is honest.
- `iotox sync retention set|status NAMESPACE ...` writes and verifies a
  reviewed content-free retention policy: keep-days, minimum revisions,
  guarded delete propagation, and GC requiring backup custody.
- `iotox evidence collect sync PATH --out DIR ...` runs fresh local preflight,
  copies only shape-checked sync receipts, carries the retention policy, and
  writes a stable sync manifest when all six sync release gates are present.
- `iotox evidence manifest DIR --out PATH` regenerates the stable sync
  manifest from an evidence directory.
- `iotox sync precious-status PATH ...` is the fail-closed dashboard. It says
  `operator-signable` only when local preflight, local storage science,
  storage-readiness, long-soak, versioned recovery custody, restore drill,
  recovery runbook, and retention policy are all accepted.

ADR 0405 later narrows the custody requirement: same-host versioned custody can
mint a passing receipt when it is outside normal IoTox sync mutation. Distinct
root devices are recorded as metadata, not treated as proof of disaster
recovery.

## Consequences

Precious data now has an ordinary native workflow:

```sh
iotox sync backup plan /dataset read-write 30
iotox sync backup verify /dataset read-write 30 ...
iotox sync backup receipt /dataset read-write 30 ... --out /proof/backup
iotox sync retention set dataset --keep-days 90 --min-revisions 8 \
  --delete-grace-days 14 --out /proof/retention.receipt
iotox evidence collect sync /dataset read-write 30 --out /proof/sync ...
iotox sync precious-status /dataset read-write 30 --evidence-dir /proof/sync
```

This does not make IoTox the sole archive of irreplaceable originals. The
native status still prints `repo-certified=0`; sign-off means the operator has
a complete retained evidence trail for using IoTox as a precious working copy.

## Validation

The native human CLI process test now covers:

- backup plan output;
- backup verify accepting a matched restore drill;
- backup receipt requiring explicit versioned recovery-custody flags;
- retention policy set/status;
- evidence collection and manifest generation from shape-checked receipts;
- precious-status becoming operator-signable with complete evidence; and
- `ship-check sync stable --evidence-manifest` accepting the collected sync
  manifest.
