# 0402 — Add operator precious-data signoff receipts

Date: 2026-09-22

Status: accepted

## Context

ADR 0401 made the precious-data path native: backup custody, restore drill,
retention policy, evidence collection, stable manifest generation, and
`sync precious-status` all fail closed in the product binary. That left one
awkward final step. Once `precious-status` reported `operator-signable`, the
operator still had no durable, content-free receipt saying “I reviewed this
specific evidence bundle and accept using this dataset as precious data.”

The project also must not turn that final receipt into a false upstream
certification. IoTox no longer pursues storage-media qualification as a
product gate, and local acceptance is not a promise that a dataset is safely
stored as a sole archive.

## Decision

Add:

```sh
iotox sync precious-signoff PATH read-write 30 \
  --evidence-dir /proof/sync \
  --reviewer owner \
  --accept-operator-responsibility \
  --out /proof/precious-signoff.receipt
```

The command reuses the same gate evaluation as `sync precious-status`. It
refuses to write unless the dataset is currently operator-signable, the
reviewer label is explicit, and the caller supplies
`--accept-operator-responsibility`.

The receipt schema is `iotox.sync-precious-data-signoff.v1`. It is
content-free: it records a hashed dataset selector, the stable evidence
manifest hash, hashes for local preflight, storage-readiness, long-soak,
backup-custody, restore-drill, recovery-runbook, and retention-policy
receipts, plus the nonclaims:

- not storage-media certification;
- not disk-loss protection;
- not host-compromise protection;
- not filesystem-wide corruption protection;
- not content custody;
- not repo certification.

The persisted receipt deliberately avoids storing dataset contents, dataset
entries, or the literal dataset path.

## Consequences

Operators now have a durable handoff artifact for the moment between “all
local evidence is green” and “I am willing to trust this copy in my own
backup/restore regime.”

Stable release manifests remain unchanged. The signoff is not a release gate;
it is local operator acceptance over a bounded evidence bundle.

## Verification

The human CLI process test covers:

- refusal to write without `--accept-operator-responsibility`;
- successful receipt creation from a complete evidence directory;
- presence of receipt hashes and nonclaims; and
- absence of the literal dataset path from the persisted receipt.
