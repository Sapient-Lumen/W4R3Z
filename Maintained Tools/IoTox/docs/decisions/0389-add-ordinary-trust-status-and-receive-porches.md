# 0389 — Add ordinary trust, status, and receive porches

Date: 2026-09-19

Status: accepted

## Context

IoTox already had strong underlying primitives for three owner goals:

- synchronized working copies with storage-readiness gates;
- Ratox daily-driver shell setup with a strict production activation check; and
- person-key delivery across many device route keys.

Those primitives were still too scattered for ordinary use. A human should not
have to remember which low-level transcript, seen, receipt, storage, profile,
and activation commands compose the safe path. At the same time, the CLI must
not turn convenience into a false claim that data is precious-data-ready, that
sudo/PTY behavior is production-certified everywhere, or that one local receive
record means every device in a person swarm received a message.

## Decision

Add native, content-conscious porch commands:

- `iotox person receive PAYLOAD_HEX ...` verifies a person/group payload,
  commits local transcript and duplicate-suppression state idempotently, and
  can create one delegated device receipt without overwriting an existing
  receipt path.
- `iotox person messenger-status ...` reports content-free local messenger
  store health: contact counts, seen entries, transcript sequence, and outbox
  pending/sent route counts.
- `iotox sync trust-plan PATH ...` runs local sync-doctor inspection and prints
  the exact next runbook commands for dataset readiness, storage readiness,
  and independent-backup custody receipt verification while keeping
  precious-data readiness blocked by default.
- `iotox terminal daily-status ...` prints a non-failing daily Ratox
  dashboard/runbook that points at the strict `terminal activation-check`
  production gate.

## Consequences

Daily operation becomes more ordinary:

- a receiving device has one command for local receive/de-dupe/status work;
- sync trust has one front door before mutation or backup-retirement decisions;
- Ratox operators can run a status command without treating “not yet
  production-attested” as an error.

The boundaries stay explicit:

- `person receive` is local receive state, not cross-device transcript
  consensus or all-device delivery proof;
- `messenger-status` is content-free health, not message content or remote read
  receipts;
- `sync trust-plan` is a runbook, not an accepted independent
  backup-custody receipt;
- `terminal daily-status` is informational, and `terminal activation-check`
  remains the fail-closed gate for production evidence.

## Validation

The dev-shell targeted gate passed:

```sh
nix develop -c ctest --test-dir build/iotox-nix-debug \
  -R '^(iotox\.human-cli|iotox\.docs-coherence|iotox\.unit-and-integration)$' \
  --output-on-failure
```

The human CLI regression now covers `person receive`,
`person messenger-status`, `sync trust-plan`, and `terminal daily-status`.
