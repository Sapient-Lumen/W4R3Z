# Network egress as a capability-mediated service

Traditional UNIX networking is effectively ambient authority: if a process can call `socket()` and `connect()`, it can talk to the world.

DeriveBSD wants:
- compartments that can run with *no* network by default
- explicit, reviewable, revocable network grants
- audit receipts that explain “what traffic happened” without requiring root

## Lessons to steal

- **Casper** demonstrates “brokered services for capability-mode programs” in FreeBSD, including `system.dns` (accessible via `cap_dns` / `libcasper`).
- **Capability routing** systems (e.g., Fuchsia) keep access explicit and reviewable; networking APIs become routed protocols, not ambient globals.

## Proposed primitive

Introduce `system.net` (a broker) and a first-class evidence object:
- `net-egress-grant` (signed): authorizes a subject to perform limited network actions
- `net-flow-receipt` (signed): records connections/flows permitted under a grant

### Model

A sandbox VM/jail typically has **no direct egress**.
To make an outbound connection it must:
1) hold a `net-egress-grant` with `connect` permission
2) request a **flow handle** from `system.net` (capability RPC)
3) use that flow handle to exchange bytes (proxy/NAT/VNET attachment are implementation details)

DNS is handled either by:
- `system.dns` (Casper adapter) or
- a `system.net` DNS sub-API
… but in both cases, DNS becomes a **mediated capability**, not a libc ambient.

See: `docs/305-dns-mediation-and-hostname-binding.md`.

### Why a broker?

Capsicum capability mode alone does not make network “go away”; egress is not a global namespace in the same way as the filesystem. A broker gives DeriveBSD:
- a single policy enforcement point (per-plan, per-workload)
- revocation/lease semantics aligned with the rest of the archive
- receipts and redaction hooks that are digest-pinned

## Evidence objects

### `net-egress-grant`

Defines:
- subject (workload identity: name + digest)
- allowed actions:
  - DNS lookup (optional)
  - connect rules (proto + port range + host patterns and/or CIDR)
- constraints:
  - lease id / expiry
  - max flows, byte budgets (tie into `193-resource-budget-capabilities.md`)
- signature by an issuer (policy engine / portal broker)

### `net-flow-receipt`

Records:
- which grant was used (digest)
- what flows were created (remote IP/port, protocol)
- optional hostname provenance (if DNS mediation is used)
- bytes counters and outcomes
- optional redaction transform digest (align with `195-deterministic-redaction-transforms.md`)

## Integration points

- `171-vnet-jails-network-compartments.md`: VNET compartments + pf anchors are a coarse boundary; `net-egress-grant` is the fine-grained “who can talk to what” layer.
- `179-portals-and-powerbox.md`: desktop apps can request network grants interactively (with consent receipts).
- `189-capability-graph-lint-and-viz.md`: treat “internet egress” as a dangerous edge category; require explicit review.

## Open questions

- Do we want separate grant types for “raw sockets / packet capture” (very high risk) vs normal connect?
- Should DNS be mandatory-mediated when `connect` rules use hostnames (to avoid TOCTOU)? (default: yes; see `docs/305-dns-mediation-and-hostname-binding.md`)
