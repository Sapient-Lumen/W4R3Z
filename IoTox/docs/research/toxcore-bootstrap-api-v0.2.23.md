# c-toxcore bootstrap and relay API — v0.2.23, rev0005 reading

**Primary API source:** https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h  
**Reviewed:** 2026-08-13

## Contract used by IoTox

IoTox consumes the public options/lifecycle and connectivity calls through a narrow ABI table. The configured Tox instance is created with accessor functions rather than direct `Tox_Options` field access.

Bootstrap and relay endpoints are modeled as:

```text
host
port
32-byte public key
source/provenance metadata outside the wire call
```

The public calls report immediate argument/lookup outcomes. They do not prove that a node is trustworthy, reachable, connected, or suitable for ownership policy.

## Product interpretation

Bootstrap nodes and TCP relays are roads. They are not:

- owners;
- friends;
- authorization records;
- data custodians;
- vendor recovery authorities;
- proof that an endpoint is healthy.

rev0005 includes a frozen default-node snapshot and allows complete operator replacement through repeatable `--bootstrap` and `--tcp-relay` arguments. `--no-default-bootstrap` and `--no-default-relays` permit an owner to use only explicitly supplied infrastructure.

Endpoint syntax is validated before the owner thread starts:

```text
HOST:PORT:64-HEX-PUBLIC-KEY
```

The current CLI does not resolve or test nodes ahead of toxcore. Retry observations are exposed as events and status; success remains a toxcore/network result.

## Route policy

```text
Tox/native    enabled research route
Tox/Tor       reserved, explicit failure
Tox/I2P       reserved, explicit failure
Tor-direct    separate future transport
I2P-direct    separate future transport
```

A requested reserved route must fail before toxcore starts. Native fallback is not allowed because that would violate the operator's routing intent.

Future Tox/Tor and Tox/I2P work must determine how bootstrap names, DNS, UDP, TCP relays, proxy configuration, and leak prevention interact. The existence of toxcore proxy options is not evidence that the complete route works.

## One-binary startup sequence

The intended sequence is:

1. parse and validate route plus endpoints;
2. load savedata atomically or create a new identity;
3. choose linked toxcore by default when compiled in, otherwise explicit runtime provider;
4. construct options through public accessors;
5. create `Tox*` on the owner thread;
6. register callbacks;
7. apply bootstrap and relay endpoints;
8. publish private local runtime/control surfaces;
9. iterate and retry according to bounded policy;
10. save after identity/friend mutations and on orderly shutdown.

## Evidence boundary

The exact loadable mock verifies that IoTox passes parsed host, port, and public-key bytes through its consumed ABI. It does not resolve DNS, perform DHT bootstrap, make a relay connection, traverse NAT, encrypt a session, or prove the frozen endpoints are currently live.

Real-network verification remains a separate gate and must retain endpoint configuration, timestamps, route policy, toxcore revision, and observed connection transitions.
