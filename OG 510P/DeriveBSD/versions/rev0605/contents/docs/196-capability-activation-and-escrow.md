# Capability activation + escrow (restart-safe authority without ambient namespaces)

In a capability-first system, a service should not need ambient global namespaces (filesystem paths, well-known ports, "the network") just to start.
But real systems also need:

- **on-demand startup** (don't run everything always)
- **crash-only restarts** (services die; authority shouldn't)
- stable **listen sockets** and other pre-opened resources

This document sketches an **activation broker** pattern that makes those properties compatible with least authority.

## Problem

If a service obtains authority by "opening" things at startup, you tend to get:

- broad ambient access (it must be able to open sockets, dirs, devices)
- brittle restart behavior (clients must rediscover endpoints)
- policy code in init scripts instead of reviewable manifests

## Pattern: activation broker owns the handles

An **activation broker**:

- pre-opens the capabilities a service needs (sockets, dirs, datasets, rpc endpoints)
- applies Capsicum rights minimization to each handle before handoff
- starts the service in capability mode, **passing only those handles**
- **escrows** handles across restarts (if the service dies, the broker keeps them and can re-issue)

This is the capability-native analogue of "socket activation", generalized beyond network sockets.

## DeriveBSD mapping

### Inputs

- a derived **service graph manifest** (see `docs/114-service-manifests-smf-lessons.md`)
- a derived **caproute manifest** (see `docs/140-capability-routing-manifests.md`)
- policy decision records for any cross-compartment edges (`docs/93-policy-decision-records.md`)

### Outputs

- `activation.capset` (signed): the named handles a service instance is allowed to receive
- `activation.claim` (receipt): what the instance actually claimed/acked

These become part of explainability:

- activation diffs show *authority diffs* (not just file changes)
- postmortems can answer "what did this process have, exactly?"

## Design notes

### Naming + discovery

To avoid the "fd 3 means what?" problem:

- each capability in a capset has a **stable name**
- the runtime provides a small library (or env var) mapping name → fd
- capability graphs (`docs/189-capability-graph-lint-and-viz.md`) can lint and diff names

### Escrow semantics

Escrow is easiest for broker-owned objects:

- listen sockets
- pre-opened directories / files
- mediated RPC endpoints

Escrow is **not** a magic "keep everything alive" layer. If the capability is itself a lease
(e.g. `portal.grant` with `lease_id`), escrow means:

- broker can renew/rebind within policy
- broker can record revoke/expiry events (`docs/182-capability-leases-and-revocation.md`)

### Interaction with portals / consent

Portals (`docs/179-portals-and-powerbox.md`) handle *interactive acquisition*.
Activation broker handles *non-interactive, derived authority*.

If a service needs a human-mediated resource, it should receive:

- a **portal client capability** (request channel)
- not the final resource directly

### Interaction with object-capability RPC

For services that expose an API, prefer capability-carrying RPC (`docs/183-object-capability-rpc.md`).
Activation then hands out:

- the server's receive endpoint
- the client's send endpoint

Clients need not rediscover by path or name.

## Non-goals

- replacing rc.d as the host orchestration backend (see `docs/86-host-activation-rcd-and-service-jails.md`)
- universal live-upgrades of arbitrary internal state
- making every possible kernel object escrowable (start with fds + mediated handles)

See RFC-0131.

Last updated: 2026-02-24
