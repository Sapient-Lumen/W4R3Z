# 238 Portal-activated services and socket activation

DeriveBSD already treats **dynamic authority** as a first-class concept via portals/powerbox (typed requests → policy decision → narrow grants + receipts).

This doc folds a classic “juicy” service-management idea into that same shape:

- **Socket activation** (systemd/launchd/inetd lineage): create listening endpoints *outside* the daemon; start the daemon on demand; hand it the already-open sockets.
- **Portal activation** (DeriveBSD twist): treat *service endpoints* as capability objects that can be granted (leased, revocable) via the portal system.

The goal is to make “start this service only when needed” work across placements (host/jail/microvm) while preserving:
- least authority
- explicit policy boundaries
- evidence output (who/what caused activation)
- deterministic rollback semantics

## Why this belongs in the ground floor

Socket activation is not novel, but it reliably solves three persistent problems:

1) **Boot ordering disappears**: dependency cycles get easier because endpoints can exist before the service.
2) **Idle footprint shrinks**: cold services cost nothing until used.
3) **Safer upgrades**: new binaries can be staged while the activator continues to own the listening socket.

DeriveBSD’s added leverage is that activation itself becomes:
- a **policy-mediated action** (like any portal grant)
- an **evidence-emitting transition** (like any change-set step)

## Model

### Entities

- **Activator** (supervised): owns “pre-created endpoints” and launches services on demand.
- **Service** (host/jail/microvm): receives already-open endpoints (FDs / channels) and begins handling requests.
- **Policy engine**: may approve/deny activation and/or connection grants.

### Endpoint types

- `unix`: AF_UNIX sockets with explicit filesystem ownership + perms
- `tcp`: bound port(s) with explicit listen policy
- `vsock`: host↔microvm
- `virtio-console`/`virtio-vsock` style channels
- `named-pipe`/`fifo` (rare; mostly for compatibility)

### Activation vs connection

We separate:

- **Activation**: start the service because a request arrived.
- **Connection grant**: allow a specific caller/workload to connect to an endpoint.

Depending on the threat model, you can choose:

- **Activation-only gating**: service starts when any request arrives; access control happens inside the service.
- **Connection gating via portals**: callers must obtain a `portal.grant` to connect; activator enforces that gate.

DeriveBSD should support both, but the default for high-risk services should be “connection gating.”

## Evidence

Every activation should emit (at least):

- a `svc.event` record with:
  - trigger type (incoming connection, policy decision, timer, admin)
  - endpoint id
  - caller identity (when known)
  - service instance id / placement

Optional (recommended when policy-mediated):

- `policy.decision`
- `portal.grant` (connection lease)

## svcdb shape

svcdb already supports `type: socket-activated`.

For socket-activated services, add a conventional `activation` object to the service entry:

- `activation.mode`: `socket` | `portal` | `hybrid`
- `activation.endpoints[]`:
  - `id`
  - `kind`: `unix` | `tcp` | `vsock` | ...
  - `listen`: address/port/path
  - `handoff`: `fdpass` | `proxy` | `rpc`
  - `granting`: `none` | `portal` (if callers must obtain a grant)

The schema is intentionally flexible because host/jail/microvm handoff differs.

## Microvm specifics

For microvms, the activator may:

- start a *minimal* microvm skeleton early (fast resume)
- or cold-boot on first request

For handoff, prefer:

- vsock: activator accepts connection → starts microvm → forwards/bridges, or gives the microvm a pre-opened host channel
- virtio-vsock “well-known CID/port” with the activator owning the listening policy on the host side

## Guardrails

- **No ambient listeners by default**: privileged ports should require explicit policy approval.
- **Explicit ownership**: the activator must own the socket path/port in a way that can’t be silently stolen.
- **Upgrade safety**: activator remains stable across service updates; only service payload changes.
- **Anti-DoS**: rate-limit activations; include exponential backoff + “enter maintenance” semantics.

## References

- systemd socket units and activation semantics: `systemd.socket(5)` and related docs.
- launchd socket acquisition APIs (`launch_activate_socket`) and `launchd.plist` socket dictionaries.
- SMF/restarter designs can combine service dependencies with stronger fault boundaries.

## Related docs

- Portals/powerbox: `docs/179-portals-and-powerbox.md`
- Object-capability RPC: `docs/183-object-capability-rpc.md`
- Service model + svcdb: `docs/214-service-supervision-health-as-evidence.md`
- Health gates + rollback: `docs/112-health-gated-updates.md`
- Process contracts / service ownership (where available): `docs/235-process-contracts-and-service-ownership.md`

- Inbound listen broker lane (listening sockets as leases): `docs/286-inbound-listen-broker-and-firewall-leases.md`
