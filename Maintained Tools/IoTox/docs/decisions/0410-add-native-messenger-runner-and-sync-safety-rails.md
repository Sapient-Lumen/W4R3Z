# ADR 0410: Add native messenger runner and sync safety rails

Status: accepted
Date: 2026-09-27

## Context

ADR 0409 made the next operator work visible but deliberately kept the person
messenger lane as plans for an external timer, and the sync freeze record as a
local warning record. The next product gate was to turn those porches into
ordinary native binary behavior while preserving the same nonclaims:

- sending to a person key should have durable retry/expiration state and a
  content-free receipt rollup;
- Toxic-compatible normal Tox bridge observations should remain separate from
  IoTox person identity;
- sync should feel like a daily folder tool, with health/status commands and
  recoverable deletion ergonomics; and
- precious-data readiness should improve through versioned recovery,
  retention, restore practice, quarantine, and signoff receipts, not through
  claims about disk loss, host compromise, or filesystem-wide corruption.

## Decision

Add native commands and store semantics instead of wrapper scripts:

- person outbox records now carry creation time, last-attempt time, and attempt
  count while retaining backward decoding of old outbox records;
- `iotox person outbox-expire` moves still-pending expired items to a
  dead-letter outbox instead of deleting them;
- `iotox person background-run` is a bounded native worker that composes
  content-free messenger status, optional dead-letter expiration, and one-shot
  outbox sending for service supervision;
- `iotox person receipt-commit`, `person receipts-status`, and
  `person receive --receipt-store` make aggregate delegated-device receipts
  durable and queryable by explicit expected device set;
- `iotox sync folder-status` becomes the content-free dashboard for one
  namespace/path;
- `iotox sync safe-delete` moves a target into namespace-labeled quarantine and
  writes a receipt instead of purging; and
- native sync mutator CLIs refuse namespaces with an active local freeze record.

## Consequences

The daily experience becomes more ordinary without widening authority:

- person messaging can be supervised by systemd/cron/Monsternix using one
  native bounded loop rather than a hand-authored shell loop;
- a sender can see pending/sent route counts, attempts, dead letters, and
  explicit expected-device receipt completion without seeing message content;
- normal Tox/Toxic bridge records remain signed observations by a delegated
  IoTox device, not claims that the external Tox key is an IoTox person key;
- sync operators get a single folder dashboard and a recoverable local delete
  porch before a logical tombstone is published; and
- local freeze is now enforced by native CLI mutators, while already-running
  Agent work and remote peers remain separate operational boundaries.

The remaining nonclaims are explicit. `person background-run` is not an
automatically installed resident messenger daemon and cannot guarantee delivery
to devices that never return online. `receipts-status` is expected-device
receipt accounting, not human read status or transcript consensus. `safe-delete`
is a local quarantine move, not backup. Local freeze is not distributed
consensus and does not revoke remote writers.
