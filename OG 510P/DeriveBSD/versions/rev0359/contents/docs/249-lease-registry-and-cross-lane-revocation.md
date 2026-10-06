# Lease registry + cross-lane revocation (unify all temporary authority)

DeriveBSD already uses **time-bounded grants** in multiple lanes:
- portals (user-driven capability grants)
- secrets (brokered secret materialization)
- debugging/tracing (record/replay and tracing sessions)
- device attach (hot-plug authority)
- breakglass (emergency recovery authority)

The archive also already has the *mechanics* for revocable capabilities (`docs/182-capability-leases-and-revocation.md`).

This doc tightens the meta-design: **every temporary authority is a lease**, and leases become
first-class, queryable evidence so that:
- supervisors can deterministically clean up on stop/rollback
- incident bundles can include a minimal answer to “what authority was live?”
- revocation is explainable and cross-lane (not “portal-only”)


## Lessons worth stealing

### Vault-style leases (TTL + renew + revoke)
HashiCorp Vault treats dynamic secrets and certain tokens as **leases** with a TTL, renewability, and revocation semantics.
That model is a good fit for DeriveBSD’s “authority as evidence” stance:
- consumers can treat data as valid only within the lease TTL
- renewal extends validity without changing secret contents
- revocation makes future use invalid even before natural expiry

See: Vault lease concepts and renewal docs.


## DeriveBSD stance

### 1) A lease is the unit of *temporary authority*
A lease is identified by a stable `lease_id` and has:
- `issued_at`, `expires_at`
- a `subject` (who/what is using it)
- a `scope` (what it authorizes)
- optional renewal and revocation metadata

A lease can back many concrete mechanisms:
- mediated proxy handle (strong revocation)
- fresh-open re-authorization (revocation via denying future opens)
- raw handle with tight TTL (weak revocation; workstation/debug-only)


### 2) Every grant object should carry `lease_id`

To make this composable, DeriveBSD also introduces a small cross-lane join object: **`lease.envelope`**.
It records common metadata (issuer/subject/timebox) and points at the lane-specific grant / lease / session object that actually grants authority. Later action receipts belong elsewhere.
This keeps lane schemas stable while enabling uniform tooling (`lease ls`, `lease revoke`).

See: `docs/252-lease-envelope-and-cross-lane-joins.md`.

Portal grants already use `lease_id`.
Other grants historically used `grant_id`.

**r45 refinement:** keep `grant_id` for backward compatibility, but standardize on:
- `lease_id` as the canonical cross-lane identifier
- `grant_id` as an alias (legacy field) where present

This enables unified correlation across:
- `secret-grant`, `breakglass-grant`
- `debug-record-grant`, `trace-session`
- `device-attach-grant`


### 3) Lease state becomes evidence
Add four lane-agnostic evidence objects (see `docs/449-lease-issue-and-use-receipts.md`):

- `lease.issue.receipt`
  - issuance/renewal/denial decision for a lease (binds to the lane grant/session by digest)

- `lease.use.receipt`
  - metadata-only record of each use attempt (allowed/denied), optionally pointing at the operation receipt

- `lease-snapshot`
  - a safe metadata snapshot of active leases on a host (or per domain)
  - used by incident bundles and support tooling

- `lease-revoke-event`
  - a structured journal record that a lease was revoked (or attempted)
  - cross-lane: revocation is not “portal-only”


## How this composes with the rest of the system

### Service restarters and contract handles
When a supervised service instance stops (or is rolled back), the restarter should be able to:
- enumerate leases held by that service instance
- revoke them deterministically

This is why leases must be correlatable to:
- `service_id` and optional `instance_id`
- a service boundary handle (`spec/svc.contract.handle.schema.json`)


### Causality graphs and bundle-min
Lease evidence is a powerful compression tool:
- rather than dumping large log volumes, a minimal bundle can include:
  - a `lease-snapshot`
  - relevant `lease-revoke-event` ids
  - the specific grants/receipts referenced by those leases

See: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`.


## Non-goals

- Perfect revocation of raw kernel FDs.
- Replacing external IAM/secret infrastructure.


## References

- Vault lease model (TTL/renew/revoke): https://developer.hashicorp.com/vault/docs/concepts/lease
- Vault lease renew command: https://developer.hashicorp.com/vault/docs/commands/lease/renew

See also: `docs/182-capability-leases-and-revocation.md`, RFC-0181.

Last updated: 2026-03-07r222
