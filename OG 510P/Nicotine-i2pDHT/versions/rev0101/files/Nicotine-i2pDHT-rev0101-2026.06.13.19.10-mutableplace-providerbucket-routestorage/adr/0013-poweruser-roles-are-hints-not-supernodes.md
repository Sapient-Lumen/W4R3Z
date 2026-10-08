# ADR-0013 — Power-user roles are hints, not supernodes

## Status

Accepted as a rev0004 design guess.

## Decision

The DHT may expose contribution roles such as gate, scout, archivist, sentinel, mirror, and publisher.  These roles are local capability hints and budget commitments.  They are not authority, consensus votes, or trusted routing privileges.

## Rationale

A future populous network needs ways for high-uptime users to help.  But if “helpful” nodes become privileged truth sources, the DHT has merely recreated centralization under another name.

## Consequences

- Lookup and validation logic must work without trusting role claims.
- Role claims can influence caching, batching, and bootstrap preference.
- Malicious nodes can lie about roles; the design must treat that as expected.
