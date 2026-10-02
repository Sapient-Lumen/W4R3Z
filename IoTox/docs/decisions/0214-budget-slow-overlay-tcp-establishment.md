# ADR 0214: Budget slow-overlay TCP establishment

Status: accepted construction prerequisite, 2026-08-28.

## Context

The first source-linked IoTox/Tox run through ADR 0213 reached every intended socket boundary: two
agents opened only the strict adapter; two admitted SAM streams reached the persistent Destination;
and two raw loopback streams reached the pinned c-toxcore TCP relay. Carrier truth nevertheless
remained `offline`. A direct strict-SOCKS control reached `tcp` immediately with the same relay
binary, key, and endpoint.

Pinned c-toxcore 0.2.23 initializes `TCP_Client_Connection::kill_at` to ten seconds before it starts
the local proxy negotiation. The same budget therefore includes TCP-to-proxy, SOCKS greeting and
CONNECT, SAM Destination lookup/STREAM creation behind the SOCKS boundary, and the encrypted Tox
relay handshake. The live instrumented retry admitted the SAM stream in 0.468 seconds, but the
relay's complete response reached the client-side boundary only at roughly 34 seconds.
The direct control proves this was not a relay-key or fixture failure.

A second live run with only `TCP_CONNECTION_TIMEOUT` raised to 120 seconds kept the relay stream
alive but still remained `offline`. That result was initially attributed to c-toxcore's shorter
onion-state lifetimes. The later topology audit falsified the attribution: the cell supplied only one
bootstrap record and replaced its real address with `192.0.2.17`, which Tox then embedded inside an
unroutable onion path. With three address-preserving service fronts, this TCP-only provider reached
`tcp` in about twenty seconds and passed the complete two-peer application gate. No onion lifetime
change is justified by this evidence.

Changing `TCP_PING_FREQUENCY` or `TCP_PING_TIMEOUT` would weaken established-carrier loss behavior
and is unrelated to this startup failure. Returning SOCKS success before SAM stream success would
make the strict boundary lie and would still leave the original provider timer running.

## Decision

Carry one exact c-toxcore 0.2.23 slow-overlay patch in the pinned source-linked provider:

```text
TCP_CONNECTION_TIMEOUT = 120 seconds
TCP_PING_FREQUENCY      = 30 seconds (unchanged)
TCP_PING_TIMEOUT        = 10 seconds (unchanged)
```

Name the combined provider variant `iotox-file-rr1-tcp-connect120`. Update Sandwurm receipts, source
provenance, SBOM description, and the strict verifier while retaining acceptance of historical
`iotox-file-rr1` evidence.

Set `i2p.streaming.profile=2` on both SAM construction sessions. This selects i2pd's interactive
streaming profile but does not replace the establishment budget or create a latency guarantee. Add
content-free `setup_us` to each client adapter route decision so future evidence can separate local
SOCKS/SAM setup from later Tox and application convergence.

## Consequences

- Slow overlay streams may complete the encrypted relay handshake instead of being killed by a
  native-network-sized setup constant.
- A dead or black-holed *establishing* TCP candidate may occupy its bounded provider slot for up to
  two minutes. Local-boundary and exact-target health remain separate fast observations.
- Established route-loss detection is not lengthened by this patch; the provider's 30/10 ping
  constants and authoritative connection callbacks are unchanged.
- Onion path, node, announce, and offline lifetimes remain byte-for-byte upstream. The rejected
  onion-retention experiment is not carried in the source-linked provider.
- The 120-second value is a construction budget, not a measured latency objective. It must be
  revisited with I2P populations and failure distributions before production enablement.
- Provider compatibility is now explicitly a source-linked IoTox property. An unpatched external
  c-toxcore 0.2.23 may still fail `tox/i2p-construction` even when every SAM/I2P boundary is correct.

See `docs/i2p-route-construction.md`.
