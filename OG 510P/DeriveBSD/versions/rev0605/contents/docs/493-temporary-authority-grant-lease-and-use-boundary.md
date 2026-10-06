# Temporary authority grant / lease / use boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

DeriveBSD already had a useful temporary-authority pattern, but one boundary was still too folkloric:

> which object actually grants temporary power, and which objects are only evidence that the power was issued or used?

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD keeps **temporary authority** and **temporary-authority evidence** separate.

The authoritative object remains lane-specific:

- `portal-grant`
- `secret-grant`
- `breakglass-grant`
- `workload-identity-lease`
- other lane-specific grant / lease / session objects

The generic evidence lane is:

- `lease.envelope`
- `lease.issue.receipt`
- `lease.use.receipt`
- `lease-snapshot`
- `lease-revoke-event`

That means:

- a `lease.envelope` is not a grant
- a `lease.issue.receipt` is not temporary authority
- a `lease.use.receipt` is not the authoritative result of the later operation
- the lane-specific grant / lease / session object remains the source of temporary authority

## `lease.envelope` points at authority, not later action evidence

`spec/lease.envelope.schema.json` stays metadata-only.
Its `target` exists to point at the object that actually grants temporary authority.

In practice, `target.kind` should name a lane-specific grant / lease / session object such as:

- `portal-grant`
- `secret-grant`
- `breakglass-grant`
- `workload-identity-lease`

It should **not** point at later action evidence such as `export.receipt` or `secret-receipt`.
Those later receipts describe what happened when the authority was exercised.
They are not the authority object itself.

## `lease.issue.receipt` stays issuance evidence only

`spec/lease.issue.receipt.schema.json` now carries `authority_semantics = lease-issue-evidence-only`.

That object records:

- which lane minted or denied authority
- which `lease_id` was involved
- which authoritative target object was created or consulted
- which policy and approvals were used
- why the issuance was allowed, renewed, or denied

This makes issuance legible and replayable.
It does **not** replace the lane-specific grant / lease / session object.

## `lease.use.receipt` stays use evidence only

`spec/lease.use.receipt.schema.json` now carries `authority_semantics = lease-use-evidence-only`.

That object records:

- which `lease_id` was exercised
- what high-level operation was attempted
- whether the use was allowed or denied
- optional machine-readable reasons
- optional linkage to the operation's own evidence object via `related`

This keeps “authority was used” queryable without confusing use evidence with authority.

## Operation receipts belong under `lease.use.receipt.related`

When an operation produces its own authoritative or lane-specific receipt, that later object should be linked from `lease.use.receipt.related`.

Examples:

- `export.receipt`
- `secret-receipt`
- `breakglass-receipt`
- `workload-identity-issue-receipt`

This is the right place to answer:

- what did the lease authorize in practice?
- which action receipt explains the later operation?

It is **not** the right place to redefine what object granted temporary authority in the first place.

## Why this is the right narrow decision

This does not redesign any temporary-authority lane.
It only makes one cross-lane pattern explicit:

- grant / lease / session = authority
- `lease.envelope` = metadata join
- `lease.issue.receipt` = issuance evidence
- `lease.use.receipt` = exercise evidence
- lane-specific operation receipt = later action evidence or result

That is a small change, but it removes the kind of archive ambiguity that becomes expensive during implementation and incident review.

## Product-shape fit (A–D without forks)

- **A / fleet host:** brokered temporary authority stays reviewable and revocable without confusing runtime actions with the grants that enabled them.
- **B / workstation:** consent-heavy lanes can explain both the grant and the later use without collapsing them into one opaque blob.
- **C / general-purpose OS:** compatibility paths stay possible because the pattern is generic and incremental rather than tied to one broker backend.
- **D / appliance factory / regulatory:** temporary maintenance authority gains cleaner evidence for issuance, use, and revocation while preserving narrow authoritative grant objects.

## Related docs

- `adrs/ADR-0083-temporary-authority-grant-lease-and-use-boundary.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`
- `docs/252-lease-envelope-and-cross-lane-joins.md`
- `docs/449-lease-issue-and-use-receipts.md`
- `docs/229-evidence-spine-overview.md`
- `spec/lease.envelope.schema.json`
- `spec/lease.issue.receipt.schema.json`
- `spec/lease.use.receipt.schema.json`

Last updated: 2026-03-07r222
