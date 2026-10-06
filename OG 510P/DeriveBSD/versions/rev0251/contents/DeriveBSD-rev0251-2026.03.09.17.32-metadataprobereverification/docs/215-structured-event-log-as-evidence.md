# Structured event log as evidence (ETW / journald / OpenTelemetry lessons)

Most systems treat “logs” as a string pile you grep later.
DeriveBSD should treat **host events** the same way it treats builds, policy, and activation:
as **typed, queryable, capability-governed evidence**.

We already introduced:
- `svc.event` (service supervision transitions)
- `fault-event` (fault detectors + diagnosis)
- `resource-event` (resource violations + pressure + actions)

The next step is to make the *storage + access plane* explicit: a small, BSD-native **event journal** that can ingest these events and export them in standard telemetry formats.

## Lessons to steal (and why)

- **ETW (Windows)**: providers emit events; consumers can subscribe live or read from a log; tracing can be enabled/disabled dynamically with low overhead.  
  (Provider/consumer model + dynamic enablement is the key idea.)  
  Reference: https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
- **systemd journal**: binary, indexed logs designed for efficient querying and rotation.  
  (We don’t need systemd; we *do* want “logs are structured + queryable, not flat files”.)  
  Reference: https://www.freedesktop.org/wiki/Software/systemd/journal-files/
- **OpenTelemetry logs model**: consistent timestamps, severities, and attributes so heterogeneous logs can be processed uniformly.  
  (It’s the portable export target.)  
  Reference: https://opentelemetry.io/docs/specs/otel/logs/data-model/

## Goals

- A single host-local **append-only event store** for:
  - service supervision (`svc.event`)
  - fault management (`fault-event`)
  - policy/activation milestones (optional future emitters)
  - state migration milestones (optional; see `docs/217-state-datasets-and-migrations-as-evidence.md`)
- Typed **event records** with stable ids for correlation.
- **Capability-gated access** (no ambient “read all logs” privilege).
- Export adapters (OTLP logs, JSONL, syslog gateway) without losing integrity metadata.

## Data model

### 1) `event.record` (base schema)

A common envelope (see `spec/event.record.schema.json`):

- `kind` + `event_version`
- `event_id` (UUID recommended)
- `at` (event time) and optional `observed_at` (collector time)
- `source` (emitter identity; compartment tags)
- optional `class`, `severity` (+ numeric severity), `tags`
- `payload` (structured object)
- optional integrity:
  - `prev_digest` (hash-chain within a stream)
  - `signature` (over canonical bytes, when required)

Concrete event types (`svc-event`, `fault-event`, `attestation-event`, `crash-event`, `debug-event`, etc.) should **conform to the envelope** and add domain-specific fields.

`debug-event` covers record/replay milestones (record start/stop, capsule emitted, export attempts) and should reference `debug.record.grant`/`debug.replay.capsule` digests when available.

`config-event` covers configuration apply/confirm/rollback milestones (and should reference `config-receipt` digests).

`fw-event` covers firmware update milestones (staged, pending reboot, applied) and should reference `fw-update-plan`/`fw-update-receipt` digests.

`pki-event` covers trust bundle updates and certificate issuance/renewal/install milestones and should reference `pki-trust-bundle` / `pki-issue-receipt` digests when available.

`storage-event` covers storage integrity and health milestones (pool degrade/fault transitions, scrub/resilver start/complete, checkpoint create/discard) and should reference `storage-health-snapshot` / `storage-scrub-receipt` digests when available.

`time-event` covers time discipline milestones (sync acquired/lost, source changes, and clock steps). Producers should reference `time-sync-snapshot` and `time-sync-receipt` digests when available.
Because clock steps happen, collectors should prefer `observed_at` for ordering in cross-host views when strict monotonicity matters.

### 2) `event.segment` (journal segment metadata)

The journal stores events in **segments** (e.g., compressed JSONL or a compact binary form).
A segment is represented by a small evidence object (`spec/event.segment.schema.json`) that binds:

- segment identity (`stream_id`, `segment_id`)
- time bounds + count
- `file_digest` of the segment blob
- `merkle_root_digest` and `chain_head_digest` for tamper-evidence
- `prev_chain_head_digest` to stitch segments into a continuous chain

Segments make it cheap to:
- rotate / GC old logs
- export/ship bounded ranges
- prove “no gaps” for audited streams

### 3) Optional: `event.seal.receipt` (signed sealing chain)

For higher-assurance deployments, periodically **seal** an event stream by emitting a signed,
hash-chainable receipt over the segment set.
This makes “did someone rewrite or delete local evidence?” verifiable from exported receipts.

- Receipt schema: `spec/event.seal.receipt.schema.json`
- Details: `docs/424-forward-secure-event-log-sealing.md`


## Access + security

### Access is an explicit capability

Access to event streams should be granted the same way we grant trace streams:

- **operator policy** can grant “read svc events for service X” for N minutes
- **interactive portal** can grant a one-off “show me recent events” capability

See also: `docs/192-observability-as-capability.md`.

### Multi-tenant safety

- Events emitted from less-trusted domains must be **identity-tagged** in `source.domain`.
- The collector should enforce per-domain rate limits and size bounds.
- Redaction profiles apply at *export/view time* (not by mutating stored events).

## Profile-shaped collection posture

The event journal should inherit the product default from `docs/478-evidence-collection-posture-by-profile.md` rather than quietly becoming a one-size-fits-all subsystem:

- **A / fleet host**: bounded local journaling is normal and should already exist when health gates or incident bundles need it.
- **B / workstation**: journaling should stay locally useful and exportable, but richer capture or external upload must stay trusted-UI-visible.
- **C / general OS**: local retention stays the baseline; remote collectors remain an explicit option, not a hidden dependency.
- **D / appliance/factory**: journals feed deterministic redacted bundles; ambient live production streaming is not the default contract.

## CLI affordances (suggested)

- `derive event tail --stream host`
- `derive event query --service sshd --since 10m`
- `derive event query --change b5a0c5a3-... --since 24h` (correlation by change_id)
- `derive event export --otel --since 1h`
- `derive event verify-chain --stream host`

## Non-goals (for now)

- A distributed event system. Start local; shipping is an adapter.
- A general pub/sub IPC bus. This is for **telemetry and audit**, not RPC.


## Related

- Incident/support bundles (bounded event ranges + snapshots): `docs/216-incident-snapshots-and-support-bundles.md`.
- Change sets + apply receipts (change execution milestones): `docs/219-change-sets-and-apply-engine.md`.
- State datasets + migration receipts (state changes as evidence): `docs/217-state-datasets-and-migrations-as-evidence.md`.


Last updated: 2026-03-06r206
