# RFC-0131: Capability activation + escrow (restart-safe authority without ambient namespaces)

Status: draft

## Motivation

DeriveBSD is leaning hard into least authority (Capsicum, caproute manifests, portals, leases).
However, real deployments also need:

- on-demand startup
- crash-only restarts
- stable endpoints for clients

If services must reacquire authority on every start (open paths, bind ports, query registries), we drift back toward ambient namespaces.

## Proposal

Introduce a small **activation broker** component that:

1. realizes a derived `activation.capset` for each service instance
2. pre-opens and rights-minimizes the referenced kernel handles
3. launches the service in capability mode and hands off the handle set
4. retains (escrows) broker-owned handles across restarts
5. emits a signed `activation.claim` receipt when the child acknowledges the capset

The broker is an **authority boundary**: it is the only component allowed to open/bind certain resources for services.

## Evidence objects

### `activation.capset` (signed)

A capset is a derived, signed description of what a service instance may receive.

Required bindings:

- service identity (name + digest)
- generation/plan context digest
- a list of named capabilities:
  - `cap_ref` (opaque broker reference)
  - type (socket/dir/file/rpc/portal/trace/budget)
  - rights list (type-specific)
  - optional `lease_id` when the handle is mediated/revocable

### `activation.claim` (signed receipt)

Emitted by the broker when the child instance:

- enumerates the named handles it received
- confirms the service digest it believes it is
- (optionally) proves it entered capability mode

The claim binds:

- capset digest
- instance id
- process identity (pid, jail id, microVM id)
- list of capability names claimed

## Hand-off ABI (v0)

- broker passes fds using standard Unix inheritance / fd passing
- names are provided via:
  - `DERIVE_ACTIVATION_CAPSET_DIGEST`
  - `DERIVE_FD_NAMES=name1:name2:...` aligned with ordering

Libraries may provide:

- `derive_activation_get_fd("name")`

## Escrow semantics

Escrow applies only to handles the broker owns and can retain safely.

- listen sockets: broker keeps open and reissues to new instance
- rpc endpoints mediated by broker: broker keeps server endpoint
- directories/files: broker may keep open, but policy should prefer fresh-open patterns when possible

Escrow does not override lease expiry. If a handle is backed by a lease, expiry/revocation is authoritative.

## Threat model notes

- Compromise of a service should not allow it to open/bind new resources; it can only use its handed-off handles.
- Compromise of the broker is high impact; keep it small, audited, and (ideally) in its own compartment with strong hardening.
- Claims are not a full attestation; they are accountability evidence for "what was handed out".

## Integration points

- caproute graph linting should validate capset contents against manifests
- portals may mint capsets for interactive sessions (policy + consent receipts)
- observed handles should be representable in capability graphs for review

## Open questions

- How to represent non-fd capabilities (e.g., CHERI caps) in capset v0 without widening scope?
- Should broker be per-host or per-compartment?
- How to express blue/green swaps (two instances sharing an escrowed listener) safely?

