# RFC-0153: Configuration transactions and receipts

Status: Draft

## Summary

Standardize system configuration management as DeriveBSD evidence artifacts:

- `config-plan` — explicit candidate→active transition plan derived from the generation Plan and policy
- `config-snapshot` — runtime view of effective configuration (digests + pointers)
- `config-receipt` — evidence emitted for each apply attempt (including rollback receipts)

Support a **commit-confirmed** mode for riskful changes (especially networking) to prevent remote lockouts.

## Motivation

Configuration is where otherwise “immutable” systems frequently devolve into:
- ad-hoc edits under `/etc`
- unclear provenance (“who changed this?”)
- partial writes / races during updates
- remote lockouts caused by a bad network change

We already have a strong DeriveBSD pattern for safety:
**explicit plans + receipts + health gating**.
Configuration should match that pattern.

## Artifacts

### config-plan

A `config-plan` describes:
- target generation / config root
- operations (write/replace pointers, reload requests, validators)
- validation requirements
- optional confirmation window (`commit-confirmed`)
- the rollback plan reference (or prior snapshot pointer)

### config-snapshot

A `config-snapshot` is a small, typed view of:
- current generation id + boot environment
- digests for important config “roots” (system, network, auth, services)
- pointers to rendered config roots in the store
- redaction policy ids (for exporting)

### config-receipt

A `config-receipt` records:
- which plan was applied (digest + id)
- start/end timestamps
- validation results
- which roots were swapped/activated
- which services were reloaded/restarted
- whether confirmation is pending / satisfied
- rollback actions taken (if any)

Receipts should be append-only and ingestible by the event journal.

## Commit-confirmed

For plans that set `confirm.required=true`:

- apply activates a candidate config root and starts a timer
- the system must observe a confirmation action before timeout
- otherwise auto-rollback to the prior config root and emit a rollback receipt

Confirmation should be capability-gated and should support automated “confirmers” (e.g., reachability tests from a remote probe domain).

## Interactions

- **Health-gated updates**: committing a generation should require successful config receipts (and confirmation, if required).
- **Service supervision**: `svcdb` can reference config roots, and supervision can drive reloads based on receipts.
- **Incident bundles**: include config snapshots and recent receipts by default.
- **Event journal**: emit `config.event` records for apply/confirm/rollback milestones.

## Alternatives considered (brief)

- “Just manage `/etc`” (traditional): lacks provenance, safety, and rollback.
- Put all config into state datasets: too heavy for all config; better to keep config receipts as a distinct lane and use state datasets only when persistence + schema evolution is essential.

## Next steps

- Define `config.event` record kinds and minimal CLI (`derive config plan/apply/confirm/rollback/show`).
- Decide default “confirm-required” scopes.
- Add validator hook conventions (BSD-native tools first).
