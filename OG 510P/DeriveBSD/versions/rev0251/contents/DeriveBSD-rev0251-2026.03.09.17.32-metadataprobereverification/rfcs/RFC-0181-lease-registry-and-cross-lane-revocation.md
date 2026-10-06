# RFC-0181: Lease registry and cross-lane revocation

Status: Draft

## Problem

DeriveBSD already uses time-bounded grants in multiple lanes (portals, secrets, debug, tracing, device attach, breakglass).
However, lease identity and revocation evidence are not fully unified:
- portal grants use `lease_id`
- some other grants use `grant_id`
- revocation evidence is portal-shaped (`portal.revoke`) rather than cross-lane

This makes it harder to answer:
- “What temporary authority is currently active on this host?”
- “What did we revoke when we stopped/rolled back service X?”

## Goals

- Standardize `lease_id` as the canonical identifier for temporary authority.
- Provide a safe, metadata-only snapshot of active leases (`lease-snapshot`).
- Provide a cross-lane revocation event (`lease-revoke-event`) for the structured journal.
- Make leases composable with service supervision (instance stop → deterministic revoke).

## Proposal

1) Add optional `lease_id` to non-portal grant objects that currently rely on `grant_id`.
   - `grant_id` remains required for backward compatibility.
   - convention: when both exist, `lease_id` SHOULD equal `grant_id`.

2) Introduce `lease-snapshot` evidence object.
   - records active leases (ids, subjects, scopes, expiry)
   - metadata-only (no secret bytes, no file contents)

3) Introduce `lease-revoke-event`.
   - emitted when a lease is revoked (or revocation attempted)
   - references the relevant lease, reason, actor, and related evidence

4) Extend incident bundles with optional include hooks:
   - `lease_snapshot`
   - `lease_revoke_events`

## Implementation sketch

- Supervisor/restarter maintains an in-memory or persisted lease index keyed by `lease_id`.
- On stop/rollback:
  - enumerate leases bound to the service instance and/or contract handle
  - revoke leases
  - emit `lease-revoke-event` for each revoked lease
- `derive lease snapshot` emits `lease-snapshot` and stores it in the evidence store.

References:
- `docs/249-lease-registry-and-cross-lane-revocation.md`
- `docs/182-capability-leases-and-revocation.md`
