# 0404 — Require native recovery-runbook receipts for precious-data signoff

Date: 2026-09-25

Status: accepted; custody terminology superseded by ADR 0405

## Context

ADRs 0401--0403 made the precious-data path native and refreshed the current
`sync.long-soak` proof. One remaining weak point was the recovery-runbook gate:
the stable checker accepted a tiny hand-authored line record with only
`schema`, `status`, `content-free`, and `operator-runbook` fields. That did
reject random prose, but it still made the easiest passing artifact a magic
four-line note rather than proof that the operator reviewed a real recovery
document for the actual dataset selector.

The runbook gate is not content custody and it is not a backup/restore drill.
It is the human “I know how I would recover this data without making sync make
things worse” gate. That makes it especially important that the receipt be
ordinary to produce and harder to fake accidentally.

## Decision

Add a native runbook porch:

```sh
iotox sync runbook plan /dataset read-write 30

iotox sync runbook receipt /dataset read-write 30 \
  --runbook /proof/recovery-runbook.md \
  --reviewer owner --accept-reviewed-runbook \
  --out /proof/recovery-runbook.receipt

iotox sync runbook status --receipt /proof/recovery-runbook.receipt
```

The receipt is content-free. It hashes the reviewed runbook file and hashes the
dataset selector, but it does not store the runbook text or the literal dataset
path. The command requires explicit `--accept-reviewed-runbook`.

Strengthen the `sync.recovery-runbook` stable-evidence checker. A passing
record must now include:

- `schema=iotox.sync-recovery-runbook-review.v1`;
- `status=reviewed`;
- `content-free=1`;
- `operator-runbook=present`;
- valid `reviewer-label`;
- `dataset-selector-sha256`;
- valid `access` and `interval-seconds`;
- `runbook-sha256`;
- nonzero `runbook-bytes`;
- coverage flags for stopping writers, restoring from versioned recovery
  custody,
  verifying before resuming sync, retiring obsolete writers, and periodic
  rehearsal;
- `accepted-reviewed-runbook=1`; and
- `not-content-custody=1`.

Minimal four-line runbook receipts are now rejected.

## Consequences

Precious-data signoff now has one fewer hand-authored weak spot. Operators can
still keep recovery runbooks private; IoTox records only a hash-bound
content-free review receipt. This does not prove that the runbook is good, that
recovery custody exists, or that a restore drill passed. It only makes
the runbook gate deliberate, dataset-bound, and native.

Existing old-format recovery-runbook receipts must be regenerated with
`iotox sync runbook receipt` before they can pass `iotox evidence collect sync`,
`iotox sync precious-status`, or stable `ship-check` evidence validation.

## Validation

```sh
iotox sync runbook plan /dataset read-write 30
iotox sync runbook receipt /dataset read-write 30 \
  --runbook /proof/recovery-runbook.md \
  --reviewer owner --accept-reviewed-runbook \
  --out /proof/recovery-runbook.receipt
iotox sync runbook status --receipt /proof/recovery-runbook.receipt
```

The human CLI tests cover the full native path, explicit acceptance refusal,
and rejection of the old minimal runbook receipt shape.
