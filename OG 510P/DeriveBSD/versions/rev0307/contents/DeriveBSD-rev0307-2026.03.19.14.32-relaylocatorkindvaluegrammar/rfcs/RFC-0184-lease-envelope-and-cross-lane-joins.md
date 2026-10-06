# RFC-0184: Lease envelope and cross-lane joins

Status: Draft

## Problem

Temporary authority exists in multiple lanes (secrets, portals, tracing, breakglass).
Even with a standardized `lease_id`, operators still need a stable way to:
- join lease snapshots with lane-specific grants/sessions
- revoke a lease and route revocation correctly
- include “authority context” in incident bundles

## Goals

- Keep lane schemas stable.
- Provide a single cross-lane join object with consistent identifiers.
- Enable uniform tooling (`lease ls`, `lease revoke`).

## Proposal

1) Add `lease.envelope` (metadata only):
   - canonical `lease_id`
   - issuer/subject selectors
   - time bounds
   - routing pointer: (lane, target kind, target digest)

2) Extend `lease.snapshot` entries with optional `envelope_digest`.

3) Encourage lanes to either:
   - mint envelopes at issuance, or
   - allow the lease registry to synthesize them.

References:
- `docs/252-lease-envelope-and-cross-lane-joins.md`

