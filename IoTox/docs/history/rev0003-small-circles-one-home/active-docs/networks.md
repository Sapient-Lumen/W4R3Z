# IoTox network stacks

## Core distinction

IoTox separates the peer protocol from the route used beneath it.

```text
peer transport: Tox
route:          native | future Tor | future I2P
```

This gives one Tox family:

```text
Tox/native
Tox/Tor
Tox/I2P
```

Potential direct transports are separate:

```text
Tor-direct
I2P-direct
```

They would not automatically inherit Tox identity, friendship, custom packets, file
transfer, bootstrap, relay, or savedata semantics.

## rev0003 status

| Stack | Status | Meaning |
|---|---|---|
| Tox/native | adapter-verified | IoTox lifecycle and packet boundary runs against an exact C++ c-toxcore ABI mock; real c-toxcore/network proof remains pending |
| Tox/Tor | reserved | Future explicitly configured TCP-only Tox route through Tor-compatible plumbing |
| Tox/I2P | reserved | Future explicitly configured Tox bootstrap/relay route through I2P plumbing |
| Tor-direct | out of scope | Separate later peer transport without Tox semantics |
| I2P-direct | out of scope | Separate later peer transport without Tox semantics |

Reserved routes fail explicitly. They never silently become native routes.

## Tox/native first

The next network gate is a pinned real c-toxcore build and a controlled two-peer fixture.
Required evidence includes:

- official-header compilation;
- explicit bootstrap and TCP relay configuration;
- two genuine identities;
- `HELLO` exchange;
- savedata restart;
- disconnect and reconnect;
- relay-only behavior;
- one file transfer;
- memory, descriptors, threads, idle CPU, and traffic;
- target-device follow-up measurements.

The public Tox network may later be tested, but deterministic integration should not
depend exclusively on public infrastructure.

## Tox infrastructure contribution

IoTox intends to contribute useful Tox infrastructure and engineering work, potentially:

- public bootstrap nodes;
- TCP relays;
- owner-operated server tooling;
- reproducible deployment and upgrades;
- capacity and health monitoring;
- network behavior reports;
- documentation and upstream fixes.

Operating infrastructure grants no IoTox ownership, authorization, recovery, namespace
membership, or object-decryption authority.

## Tox/Tor research shape

Tor provides stream circuits rather than toxcore's ordinary UDP environment. A credible
route likely requires:

- UDP disabled;
- local discovery disabled;
- TCP-only toxcore behavior;
- explicit proxy or stream tunnel;
- reachable Tox TCP relays/bootstrap endpoints;
- no native DNS or silent direct fallback;
- route-leak tests at socket and packet level;
- measured bootstrap, reconnect, latency, traffic, and memory behavior.

Open architecture question: can one Tox instance switch route policy safely, or should
native, Tor, and I2P use separate configured instances/endpoints? Separate instances may
improve isolation but increase identity, memory, synchronization, and deduplication work.

## Tox/I2P research shape

A plausible experiment uses local I2P stream tunnels and Tox TCP relay/bootstrap
services reachable through the overlay. It may require owner-operated or community
relay endpoints inside I2P.

Required evidence includes:

- reproducible local tunnel configuration;
- no clearnet bootstrap or DNS leak;
- reconnect after I2P router restart;
- stable endpoint and destination distribution policy;
- idle and active resource measurements;
- relay capacity and failure behavior;
- interaction with route identities and RecallRoot re-entry.

Until an end-to-end fixture passes, Tox/I2P remains research rather than claimed
functionality.

## Multi-route policy

Having three possible routes can improve reachability, but blindly dialing all three
can increase traffic, battery cost, server load, and identity linkability.

Future policy should make explicit:

```text
preferred route
allowed fallbacks
forbidden fallbacks
parallel dialing allowed or prohibited
route pinned for a peer
route health memory
leak policy
identity mode
```

A privacy-sensitive choice must not be overridden by an automatic “helpful” native
fallback.

## Route identity privacy

One Tox identity reused across native, Tor, and I2P is directly linkable. Separate route
Tox identities reduce that linkage but complicate owner re-entry, authorization, peer
mapping, and revocation.

The likely architecture is a stable IoTox application identity with signed bindings to
replaceable route endpoint identities. The exact derivation and rotation policy is not
frozen.

## Mutorr above the network

Mutorr consumes authorized application identities and produces namespace-neighbor and
custodian plans. It does not open sockets, decide routes, or make peers legitimate.

```text
Mutorr Cube for namespace A
            |
union of required application peers
            |
IoTox connection scheduler
            |
Tox/native or explicit future route
```

A peer may be a neighbor in several namespaces. One Tox relationship should be reused.
A Tox friend may be online but absent from every authorized Cube.

Custodian placement is independent of route choice. A future scheduler may consider
liveness and route cost when selecting a source, but it must not silently change the
authorized replica policy.
