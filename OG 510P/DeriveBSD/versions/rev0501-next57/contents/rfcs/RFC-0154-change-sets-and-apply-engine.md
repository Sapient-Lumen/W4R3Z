# RFC-0154: Change sets + apply engine

Status: Draft

## Motivation

DeriveBSD already models critical transitions as explicit artifacts with receipts:

- configuration: `config-plan` → `config-receipt`
- persistent state: `state-migration-plan` → `state-migration-receipt`
- service health: `svc.snapshot` / `svc.event`
- updates: health-gated commit/rollback

Without a unifying orchestration primitive, real deployments will converge on scripting
that reintroduces partial apply hazards and makes “what changed?” hard to answer.

## Proposal

Introduce two evidence objects:

- `change-set`: a signed, verifiable bundle describing a multi-step transition by *referencing* component plans.
- `change-receipt`: emitted by the apply engine, referencing per-step receipts + event pointers.

And a minimal apply engine that:

- executes the `change-set` in declared/default order
- emits `change-receipt` for success/failure
- integrates with the event journal (`event.record`) and optional incident bundling

## Non-goals

- A general purpose workflow engine.
- A pub/sub control plane or RPC bus.
- Baking fleet orchestration into the host (fleet tools can generate many host-local change sets).

## Data model

### `change-set`

Required fields:

- target generation id (and optional BE pointer)
- `steps[]`: ordered list of operations
- references (digests) to component plans (e.g., `config-plan`, `state-migration-plan`)
- declared preconditions/checks
- declared rollback hints
- optional confirm window (`commit-confirmed` at the change level)

### `change-receipt`

Required fields:

- reference/digest of the executed `change-set`
- per-step status and pointers to produced receipts
- pointers to relevant event journal segments/events
- final decision: committed / rolled back / requires confirmation

## Execution model

Default ordering is:

1) snapshot (config/state) + holds
2) apply config
3) run state migrations
4) reconcile services
5) run health checks
6) commit or rollback

The apply engine must be designed as a small TCB component:

- privilege-separated helpers for ZFS/pf/rctl/etc
- deterministic redaction transforms for anything exported
- capability-gated confirmation

## Security considerations

- `change-set` is signed and policy-validated before execution.
- `change-receipt` must be append-only and integrity-protected.
- receipts/events must not contain secrets; only references/digests.
- export of change artifacts is gated by trace/debug grants.

## References

See:

- `docs/219-change-sets-and-apply-engine.md`
- `docs/218-configuration-transactions-and-receipts.md`
- `docs/217-state-datasets-and-migrations-as-evidence.md`
- `docs/214-service-supervision-health-as-evidence.md`
- `docs/215-structured-event-log-as-evidence.md`

