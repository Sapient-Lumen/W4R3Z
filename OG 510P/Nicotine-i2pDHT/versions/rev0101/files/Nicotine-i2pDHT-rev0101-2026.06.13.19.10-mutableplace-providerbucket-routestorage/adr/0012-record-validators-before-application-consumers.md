# ADR 0012 — Record validators before application consumers

Decision: every record family needs core validation before future application
semantics are added.

Rationale: DHT storage nodes should validate universal properties — signatures,
size, expiry, target matching, monotonic sequence — without understanding every
application namespace.

Consequence: app-specific search/index features remain deferred until validators
and wire records are stable.
