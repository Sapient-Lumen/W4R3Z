# RFC-0187: Policy-constrained transports

## Problem

Exports need to move bytes (ticketing uploads, vendor portals, HTTPS uploads, OOB media).
When transport is embedded in scripts, it becomes:
- hard to review destinations
- hard to audit what actually happened
- easy to leak secrets into logs

## Proposal

Introduce transport as a typed adapter lane:

- New artifacts:
  - `transport.policy` (`spec/transport.policy.schema.json`)
  - `transport.receipt` (`spec/transport.receipt.schema.json`)
- Extend `export.policy` with optional `transport_policy_digest`
- Extend `export.receipt` with optional `transport_receipt_digest`

## Transport adapter contract (sketch)

- Inputs: artifact digest + size, destination parameters (ticket id, recipient class), transport.policy digest
- Output: transport.receipt (metadata-only), including remote id / status and redacted uri hints

## Why now

Ticketing and vendor portals are the default reality of operations.
First-class transport policies keep DeriveBSD’s “least authority + evidence” story coherent at the boundary where bytes leave.

See also: `docs/255-policy-constrained-transports.md`.
