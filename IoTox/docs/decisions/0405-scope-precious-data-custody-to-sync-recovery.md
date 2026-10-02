# 0405 — Scope precious-data custody to sync-layer recovery

Date: 2026-09-25

Status: accepted

## Context

Recent precious-data work used the phrase “independent backup custody” too
loosely. That phrasing suggested IoTox might eventually certify disk loss,
host compromise, off-machine custody, or filesystem-wide corruption recovery as
part of the product. That is the wrong scope. Ordinary user sync tools do not
solve those problems, and IoTox should not imply that it does.

Those are not merely unproven future claims. Disk-loss survival,
host-compromise survival, filesystem-wide corruption repair, storage-media
certification, and true backup/disaster recovery are explicit non-goals for
IoTox itself. IoTox may require and verify recovery-practice evidence before a
sync folder is promoted, but the backup, storage, host-security, and operator
recovery layers remain separate.

IoTox can own a narrower and useful claim: for a selected dataset, an operator
can provide content-free evidence that a versioned or immutable recovery source
outside normal IoTox sync write/delete/GC mutation restored to an equivalent
tree, and that the recovery procedure is rehearsed and documented.

## Decision

Rename the active stable sync gate from `sync.independent-backup` to
`sync.recovery-custody`. Keep `sync.independent-backup` only as a legacy
manifest alias so old retained evidence can still be read deliberately.

Define accepted sync recovery custody as:

- a content-free `iotox.sync-backup-custody.v1` receipt;
- a supported `custody_class` such as `same-host-versioned`,
  `sync-external-versioned`, `off-host-versioned`, or
  `offline-or-remote-versioned`;
- immutable or versioned generation labeling;
- a verified restore whose inventory matches the custody source;
- repeatable operator rehearsal;
- recorded distinct-device observation as metadata, not a requirement; and
- explicit nonclaims for storage-media certification, disk-loss protection,
  host-compromise protection, filesystem-wide corruption protection, and
  content custody.

The native `iotox sync backup receipt` command no longer requires
`backup-independent=1` or distinct root devices. It requires
`custody-class=CLASS`, `immutable-or-versioned=1`, and
`operator-rehearsal-repeatable=1`. Same-host versioned custody can pass when it
is outside normal IoTox sync mutation; it still does not become disaster
recovery.

Recovery runbook receipts now cover
`covers-restore-from-versioned-recovery-custody=1`. The old
`covers-restore-from-independent-custody=1` field remains accepted only as a
legacy alias.

## Consequences

IoTox precious-data signoff becomes more honest and more achievable:

- it can say “this synchronized working copy has versioned recovery and restore
  evidence”;
- it cannot say “this survives disk loss, host compromise, or filesystem-wide
  corruption”;
- it does not ask operators to prove physical-media independence as an IoTox
  product gate; and
- it stops treating same-host versioned recovery as useless when it is exactly
  the recovery class many ordinary sync users can operate.

Historical ADRs and evidence that used “independent backup” are superseded for
current policy by this decision. They remain useful as provenance for why the
gate exists, not as current product language.

## Validation

```sh
iotox sync backup receipt /dataset read-write 30 \
  backup-root=/backup/dataset restored-root=/restore-drill/dataset \
  backup-system=borg backup-generation=gen001 \
  live-failure-domain=live.host \
  backup-failure-domain=same-host.versioned \
  restored-failure-domain=restore.drill \
  restore-provenance=restore.drill \
  custody-class=same-host-versioned \
  immutable-or-versioned=1 \
  operator-rehearsal-repeatable=1 \
  --out /proof/sync-backup

tools/iotox-repo.sh sync-backup-custody-verify \
  /proof/sync-backup/backup-custody.json

iotox sync graduation-check /dataset read-write 30 \
  --evidence local-preflight=doctor \
  --evidence storage-readiness=repo.storage \
  --evidence recovery-custody=backup.receipt \
  --evidence restore-drill=restore.drill \
  --evidence recovery-runbook=runbook.review
```
