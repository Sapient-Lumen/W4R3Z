# ADR 0388: Add outbox send, storage graduation receipts, and Ratox activation check

Status: accepted; sync custody terminology superseded by ADR 0405
Date: 2026-09-19

## Context

The multidevice person layer had durable outgoing route accounting, but sending
was still a human script exercise: `outbox-plan` printed `message-hex` commands
and a separate `outbox-mark-sent` command. Storage readiness had the correct
default refusal for precious data, but recovery custody was a prose gate rather
than a first-class receipt validator. Ratox had
daily-driver pieces (`daily-plan`, `terminal doctor`, profile stale checks, and
focused daily-control scripts), but no single native command that failed closed
until the operator had gathered activation evidence.

## Decision

Add three bounded native/operator surfaces without weakening the project
boundaries.

### Person outbox send

`iotox [CONTROL_OPTIONS] person outbox-send OUTBOX [--max-routes N]
[--dry-run]` walks the durable outbox in canonical order. In dry-run mode it
prints the exact send and mark-sent commands without mutation. In live mode it
resolves each pending route as a current Tox friend, submits the signed payload
through the local control socket, and only then marks that route sent.

The command deliberately records local transport acceptance only. Remote person
receipt, all-device delivery, background retry, expiration, card refresh, and
transcript consensus remain separate messenger work.

### Storage receipts

Add one content-free verifier:

- `tools/verify-sync-backup-custody.py` for
  `iotox.sync-backup-custody.v1` receipts.

`tools/qualify-storage-readiness.py` now consumes that receipt through
`--backup-custody-proof`, also discovering retained runs below
`.sandwurm/exports/sync-backup-custody`. The default report stays blocked when
that proof is absent. Synthetic self-tests cover the accept path, but they do
not create real deployment evidence. ADR 0400 later removed storage-media
certification from IoTox scope.

`tools/iotox-repo.sh` exposes the verifier as `sync-backup-custody-verify`.

### Ratox activation check

`iotox terminal activation-check [--root PATH] [--peer PEER]
[--evidence NAME=LABEL...]` prints the daily plan, doctor, daily-control,
delegated-cgroup, service-check, reconnect, and profile-freshness commands.
It exits blocked until all six gate labels are supplied:

```text
daily-control
profile-freshness
service-supervision
reconnect-continuity
cgroup-delegation
route-loss
```

With all labels present it reports
`production-activation=operator-attested` and `repo-certified=0`. Evidence
labels are content-free operator custody, not cryptographic proof of fleet,
kernel, sudo, or network behavior.

## Consequences

- Person messaging now has a practical one-shot/timer-friendly route sender.
- Storage graduation can accept genuine independent-custody receipts later
  without changing the truth boundary.
- Ratox daily-driver readiness is a repeatable command rather than a prose
  checklist.
- The repo still does not claim background messenger delivery, precious-data
  readiness, or production Ratox certification by default.

## Evidence

- `src/cli.cpp` implements `person outbox-send` and
  `terminal activation-check`.
- `tools/verify-sync-backup-custody.py` and
  `tools/qualify-storage-readiness.py` implement and aggregate the storage
  receipt gates.
- `tests/test_human_cli.py` covers outbox dry-run and activation check
  behavior.
- CTest includes self-tests for the storage verifier and the combined
  storage readiness report.
