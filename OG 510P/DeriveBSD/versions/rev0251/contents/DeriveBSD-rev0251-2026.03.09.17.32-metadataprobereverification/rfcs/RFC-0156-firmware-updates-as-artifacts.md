# RFC-0156: Firmware updates as artifacts (inventory + plans + receipts)

Status: Draft

## Motivation

Firmware is a recurring source of real-world outages and security exposure, yet most OS update systems treat it as “out of band”:

- vendor tools or manual boot media
- unclear provenance and approvals
- weak audit trails (what changed?)
- poor integration with rollback/health gating

DeriveBSD already has a strong pattern for safe change management:
explicit plans, typed evidence objects, receipts, and policy gates.
Firmware should follow the same pattern.

## Proposal

Add three evidence objects:

- `fw-device-inventory`: a privacy-safe inventory of updatable firmware-bearing components.
- `fw-update-plan`: an explicit plan referencing firmware payload artifacts by digest.
- `fw-update-receipt`: an integrity-protected receipt describing what happened.

And integrate firmware updates into:

- `change-set` orchestration (`apply-firmware` step)
- incident bundles (include inventory + recent receipts)
- health-gated updates (optional floor checks)
- the structured event journal (typed milestones)

## Non-goals

- Replacing vendor firmware signing schemes.
- Guaranteeing rollback for every firmware class.
- A universal firmware updater for every device on day one.

## Data model

### `fw-device-inventory`

Required:
- created_at
- host id + generation digest
- list of components with:
  - stable component id (e.g., ESRT firmware class GUID, or a derived id for non-ESRT devices)
  - current version
  - supported update mechanisms
  - privacy-safe device identifier hash (no raw serial)

### `fw-update-plan`

Required:
- created_at
- target host id (optional binding)
- components[] with:
  - component id
  - expected current version (optional guard)
  - target version
  - payload digest (and optional store path)
  - mechanism + preconditions

### `fw-update-receipt`

Required:
- created_at
- plan digest
- per-component outcome:
  - status (success/failure/pending)
  - observed versions before/after
  - reboot requirement
  - event pointers (event ids / segment digests)

## Execution model

- Firmware updates are executed by a small privileged worker (or helper) under service supervision.
- `change-set.steps[].op = apply-firmware` references one `fw-update-plan` by digest.
- The worker emits:
  - structured journal events (`event.record`)
  - `fw-update-receipt`

Default ordering recommendation within a change set:

snapshot → apply-config → run-migrations → apply-firmware → reconcile-services → health-check → commit

## Security considerations

- Firmware payloads are treated as a high-risk trust lane:
  - allowlists by vendor/model/class
  - signatures required
  - optional transparency publication
- Inventory is **not authority**.
  - updates require explicit plan + policy decision.
- Receipts and event records must never include secret material.

## References

See:

- `docs/221-firmware-updates-as-artifacts.md`
- `docs/219-change-sets-and-apply-engine.md`
- `docs/215-structured-event-log-as-evidence.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/112-health-gated-updates.md`
