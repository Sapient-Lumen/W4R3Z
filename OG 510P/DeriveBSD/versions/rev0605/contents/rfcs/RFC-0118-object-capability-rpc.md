# RFC-0118: Object-capability RPC lane (capability-carrying crossings)

Status: **draft**

## Motivation

DeriveBSD needs cross-compartment control operations (host ↔ service-jails ↔ microVMs) without
falling back to ambient naming + ad-hoc ACLs.

We already have:
- capability routing manifests (`docs/140-capability-routing-manifests.md`)
- qrexec-style deny-by-default RPC policy (`docs/135-qrexec-style-rpc-policy.md`)
- portals/powerbox for dynamic grants (`docs/179-portals-and-powerbox.md`)

What’s missing is a standard way to *transport capabilities* across those crossings.

## Goals

- Standardize a capability-carrying RPC substrate for local transports (vsock/unix sockets).
- Make “authority edges” explicit: handoffs are the unit of access.
- Enable lease/revocation semantics via proxies (`RFC-0117`).
- Keep the v0 interface small; do not force a service mesh.

## Non-goals

- Choosing an internet-wide protocol for all time.
- Replacing higher-level policy.
- Making every kernel primitive revocable.

## Proposal

### Substrate candidates

1) **Cap’n Proto RPC** (capability-based by design)
- local, efficient, capability references, promise pipelining

2) **OCapN / CapTP** (interoperable capability transport)
- better fit for multi-language distributed objects and third-party handoff

DeriveBSD can start with Cap’n Proto RPC for host-local crossings, while documenting an OCapN adapter lane.

### DeriveBSD “derive-rpc” lane

- Transport: vsock for microVMs; Unix sockets for service-jails
- Auth:
  - baseline: pinned keys / channel trust roots
  - optional: workload identity binding (SPIFFE/SVID-shaped, `RFC-0116`)

### Minimal capability kinds

- `Control`: start/stop/inspect/attach logs
- `FileStream`: export read-only streams with byte limits
- `SecretOp`: brokered decrypt/sign/token-mint (never raw keys)
- `DatasetOp`: snapshot/clone/promote on explicit datasets

### Evidence

- Policy decision object already exists (`policy.decision`): record allow/deny
- For allowed sessions:
  - transcript digest (no plaintext secrets)
  - portal grants for any long-lived capability references (leases)

## Relationship to existing docs

- qrexec doc remains the policy model; object-capability RPC is the mechanism layer.
- portal brokers can return RPC object references.
- capability routing manifests can specify initial handoff graphs at activation time.

## Security considerations

- Resource-exhaustion defenses must be explicit (rate limits, max message sizes).
- Capability references should be unforgeable and scoped to a session unless explicitly delegated.
- Prefer proxy capabilities for revocation.

## References

- Cap’n Proto RPC overview: https://capnproto.org/rpc.html
- Cap’n Proto FAQ: https://capnproto.org/faq.html
- OCapN overview: https://ocapn.org/
- CapTP draft spec: https://github.com/ocapn/ocapn/blob/main/draft-specifications/CapTP%20Specification.md
