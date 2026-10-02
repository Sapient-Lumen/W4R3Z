# ADR 0215: Preserve Tox node addresses across I2P service fronts

Status: accepted construction rule, 2026-08-28.

## Context

The first Tox-over-I2P carrier cells mapped a documentation address such as `192.0.2.17:33445` to
an I2P Destination. Raw TCP and the encrypted Tox relay handshake crossed that mapping, but carrier
truth stayed `offline`. A one-record direct SOCKS control also stayed offline, while a three-record
direct control reached `tcp`.

Tox bootstrap records are not mere socket locators. c-toxcore also uses their numeric addresses as
onion path nodes and embeds those addresses in packets sent through a TCP relay. Replacing a real
node address with a locally invented alias therefore tells the remote relay to forward onion traffic
to the alias. A SOCKS adapter cannot repair that encrypted protocol-layer address after the fact.

Fresh TCP-only c-toxcore also needs a useful node population. The successful control supplied three
distinct bootstrap/TCP-relay records, matching c-toxcore's three recommended onion TCP connections.
One new, otherwise unconnected local `DHT_bootstrap` process was a valid TCP server but not a
substitute for that population.

## Decision

- The left side of every I2P adapter map is the exact real numeric Tox node endpoint also supplied to
  c-toxcore. Documentation-only aliases are forbidden for Tox carrier qualification.
- Fresh I2P construction gates supply at least three explicit bootstrap records and three explicit
  TCP-relay records. The real-peer harness enforces that lower bound for this route.
- Each exact node endpoint maps to an explicit canonical b32 Destination. The current single-target
  service forward therefore uses one persistent Destination per node front.
- The Destination terminates at a numeric-loopback service. A bounded operator egress shim may then
  reach the exact public Tox node for construction; IoTox itself still opens only adapter sockets.
- No public node catalog becomes an IoTox default. Records and mappings remain explicit operator
  input, and their observed health is evidence-time state rather than permanent project authority.

The live falsification used three currently healthy public records. The address-preserving I2P cell
reached `self-connection=tcp` in about twenty seconds with the TCP-establishment-only
`iotox-file-rr1-tcp-connect120` provider. The complete two-peer smoke then passed friendship,
protocol confirmation, authority, text, durable command, exact file, two process restarts, ownership
epoch transition, and friendship removal/re-add.

## Consequences

- The I2P adapter remains a transport selector, not a Tox address-translation layer.
- A single I2P service front can prove raw streams and relay handshake establishment but is not a
  fresh TCP-only Tox network qualification topology.
- The rejected onion-timeout patch is not carried. Upstream onion lifetimes, request cadence, and
  established TCP ping behavior remain unchanged; only the already-accepted connection setup budget
  is longer.
- The pass proves actual I2P carriage on one physical host. It does not prove anonymity, independent
  router operators, guest packet containment, service availability, or production suitability.

See `docs/i2p-route-construction.md` and
`docs/evidence/2026-08-28-actual-i2p-real-peer-e2e.md`.
