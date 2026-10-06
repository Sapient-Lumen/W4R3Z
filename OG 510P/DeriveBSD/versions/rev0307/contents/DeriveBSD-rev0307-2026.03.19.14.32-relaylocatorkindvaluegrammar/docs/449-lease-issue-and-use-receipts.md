# Lease issue + use receipts (make Broker→Lease→Receipt real)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Broker→Lease→Receipt, Bundles

DeriveBSD’s least-authority stance relies on **temporary authority**: brokers issue time-bounded leases instead of handing out ambient power.

The archive already has:
- a cross-lane join envelope: `lease.envelope`
- a safe inventory snapshot: `lease-snapshot`
- a revocation event: `lease-revoke-event`

But the Broker→Lease→Receipt pattern is incomplete without two missing pieces:
1) a receipt for **issuance/renewal/denial** (why a lease exists), and
2) a receipt for **use** (what the lease actually authorized).

This doc introduces two generic, metadata-only receipts that any lane can emit without forking schemas.

## New evidence primitives

### `lease.issue.receipt`
Emitted by the broker at the moment it decides to issue (or renew) a lease, or when it denies an issuance attempt.

**Goals:**
- make the *decision* legible (lane, policy consulted, approvals)
- bind the issuance to a concrete grant / lease / session object (by digest)
- provide a stable join key for incident timelines and bundle-min (`lease_id`)

Schema: `spec/lease.issue.receipt.schema.json` (example: `spec/examples/lease.issue.receipt.json`).

### `lease.use.receipt`
Emitted when a lease is exercised to perform an operation (allowed or denied).

**Goals:**
- turn “authority was used” into queryable evidence
- keep the record safe-by-default (metadata only; no sensitive payloads)
- optionally point at the operation’s own receipt (by digest)

Schema: `spec/lease.use.receipt.schema.json` (example: `spec/examples/lease.use.receipt.json`).

## How this composes

The authoritative temporary-authority object is still lane-specific. In r222 the generic receipts become explicit evidence-only surfaces: `lease.issue.receipt` explains issuance, `lease.use.receipt` explains exercise, and neither one replaces the original grant / lease / session object.


- `lease.envelope` (optional): captures common issuer/subject/timebox metadata and points at a lane grant/session.
- `lease.issue.receipt` (new): captures the issuance decision and links to the grant/session (and optionally the envelope).
- `lease.use.receipt` (new): captures each use attempt (allowed/denied) and can link to the operation’s receipt.
- `lease-revoke-event`: captures revocation attempts and results.
- `lease-snapshot`: compresses “what authority is live” for supervisors and incident bundles.

See also:
- lease registry + revocation stance: `docs/249-lease-registry-and-cross-lane-revocation.md`
- lease envelope joins: `docs/252-lease-envelope-and-cross-lane-joins.md`
- evidence spine overview: `docs/229-evidence-spine-overview.md`

## Guidance (keep it boring)

1) **Metadata only.** Never embed secret material; summarize resources and use digests for join points.
2) **Always capture denials.** “Denied” issuance/use is often the most valuable signal during IR.
3) **Prefer digests over names.** If a lane has its own grant/receipt, link it by digest.
4) **Bundle-min friendly.** `lease_id` should let tooling pull the minimal set of receipts needed to explain authority.

## References

- Vault leases (TTL/renew/revoke model): https://developer.hashicorp.com/vault/docs/concepts/lease
- Vault lease renew command: https://developer.hashicorp.com/vault/docs/commands/lease/renew

Last updated: 2026-03-07r222
