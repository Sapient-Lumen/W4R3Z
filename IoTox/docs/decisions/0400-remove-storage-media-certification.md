# 0400: Remove storage-media certification from IoTox scope

Date: 2026-09-22

Status: accepted; custody terminology superseded by ADR 0405

## Context

Earlier sync graduation plans treated destructive physical-media qualification
as a possible future gate before precious-data readiness. That would have meant
asking operators to provide explicit sacrificial media, health snapshots,
controller/write-cache observations, and cold-remount or power-variation cells.

The project will not do that. IoTox is a synchronization and remote-control
tool, not a disk, controller, firmware, or power-loss certification program.

## Decision

Remove storage-media certification from IoTox product goals, stable evidence,
storage-readiness, repo helper commands, and dataset readiness.

IoTox will keep testing what it owns:

- sync metadata and content-addressed storage logic;
- rollback refusal against acknowledged floors;
- exact block-prefix replay of IoTox-shaped transactions;
- long multi-writer soak behavior;
- versioned recovery-custody receipt intake;
- restore drills; and
- operator recovery runbooks.

IoTox will not require, plan, or provide destructive physical-media
qualification. The active planner now writes backup-custody and recovery-runbook
templates only, and says `storage-media-qualification=not-an-iotox-goal`.

## Consequences

Precious-data readiness is still not automatic. The trust boundary shifts to:

- accepted local storage-science receipts;
- accepted immutable/versioned recovery custody outside normal IoTox sync
  mutation;
- restore verification for the actual dataset class; and
- a reviewed operator recovery runbook.

The product can be honest without pretending to certify the user's disks.
Release/stable evidence no longer includes `sync.real-media`. Backup-custody
receipts carry the nonclaim `not-storage-media-certification`.

Historical evidence remains valid as storage-science evidence, but any older
roadmap text that treated media qualification as a next gate is superseded by
this decision.

## Validation

```sh
rg -n "sync\\.real|sync-real-media|real-media-verify" src tools tests CMakeLists.txt
python3 tools/plan-sync-precious-data-gates.py --self-test
python3 tools/qualify-storage-readiness.py --self-test
python3 tools/verify-sync-backup-custody.py --self-test
```
