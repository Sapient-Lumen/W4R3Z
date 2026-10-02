# ADR 0203: Qualify two independent Tor route workers

Status: accepted, implemented, and first live sample qualified, 2026-08-27.

## Context

The retained operator-Tor gate proves one IoTox transport reaches one public Tox relay through a
real Tor process. The mixed-route Sandwurm gate proves two IoTox Agents converge through native and
strict generic-SOCKS workers. Neither proves that two independently keyed IoTox auxiliaries can
discover, authenticate, and carry application synchronization through actual Tor.

One shared Tor daemon would make both guest streams visible in one process and weaken route/source
attribution. Replacing all Sandwurm rendezvous with public infrastructure would also turn the native
control paths into an uncontrolled variable.

## Decision

Add explicit scenario `sync-tree-route-private-actual-tor`, available only with a native UDP
primary. Keep both primary transports and first bulk workers on the pinned host fixture. Bind the
second exact-key TCP worker in each guest to its own endpoint catalog from ADR 0202 and to one of two
separate host Tor clients:

```text
client guest 10.0.0.11 -> 10.0.0.1:39051 -> client Tor
device guest 10.0.0.12 -> 10.0.0.1:39052 -> device Tor
```

Each Tor instance has a separate data directory, control socket, authentication cookie, process,
source-only SOCKS policy, and circuit population. The operator must supply an exact public IPv4 Tox
bootstrap/TCP-relay record; the runner never downloads or substitutes one.

Retain authenticated extended STREAM/CIRC events, bootstrap and circuit-status projections, Tor
process-owned public-socket commitments, both guest TAP captures, and normal IoTox receipts. The
offline verifier must independently join each exact guest source through NEW and SUCCEEDED to a
built three-or-more-hop `GENERAL` or `CONFLUX_LINKED` circuit targeting only the supplied Tox node.
It must also require two distinct process IDs/control-socket inodes and role-specific packet
containment. The same signed 4,194,389-byte tree and private route-binding v2 conditions remain the
application gate.

## Consequences

- Accepted compact proof `pair.2mycvy9n` closes the first two-IoTox actual-Tor auxiliary-route
  sample without conflating it with the generic SOCKS forwarder. Both roles reached two ready bulk
  members and converged the signed 4,194,389-byte tree while their exact Tor members used separate
  three-hop `CONFLUX_LINKED` circuits.
- Native fixture traffic remains an explicit non-contained control class; only the exact Tor worker
  is claimed to cross Tor.
- This baseline does not attribute the tree's object bytes to the Tor worker. Forced-carrier
  payload and Tor loss/recovery remain separate gates.
- One public node, two Tor circuits, one host, and one time window do not prove anonymity,
  correlation resistance, public relay reliability, physical path independence, long-duration
  recovery, or representative deployment behavior.
