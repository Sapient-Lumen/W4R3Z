# Replacing Resilio Sync with IoTox

Status: pragmatic migration guide, not a precious-data recommendation.
Updated 2026-09-25.

## Short answer

For a noncritical private Linux regular-file directory, yes: IoTox can now be
treated as a serious synchronized working-copy candidate.

For irreplaceable originals, no: IoTox is not the sole system of record.
Keep versioned recovery custody outside normal IoTox sync mutation and rehearse
restore before promotion. That is sync-layer recovery practice, not a promise
and not a goal to handle disk loss, host compromise, or filesystem-wide
corruption.

## What feels similar

- multiple machines can keep an ordinary directory converged;
- changes can move without a vendor account;
- peers can be offline and later catch up;
- conflicts preserve alternatives instead of silently discarding a value;
- a local machine chooses its own path.

## What is intentionally different

| Question | Resilio-shaped expectation | IoTox answer |
| --- | --- | --- |
| Account/control plane | Product/service identity | Self-owned device identity and authority ledger |
| Path setup | Share membership often feels like one object | Every machine chooses its own local path |
| Write authority | Joining a share can feel like access | Friendship is not authority; `sync-share` grants exact capability |
| Conflict policy | Product-defined UX | Tree-v2 preserves concurrent values until a later ordinary edit resolves |
| Backup story | Often mistaken for backup | Explicitly not backup |
| Unsupported files | Product may hide details | IoTox refuses unsupported filesystem semantics early |

## Use IoTox sync now when

- the directory is noncritical, or it has versioned recovery custody you have
  restored and verified;
- the data fits private regular files/directories and IoTox's mode/path model;
- every writer is a device/principal you actually intend to authorize;
- you are willing to resolve conflicts by normal later edits;
- you can tolerate current Linux/KVM-heavy evidence boundaries.

## Wait or keep shadowing when

- this is the only copy of precious data;
- the directory depends on symlinks, ACLs, xattrs, sparse files, devices,
  sockets, FIFOs, ownership translation, or case-folding portability;
- you need arbitrary remote-selected destination paths;
- you need mobile/desktop GUI polish rather than a shell-first tool;
- you cannot explain who may still write after a device is lost or retired.

## Migration path

1. Keep Resilio or another trusted synchronizer/backups in place.
2. Pick a representative noncritical copy.
3. Run:

   ```sh
   iotox sync trust-plan /absolute/path read-write 30
   iotox sync-doctor /absolute/path read-write 30
   iotox sync-dataset-readiness /absolute/path read-write 30
   iotox sync graduation-check /absolute/path read-write 30
   iotox ship-check sync stable
   iotox readiness storage
   ```

4. Pair machines with `iotox pair-card`.
5. Plan before mutating:

   ```sh
   iotox sync plan-pair notes /local/notes alias:laptop /remote/notes read-write 30
   ```

6. Start and share on both sides:

   ```sh
   iotox sync start notes /local/notes read-write 30
   cat RECALLROOT.txt | \
     iotox sync share notes alias:laptop read-write
   ```

   `RECALLROOT.txt` is a private local ceremony placeholder, not a required
   filename. The phrase is read from stdin; do not put it in argv or the
   environment.

7. Exercise ordinary edits, offline edits, concurrent edits, deletion, restart,
   conflict explanation, repair, and restore verification.
   Use `iotox sync folder-status NAME PATH read-write 30` as the ordinary
   dashboard and `iotox sync safe-delete NAME TARGET --quarantine-root DIR`
   when you want a recoverable local delete porch before publishing a logical
   tombstone.
8. Only then consider a real working directory, and only with versioned
   recovery custody and a restore drill you have actually rehearsed.

## Commands that matter during evaluation

```sh
iotox sync-status
iotox sync folder-status notes /local/notes read-write 30
iotox sync-health notes cached
iotox sync-repair notes
iotox sync-conflicts-summary notes
iotox sync-conflict-explain notes path/to/file
iotox sync freeze notes --reason operator.review
iotox sync unfreeze notes --reason operator.resume
iotox sync safe-delete notes /local/notes/obsolete.txt \
  --quarantine-root /local/.iotox-delete-quarantine \
  --reason operator.reviewed-delete
iotox sync-dataset-readiness /local/notes read-write 30 \
  backup-root=/backup/notes restored-root=/restore-drill/notes \
  backup-system=borg backup-generation=gen001 \
  backup-failure-domain=external-ssd restore-provenance=drill \
  verify-recovery=1
iotox sync graduation-check /local/notes read-write 30 \
  --evidence local-preflight=doctor \
  --evidence storage-readiness=repo.storage \
  --evidence recovery-custody=backup.receipt \
  --evidence restore-drill=restore.drill \
  --evidence recovery-runbook=runbook.review
iotox ship-check sync stable
iotox sync-recovery-verify /backup/root /restored/root
iotox support-bundle plan ./iotox.support
```

`sync-dataset-readiness` joins local source preflight, storage-readiness review,
backup/restore command planning, optional inline restore verification,
and the explicit `precious-data-repo-certified=0` nonclaim
in one report. Treat a green-looking report as “working-copy candidate,” not
“delete my other backups.”

`sync graduation-check` is the fail-closed review target for that working copy.
It can record `working-copy-graduation=operator-attested` only after all six
evidence labels are present, and it still reports
`precious-data-readiness=blocked`.

`sync folder-status` is the daily one-line dashboard for one namespace/path. It
runs the source doctor, reports whether the local operator freeze is active,
summarizes Agent status when reachable, and prints the next exact commands for
health, conflicts, freeze/unfreeze, precious-status, and safe-delete. `sync
safe-delete` moves a target into a namespace-labeled quarantine directory and
writes a receipt beside it; it never purges. Native sync mutator commands now
refuse a namespace while its default runtime local freeze record is active,
although already running Agent jobs and remote peers are still separate
operational concerns.

`ship-check sync stable` is stricter than both. It remains blocked for
no-concern shipping; the current honest release channel is
`ship-check sync founder-preview`, meaning working-copy use with versioned
recovery custody and explicit nonclaims.

## The honest product sentence

```text
IoTox sync is becoming a humane, owner-controlled working-copy system.
It is not yet the sole backup or system of record for precious originals.
```
