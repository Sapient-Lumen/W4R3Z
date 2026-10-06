# RFC-0170: Portal-activated services and socket activation as a first-class pattern

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD services today are primarily modeled as “start at boot, keep running.”

This creates avoidable complexity:

- boot ordering constraints and dependency cycles
- persistent idle footprint
- upgrade/rollback hazards when the service owns its own listening sockets

Other ecosystems use **socket activation** (systemd, launchd, inetd lineage) to decouple endpoint ownership from daemon lifetime.

DeriveBSD also has a powerful primitive most OSes lack: **portals/powerbox** (policy-mediated grants + evidence).

We want to unify these.

## Goals

- Support **socket-activated** and **portal-activated** services across placements (host/jail/microvm).
- Keep activation behavior **policy-expressible**, **lintable**, and **evidence-bearing**.
- Preserve DeriveBSD’s rollback contract: activation must not create “hidden state” that escapes snapshots.
- Provide a migration path from classic inetd/rc.d styles.

## Non-goals

- Replacing all long-running daemons.
- Standardizing a cross-OS socket-activation ABI.

## Proposal

### 1) Formalize an activator component

Introduce/standardize a supervised service:

- `derive.activatord` (name placeholder)

Responsibilities:

- create and own endpoint(s) specified in svcdb
- observe activity (accept/connect)
- decide whether to start a service instance
- hand off channels to the service (fdpass/proxy/rpc)

### 2) svcdb additions (convention + schema documentation)

For `type: socket-activated`, allow an `activation` object:

- `mode`: `socket` | `portal` | `hybrid`
- `endpoints[]` with:
  - `id`
  - `kind`: `unix` | `tcp` | `vsock` | ...
  - `listen` descriptor
  - `handoff`: `fdpass` | `proxy` | `rpc`
  - `granting`: `none` | `portal`

### 3) Evidence contract

Activation must emit:

- `svc.event` with:
  - trigger type
  - endpoint id
  - caller identity (when known)
  - resulting instance id / placement

When policy-mediated:

- `policy.decision`
- `portal.grant` (for connection lease) when granting is `portal`

### 4) Rollback interaction

- Endpoints live in the currently booted generation’s runtime directory (e.g. `/run/derive/activator/...`) and are destroyed on reboot.
- When switching generations, the new activator configuration takes effect atomically.
- Rollback must restore the previous activator + endpoint set.

### 5) Microvm specifics

For microvms:

- `handoff=proxy` is acceptable early (activator proxies traffic into a booting microvm).
- `handoff=rpc` is preferred for richer capability semantics.

## Alternatives considered

- Keep inetd-style config only (doesn’t integrate with portals/evidence).
- Systemd-style socket units (powerful, but not portable to BSD without adopting the whole stack).

## References

- systemd socket units: `systemd.socket(5)`.
- launchd socket activation APIs (`launch_activate_socket`) and `launchd.plist(5)`.

## Related work in this archive

- `docs/238-portal-activated-services-and-socket-activation.md`
- `docs/179-portals-and-powerbox.md`
- `docs/214-service-supervision-health-as-evidence.md`
- `spec/svcdb.schema.json`
