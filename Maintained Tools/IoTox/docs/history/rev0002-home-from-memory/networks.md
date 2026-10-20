# Network planning: Tox native, Tox over I2P, and Tox over Tor

## Scope statement

rev0002 builds the **Tox/native adapter**, not a complete live-network node. It creates explicit architecture space for **Tox/I2P** and **Tox/Tor**. It does not build direct I2P or Tor peer transports.

Tox remains the primary network by accepted decision. The project will not discard it merely because ownership recovery must be solved above the transport.

## Status vocabulary

```text
reserved           represented in design only
compiled           code builds
adapter-verified   ABI/lifecycle verified against exact test doubles
integration-verified verified against real dependency in a controlled fixture
network-verified   bootstrap, peer exchange, reconnect, and persistence proven
route-verified     overlay route proven with no forbidden fallback/leak
production         target hardware and operational requirements passed
```

Tox/native is currently `adapter-verified`.

## Why three routes can improve connectability

The routes can fail differently:

- Native Tox can use normal UDP/DHT behavior and TCP relays.
- A Tor-routed Tox profile may help where UDP is blocked, native egress is monitored, or an owner deliberately prefers a Tor path.
- An I2P-routed Tox profile may provide connectivity inside an owner-selected I2P environment or between Tox relays exposed through I2P tunnels.

Multiple routes are not automatically redundancy. They need health checks, route policy, identity behavior, reconnection strategy, and clear privacy semantics. Running every route simultaneously can increase traffic, battery use, attack surface, and linkability.

## Tox/native — adapter-verified foundation

The current adapter enables UDP and local discovery using toxcore defaults. Public bootstrap-node and relay configuration has not been added, and the container still lacks a real c-toxcore library. rev0002 therefore makes no public-network claim.

The next native step is typed bootstrap/TCP-relay configuration:

```text
host or numeric IP
UDP bootstrap port
DHT public key
optional TCP relay ports
transport policy
source and update policy
health status
```

Node lists must be data, not compile-time code. IoTox should support owner-controlled lists, deterministic validation, safe refresh, and no mandatory vendor account.

The controlled test fixture should first run isolated bootstrap and relay services. Public-network testing follows after deterministic local behavior is understood.

## Contributing to the Tox commons

IoTox should plan to operate and help owners operate useful Tox infrastructure.

Potential contributions:

- geographically and administratively diverse bootstrap nodes;
- reliable TCP relays;
- reproducible container/systemd/OpenRC deployment;
- health endpoints that expose server status without user tracking;
- signed machine-readable node descriptors;
- load, abuse, and update runbooks;
- upstream bug reports and patches found by IoTox testing;
- long-running compatibility and reconnect reports.

Infrastructure remains optional and replaceable. An IoTox-operated node has no ownership key, authorization ledger access, phrase material, or privileged protocol role.

## Recall-root interaction with Tox

The intended memory-reentry design may derive stable route-specific Tox controller secrets from the recall root. The device retains enough information to contact that owner endpoint and present an owner-signed device certificate.

Real toxcore testing must answer:

- whether secret-key import plus deterministic no-spam reproduces the expected address;
- whether a device can reintroduce itself when the controller has lost the friend list;
- what friend-request and anti-spam behavior is reliable;
- whether separate route identities are required for privacy;
- how savedata caches coexist with deterministic root recovery.

## Tox/Tor — reserved

The likely shape is a Tox instance configured for TCP-only operation plus explicit proxy or local stream-tunnel plumbing. Unresolved questions must be tested rather than assumed:

- whether the chosen SOCKS/tunnel configuration contains every DNS and network action;
- how bootstrap discovery works without accidental native resolution;
- whether public TCP relays, onion-exposed relays, or local forwards are required;
- whether one toxcore instance can switch routes safely;
- whether route-specific Tox identity is necessary;
- reconnect, latency, traffic, and memory behavior on actual hardware.

A Tor route must fail closed. If Tor is unavailable, IoTox must not silently send the same profile over native networking unless owner policy explicitly permits fallback.

## Tox/I2P — reserved

The I2P route likely needs owner-controlled stream tunnels to Tox TCP relay/bootstrap services, or relay services exposed inside I2P. Standard Tox UDP behavior does not map directly onto an I2P stream path. The architecture reserves a route adapter rather than claiming that a generic proxy field proves Tox-over-I2P.

Questions for an experiment:

- Which I2P tunnel type carries toxcore TCP relay traffic correctly?
- Must bootstrap and relay services be reachable at I2P destinations?
- Can a local tunnel present stable loopback endpoints so toxcore sees no clearnet target?
- How are DHT public keys and endpoint descriptors distributed without a vendor service?
- What are setup time, idle traffic, memory, and router-restart behavior?
- Can leak tests prove that native networking is never used?

## Direct I2P and Tor transports — separate future work

A direct overlay transport would implement IoTox's peer-transport contract without Tox friend semantics, custom-packet limits, or toxcore savedata. That is a different engineering program and remains out of scope.

The code reflects that distinction with `TransportKind` and `ToxRoute`, rather than one flat `Network` enum.

## Route policy seed

A future policy could express:

```text
preferred: Tox/native
alternates: [Tox/Tor, Tox/I2P]
fallback: explicit
parallel dialing: disabled by default
route pinning per peer: supported
route health memory: local and bounded
route identity: shared or separated by explicit privacy mode
```

Before enabling multi-route operation, the threat model must decide whether identity reuse defeats the owner's privacy goal. One application owner identity with route-specific Tox endpoint keys is the leading design direction, not yet a frozen protocol.
